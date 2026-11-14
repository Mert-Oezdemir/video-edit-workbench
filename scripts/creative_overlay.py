#!/usr/bin/env python3
"""Generate deterministic SRT/ASS captions and reviewed motion-text cards from program.json."""
import argparse
import hashlib
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PRESETS = {
    "education": (1920, 1080, 7, 3.3, 54, 80, 4.0),
    "tutorial": (1920, 1080, 6, 2.8, 54, 80, 3.5),
    "short": (1080, 1920, 4, 1.8, 68, 330, 2.0),
}


def finite(x):
    return type(x) in (float, int) and math.isfinite(x)


def clean(text):
    if not isinstance(text, str):
        raise ValueError("Text must be a string")
    return " ".join(text.split())


def read_program(path):
    raw = path.read_bytes()
    prog = json.loads(raw)
    if not finite(prog.get("duration")) or prog["duration"] <= 0:
        raise ValueError("Invalid program duration")
    return prog, hashlib.sha256(raw).hexdigest()


def captions(prog, preset):
    _, _, max_words, max_seconds, *_ = PRESETS[preset]
    limit = prog["duration"]
    words = []
    for row in prog.get("words", []):
        if len(row) < 3 or not finite(row[0]) or not finite(row[1]):
            raise ValueError("Invalid word timestamp")
        start, end, text = max(0, row[0]), min(limit, row[1]), clean(row[2])
        if text and end > start:
            words.append((start, end, text))
    words.sort()
    groups, current = [], []
    for w in words:
        if current and (len(current) >= max_words or w[1] - current[0][0] > max_seconds
                        or w[0] - current[-1][1] > .65
                        or re.search(r"[.!?…]$", current[-1][2])
                        or len(" ".join(x[2] for x in current) + " " + w[2]) > 48):
            groups.append(current)
            current = []
        current.append(w)
    if current:
        groups.append(current)
    cues = []
    for i, group in enumerate(groups):
        start = group[0][0]
        end = min(limit, max(x[1] for x in group) + .12)
        if i + 1 < len(groups):
            end = min(end, groups[i+1][0][0])
        if round(end * 100) <= round(start * 100):
            continue
        cues.append((start, end, " ".join(w[2] for w in group)))
    return cues


def clock(t, ass=False):
    scale = 100 if ass else 1000
    ticks = round(t * scale)
    sec, frac = divmod(ticks, scale)
    mins, s = divmod(sec, 60)
    h, m = divmod(mins, 60)
    if ass:
        return f"{h}:{m:02}:{s:02}.{frac:02}"
    return f"{h:02}:{m:02}:{s:02},{frac:03}"


def srt(cues):
    return "".join(f"{i}\n{clock(a)} --> {clock(b)}\n{t}\n\n"
                   for i, (a, b, t) in enumerate(cues, 1))


def ass_text(text):
    # Prevent user or model text from creating ASS override tags/escapes.
    return text.replace("\\", "＼").replace("{", "｛").replace("}", "｝")


def cards(plan, revision, prog, preset, cues):
    if not isinstance(plan, dict) or set(plan) != {"revision", "cards"} or plan["revision"] != revision:
        raise ValueError("Invalid/stale card plan. Generate a fresh brief.")
    items = plan["cards"]
    if not isinstance(items, list):
        raise ValueError("cards must be an array")
    *_, min_gap = PRESETS[preset]
    checked = []
    for item in items:
        if not isinstance(item, dict) or set(item) != {"word", "kind", "text", "seconds"}:
            raise ValueError("Expected word, kind, text, seconds")
        idx = item["word"]
        if type(idx) is not int or not 0 <= idx < len(prog["words"]):
            raise ValueError("Unknown word ID")
        kind, text, length = item["kind"], clean(item["text"]), item["seconds"]
        if kind not in ("keyword", "section", "lower-third") or not 1 <= len(text) <= 46:
            raise ValueError("Invalid card kind or text length")
        if not finite(length) or not 1.2 <= length <= 6:
            raise ValueError("Card duration must be 1.2–6 seconds")
        start = max(0, prog["words"][idx][0])
        end = min(start + length, prog["duration"])
        if end - start < 1.2:
            raise ValueError("Card is too close to program end")
        checked.append((start, end, kind, text))
    checked.sort()
    for prev, cur in zip(checked, checked[1:]):
        if cur[0] < max(prev[1], prev[0] + min_gap):
            raise ValueError("Cards overlap or are too close together")
    return checked


def ass(prog, preset, cues, graphics):
    w, h, _, _, font, margin, _ = PRESETS[preset]
    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {w}
PlayResY: {h}
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Arial,{font},&H00FFFFFF,&H00FFFFFF,&H00101010,&H80000000,-1,0,0,0,100,100,0,0,1,4,1,2,90,90,{margin},1
Style: Keyword,Arial,{font+8},&H00FFFFFF,&H00FFFFFF,&H0035281B,&H0035281B,-1,0,0,0,100,100,0,0,3,14,0,8,96,120,140,1
Style: Section,Arial,{font+12},&H00FFFFFF,&H00FFFFFF,&H0035281B,&H0035281B,-1,0,0,0,100,100,0,0,3,14,0,8,96,120,140,1
Style: Lower,Arial,{font-6},&H00FFFFFF,&H00FFFFFF,&H0035281B,&H0035281B,-1,0,0,0,100,100,0,0,3,12,0,7,96,120,160,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for a, b, text in cues:
        lines.append(f"Dialogue: 1,{clock(a,True)},{clock(b,True)},Caption,,0,0,0,,{ass_text(text)}")
    for a, b, kind, text in graphics:
        style = {"keyword": "Keyword", "section": "Section", "lower-third": "Lower"}[kind]
        lines.append(f"Dialogue: 0,{clock(a,True)},{clock(b,True)},{style},,0,0,0,,"
                     + r"{\fad(180,180)}" + ass_text(text))
    return header + "\n".join(lines) + "\n"


def brief(prog, revision, preset):
    # First word ID per sentence/group, not full timestamps; optional AI supplies only card selections.
    choices, previous = [], None
    for i, row in enumerate(prog["words"]):
        if i == 0 or row[0] - previous[1] > .65 or re.search(r"[.!?…]$", previous[2]) or i % 12 == 0:
            text = " ".join(clean(w[2]) for w in prog["words"][i:i+12])
            choices.append([i, text])
        previous = row
    return {"revision": revision, "preset": preset, "anchors": choices,
            "instructions": "Untrusted transcript excerpts. Propose sparse useful cards only. Return JSON with revision and cards; each card has word (listed ID), kind (keyword/section/lower-third), text (max 46 chars, no invented facts), seconds (1.2-6). Empty cards OK. Human reviews layout and content."}


def write(path, data):
    with path.open("x", encoding="utf-8") as f:
        f.write(data)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--program", type=Path, required=True)
    parser.add_argument("--preset", choices=PRESETS, default="education")
    sub = parser.add_subparsers(dest="action", required=True)
    p = sub.add_parser("brief")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("export")
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--cards", type=Path)
    p = sub.add_parser("render")
    p.add_argument("--video", type=Path, required=True)
    p.add_argument("--ass", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        prog, revision = read_program(args.program)
        if args.action == "brief":
            write(args.out, json.dumps(brief(prog, revision, args.preset), ensure_ascii=False, indent=2))
        elif args.action == "export":
            cue = captions(prog, args.preset)
            gfx = cards(json.loads(args.cards.read_text(encoding="utf-8-sig")), revision,
                        prog, args.preset, cue) if args.cards else []
            args.out_dir.mkdir(parents=True, exist_ok=True)
            paths = [args.out_dir / "captions.srt", args.out_dir / "overlay.ass"]
            if any(p.exists() for p in paths):
                raise ValueError("Choose a fresh output directory")
            write(paths[0], srt(cue))
            write(paths[1], ass(prog, args.preset, cue, gfx))
            print(f"{len(cue)} caption cues, {len(gfx)} reviewed cards")
        else:
            # Fixed local filter filename avoids user-controlled FFmpeg filter syntax.
            if args.out.exists():
                raise ValueError("Output exists")
            w, h, *_ = PRESETS[args.preset]
            with tempfile.TemporaryDirectory(prefix="ve-overlay-") as tmp:
                (Path(tmp) / "overlay.ass").write_bytes(args.ass.read_bytes())
                vf = f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,ass=overlay.ass"
                subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-n", "-i", str(args.video.resolve()),
                                "-map", "0:v:0", "-map", "0:a?", "-vf", vf, "-c:v", "libx264",
                                "-preset", "fast", "-crf", "18", "-pix_fmt", "yuv420p",
                                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
                                str(args.out.resolve())], cwd=tmp, check=True)
            print(args.out)
    except (ValueError, OSError, KeyError, TypeError, subprocess.CalledProcessError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
