#!/usr/bin/env python3
"""Final mix: rendered video + program voice + sound-effects track -> one file.

The voice keeps the level build.py gave it. Effects are added under it. If the sum would pass the true-peak
ceiling, the whole mix is lowered by the excess (linear, no limiter), and the report says so.

usage:
  python3 scripts/mix.py --project . --video out/frames --out out/FINAL.mp4 [--sfx-gain 0] [--no-sfx]
    --video   a render folder from render.mjs (part_*.mp4 + sfx.json) or a single video file
"""
import argparse
import glob
import json
import os
import re
import sys
import tempfile

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import decode, ffmpeg, loudness, project_paths, write_wav  # noqa: E402
from sfx import SR, MAKERS, make  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--project', default='.')
    ap.add_argument('--video', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--sfx-gain', type=float, default=0.0)
    ap.add_argument('--no-sfx', action='store_true')
    ap.add_argument('--ceiling', type=float, default=-1.0)
    a = ap.parse_args()
    root, work = project_paths(a.project)
    tmp = tempfile.mkdtemp(prefix='ve-mix-')

    if os.path.isdir(a.video):
        parts = sorted(glob.glob(os.path.join(a.video, 'part_*.mp4')),
                       key=lambda p: int(re.search(r'part_(\d+)', p).group(1)))
        if not parts:
            sys.exit(f'no part_*.mp4 in {a.video}')
        lst = os.path.join(tmp, 'parts.txt')
        with open(lst, 'w') as f:
            f.write(''.join(f"file '{os.path.abspath(p)}'\n" for p in parts))
        video_in = ['-f', 'concat', '-safe', '0', '-i', lst]
        cues_path = os.path.join(a.video, 'sfx.json')
    else:
        video_in = ['-i', a.video]
        cues_path = os.path.join(os.path.dirname(a.video), 'sfx.json')

    voice = decode(os.path.join(work, 'prog.wav'), SR, 2).astype(np.float64)
    mix = voice.copy()
    cues = []
    if not a.no_sfx and os.path.exists(cues_path):
        with open(cues_path, encoding='utf-8') as f:
            cues = json.load(f)
        lib = {}
        for c in cues:
            if c['name'] not in MAKERS:
                sys.exit(f'unknown effect {c["name"]}')
            if c['name'] not in lib:
                lib[c['name']] = make(c['name'], a.sfx_gain)
            x = lib[c['name']] * 10 ** (c.get('gain', 0) / 20)
            s = int(c['t'] * SR)
            if s < len(mix):
                mix[s:s + len(x)] += x[:len(mix) - s]
    wav = os.path.join(tmp, 'mix.wav')
    write_wav(wav, mix)
    i, tp, lra = loudness(wav)
    if tp > a.ceiling:
        g = a.ceiling - tp - 0.1
        mix *= 10 ** (g / 20)
        write_wav(wav, mix)
        print(f'note: effects pushed the true peak to {tp:.1f} dBTP; whole mix lowered by {-g:.1f} dB')
        i, tp, lra = loudness(wav)

    ffmpeg(*video_in, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '320k',
           '-shortest', '-movflags', '+faststart', a.out)
    print(f'{a.out}: {len(cues)} effects, {i:.1f} LUFS, true peak {tp:.1f} dBTP, LRA {lra:.1f} LU')


if __name__ == '__main__':
    main()
