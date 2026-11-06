#!/usr/bin/env python3
"""Edit list -> program: frame-exact pieces whose cut points sit on real word edges.

Cut points come from the 10 ms energy envelope, not from Whisper word times (those are often 0.1-0.4 s off):
  - long pauses inside a kept utterance are removed (pace: natural / tight)
  - word ends are extended while the level stays above the soft floor (decaying syllables are kept)
  - a short release burst after a stop consonant (t, k, p) is kept
  - word starts are pulled back over soft onsets
  - frame rounding goes outward, never into a word

usage:
  python3 scripts/cuts.py --project .                    # work/edl.json -> work/program.json + work/chapters.txt
  python3 scripts/cuts.py --project . --peek CLIP A B    # print the envelope between A and B seconds (finding cut points)
"""
import argparse
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import ENV_HOP, fmt_time, load_json, project_paths, save_json, yt_time  # noqa: E402

PACES = {
    'natural': {'head': 0.10, 'tail': 0.16, 'maxgap': 0.35},
    'tight': {'head': 0.04, 'tail': 0.06, 'maxgap': 0.15},
}
SOFT = -61.0        # a decaying syllable is still "speech" above this level (dB)
END_EXT = 0.10      # max extension of a word end over a soft decay
START_EXT = 0.06    # max extension of a word start over a soft onset
BURST_ON, BURST_OFF, BURST_MAX = -68.0, -72.0, 12     # release burst after a stop consonant (max 12 x 10 ms)
SNAP_WIN = 0.15     # hand-set points snap to the quietest 10 ms within this window


class Clip:
    def __init__(self, work, cid):
        tp = os.path.join(work, 'transcripts', f'{cid}.json')
        ep = os.path.join(work, 'env', f'{cid}.npy')
        if not os.path.exists(tp) or not os.path.exists(ep):
            sys.exit(f'clip "{cid}" has no transcript/envelope: run transcribe.py on it first')
        self.t = load_json(tp)
        self.env = np.load(ep).astype(np.float64)
        self.speech = self.t['regions']
        self.utts = self.t['utterances']
        self.src = self.t['src']
        # levels were tuned on a quiet room (noise floor about -80 dB); in a noisier room they follow the floor
        floor = float(np.percentile(self.env, 10))
        self.soft = max(SOFT, floor + 6)
        self.burst_on, self.burst_off = max(BURST_ON, floor + 10), max(BURST_OFF, floor + 5)

    def db(self, t):
        i = int(t / ENV_HOP)
        return self.env[min(max(i, 0), len(self.env) - 1)]

    def snap(self, t):
        e = self.env
        i0, i1 = max(0, int((t - SNAP_WIN) / ENV_HOP)), min(len(e) - 1, int((t + SNAP_WIN) / ENV_HOP))
        i = min(range(i0, i1 + 1), key=lambda j: (e[j], abs(j - t / ENV_HOP)))
        return (i + 0.5) * ENV_HOP


def refine(clip, regs, lo_bound, hi_bound):
    """Extend each speech region over soft word ends, release bursts and soft onsets, staying inside bounds."""
    env, n = clip.env, len(clip.env)
    out = []
    for j, (a, b) in enumerate(regs):
        lo = regs[j - 1][1] + 0.05 if j else lo_bound
        hi = regs[j + 1][0] - 0.05 if j + 1 < len(regs) else hi_bound
        i = int(round(b / ENV_HOP))
        q = i
        while q < n and q - i < round(END_EXT / ENV_HOP) and env[q] > clip.soft and (q + 1) * ENV_HOP < hi:
            q += 1
        for kb in range(q, min(n, q + 8)):           # closure of up to 80 ms, then a short burst, then silence
            if (kb + 1) * ENV_HOP >= hi:
                break
            if env[kb] > clip.burst_on:
                L = 0
                while kb + L < n and env[kb + L] > clip.burst_off and L <= BURST_MAX:
                    L += 1
                if L <= BURST_MAX and kb + L < n and env[kb + L] <= clip.burst_off and (kb + L) * ENV_HOP < hi:
                    q = kb + L
                break
        i0 = int(round(a / ENV_HOP))
        h = i0
        while h > 0 and i0 - h < round(START_EXT / ENV_HOP) and env[h - 1] > clip.soft and (h - 1) * ENV_HOP > lo:
            h -= 1
        out.append([min(a, h * ENV_HOP), max(b, q * ENV_HOP)])
    return out


def build(project):
    root, work = project_paths(project)
    edl = load_json(os.path.join(work, 'edl.json'))
    fps = int(edl.get('fps', 30))
    pace = PACES[edl.get('pace', 'natural')]
    clips_map = dict(load_json(os.path.join(work, 'clips.json'))) if os.path.exists(os.path.join(work, 'clips.json')) else {}
    clips_map.update(edl.get('clips', {}))
    cache = {}

    def C(cid):
        if cid not in cache:
            cache[cid] = Clip(work, cid)
        return cache[cid]

    pieces, entries, chapters, pf = [], [], [], 0
    for item in edl['items']:
        if 'note' in item and len(item) == 1:
            continue
        if 'chapter' in item:
            chapters.append({'title': item['chapter'], 'frame': pf, 'time': round(pf / fps, 3)})
            continue
        cid = item['clip']
        c = C(cid)
        if 'range' in item:
            a, b = item['range']
            af, bf = int(a * fps), -int(-b * fps)
            pieces.append({'clip': cid, 'a': af, 'b': bf, 'p': pf, 'e': len(entries)})
            entries.append({'clip': cid, 'range': [a, b], 'pieces': [len(pieces) - 1], 'text': ''})
            pf += bf - af
            continue
        u = item['utt']
        ui = u if isinstance(u, list) else [u, u]
        if ui[1] >= len(c.utts):
            sys.exit(f'{cid}: utterance {ui[1]} does not exist ({len(c.utts)} utterances)')
        exact = item.get('exact', False)
        cutS, cutE = item.get('start') is not None, item.get('end') is not None
        S = (item['start'] if exact else c.snap(item['start'])) if cutS else c.utts[ui[0]]['start']
        E = (item['end'] if exact else c.snap(item['end'])) if cutE else c.utts[ui[1]]['end']
        sp = c.speech
        regs = [[max(a, S), min(b, E)] for a, b in sp if b > S and a < E]
        regs = [r for r in regs if r[1] - r[0] > 0.03]
        if not regs:
            print(f'warning: {cid} utt {u}: no speech between {S:.2f} and {E:.2f}, skipped')
            continue
        prev_sp = max([b for a, b in sp if b <= regs[0][0] + 1e-6] or [0.0])
        next_sp = min([a for a, b in sp if a >= regs[-1][1] - 1e-6] or [1e9])
        lo_bound = S if cutS else prev_sp + 0.05
        hi_bound = E if cutE else next_sp - 0.05
        regs = refine(c, regs, lo_bound, hi_bound)
        gap = 1e9 if item.get('keep_pauses') else pace['maxgap']
        merged = []
        for r in regs:
            if merged and r[0] - merged[-1][1] <= gap:
                merged[-1][1] = r[1]
            else:
                merged.append(list(r))
        ent = {'clip': cid, 'utt': ui, 'pieces': [],
               'text': ' '.join(c.utts[i]['text'] for i in range(ui[0], ui[1] + 1))}
        for j, (a, b) in enumerate(merged):
            pe = max([y for x, y in sp if y <= a + 1e-6] or [0.0])
            ns = min([x for x, y in sp if x >= b - 1e-6] or [1e9])
            a2 = a - 0.02 if (j == 0 and cutS) else max(a - pace['head'], pe + 0.04, (a + pe) / 2)
            b2 = b + 0.02 if (j == len(merged) - 1 and cutE) else min(b + pace['tail'], ns - 0.04, (b + ns) / 2)
            af, bf = int(max(0.0, a2) * fps), -int(-b2 * fps)
            if bf <= af:
                continue
            p = {'clip': cid, 'a': af, 'b': bf, 'p': pf, 'e': len(entries)}
            if j == len(merged) - 1 and cutE and exact:
                p['fade_out'] = 0.05      # a hand-set end inside running speech fades over 50 ms
            pieces.append(p)
            ent['pieces'].append(len(pieces) - 1)
            pf += bf - af
        entries.append(ent)

    words = []
    for p in pieces:
        a, b = p['a'] / fps, p['b'] / fps
        for u in C(p['clip']).utts:
            if u['end'] < a or u['start'] > b:
                continue
            for w0, w1, w in u['words']:
                if w1 > a + 0.04 and w0 < b - 0.04:
                    s0, e0 = max(w0, a), min(w1, b)
                    words.append([round(p['p'] / fps + s0 - a, 3), round(p['p'] / fps + e0 - a, 3), w, p['e']])
    words.sort()
    joins = [round(p['p'] / fps, 3) for p in pieces[1:]]
    prog = {'fps': fps, 'frames': pf, 'duration': round(pf / fps, 3), 'clips': clips_map, 'pieces': pieces,
            'entries': entries, 'chapters': chapters, 'joins': joins, 'words': words}
    save_json(os.path.join(work, 'program.json'), prog)

    raw = sum(C(k).speech[-1][1] for k in {p['clip'] for p in pieces} if C(k).speech)
    print(f'{len(pieces)} pieces, {len(entries)} entries, program {fmt_time(pf / fps)} (speech in used clips {fmt_time(raw)})')
    if chapters:
        if chapters[0]['frame'] != 0:
            print('note: the first chapter does not start at 0:00; YouTube needs one there')
        lines = [f"{yt_time(ch['time'])} {ch['title']}" for ch in chapters]
        with open(os.path.join(work, 'chapters.txt'), 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        print('YouTube chapters (work/chapters.txt):')
        for ln in lines:
            print('  ' + ln)
        short = [ch['title'] for ch, nx in zip(chapters, chapters[1:] + [{'time': pf / fps}]) if nx['time'] - ch['time'] < 10]
        if short or len(chapters) < 3:
            print('note: YouTube needs at least 3 chapters, each 10 s or longer')


def peek(project, cid, a, b):
    _, work = project_paths(project)
    c = Clip(work, cid)
    print(f'{cid} envelope {a:.2f}-{b:.2f} s (dB per 10 ms; threshold {c.t["threshold"]:.1f}, soft floor {c.soft:.1f})')
    words = [w for u in c.utts for w in u['words'] if w[1] > a and w[0] < b]
    for i in range(int(a / ENV_HOP), int(b / ENV_HOP)):
        t = i * ENV_HOP
        lab = ' '.join(w[2] for w in words if abs(w[0] - t) < ENV_HOP / 2)
        bar = '#' * max(0, int((c.env[i] + 80) / 2))
        print(f'{t:8.2f} {c.env[i]:6.1f} {bar:<40} {lab}')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--project', default='.')
    ap.add_argument('--peek', nargs=3, metavar=('CLIP', 'A', 'B'))
    a = ap.parse_args()
    if a.peek:
        peek(a.project, a.peek[0], float(a.peek[1]), float(a.peek[2]))
    else:
        build(a.project)
