#!/usr/bin/env python3
"""Local-only media helpers for the ergonomic Workbench entry point.

No network, API access, package installation or shell execution. All outputs
are new and stay inside the caller's project/out directory.
"""
import json
import math
import re
import shutil
import subprocess
import textwrap
from pathlib import Path

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}
AUDIO_EXT = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".webp"}
SUB_EXT = {".srt"}
FPS = 30


def project_root(value):
    root = Path(value).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Project directory missing: {root}. Run 'init' first.")
    return root


def inside(path, root):
    return path == root or path.is_relative_to(root)


def local_file(root, value, allowed):
    path = Path(value).expanduser()
    path = (path if path.is_absolute() else root / path).resolve()
    if not inside(path, root) or not path.is_file() or path.suffix.lower() not in allowed:
        raise ValueError("Expected an existing supported file within your project: " + str(value))
    return path


def safe_output(root, value):
    path = Path(value).expanduser()
    path = (path if path.is_absolute() else root / path).resolve()
    base = (root / "out").resolve()
    if path == base or not inside(path, base):
        raise ValueError("Output must be inside project/out/")
    if path.exists():
        raise ValueError(f"Refusing to overwrite existing output: {path}")
    return path


def safe_new_dir(root, value):
    dest = safe_output(root, value)
    if dest.suffix:
        raise ValueError("Output directory must have no extension")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.mkdir(exist_ok=False)
    return dest


def must_have(*names):
    missing = [name for name in names if not shutil.which(name)]
    if missing:
        raise ValueError("Missing local executable(s): " + ", ".join(missing))


def run(cmd, *, input_text=None, timeout=3600):
    try:
        proc = subprocess.run([str(x) for x in cmd], input=input_text,
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError(f"Command unavailable or timed out: {cmd[0]}") from exc
    if proc.returncode:
        raise ValueError(f"{cmd[0]} failed ({proc.returncode}): {proc.stderr[-900:]}")
    return proc


def probe(path):
    must_have("ffprobe")
    result = run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                  "-of", "json", str(path)], timeout=50)
    try:
        value = json.loads(result.stdout)
        dur = float(value["format"]["duration"])
        if not math.isfinite(dur) or dur <= 0:
            raise ValueError("Invalid duration")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError("Cannot determine input duration: " + str(path)) from exc
    vids = [s for s in value.get("streams", []) if s.get("codec_type") == "video"]
    audio = any(s.get("codec_type") == "audio" for s in value.get("streams", []))
    return {"duration": dur, "video": bool(vids), "audio": audio,
            "width": vids[0].get("width") if vids else None,
            "height": vids[0].get("height") if vids else None}


def ensure_video(path):
    info = probe(path)
    if not info["video"]:
        raise ValueError("Video stream missing: " + str(path))
    return info


TIME = re.compile(r"(?P<h>\d+):(?P<m>\d{2}):(?P<s>\d{2})[,.](?P<ms>\d{3})")
RANGE = re.compile(r"^\s*(\d+:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d+:\d{2}:\d{2}[,.]\d{3})")


def read_time(s):
    m = TIME.fullmatch(s.strip())
    if not m:
        raise ValueError("Invalid subtitle time")
    return 3600 * int(m["h"]) + 60 * int(m["m"]) + int(m["s"]) + int(m["ms"]) / 1000


def parse_srt(data):
    blocks = re.split(r"\r?\n\s*\r?\n", data.strip())
    rows = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        idx = next((i for i, line in enumerate(lines) if RANGE.match(line)), None)
        if idx is None:
            continue
        m = RANGE.match(lines[idx])
        start, end = read_time(m[1]), read_time(m[2])
        text = " ".join(lines[idx + 1:]).strip()
        if not text or start >= end:
            continue
        rows.append({"start": start, "end": end, "text": text})
    rows.sort(key=lambda row: (row["start"], row["end"]))
    if not rows:
        raise ValueError("No valid subtitle entries found")
    return rows


def srt_time(sec):
    ticks = max(0, int(round(sec * 1000)))
    ms = ticks % 1000
    whole = ticks // 1000
    return f"{whole // 3600:02}:{(whole // 60) % 60:02}:{whole % 60:02},{ms:03}"


def sliced_subtitles(rows, start, end):
    return [
        {"start": max(0, r["start"] - start), "end": min(end, r["end"]) - start,
         "text": r["text"]}
        for r in rows if r["end"] > start and r["start"] < end
    ]


def write_srt(path, rows):
    lines = []
    for i, row in enumerate(rows, 1):
        lines += [str(i), f'{srt_time(row["start"])} --> {srt_time(row["end"])}',
                  row["text"], ""]
    path.write_text("\n".join(lines), encoding="utf-8")


def ass_time(t):
    cs = max(0, int(round(t * 100)))
    return f"{cs // 360000}:{(cs // 6000) % 60:02}:{(cs // 100) % 60:02}.{cs % 100:02}"


def ass_clean(text):
    # ASS user text is data, never style directives.
    return text.replace("\\", " ").replace("{", "(").replace("}", ")").replace("\r", " ")


def make_ass(path, rows, portrait=True, centre=False):
    size = 72 if portrait else 48
    alignment = 5 if centre else 2
    margin = 160 if portrait and not centre else 85
    header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name,Fontname,Fontsize,PrimaryColour,SecondaryColour,OutlineColour,BackColour,Bold,Italic,Underline,StrikeOut,ScaleX,ScaleY,Spacing,Angle,BorderStyle,Outline,Shadow,Alignment,MarginL,MarginR,MarginV,Encoding
Style: Default,DejaVu Sans,%d,&H00FFFFFF,&H0000FFFF,&H00202020,&H7F000000,-1,0,0,0,100,100,0,0,1,4,2,%d,78,78,%d,1
[Events]
Format: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text
""" % (size, alignment, margin)
    events = []
    for row in rows:
        if row["end"] <= row["start"]:
            continue
        # Limit length of a single line to keep text in portrait safe area.
        text = ass_clean(row["text"])
        text = "\\N".join(textwrap.wrap(text, width=30 if portrait else 52,
                                          break_long_words=False, break_on_hyphens=False)[:7])
        events.append(f'Dialogue: 0,{ass_time(row["start"])},{ass_time(row["end"])},Default,,0,0,0,,{text}')
    path.write_text(header + "\n".join(events) + "\n", encoding="utf-8")


def escape_filter_path(path):
    # FFmpeg filter-option escaping: literal backslash, colon, quote and comma.
    return str(path).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'").replace(",", "\\,")


def video_filter(orientation="portrait", burn_ass=None, fit="pad"):
    if orientation == "source":
        filters = ["setsar=1", "fps=30"]
    else:
        width, height = (1080, 1920) if orientation == "portrait" else (1920, 1080)
        if fit == "crop":
            filters = [f"scale={width}:{height}:force_original_aspect_ratio=increase:flags=lanczos",
                       f"crop={width}:{height}"]
        else:
            filters = [f"scale={width}:{height}:force_original_aspect_ratio=decrease:flags=lanczos",
                       f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=0x101820"]
        filters += ["setsar=1", "fps=30"]
    if burn_ass:
        filters.append("ass='" + escape_filter_path(burn_ass) + "'")
    filters.append("format=yuv420p")
    return ",".join(filters)


def video_cmd(src, out, *, start=0, end=None, orientation="portrait",
              fit="pad", ass=None):
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n"]
    if start:
        cmd += ["-ss", f"{start:.3f}"]
    cmd += ["-i", str(src)]
    if end is not None:
        cmd += ["-t", f"{end - start:.3f}"]
    cmd += ["-map", "0:v:0", "-map", "0:a:0?",
            "-vf", video_filter(orientation, ass, fit),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
            "-pix_fmt", "yuv420p", "-r", "30",
            "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)]
    return cmd


def silence_intervals(video, duration, *, threshold="-35dB", minimum=0.65):
    # FFmpeg silencedetect reports events on stderr; all source stays local.
    cmd = ["ffmpeg", "-hide_banner", "-nostdin", "-i", str(video),
           "-af", f"silencedetect=noise={threshold}:d={minimum}",
           "-f", "null", "-"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", timeout=240)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Local silence detection failed") from exc
    if proc.returncode:
        raise ValueError("Silence detection failed: " + proc.stderr[-400:])
    starts = [float(x) for x in re.findall(r"silence_start:\s*([\d.]+)", proc.stderr)]
    ends = [float(x) for x in re.findall(r"silence_end:\s*([\d.]+)", proc.stderr)]
    silence = []
    for i, a in enumerate(starts):
        b = ends[i] if i < len(ends) else duration
        if b > a:
            silence.append((a, b))
    # If the final silence did not have a closing event, use duration.
    if len(ends) < len(starts) and silence:
        silence[-1] = (silence[-1][0], duration)
    return silence


def keep_ranges(start, end, silence, padding=0.12):
    gaps = []
    for a, b in silence:
        a, b = max(start, a + padding), min(end, b - padding)
        if a < b:
            gaps.append((a, b))
    gaps.sort()
    kept, cursor = [], start
    for a, b in gaps:
        if a - cursor >= 0.25:
            kept.append((cursor, a))
        cursor = max(cursor, b)
    if end - cursor >= 0.25:
        kept.append((cursor, end))
    return kept


def write_json_new(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")
