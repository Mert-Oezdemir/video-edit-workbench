#!/usr/bin/env python3
"""Sound effects synthesized from math. No downloads, no licences, the same file every time (fixed seeds).

  whoosh       filtered noise whose band sweeps up and back down, panned left to right (chapter veils)
  soft-whoosh  lower, longer, darker whoosh (calm videos)
  tick         tiny high sine blip (a counter step, a checkbox)
  click        mouse click: short bright noise burst + a small low thump
  key          one mechanical key press: bright contact click, a woody body, a softer bottom-out
  typing       a burst of key presses at human pace (pitch, level and timing vary a little)
  pop          short sine with a falling pitch (a card or a badge appearing)
  chime        soft bar-like bell from inharmonic partials (a success / done moment)

Levels are peaks of each effect alone, set low on purpose (see reference/audio.md). Shift them all with --gain.

usage:
  python3 scripts/sfx.py lib --out scene/sfx [--gain 0]                     # write every effect as WAV
  python3 scripts/sfx.py track --cues out/sfx.json --duration 612.4 --out work/sfx.wav [--gain 0]
      cues: [{"t": 12.30, "name": "whoosh", "gain": 0}, ...]  (exported by the scene / render.mjs)
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import write_wav  # noqa: E402

SR = 48000
LEVELS = {  # default peak in dBFS of each effect on its own
    'whoosh': -32, 'soft-whoosh': -32, 'tick': -30, 'click': -30, 'key': -32, 'typing': -32, 'pop': -30, 'chime': -30,
}


def t_axis(dur):
    return np.arange(int(dur * SR)) / SR


def one_pole_lowpass(x, fc):
    """Lowpass whose cutoff may change per sample (fc array in Hz)."""
    a = np.exp(-2 * np.pi * np.asarray(fc, dtype=np.float64) / SR) * np.ones(len(x))
    y = np.empty(len(x))
    s = 0.0
    for i in range(len(x)):
        s = (1 - a[i]) * x[i] + a[i] * s
        y[i] = s
    return y


def bandpass_noise(n, lo, hi, rng):
    x = rng.standard_normal(n)
    y = one_pole_lowpass(x, np.full(n, hi))
    return y - one_pole_lowpass(y, np.full(n, lo))


def stereo(sig, pan0=0.5, pan1=None):
    """Equal-power pan, 0 = left, 1 = right; a sweep when pan1 is given."""
    p = np.full(len(sig), pan0) if pan1 is None else np.linspace(pan0, pan1, len(sig))
    return np.stack([sig * np.cos(p * np.pi / 2), sig * np.sin(p * np.pi / 2)], 1)


def whoosh(dur=1.15, f0=260, f1=2600, f2=700, pan=(0.15, 0.85), seed=7, peak_at=0.58):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    u = np.arange(n) / n
    fc = np.where(u < peak_at, f0 + (f1 - f0) * (u / peak_at) ** 1.4, f1 + (f2 - f1) * ((u - peak_at) / (1 - peak_at)))
    lp = one_pole_lowpass(rng.standard_normal(n), fc)
    hp = lp - np.convolve(lp, np.ones(64) / 64, mode='same')
    sig = 0.6 * lp + 0.4 * hp
    env = np.where(u < peak_at, np.sin(np.pi / 2 * u / peak_at) ** 2, np.cos(np.pi / 2 * (u - peak_at) / (1 - peak_at)) ** 2)
    return stereo(sig * env, *pan)


def soft_whoosh():
    return whoosh(dur=1.45, f0=160, f1=1300, f2=420, pan=(0.3, 0.7), seed=11, peak_at=0.5)


def tick(f=2300, seed=3):
    t = t_axis(0.05)
    sig = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.009)
    rng = np.random.default_rng(seed)
    sig[:96] += 0.25 * rng.standard_normal(96) * np.linspace(1, 0, 96)
    return stereo(sig)


def click(seed=5):
    rng = np.random.default_rng(seed)
    t = t_axis(0.08)
    burst = bandpass_noise(len(t), 1800, 7000, rng) * np.exp(-t / 0.0025)
    thump = np.sin(2 * np.pi * 170 * t) * np.exp(-t / 0.02) * 0.5
    return stereo(burst / (np.abs(burst).max() + 1e-9) + thump)


def key(seed=1, pitch=1.0, level=1.0):
    """One key press: contact click, body resonance, bottom-out."""
    rng = np.random.default_rng(seed)
    t = t_axis(0.16)
    n = len(t)
    contact = bandpass_noise(n, 2500, 9000, rng) * np.exp(-t / 0.0018)
    contact /= np.abs(contact).max() + 1e-9
    f_body = 300 * pitch * (1 + 0.06 * rng.standard_normal())
    body = (np.sin(2 * np.pi * f_body * t) + 0.4 * np.sin(2 * np.pi * f_body * 2.3 * t)) * np.exp(-t / 0.028) * 0.55
    d = int((0.018 + 0.012 * rng.random()) * SR)
    bottom = np.zeros(n)
    bt = t[:n - d]
    bottom[d:] = (bandpass_noise(n - d, 900, 5000, rng) * np.exp(-bt / 0.004))
    bottom /= np.abs(bottom).max() + 1e-9
    sig = contact * 0.9 + body + bottom * 0.45
    return stereo(sig * level, 0.5 + 0.08 * rng.standard_normal())


def typing(chars=14, seed=2, mean_gap=0.105):
    """A burst of key presses at human pace; a space bar is a little lower and longer."""
    rng = np.random.default_rng(seed)
    times, t = [], 0.0
    for i in range(chars):
        times.append(t)
        t += max(0.045, rng.normal(mean_gap, mean_gap * 0.35))
    out = np.zeros((int((t + 0.2) * SR), 2))
    for i, s in enumerate(times):
        space = rng.random() < 0.15
        k = key(seed=seed * 1000 + i, pitch=0.8 if space else 1 + 0.05 * rng.standard_normal(),
                level=0.8 + 0.25 * rng.random())
        a = int(s * SR)
        out[a:a + len(k)] += k[:len(out) - a]
    return out


def pop(seed=0):
    t = t_axis(0.09)
    f = 300 + 600 * np.exp(-t / 0.012)
    phase = 2 * np.pi * np.cumsum(f) / SR
    sig = np.sin(phase) * np.exp(-t / 0.03) * np.minimum(1, t / 0.002)
    return stereo(sig)


def chime(f=880.0):
    t = t_axis(1.6)
    ratios, decays, amps = [1.0, 2.756, 5.404, 8.933], [0.55, 0.25, 0.12, 0.06], [1.0, 0.45, 0.25, 0.12]
    sig = sum(a * np.sin(2 * np.pi * f * r * t) * np.exp(-t / d) for r, d, a in zip(ratios, decays, amps))
    sig *= np.minimum(1, t / 0.003)
    return stereo(sig)


MAKERS = {'whoosh': whoosh, 'soft-whoosh': soft_whoosh, 'tick': tick, 'click': click, 'key': key,
          'typing': typing, 'pop': pop, 'chime': chime}


def make(name, gain=0.0):
    x = MAKERS[name]()
    x = x / (np.abs(x).max() + 1e-12) * 10 ** ((LEVELS[name] + gain) / 20)
    return x.astype(np.float32)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    p = sub.add_parser('lib')
    p.add_argument('--out', required=True)
    p.add_argument('--gain', type=float, default=0.0, help='dB added to every default level')
    p = sub.add_parser('track')
    p.add_argument('--cues', required=True)
    p.add_argument('--duration', type=float, required=True)
    p.add_argument('--out', required=True)
    p.add_argument('--gain', type=float, default=0.0)
    a = ap.parse_args()

    if a.cmd == 'lib':
        os.makedirs(a.out, exist_ok=True)
        for name in MAKERS:
            x = make(name, a.gain)
            write_wav(os.path.join(a.out, f'{name}.wav'), x, bits=16)
            print(f'{name:12s} {len(x) / SR:.2f} s  peak {LEVELS[name] + a.gain:.0f} dBFS')
        return

    with open(a.cues, encoding='utf-8') as f:
        cues = json.load(f)
    lib = {}
    out = np.zeros((int(a.duration * SR) + 1, 2), np.float32)
    for c in cues:
        name = c['name']
        if name not in MAKERS:
            sys.exit(f'unknown effect "{name}"; known: {", ".join(MAKERS)}')
        if name not in lib:
            lib[name] = make(name, a.gain)
        x = lib[name] * 10 ** (c.get('gain', 0) / 20)
        s = int(c['t'] * SR)
        if s >= len(out):
            continue
        out[s:s + len(x)] += x[:len(out) - s]
    write_wav(a.out, out)
    peak = 20 * np.log10(np.abs(out).max() + 1e-12)
    print(f'{len(cues)} cues -> {a.out} ({a.duration:.1f} s, peak {peak:.1f} dBFS)')


if __name__ == '__main__':
    main()
