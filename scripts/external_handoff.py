#!/usr/bin/env python3
"""Safely register an optional tool's *existing* local output for human review.

Never calls an AI provider, installs software, moves, imports or overwrites
source files. A video is inspected with locally installed ffprobe (no shell).
Outputs a NEW review manifest in project/work/handoffs, not an approved EDL.
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

from video_tool_stack import eligibility, registry

KINDS = {
    "rendered-video": {".mp4", ".mov", ".mkv", ".webm"},
    "reference-report": {".md", ".html", ".pdf", ".json"},
    "audio": {".wav", ".mp3", ".flac", ".ogg"},
    "image": {".png", ".jpg", ".jpeg", ".webp"}
}


def within(child, parent):
    return child == parent or child.is_relative_to(parent)


def inspect_video(path):
    command = ["ffprobe", "-v", "error", "-show_streams", "-show_format",
               "-of", "json", str(path)]
    try:
        result = subprocess.run(command, check=False, capture_output=True,
                                text=True, encoding="utf-8", timeout=45)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("Local ffprobe unavailable or timed out") from exc
    if result.returncode:
        raise ValueError("ffprobe rejected video: " + result.stderr[:400])
    try:
        info = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid ffprobe output") from exc
    streams = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
    if not streams:
        raise ValueError("No video stream found")
    stream = streams[0]
    return {
        "width": stream.get("width"),
        "height": stream.get("height"),
        "codec": stream.get("codec_name"),
        "duration_seconds": info.get("format", {}).get("duration"),
        "note": "Presence/metadata only; not a content, license or quality review"
    }


def make_handoff(project, tool_id, mode, asset, kind, provenance=""):
    data = registry()
    tools = {tool["id"]: tool for tool in data["tools"]}
    if tool_id not in tools:
        raise ValueError("Unknown tool ID")
    tool = tools[tool_id]
    if mode not in data["modes"] or mode not in tool["modes"]:
        raise ValueError("Tool cannot be routed to requested mode")
    if eligibility(tool) == "blocked-no-extra-spend":
        raise ValueError("Paid-service integration disabled in zero-extra-spend mode")
    root = project.resolve(strict=True)
    work = (root / "work").resolve()
    file = asset if asset.is_absolute() else root / asset
    file = file.resolve(strict=True)
    if not file.is_file() or not within(file, root):
        raise ValueError("Input must be an existing regular file inside the project")
    if file.suffix.lower() not in KINDS[kind]:
        raise ValueError("Unexpected file type for " + kind)
    details = inspect_video(file) if kind == "rendered-video" else {}
    return {
        "schema_version": 1,
        "tool": tool_id,
        "mode": mode,
        "kind": kind,
        "file": file.relative_to(root).as_posix(),
        "source_url": tool["url"],
        "provenance": provenance,
        "review_status": "pending-human-review",
        "approved": False,
        "cost_classification": eligibility(tool),
        "metadata": details,
        "action": "Review rights, authenticity, duration, sync, framing and quality. "
                  "Only then reference this material explicitly in an EDL; this "
                  "manifest never changes work/program.json or work/edl.json."
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", required=True, type=Path)
    ap.add_argument("--tool", required=True)
    ap.add_argument("--mode", required=True, choices=["long-to-shorts", "faceless", "own-footage"])
    ap.add_argument("--kind", required=True, choices=KINDS.keys())
    ap.add_argument("--asset", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path,
                    help="New manifest in project/work/handoffs/ (exclusive write)")
    ap.add_argument("--provenance", default="", help="Local creation notes or rights reference")
    args = ap.parse_args(argv)
    try:
        manifest = make_handoff(args.project, args.tool, args.mode, args.asset,
                                args.kind, args.provenance)
        root = args.project.resolve(strict=True)
        folder = (root / "work" / "handoffs").resolve()
        out = args.out if args.out.is_absolute() else root / args.out
        # Parents can be absent, but must not use symlinks that escape the folder.
        resolved = out.resolve()
        if not within(resolved, folder) or resolved == folder:
            raise ValueError("Manifest must be inside project/work/handoffs/")
        folder.mkdir(parents=True, exist_ok=True)
        if not within(out.resolve(), folder.resolve()):
            raise ValueError("Unsafe manifest path")
        # Do not create nested directories or overwrite an existing manifest.
        with out.open("x", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("Review manifest created:", out)
        return 0
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("Error:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
