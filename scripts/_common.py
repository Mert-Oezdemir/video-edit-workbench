"""Shared helpers: project paths, audio decoding, the 10 ms energy envelope, loudness measurement."""
import json
import os
import re
import subprocess
import sys

import numpy as np

ENV_HOP = 0.01  # envelope resolution: 10 ms


def project_paths(project):
    root = os.path.abspath(project)
    work = os.path.join(root, 'work')
    os.makedirs(work, exist_ok=True)
    return root, work


def need(tool):
    from shutil import which
    if not which(tool):
        sys.exit(f'{tool} not found on PATH')


def ffmpeg(*args, check=True, capture=False, inp=None):
    need('ffmpeg')
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', *args], input=inp,
                       capture_output=capture)
    if check and r.returncode != 0:
        err = r.stderr.decode(errors='replace') if capture and r.stderr else ''
        sys.exit(f'ffmpeg failed ({r.returncode}): {" ".join(args[:6])} ... {err}')
    return r


def decode(path, sr=48000, channels=2):
    """Decode any audio/video file to float32 samples, shape (n, channels)."""
    need('ffmpeg')
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-vn', '-f', 'f32le', '-ac', str(channels),
                          '-ar', str(sr), '-'], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, channels)


def envelope(path_or_samples, sr=16000):
    """10 ms RMS envelope in dB of the mono signal, high-passed at 80 Hz so rumble does not count as speech."""
    if isinstance(path_or_samples, str):
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path_or_samples, '-vn', '-af', 'highpass=f=80',
                              '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'], capture_output=True).stdout
        x = np.frombuffer(raw, np.float32)
    else:
        x = path_or_samples
    hop = int(sr * ENV_HOP)
    n = len(x) // hop
    rms = np.sqrt(np.mean(x[:n * hop].reshape(n, hop) ** 2, axis=1) + 1e-12)
    return 20 * np.log10(rms)


def speech_threshold(env, override=None):
    """Speech/silence threshold from the clip's own noise floor (10th percentile) unless given."""
    if override is not None:
        return float(override)
    floor = float(np.percentile(env, 10))
    return float(np.clip(floor + 18, -60, -40))


def speech_regions(env, thr, bridge=0.25, min_len=0.08):
    """Regions above thr; gaps shorter than bridge are closed, blips shorter than min_len dropped. Seconds."""
    on = env > thr
    segs, i, n = [], 0, len(env)
    while i < n:
        if on[i]:
            j = i
            while j < n and on[j]:
                j += 1
            segs.append([i, j])
            i = j
        else:
            i += 1
    merged = []
    for a, b in segs:
        if merged and (a - merged[-1][1]) * ENV_HOP < bridge:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    return [[round(a * ENV_HOP, 2), round(b * ENV_HOP, 2)] for a, b in merged if (b - a) * ENV_HOP >= min_len]


def loudness(path):
    """Integrated loudness (LUFS), true peak (dBTP), loudness range (LU) via ffmpeg ebur128 on the real channels."""
    need('ffmpeg')
    err = subprocess.run(['ffmpeg', '-nostats', '-hide_banner', '-i', path, '-vn', '-af', 'ebur128=peak=true',
                          '-f', 'null', '-'], capture_output=True, text=True).stderr
    s = err[err.rindex('Summary:'):]
    i = float(re.search(r'I:\s+(-?[\d.]+|-inf) LUFS', s).group(1))
    tp = float(re.search(r'Peak:\s+(-?[\d.]+|-inf) dBFS', s).group(1))
    lra = float(re.search(r'LRA:\s+(-?[\d.]+) LU', s).group(1))
    return i, tp, lra


def write_wav(path, x, sr=48000, bits=24):
    """Write float samples (n, ch) to WAV through ffmpeg (24-bit by default)."""
    x = np.ascontiguousarray(x, dtype=np.float32)
    ch = 1 if x.ndim == 1 else x.shape[1]
    ffmpeg('-f', 'f32le', '-ar', str(sr), '-ac', str(ch), '-i', '-', '-c:a', f'pcm_s{bits}le', path, inp=x.tobytes())


def load_json(path):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=1)


def fmt_time(t):
    t = max(0.0, t)
    return f'{int(t // 60)}:{t % 60:05.2f}'


def yt_time(t):
    t = int(t)
    h, m, s = t // 3600, t % 3600 // 60, t % 60
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'
