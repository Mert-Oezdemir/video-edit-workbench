#!/usr/bin/env python3
"""Check every join of the built program: clipped words, cuts through sound, leftover repeats.

Two checks, both measurements (a human still has to listen to the flagged spots):
  1. energy at each cut in the source: a piece that ends or starts while the voice is still sounding is flagged
  2. the program audio around each join is transcribed again; doubled words ("and and") and doubled phrases are flagged

usage:
  python3 scripts/verify.py --project . [--lang en] [--window 1.6] [--all]
writes work/verify.txt (every join with its transcript; flagged ones marked with !)
"""
import argparse
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import ENV_HOP, fmt_time, load_json, project_paths  # noqa: E402
from cuts import Clip  # noqa: E402
from transcribe import SR, load_mono, pick_backend, transcribe_arrays  # noqa: E402


def norm(w):
    return re.sub(r'[^\w]+', '', w.lower())


def repeats(words):
    ws = [norm(w) for w in words if norm(w)]
    hits = []
    for i in range(1, len(ws)):
        if ws[i] == ws[i - 1] and len(ws[i]) > 1:
            hits.append(ws[i])
    for n in (2, 3):
        for i in range(n, len(ws) - n + 1):
            if ws[i - n:i] == ws[i:i + n]:
                hits.append(' '.join(ws[i:i + n]))
    return hits


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--project', default='.')
    ap.add_argument('--lang', default=None)
    ap.add_argument('--backend', default='auto')
    ap.add_argument('--model', default='large-v3')
    ap.add_argument('--window', type=float, default=1.6)
    ap.add_argument('--all', action='store_true', help='print every join, not only flagged ones')
    a = ap.parse_args()
    root, work = project_paths(a.project)
    prog = load_json(os.path.join(work, 'program.json'))
    fps, pieces = prog['fps'], prog['pieces']
    clips = {}

    def C(cid):
        if cid not in clips:
            clips[cid] = Clip(work, cid)
        return clips[cid]

    edge = []
    for i, p in enumerate(pieces):
        c = C(p['clip'])
        nxt = pieces[i + 1] if i + 1 < len(pieces) else None
        prv = pieces[i - 1] if i else None
        contig_out = nxt and nxt['clip'] == p['clip'] and nxt['a'] == p['b']
        contig_in = prv and prv['clip'] == p['clip'] and prv['b'] == p['a']
        out_db = float(np.mean(c.env[max(0, int(p['b'] / fps / ENV_HOP) - 2):int(p['b'] / fps / ENV_HOP)]))
        in_db = float(np.mean(c.env[int(p['a'] / fps / ENV_HOP):int(p['a'] / fps / ENV_HOP) + 2]))
        notes = []
        if not contig_out and nxt is not None and out_db > c.soft + 3:
            notes.append(f'piece ends while sounding ({out_db:.0f} dB)')
        if not contig_in and prv is not None and in_db > c.soft + 3:
            notes.append(f'piece starts mid-sound ({in_db:.0f} dB)')
        edge.append(notes)

    wav = os.path.join(work, 'prog.wav')
    if not os.path.exists(wav):
        sys.exit('work/prog.wav missing: run build.py audio first')
    x = load_mono(wav)
    joins = [p['p'] / fps for p in pieces[1:]]
    wins = [x[int(max(0, t - a.window) * SR):int((t + a.window) * SR)] for t in joins]
    backend = pick_backend(a.backend)
    print(f'{len(joins)} joins, transcribing windows with {backend} ...')
    res = transcribe_arrays(wins, a.lang, backend, a.model) if wins else []

    lines, flagged = [], 0
    for k, (t, (text, words)) in enumerate(zip(joins, res)):
        notes = edge[k] + edge[k + 1]
        rep = repeats([w for _, _, w in words])
        if rep:
            notes.append('repeat: ' + ', '.join(sorted(set(rep))))
        mark = '!' if notes else ' '
        flagged += bool(notes)
        if notes or a.all:
            pa, pb = pieces[k], pieces[k + 1]
            lines.append(f"{mark} join {k + 1:<4d} {fmt_time(t)}  [{pa['clip']} {pa['b'] / fps:.2f} -> {pb['clip']} "
                         f"{pb['a'] / fps:.2f}]  {text}")
            for n in notes:
                lines.append(f'      - {n}')
    out = os.path.join(work, 'verify.txt')
    with open(out, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    print(f'{flagged} of {len(joins)} joins flagged -> work/verify.txt. Listen to the flagged spots; '
          f'a clean report does not mean every join sounds right.')


if __name__ == '__main__':
    main()
