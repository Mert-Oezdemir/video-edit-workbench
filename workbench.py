#!/usr/bin/env python3
"""Video Edit Workbench: one local-first entry point for humans and AI agents.

Quick examples (run in the repository directory):
  python workbench.py init ~/Videos/my-project
  python workbench.py doctor
  python workbench.py shorts --project ~/Videos/my-project --input src/talk.mp4 --use-whisper --allow-model-download
  python workbench.py faceless --project ~/Videos/my-project --script src/script.txt
  python workbench.py edit --project ~/Videos/my-project --input src/talk.mp4 --format portrait

No paid API, credit, remote rendering, upload or automatic package installer.
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent / "scripts"
sys.path.insert(0, str(SCRIPTS))

from workbench_media import must_have, probe, run
from workbench_modes import mode_edit, mode_faceless, mode_shorts
from video_tool_stack import eligibility, registry


def project_init(path):
    root = Path(path).expanduser().resolve()
    if root.exists() and not root.is_dir():
        raise ValueError("Project path exists but is not a folder")
    cfg = root / "video-workbench.json"
    if cfg.exists():
        raise ValueError("Project already initialized; refusing to replace its config")
    for name in ("src", "work", "out"):
        (root / name).mkdir(parents=True, exist_ok=True)
    # The project owns media and outputs. Optional tools remain in separate environments.
    config = {"schema_version": 1, "source_dir": "src", "work_dir": "work",
              "output_dir": "out", "default_format": "portrait",
              "extra_api_spend": False, "cloud_render": False,
              "upload_private_footage": False, "review_before_publish": True}
    with cfg.open("x", encoding="utf-8") as stream:
        json.dump(config, stream, indent=2)
        stream.write("\n")
    print(f"Created non-destructive project: {root}")
    print("Add your owned/authorized media to src/ and run a mode with --project", root)


def check_doctor(as_json=False):
    import importlib.util
    data = registry()
    core = {"python_3_10_plus": sys.version_info >= (3, 10),
            "ffmpeg": shutil.which("ffmpeg") is not None,
            "ffprobe": shutil.which("ffprobe") is not None,
            "numpy": importlib.util.find_spec("numpy") is not None,
            "faster_whisper": importlib.util.find_spec("faster_whisper") is not None}
    report = {
        "core": core,
        "ready_to_edit_without_transcription": core["ffmpeg"] and core["ffprobe"],
        "ready_to_transcribe_locally": core["faster_whisper"] and core["ffmpeg"],
        "tool_count": len(data["tools"]),
        "modes": data["modes"],
        "cost_policy": data["policy"],
        "warnings": [
            "Whisper model weights are downloaded only with explicit --allow-model-download.",
            "The tool catalog is a selection guide, not installed working integrations.",
            "Voice model, stock image, copyright and source licenses require review.",
            "Results need human quality checks; 'viral' is not guaranteed."
        ]
    }
    if as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("Video Edit Workbench — local readiness\n")
        for name, ok in core.items():
            print(f"  {'OK' if ok else '--'}  {name}")
        print("\nLocal edit ready:", "yes" if report["ready_to_edit_without_transcription"] else "no")
        print("Local Whisper ready:", "yes" if report["ready_to_transcribe_locally"] else "no")
        print("Free-first policy: no paid API / no cloud render / no implicit media upload")
        print("Try: python workbench.py --help")
    return 0 if core["ffmpeg"] and core["ffprobe"] else 1


def list_tools(mode, as_json):
    data = registry()
    tools = [t for t in data["tools"] if mode is None or mode in t["modes"]]
    if as_json:
        print(json.dumps({"mode": mode, "tools": [
            {"id": t["id"], "name": t["name"], "url": t["url"],
             "eligibility": eligibility(t), "note": t["note"]} for t in tools]},
            ensure_ascii=False, indent=2))
    else:
        for t in tools:
            print(f"{t['id']:20} {eligibility(t):27} {t['role']}")
        print("Local-free means free-code processing, not automatically installed or tested.")
    return 0


def make_parser():
    parser = argparse.ArgumentParser(
        description="Create Shorts and local video edits with no extra AI/API charges.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="See QUICKSTART_TR.md and AI_START.md. All outputs are review-first and local.")
    commands = parser.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="Create safe src/work/out project folders")
    init.add_argument("path", help="New project folder")

    doctor = commands.add_parser("doctor", help="Check installed local capabilities; no downloads")
    doctor.add_argument("--json", action="store_true")

    tools = commands.add_parser("tools", help="List free-code tools and their limitations")
    tools.add_argument("--mode", choices=["long-to-shorts", "faceless", "own-footage"])
    tools.add_argument("--json", action="store_true")

    shorts = commands.add_parser("shorts", help="Suggest and render vertical clips from an owned long recording")
    shorts.add_argument("--project", required=True)
    shorts.add_argument("--input", required=True, help="Video file within project/src/")
    transcript = shorts.add_mutually_exclusive_group()
    transcript.add_argument("--srt", help="Existing subtitles within the project")
    transcript.add_argument("--use-whisper", action="store_true",
                            help="Transcribe using installed faster-whisper locally")
    shorts.add_argument("--model", default="small", help="Whisper model or local model directory")
    shorts.add_argument("--device", choices=["cpu", "cuda", "auto"], default="cpu")
    shorts.add_argument("--allow-model-download", action="store_true",
                        help="Allow Whisper weights download (never an inference API)")
    shorts.add_argument("--selections", help="Reviewed JSON with clips start/end/title, overrides scoring")
    shorts.add_argument("--count", type=int, default=3)
    shorts.add_argument("--minimum", type=float, default=12)
    shorts.add_argument("--maximum", type=float, default=55)
    shorts.add_argument("--fit", choices=["pad", "crop"], default="pad")
    shorts.add_argument("--burn-captions", action="store_true",
                        help="Burn in local SRT/Whisper captions (FFmpeg libass required)")
    shorts.add_argument("--plan-only", action="store_true", help="Write candidate plan, do not render")
    shorts.add_argument("--plan-out", help="New plan file under project/out")
    shorts.add_argument("--out-dir", help="New output folder under project/out")

    edit = commands.add_parser("edit", help="Quick edit or silence trim of owned local footage")
    edit.add_argument("--project", required=True)
    edit.add_argument("--input", required=True, action="append", help="One or more local source videos")
    edit.add_argument("--start", type=float, help="Optional start seconds (single source only)")
    edit.add_argument("--end", type=float, help="Optional end seconds (single source only)")
    edit.add_argument("--format", choices=["source", "portrait", "landscape"], default="source")
    edit.add_argument("--fit", choices=["pad", "crop"], default="pad")
    edit.add_argument("--remove-silence", action="store_true",
                      help="Non-destructive FFmpeg silence detection and cut")
    edit.add_argument("--silence-threshold", default="-35dB")
    edit.add_argument("--silence-duration", type=float, default=0.65)
    edit.add_argument("--srt", help="Local subtitles for single continuous input")
    edit.add_argument("--plan-only", action="store_true")
    edit.add_argument("--plan-out", help="New local plan under project/out")
    edit.add_argument("--output", help="New MP4 under project/out (default out/edited.mp4)")

    face = commands.add_parser("faceless", help="Create 9:16 caption-card video with optional images/voice")
    face.add_argument("--project", required=True)
    face.add_argument("--script", required=True, help="Local UTF-8 txt/md, paragraphs become scenes")
    face.add_argument("--images", help="Optional project directory with licensed JPG/PNG/WebP images")
    face.add_argument("--narration", help="Optional existing local voice-over audio")
    face.add_argument("--piper-model", help="Optional local Piper ONNX voice model")
    face.add_argument("--voice-license-confirmed", action="store_true",
                      help="Affirm permission to use the specific TTS model")
    face.add_argument("--seconds-per-scene", type=float, default=4.5)
    face.add_argument("--plan-only", action="store_true")
    face.add_argument("--plan-out", help="New storyboard JSON in project/out")
    face.add_argument("--output", help="New MP4 in project/out (default out/faceless.mp4)")
    return parser


def main(argv=None):
    options = make_parser().parse_args(argv)
    try:
        if options.command == "init":
            project_init(options.path)
        elif options.command == "doctor":
            return check_doctor(options.json)
        elif options.command == "tools":
            return list_tools(options.mode, options.json)
        elif options.command == "shorts":
            mode_shorts(options)
        elif options.command == "edit":
            mode_edit(options)
        elif options.command == "faceless":
            mode_faceless(options)
    except (ValueError, OSError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("Workbench error:", exc, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
