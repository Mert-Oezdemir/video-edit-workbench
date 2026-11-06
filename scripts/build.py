#!/usr/bin/env python3
"""Program -> audio and video.

audio: every piece is taken sample-exact from its source at 48 kHz, with a 4 ms fade-in and a 15 ms fade-out at
       each join (no clicks). Then ONE linear gain: as close to the loudness target as the true-peak ceiling
       allows. No noise reduction, EQ, compression or gate: they make voices muffled (see reference/audio.md).
video: every piece is encoded frame-exact from its source, then joined without re-encoding.

usage:
  python3 scripts/build.py --project . audio video            # work/prog.wav + work/proxy.mp4 (1080p preview)
  python3 scripts/build.py --project . video --final          # work/prog-final.mp4 at source resolution (render background)
options:
  --target -14        loudness target (LUFS)
  --ceiling -1        true-peak ceiling (dBTP)
  --limiter           allow a gentle peak limiter when the ceiling stops the gain short of the target (ask the user first)
  --highpass 70       high-pass filter in Hz, only for rumble / hum the user asked to remove
  --hw                hardware encoder on macOS (h264_videotoolbox) for the preview
  --workers 4         parallel encodes
"""
import argparse
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import decode, ffmpeg, fmt_time, load_json, loudness, project_paths, write_wav  # noqa: E402

SR = 48000
FADE_IN, FADE_OUT = 0.004, 0.015


def sample(frame, fps):
    return int(round(frame * SR / fps))


def build_audio(root, work, prog, a):
    fps, cache, parts = prog['fps'], {}, []
    for p in prog['pieces']:
        cid = p['clip']
        if cid not in cache:
            cache[cid] = decode(os.path.join(root, prog['clips'][cid]), SR, 2)
        s0, s1 = sample(p['a'], fps), sample(p['b'], fps)
        x = cache[cid][s0:s1].copy()
        if len(x) < s1 - s0:
            x = np.vstack([x, np.zeros((s1 - s0 - len(x), 2), np.float32)])
        fi = int(FADE_IN * SR)
        fo = int(p.get('fade_out', FADE_OUT) * SR)
        x[:fi] *= np.linspace(0, 1, fi, dtype=np.float32)[:, None]
        x[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)[:, None]
        parts.append(x)
    y = np.vstack(parts)
    rawp = os.path.join(work, 'prog-raw.wav')
    write_wav(rawp, y)
    i0, tp0, lra0 = loudness(rawp)

    pre = f'highpass=f={a.highpass},' if a.highpass else ''
    want = a.target - i0
    room = a.ceiling - tp0
    outp = os.path.join(work, 'prog.wav')
    if want <= room or not a.limiter:
        g = min(want, room)
        ffmpeg('-i', rawp, '-af', f'{pre}volume={g:.2f}dB', '-ar', str(SR), '-c:a', 'pcm_s24le', outp)
        how = 'linear gain'
    else:
        g = want
        lim = 10 ** ((a.ceiling - 0.5) / 20)
        ffmpeg('-i', rawp, '-af', f'{pre}volume={g:.2f}dB,alimiter=limit={lim:.4f}:attack=5:release=60:level=disabled',
               '-ar', str(SR), '-c:a', 'pcm_s24le', outp)
        how = 'gain + gentle limiter'
    i1, tp1, lra1 = loudness(outp)
    print(f'audio: {fmt_time(len(y) / SR)}  {i0:.1f} LUFS (true peak {tp0:.1f}) -> {i1:.1f} LUFS, true peak {tp1:.1f} dBTP, '
          f'LRA {lra1:.1f} LU ({how} {g:+.1f} dB)')
    if not a.limiter and want > room + 0.3:
        print(f'note: the true-peak ceiling stopped the gain {want - room:.1f} dB short of {a.target} LUFS. '
              f'Ask the user before using --limiter (a gentle peak limiter), and let them listen to both.')
    if tp1 > a.ceiling + 0.2:
        print(f'warning: true peak {tp1:.1f} dBTP is above the ceiling')


def build_video(root, work, prog, a):
    fps = prog['fps']
    seg_dir = os.path.join(work, 'seg-final' if a.final else 'seg')
    os.makedirs(seg_dir, exist_ok=True)
    for f in os.listdir(seg_dir):
        if f.endswith('.mp4') or f == 'list.txt':
            os.remove(os.path.join(seg_dir, f))
    if a.final:
        enc = ['-c:v', 'libx264', '-preset', 'medium', '-crf', '14', '-profile:v', 'high']
        vf = 'format=yuv420p'
    elif a.hw:
        enc = ['-c:v', 'h264_videotoolbox', '-b:v', '12M', '-profile:v', 'high']
        vf = 'scale=-2:1080:flags=lanczos,format=yuv420p'
    else:
        enc = ['-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20']
        vf = 'scale=-2:1080:flags=lanczos,format=yuv420p'
    common = ['-pix_fmt', 'yuv420p', '-g', str(fps), '-r', str(fps), '-video_track_timescale', str(fps * 1000),
              '-color_primaries', 'bt709', '-color_trc', 'bt709', '-colorspace', 'bt709', '-an']

    def seg(i):
        p = prog['pieces'][i]
        src = os.path.join(root, prog['clips'][p['clip']])
        # seek half a frame early: the first decoded frame is then exactly frame a
        ffmpeg('-ss', f'{(p["a"] - 0.5) / fps:.5f}', '-i', src, '-frames:v', str(p['b'] - p['a']), '-vf', vf, *enc,
               *common, os.path.join(seg_dir, f'{i:05d}.mp4'))

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(seg, range(len(prog['pieces']))))
    lst = os.path.join(seg_dir, 'list.txt')
    with open(lst, 'w') as f:
        f.write(''.join(f"file '{seg_dir}/{i:05d}.mp4'\n" for i in range(len(prog['pieces']))))
    vid = os.path.join(work, 'prog-final.mp4' if a.final else 'proxy-video.mp4')
    ffmpeg('-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', '-movflags', '+faststart', vid)
    n = int(subprocess.run(['ffprobe', '-v', 'error', '-count_packets', '-select_streams', 'v', '-show_entries',
                            'stream=nb_read_packets', '-of', 'csv=p=0', vid], capture_output=True, text=True).stdout.strip())
    print(f'video: {n} frames (expected {prog["frames"]})' + ('' if n == prog['frames'] else '  <-- MISMATCH'))
    if not a.final:
        wav = os.path.join(work, 'prog.wav')
        if not os.path.exists(wav):
            sys.exit('work/prog.wav missing: run the audio step first')
        ffmpeg('-i', vid, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k',
               '-movflags', '+faststart', os.path.join(work, 'proxy.new.mp4'))
        os.replace(os.path.join(work, 'proxy.new.mp4'), os.path.join(work, 'proxy.mp4'))
        os.remove(vid)
        print('preview: work/proxy.mp4')
    else:
        print('render background: work/prog-final.mp4')
    for f in os.listdir(seg_dir):
        os.remove(os.path.join(seg_dir, f))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('steps', nargs='*', default=['audio', 'video'])
    ap.add_argument('--project', default='.')
    ap.add_argument('--final', action='store_true')
    ap.add_argument('--target', type=float, default=-14.0)
    ap.add_argument('--ceiling', type=float, default=-1.0)
    ap.add_argument('--limiter', action='store_true')
    ap.add_argument('--highpass', type=float, default=None)
    ap.add_argument('--hw', action='store_true')
    ap.add_argument('--workers', type=int, default=4)
    a = ap.parse_args()
    root, work = project_paths(a.project)
    prog = load_json(os.path.join(work, 'program.json'))
    if 'audio' in a.steps:
        build_audio(root, work, prog, a)
    if 'video' in a.steps:
        build_video(root, work, prog, a)


if __name__ == '__main__':
    main()
