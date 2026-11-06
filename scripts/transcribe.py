#!/usr/bin/env python3
"""Transcribe raw clips into numbered utterances with word times.

Each clip is split at pauses into short chunks (<= 16 s). Every chunk is transcribed on its own, padded with
silence (not with neighbouring audio, which makes Whisper invent half words). Transcribing whole files hides
retakes: Whisper merges repeated sentences and drops repeated words.

usage:
  python3 scripts/transcribe.py --project . src/*.mov [--lang en] [--backend auto|faster-whisper|whisperkit]
                                [--model large-v3] [--thr -50]
writes:
  work/clips.json                  clip id -> source path
  work/env/<id>.npy                10 ms energy envelope (dB), used by cuts.py
  work/transcripts/<id>.json/.txt  utterances: start, end, text, words [[start, end, word], ...] in source seconds
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (ENV_HOP, envelope, fmt_time, load_json, project_paths, save_json,  # noqa: E402
                     speech_regions, speech_threshold)

SR = 16000
PAD = 0.3          # seconds of silence around each chunk
SPLIT_GAP = 0.42   # a pause this long starts a new utterance
MAX_CHUNK = 16.0   # longer utterance groups are split at their largest pause


def clip_id(path, taken):
    base = re.sub(r'[^a-z0-9]+', '-', os.path.splitext(os.path.basename(path))[0].lower()).strip('-') or 'clip'
    cid, k = base, 2
    while cid in taken and taken[cid] != path:
        cid, k = f'{base}-{k}', k + 1
    return cid


def plan_chunks(regions):
    groups = []
    for a, b in regions:
        if groups and a - groups[-1][-1][1] < SPLIT_GAP:
            groups[-1].append([a, b])
        else:
            groups.append([[a, b]])
    out = []

    def cut(rs):
        if rs[-1][1] - rs[0][0] <= MAX_CHUNK or len(rs) < 2:
            out.append([rs[0][0], rs[-1][1]])
            return
        gi = max(range(1, len(rs)), key=lambda i: rs[i][0] - rs[i - 1][1])
        cut(rs[:gi])
        cut(rs[gi:])

    for rs in groups:
        cut(rs)
    return out


def pick_backend(name):
    if name in ('auto', 'faster-whisper'):
        try:
            import faster_whisper  # noqa: F401
            return 'faster-whisper'
        except ImportError:
            if name == 'faster-whisper':
                sys.exit('faster-whisper is not installed: pip install faster-whisper')
    if name in ('auto', 'whisperkit') and shutil.which('whisperkit-cli'):
        return 'whisperkit'
    sys.exit('No Whisper backend found. Install one: pip install faster-whisper (any OS) '
             'or brew install whisperkit-cli (Apple Silicon).')


_FW = {}


def transcribe_arrays(chunks, lang, backend, model):
    """chunks: list of float32 mono arrays at 16 kHz. Returns a list of (text, [[s, e, word], ...]) per chunk,
    times relative to the chunk start (padding removed)."""
    pad = np.zeros(int(PAD * SR), np.float32)
    tmp = tempfile.mkdtemp(prefix='ve-tr-')
    try:
        paths = []
        for i, x in enumerate(chunks):
            p = os.path.join(tmp, f'c{i:05d}.wav')
            y = np.concatenate([pad, x.astype(np.float32), pad])
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', p],
                           input=y.tobytes(), check=True)
            paths.append(p)
        res = []
        if backend == 'faster-whisper':
            from faster_whisper import WhisperModel
            if model not in _FW:
                _FW[model] = WhisperModel(model, device='auto', compute_type='int8')
            m = _FW[model]
            for p in paths:
                segs, _ = m.transcribe(p, language=lang, word_timestamps=True, condition_on_previous_text=False,
                                       vad_filter=False, beam_size=5)
                words, text = [], []
                for s in segs:
                    text.append(s.text.strip())
                    for w in s.words or []:
                        if w.word.strip():
                            words.append([round(w.start - PAD, 3), round(w.end - PAD, 3), w.word.strip()])
                res.append((' '.join(text).strip(), words))
        else:
            out = os.path.join(tmp, 'out')
            os.makedirs(out)
            cmd = ['whisperkit-cli', 'transcribe', '--audio-folder', tmp, '--word-timestamps', '--skip-special-tokens',
                   '--report', '--report-path', out]
            if lang:
                cmd += ['--language', lang]
            cmd += ['--model-path', model] if os.path.isdir(model) else ['--model', model]
            tok = os.environ.get('WHISPERKIT_TOKENIZER', os.path.expanduser('~/.cache/whisperkit/tok'))
            if os.path.isdir(tok):   # an offline tokenizer folder avoids a network fetch that can hang
                cmd += ['--download-tokenizer-path', tok]
            r = subprocess.run(cmd, capture_output=True, text=True)
            for p in paths:
                js = os.path.join(out, os.path.basename(p)[:-4] + '.json')
                if not os.path.exists(js):
                    if r.returncode:
                        sys.exit(f'whisperkit-cli failed: {r.stderr[-800:]}')
                    res.append(('', []))
                    continue
                d = load_json(js)
                words = [[round(w['start'] - PAD, 3), round(w['end'] - PAD, 3), w['word'].strip()]
                         for s in d.get('segments', []) for w in s.get('words', []) if w['word'].strip()]
                res.append((d.get('text', '').strip(), words))
        return res
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def load_mono(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vn', '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.float32)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('clips', nargs='+')
    ap.add_argument('--project', default='.')
    ap.add_argument('--lang', default=None, help='language code (en, tr, de ...); auto-detect if omitted')
    ap.add_argument('--backend', default='auto')
    ap.add_argument('--model', default='large-v3', help='model name or local model folder')
    ap.add_argument('--thr', type=float, default=None, help='speech threshold in dB (default: noise floor + 18)')
    a = ap.parse_args()

    root, work = project_paths(a.project)
    backend = pick_backend(a.backend)
    os.makedirs(os.path.join(work, 'env'), exist_ok=True)
    os.makedirs(os.path.join(work, 'transcripts'), exist_ok=True)
    cpath = os.path.join(work, 'clips.json')
    clips = load_json(cpath) if os.path.exists(cpath) else {}

    for src in a.clips:
        rel = os.path.relpath(os.path.abspath(src), root)
        cid = next((k for k, v in clips.items() if v == rel), None) or clip_id(rel, clips)
        clips[cid] = rel
        save_json(cpath, clips)

        x = load_mono(os.path.abspath(src))
        if not len(x):
            print(f'{cid}: no audio, skipped')
            continue
        env = envelope(os.path.abspath(src))
        np.save(os.path.join(work, 'env', f'{cid}.npy'), env.astype(np.float32))
        thr = speech_threshold(env, a.thr)
        regions = speech_regions(env, thr)
        chunks = plan_chunks(regions)
        print(f'{cid}: {len(x) / SR:.1f} s, threshold {thr:.1f} dB, {len(chunks)} chunks, backend {backend}')

        arrays = [x[int(s * SR):int(e * SR)] for s, e in chunks]
        res = transcribe_arrays(arrays, a.lang, backend, a.model)
        utts = []
        for (s, e), (text, words) in zip(chunks, res):
            ws = [[round(w0 + s, 3), round(w1 + s, 3), w] for w0, w1, w in words]
            utts.append({'start': s, 'end': e, 'text': text, 'words': ws})
        save_json(os.path.join(work, 'transcripts', f'{cid}.json'),
                  {'clip': cid, 'src': rel, 'threshold': thr, 'hop': ENV_HOP, 'regions': regions, 'utterances': utts})
        with open(os.path.join(work, 'transcripts', f'{cid}.txt'), 'w', encoding='utf-8') as f:
            f.write(f'# {cid}  ({rel})  utterance index [start-end] text\n')
            for i, u in enumerate(utts):
                f.write(f"#{i:<4d}[{fmt_time(u['start'])}-{fmt_time(u['end'])}] {u['text']}\n")
        print(f'  -> work/transcripts/{cid}.txt ({len(utts)} utterances)')


if __name__ == '__main__':
    main()
