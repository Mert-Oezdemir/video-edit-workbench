#!/usr/bin/env python3
"""Loudness report for any audio or video file: integrated LUFS, true peak, loudness range, with a plain verdict.

usage: python3 scripts/loudness.py FILE [FILE ...] [--target -14]
Measures the real channels (a mono downmix with -ac 1 would report a false peak about 3 dB too high).
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import loudness  # noqa: E402


def verdict(i, tp, lra, target):
    out = []
    if i < target - 2:
        out.append(f'quiet: {target - i:.1f} dB under {target} LUFS. Platforms do not turn quiet videos up.')
    elif i > target + 1:
        out.append(f'loud: platforms will turn it down by about {i - target:.1f} dB; peaks get no benefit.')
    else:
        out.append('loudness is on target.')
    if tp > -1.0:
        out.append(f'true peak {tp:.1f} dBTP is above -1 dBTP: risk of distortion after encoding.')
    if lra > 12:
        out.append(f'loudness range {lra:.1f} LU is wide: some parts are much quieter than others.')
    return ' '.join(out)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('files', nargs='+')
    ap.add_argument('--target', type=float, default=-14.0)
    a = ap.parse_args()
    for f in a.files:
        i, tp, lra = loudness(f)
        print(f'{os.path.basename(f)}: {i:.1f} LUFS, true peak {tp:.1f} dBTP, LRA {lra:.1f} LU')
        print('  ' + verdict(i, tp, lra, a.target))
