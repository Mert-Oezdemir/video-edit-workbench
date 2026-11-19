#!/usr/bin/env python3
"""Local three-mode production. No AI APIs, installers or downloaded models.

init -> edit production.json with your existing agent -> doctor -> preview
-> watch preview -> final --approve-preview SHA256. Sources are never modified.
"""
import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

from creative_overlay import ass, captions

MODES = ("long-to-shorts", "faceless", "own-footage")
SIZES = {"preview": (360, 640), "final": (1080, 1920)}
IMAGE_TYPES = {".png", ".jpg", ".jpeg", ".webp"}


def write_new(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def digest(path):
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(block)
    return result.hexdigest()


def local_file(root, value):
    if not isinstance(value, str) or not value or "://" in value:
        raise ValueError("Media must be a local project-relative file")
    path = Path(value)
    if path.is_absolute():
        raise ValueError("Use project-relative media paths")
    resolved = (root / path).resolve(strict=True)
    if not resolved.is_relative_to(root) or not resolved.is_file():
        raise ValueError("Media must stay inside the project: " + value)
    return resolved


def number(value, label, positive=False):
    if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
        raise ValueError("Invalid " + label)
    if positive and value <= 0:
        raise ValueError(label + " must be positive")
    return value


def command(argv, cwd=None, timeout=1800):
    result = subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                            encoding="utf-8", errors="replace", timeout=timeout)
    if result.returncode:
        raise ValueError(Path(argv[0]).name + " failed: " + result.stderr[-1800:])
    return result.stdout


def probe(path):
    return json.loads(command(["ffprobe", "-v", "error", "-protocol_whitelist", "file,pipe",
                               "-show_streams", "-show_format", "-of", "json", str(path)], timeout=45))



def validate_visual_component(root, item, path):
    """Treat an external Lemo clip as one native, reviewable timeline segment."""
    data = item.get("visual_component")
    if data is None:
        return None
    if (not isinstance(data, dict) or set(data) != {"tool", "style", "handoff"}
            or data.get("tool") != "lemo-opuscar"
            or not isinstance(data.get("style"), str)
            or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", data["style"])):
        raise ValueError("visual_component needs tool=lemo-opuscar, style slug and handoff")
    manifest_file = local_file(root, data["handoff"])
    if manifest_file.suffix != ".json" or manifest_file.parent != (root / "work" / "handoffs").resolve():
        raise ValueError("Visual component handoff must be project/work/handoffs/*.json")
    if manifest_file.stat().st_size > 1024 * 1024:
        raise ValueError("Visual component handoff is too large")
    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    if (not isinstance(manifest, dict)
            or manifest.get("tool") != "lemo-opuscar"
            or manifest.get("kind") != "rendered-video"
            or manifest.get("file") != path.relative_to(root).as_posix()
            or manifest.get("review_status") != "pending-human-review"
            or manifest.get("approved") is not False):
        raise ValueError("Lemo component requires matching, unapproved local video handoff")
    if path.suffix.lower() not in {".mp4", ".mov", ".mkv", ".webm"}:
        raise ValueError("Lemo visual component must be a video, not a still image")
    return {"tool": data["tool"], "style": data["style"], "handoff": manifest_file}


def load_job(root):
    raw = json.loads((root / "production.json").read_text(encoding="utf-8-sig"))
    allowed = {"schema_version", "mode", "segments", "narration", "captions", "framing"}
    if not isinstance(raw, dict) or set(raw) - allowed:
        raise ValueError("Unknown production fields; see examples/production")
    if type(raw.get("schema_version")) is not int or raw["schema_version"] != 1 or raw.get("mode") not in MODES:
        raise ValueError("Expected schema_version 1 and a supported mode")
    if raw.get("framing", "fit") not in ("fit", "crop"):
        raise ValueError("framing must be fit or crop (center crop; no face tracking)")
    segments = raw.get("segments")
    if not isinstance(segments, list) or not 1 <= len(segments) <= 200:
        raise ValueError("Provide 1..200 reviewed segments")
    media, total, handoffs = [], 0, set()
    for item in segments:
        if not isinstance(item, dict) or set(item) - {"source", "start", "duration", "visual_component"}:
            raise ValueError("Segment fields: source, start, duration")
        path = local_file(root, item.get("source"))
        component = validate_visual_component(root, item, path)
        if component:
            handoffs.add(component["handoff"])
        start = number(item.get("start", 0), "start")
        duration = number(item.get("duration"), "duration", True)
        if duration > 3600 or total + duration > 7200:
            raise ValueError("Limit: 3600 seconds per segment, 7200 per job")
        info = probe(path)
        streams = info.get("streams", [])
        if not any(s.get("codec_type") == "video" for s in streams):
            raise ValueError("No video/image stream: " + str(path))
        image = path.suffix.lower() in IMAGE_TYPES
        if image and start:
            raise ValueError("Image start must be zero")
        if not image:
            length = float(info.get("format", {}).get("duration", 0))
            if not math.isfinite(length) or start + duration > length + .02:
                raise ValueError("Segment exceeds source duration: " + str(path))
        media.append({"path": path, "start": start, "duration": duration, "image": image,
                      "audio": any(s.get("codec_type") == "audio" for s in streams),
                      "visual_component": component})
        total += duration
    narration = None
    if raw.get("narration") is not None:
        if raw["mode"] != "faceless":
            raise ValueError("Separate narration is supported only in faceless mode")
        narration = local_file(root, raw["narration"])
        info = probe(narration)
        if not any(s.get("codec_type") == "audio" for s in info.get("streams", [])):
            raise ValueError("Narration has no audio stream")
        length = float(info.get("format", {}).get("duration", 0))
        if not math.isfinite(length) or length < total - .05:
            raise ValueError("Narration is shorter than the storyboard")
    cues = raw.get("captions", [])
    if not isinstance(cues, list):
        raise ValueError("captions must be a list")
    words = []
    for cue in cues:
        if not isinstance(cue, dict) or set(cue) != {"start", "end", "text"}:
            raise ValueError("Caption fields: start, end, text")
        start, end = number(cue["start"], "caption start"), number(cue["end"], "caption end")
        if not start < end <= total or not isinstance(cue["text"], str) or not cue["text"].strip():
            raise ValueError("Invalid caption text or output-timeline bounds")
        words.append([start, end, cue["text"]])
    files = {m["path"] for m in media} | handoffs
    if narration:
        files.add(narration)
    fingerprint = hashlib.sha256(json.dumps(raw, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    inputs = {p.relative_to(root).as_posix(): digest(p) for p in sorted(files)}
    return {"spec": raw, "media": media, "narration": narration, "duration": total,
            "words": words, "identity": {"manifest_sha256": fingerprint, "inputs_sha256": inputs}}


def doctor(root):
    checks = {name: bool(shutil.which(name)) for name in ("ffmpeg", "ffprobe")}
    errors = []
    if all(checks.values()):
        try:
            encoders = command(["ffmpeg", "-hide_banner", "-encoders"], timeout=30)
            filters = command(["ffmpeg", "-hide_banner", "-filters"], timeout=30)
            checks.update({"libx264": "libx264" in encoders, "aac": " aac " in encoders,
                           "ass": " ass " in filters})
            load_job(root)
        except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
            errors.append(str(exc))
    return {"ready": all(checks.values()) and not errors, "checks": checks, "errors": errors,
            "scope": "Local binaries, codecs, filters and project media metadata; no model/GPU/AI test"}


def render(root, job, kind, approval=None):
    out = root / "out"
    out.mkdir(exist_ok=True)
    if not out.resolve().is_relative_to(root):
        raise ValueError("out must remain inside the project")
    preview = out / "preview.mp4"
    receipt_path = out / "preview-review.json"
    if kind == "final":
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        if (not approval or approval != receipt.get("preview_sha256") or
                approval != digest(preview) or job["identity"] != receipt.get("identity")):
            raise ValueError("Preview approval missing/stale: review a fresh preview and pass its SHA256")
    target = out / (kind + ".mp4")
    if target.exists() or (kind == "preview" and receipt_path.exists()):
        raise ValueError("Output exists; use a new project or archive the previous output")
    work = root / "work"
    work.mkdir(exist_ok=True)
    if not work.resolve().is_relative_to(root):
        raise ValueError("work must remain inside the project")
    # Exclusive directory reserves this run; keep logs/partials after failure for diagnosis.
    import tempfile
    run = Path(tempfile.mkdtemp(prefix="production-", dir=work))
    width, height = SIZES[kind]
    framing = job["spec"].get("framing", "fit")
    vf = (f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
          f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2") if framing == "fit" else (
          f"scale={width}:{height}:force_original_aspect_ratio=increase,crop={width}:{height}")
    vf += ",setsar=1,fps=30,format=yuv420p"
    ff = ["ffmpeg", "-nostdin", "-v", "error", "-n"]
    encode = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
              "-c:a", "aac", "-ar", "48000", "-ac", "2"]
    for index, segment in enumerate(job["media"]):
        cmd = ff + ["-protocol_whitelist", "file,pipe"]
        cmd += ["-loop", "1"] if segment["image"] else ["-ss", str(segment["start"])]
        cmd += ["-i", str(segment["path"])]
        if not segment["audio"]:
            cmd += ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"]
        cmd += ["-map", "0:v:0", "-map", "0:a:0" if segment["audio"] else "1:a:0",
                "-t", str(segment["duration"]), "-vf", vf,
                "-af", "apad,aresample=48000", *encode, str(run / f"part-{index}.mp4")]
        command(cmd)
    (run / "parts.txt").write_text("".join(f"file 'part-{i}.mp4'\n" for i in range(len(job["media"]))), encoding="utf-8")
    command(ff + ["-f", "concat", "-safe", "1", "-i", "parts.txt", "-c", "copy", "joined.mp4"], cwd=run)
    prog = {"duration": job["duration"], "words": job["words"]}
    (run / "overlay.ass").write_text(ass(prog, "short", captions(prog, "short"), []), encoding="utf-8")
    cmd = ff + ["-i", "joined.mp4"]
    if job["narration"]:
        cmd += ["-protocol_whitelist", "file,pipe", "-i", str(job["narration"])]
    cmd += ["-map", "0:v:0", "-map", "1:a:0" if job["narration"] else "0:a:0",
            "-vf", "ass=overlay.ass", "-t", str(job["duration"]), *encode,
            "-movflags", "+faststart", "result.mp4"]
    command(cmd, cwd=run)
    result = run / "result.mp4"
    info = probe(result)
    video = next(s for s in info["streams"] if s["codec_type"] == "video")
    if (video["width"], video["height"]) != (width, height):
        raise ValueError("Unexpected output dimensions")
    if abs(float(info["format"]["duration"]) - job["duration"]) > .2 + len(job["media"]) / 30:
        raise ValueError("Output duration mismatch")
    command(["ffmpeg", "-nostdin", "-v", "error", "-i", str(result), "-f", "null", "-"], timeout=1800)
    # Exclusive copy prevents another invocation overwriting a reviewed render.
    with target.open("xb") as dest, result.open("rb") as source:
        shutil.copyfileobj(source, dest)
    receipt = {"identity": job["identity"], "preview_sha256": digest(target),
               "review_status": "pending-human-review", "mode": job["spec"]["mode"]}
    if kind == "preview":
        write_new(receipt_path, receipt)
        print("Watch", target, "then final --approve-preview", receipt["preview_sha256"])
    else:
        print("Final:", target)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, required=True)
    sub = parser.add_subparsers(dest="action", required=True)
    init = sub.add_parser("init")
    init.add_argument("--mode", choices=MODES, required=True)
    sub.add_parser("doctor")
    sub.add_parser("preview")
    final = sub.add_parser("final")
    final.add_argument("--approve-preview", required=True)
    args = parser.parse_args(argv)
    try:
        root = args.project.resolve()
        if args.action == "init":
            root.mkdir(parents=True, exist_ok=True)
            write_new(root / "production.json", {"schema_version": 1, "mode": args.mode,
                      "framing": "fit", "segments": [{"source": "src/replace-me.mp4", "start": 0,
                      "duration": 5}], "captions": []})
            (root / "src").mkdir(exist_ok=True)
            print("Edit production.json with your existing coding agent; supply local media, reviewed cuts and captions.")
            return 0
        report = doctor(root)
        if args.action == "doctor" or not report["ready"]:
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0 if report["ready"] else 1
        render(root, load_job(root), args.action, getattr(args, "approve_preview", None))
        return 0
    except (ValueError, OSError, KeyError, TypeError, StopIteration, subprocess.TimeoutExpired) as exc:
        print("Error:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
