#!/usr/bin/env python3
"""Local, non-destructive visual/audio review hints using FFmpeg and FFprobe."""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

NUMBER = r"-?\d+(?:\.\d+)?"
PATTERNS = {
    "black_start": rf"black_start:({NUMBER})",
    "black_end": rf"black_end:({NUMBER})",
    "freeze_start": rf"freeze_start:\s*({NUMBER})",
    "freeze_end": rf"freeze_end:\s*({NUMBER})",
    "silence_start": rf"silence_start:\s*({NUMBER})",
    "silence_end": rf"silence_end:\s*({NUMBER})",
    "shot_change": rf"\bpts_time:({NUMBER})",
}


def events(log, keys):
    result = []
    for line in log.splitlines():
        if "showinfo" in line and "shot_change" in keys:
            match = re.search(PATTERNS["shot_change"], line)
            if match:
                result.append({"type": "shot_change", "seconds": float(match[1])})
        for key in keys:
            if key == "shot_change":
                continue
            match = re.search(PATTERNS[key], line)
            if match:
                result.append({"type": key, "seconds": float(match[1])})
    return sorted(result, key=lambda item: item["seconds"])


def run(args):
    proc = subprocess.run(args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", check=False)
    if proc.returncode:
        raise ValueError(f"{args[0]} failed ({proc.returncode}): {proc.stderr[-600:]}")
    return proc


def inspect(video, threshold):
    probe = run(["ffprobe", "-v", "error", "-show_format", "-show_streams",
                 "-of", "json", str(video)])
    meta = json.loads(probe.stdout)
    streams = meta.get("streams", [])
    v = next((s for s in streams if s.get("codec_type") == "video"), None)
    if v is None:
        raise ValueError("No video stream")
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    base = ["ffmpeg", "-nostdin", "-hide_banner", "-nostats", "-i", str(video)]
    vf = ("scale=640:-2,blackdetect=d=0.4:pix_th=0.10,"
          "freezedetect=n=-50dB:d=2,select=gt(scene\\," + str(threshold) + "),showinfo")
    visual = run([*base, "-map", "0:v:0", "-an", "-vf", vf, "-f", "null", "-"])
    found = events(visual.stderr, ("black_start", "black_end", "freeze_start",
                                   "freeze_end", "shot_change"))
    if audio:
        sound = run([*base, "-map", "0:a:0", "-vn", "-af", "silencedetect=n=-45dB:d=0.7",
                     "-f", "null", "-"])
        found.extend(events(sound.stderr, ("silence_start", "silence_end")))
    found.sort(key=lambda item: item["seconds"])
    return {"file": video.name, "duration": meta.get("format", {}).get("duration"),
            "width": v.get("width"), "height": v.get("height"),
            "fps": v.get("avg_frame_rate"), "audio_present": audio is not None,
            "scene_threshold": threshold, "events": found,
            "note": "Heuristic review hints only. Static slides, black transitions and pauses may be intentional. End events may be absent at EOF. No media is modified."}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("video", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--scene-threshold", type=float, default=.35)
    a = ap.parse_args()
    try:
        if not 0 < a.scene_threshold < 1:
            raise ValueError("Scene threshold must be between 0 and 1")
        if a.out.exists():
            raise ValueError("Output exists")
        report = inspect(a.video.resolve(), a.scene_threshold)
        with a.out.open("x", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        counts = {}
        for event in report["events"]:
            kind = event["type"]
            counts[kind] = counts.get(kind, 0) + 1
        print(json.dumps(counts, ensure_ascii=False) + f" -> {a.out}")
    except (OSError, ValueError, KeyError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
