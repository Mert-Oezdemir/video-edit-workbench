#!/usr/bin/env python3
"""Three practical, local-first video modes used by workbench.py.

These are intentionally small, conservative paths. Workbench's existing
word-accurate editor remains available for detailed human-guided edits.
"""
import json
import math
import re
import shutil
import tempfile
from pathlib import Path

from workbench_media import (
    AUDIO_EXT, IMAGE_EXT, SUB_EXT, VIDEO_EXT, ensure_video, inside, keep_ranges,
    local_file, make_ass, parse_srt, probe, project_root, run, safe_new_dir,
    safe_output, silence_intervals, sliced_subtitles, video_cmd, video_filter,
    write_json_new, write_srt, must_have
)


def rows_from_whisper(src, model, device, allow_download):
    try:
        from faster_whisper import WhisperModel
    except ImportError as exc:
        raise ValueError("faster-whisper missing: pip install faster-whisper") from exc
    # Cache-only unless the user knowingly permits a model-weight download.
    try:
        backend = WhisperModel(model, device=device, compute_type="int8",
                               local_files_only=not allow_download)
        segs, _ = backend.transcribe(str(src), word_timestamps=False,
                                    vad_filter=True, beam_size=3)
        rows = [{"start": float(s.start), "end": float(s.end), "text": s.text.strip()}
                for s in segs if s.text.strip() and s.end > s.start]
    except Exception as exc:
        raise ValueError("Local Whisper transcription failed. Use a local SRT or "
                         "explicitly allow model download; details: " + str(exc)[:400]) from exc
    if not rows:
        raise ValueError("No speech found. Use --selections with explicit timings.")
    return rows


def score_text(text, duration):
    words = re.findall(r"\w+", text, flags=re.UNICODE)
    lower = text.casefold()
    hooks = ("neden", "nasıl", "işte", "secret", "why", "how", "what if",
             "şimdi", "ama", "because", "surprisingly", "problem")
    hook = 0.9 if "?" in text[:125] or any(w in lower[:135] for w in hooks) else 0
    cadence = 0.25 if text.rstrip().endswith((".", "?", "!")) else 0
    density = min(len(words) / max(duration, 1), 3.5)
    return round(density + hook + cadence, 3)


def suggest_clips(rows, duration, count=3, low=12, high=55):
    candidates = []
    for i, first in enumerate(rows):
        if first["start"] < 0 or first["start"] >= duration:
            continue
        for j in range(i, min(len(rows), i + 120)):
            end = min(duration, rows[j]["end"])
            length = end - first["start"]
            if length > high + 1:
                break
            if length < low:
                continue
            text = " ".join(r["text"] for r in rows[i:j + 1])
            s = score_text(text, length) - abs(length - min(35, high * 0.7)) / (high * 9)
            candidates.append({"start": round(first["start"], 3),
                               "end": round(end, 3), "title": text[:100],
                               "score": round(s, 3),
                               "reason": "Transcript-density/hook heuristic; human review required"})
    candidates.sort(key=lambda c: (-c["score"], c["start"]))
    selected = []
    for c in candidates:
        if all(c["end"] <= v["start"] + 0.02 or c["start"] >= v["end"] - 0.02
               for v in selected):
            selected.append(c)
        if len(selected) >= count:
            break
    return sorted(selected, key=lambda c: c["start"])


def validate_selections(data, src, root, duration):
    if not isinstance(data, dict) or not isinstance(data.get("clips"), list):
        raise ValueError("Selections must be a JSON object with a clips array")
    if "source" in data and (root / str(data["source"])).resolve() != src:
        raise ValueError("Selections refer to a different source video")
    if not 1 <= len(data["clips"]) <= 30:
        raise ValueError("Choose between 1 and 30 clips")
    out = []
    for c in data["clips"]:
        if not isinstance(c, dict):
            raise ValueError("Clip selections must be objects")
        a, b = c.get("start"), c.get("end")
        if (type(a) not in (float, int) or type(b) not in (float, int)
                or not math.isfinite(a) or not math.isfinite(b)
                or a < 0 or b > duration + 0.08 or b - a < 0.25):
            raise ValueError("Invalid clip start/end or range outside source")
        out.append({"start": round(float(a), 3), "end": round(min(duration, float(b)), 3),
                    "title": str(c.get("title", "Untitled"))[:120],
                    "reason": str(c.get("reason", "User/agent selected"))[:250]})
    return out


def mode_shorts(args):
    root = project_root(args.project)
    src = local_file(root, args.input, VIDEO_EXT)
    info = ensure_video(src)
    if not args.srt and not args.use_whisper and not args.selections:
        raise ValueError("Shorts selection needs --srt, --use-whisper or --selections. "
                         "No subscription API is used.")
    if args.srt and args.use_whisper:
        raise ValueError("Choose --srt or --use-whisper, not both")
    if not 1 <= args.count <= 10 or not 0.5 <= args.minimum < args.maximum <= 180:
        raise ValueError("Invalid --count / --minimum / --maximum")
    rows = []
    if args.srt:
        rows = parse_srt(local_file(root, args.srt, SUB_EXT).read_text(encoding="utf-8-sig"))
    elif args.use_whisper:
        rows = rows_from_whisper(src, args.model, args.device, args.allow_model_download)
    if args.selections:
        path = local_file(root, args.selections, {".json"})
        choices = validate_selections(json.loads(path.read_text(encoding="utf-8")), src, root,
                                      info["duration"])
    else:
        choices = suggest_clips(rows, info["duration"], args.count, args.minimum, args.maximum)
    if not choices:
        raise ValueError("No valid speech candidates found. Try lowering --minimum "
                         "or provide a hand-reviewed --selections JSON.")
    source = src.relative_to(root).as_posix()
    plan = {"schema_version": 1, "mode": "long-to-shorts", "source": source,
            "source_duration": info["duration"],
            "selection_method": "agent-provided" if args.selections else
                                "heuristic (NOT guaranteed viral)",
            "clips": choices, "approved": False,
            "disclaimer": "Review source rights, hook quality, cut boundaries and titles."}
    if args.plan_only:
        out = safe_output(root, args.plan_out or f"out/{src.stem}-shorts-plan.json")
        write_json_new(out, plan)
        print("Draft selection plan:", out)
        return
    dest = safe_new_dir(root, args.out_dir or f"out/shorts-{src.stem}")
    write_json_new(dest / "selections.json", plan)
    must_have("ffmpeg", "ffprobe")
    for idx, clip in enumerate(choices, 1):
        tag = f"short-{idx:02}"
        sub = sliced_subtitles(rows, clip["start"], clip["end"])
        ass = None
        if sub:
            write_srt(dest / (tag + ".srt"), sub)
            if args.burn_captions:
                ass = dest / (tag + ".ass")
                make_ass(ass, sub)
        elif args.burn_captions:
            raise ValueError("Cannot burn captions without SRT or Whisper transcript")
        path = dest / (tag + ".mp4")
        run(video_cmd(src, path, start=clip["start"], end=clip["end"],
                      orientation="portrait", fit=args.fit, ass=ass))
        output_info = ensure_video(path)
        if output_info["width"] != 1080 or output_info["height"] != 1920:
            raise ValueError("Unexpected output dimensions")
    print(f"Created {len(choices)} local Shorts in: {dest}")
    print("Selections are suggestions, not a virality guarantee; review before posting.")


def mode_edit(args):
    root = project_root(args.project)
    if not args.input:
        raise ValueError("At least one --input is required")
    inputs = [local_file(root, name, VIDEO_EXT) for name in args.input]
    if len(inputs) > 30 or len(set(inputs)) != len(inputs):
        raise ValueError("Use 1-30 distinct source files")
    if len(inputs) > 1 and (args.start is not None or args.end is not None or args.srt):
        raise ValueError("Trim times and subtitles require a single input")
    if args.srt and args.remove_silence:
        raise ValueError("Use either --srt or --remove-silence for this quick edit; "
                         "word-accurate retiming belongs in the existing precise workflow")
    sources = []
    for src in inputs:
        meta = ensure_video(src)
        a = 0 if args.start is None else args.start
        b = meta["duration"] if args.end is None else args.end
        if a < 0 or b > meta["duration"] + 0.08 or b - a < 0.25:
            raise ValueError("Invalid cut range for " + str(src))
        if args.remove_silence:
            if not meta["audio"]:
                raise ValueError("No audio stream for silence detection")
            detected = silence_intervals(src, meta["duration"],
                                         threshold=args.silence_threshold,
                                         minimum=args.silence_duration)
            keeps = keep_ranges(a, b, detected)
        else:
            keeps = [(a, b)]
        if not keeps:
            raise ValueError("Silence trimming would remove the entire recording")
        sources.extend({"src": src, "start": a0, "end": b0} for a0, b0 in keeps)
    plan = {"mode": "own-footage", "source_count": len(inputs),
            "segments": [{"source": x["src"].relative_to(root).as_posix(),
                          "start": round(x["start"], 3), "end": round(x["end"], 3)}
                         for x in sources],
            "options": {"orientation": args.format, "fit": args.fit,
                        "remove_silence": args.remove_silence},
            "approved": False}
    if args.plan_only:
        out = safe_output(root, args.plan_out or "out/edit-plan.json")
        write_json_new(out, plan)
        print("Draft edit plan:", out)
        return
    dest = safe_output(root, args.output or "out/edited.mp4")
    if dest.suffix.lower() != ".mp4":
        raise ValueError("Output needs .mp4 extension")
    report = safe_output(root, dest.with_suffix(".json"))
    ass = None
    if args.srt:
        rows = parse_srt(local_file(root, args.srt, SUB_EXT).read_text(encoding="utf-8-sig"))
        ass = safe_output(root, dest.with_suffix(".ass"))
        sub = sliced_subtitles(rows, sources[0]["start"], sources[0]["end"])
        if not sub:
            raise ValueError("SRT has no entries in the selected time span")
    must_have("ffmpeg", "ffprobe")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if ass:
        make_ass(ass, sub, portrait=args.format == "portrait")
    if len(sources) == 1:
        x = sources[0]
        run(video_cmd(x["src"], dest, start=x["start"], end=x["end"],
                      orientation=args.format, fit=args.fit, ass=ass))
    else:
        with tempfile.TemporaryDirectory(prefix="workbench-cut-", dir=root / "out") as td:
            folder = Path(td)
            parts = []
            for i, x in enumerate(sources):
                part = folder / f"part-{i:04d}.mp4"
                run(video_cmd(x["src"], part, start=x["start"], end=x["end"],
                              orientation=args.format, fit=args.fit))
                parts.append(part)
            listing = folder / "parts.txt"
            listing.write_text("".join("file '" + str(p).replace("'", "'\\''") + "'\n"
                                       for p in parts), encoding="utf-8")
            run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin",
                 "-n", "-f", "concat", "-safe", "0", "-i", str(listing),
                 "-c", "copy", "-movflags", "+faststart", str(dest)])
    plan["result"] = {"path": dest.relative_to(root).as_posix(), "probe": ensure_video(dest)}
    write_json_new(report, plan)
    print(f"Edited local video: {dest}")
    print("Review voice quality, transitions and framing before publication.")


def split_scenes(script):
    chunks = [re.sub(r"\s+", " ", part).strip()
              for part in re.split(r"\n\s*\n", script.strip()) if part.strip()]
    # Split very long paragraphs into readable ~100 character cards.
    scenes = []
    for para in chunks:
        if len(para) <= 120:
            scenes.append(para)
        else:
            scenes.extend(re.findall(r".{1,110}(?:\s|$)|\S+", para))
    scenes = [s.strip() for s in scenes if s.strip()]
    if not 1 <= len(scenes) <= 60:
        raise ValueError("Script needs 1-60 readable scenes; separate paragraphs by blank lines")
    if any(len(s) > 500 for s in scenes):
        raise ValueError("Too much text in one scene")
    return scenes


def scene_times(scenes, total):
    if total < len(scenes) * 1.25:
        raise ValueError("Narration is too short for the number of scenes")
    weights = [max(2, len(re.findall(r"\w+", s))) for s in scenes]
    duration = total - len(scenes) * 1.25
    boundaries = []
    pos = 0.0
    for i, (scene, weight) in enumerate(zip(scenes, weights)):
        length = 1.25 + duration * weight / sum(weights)
        end = total if i == len(scenes) - 1 else pos + length
        boundaries.append({"start": round(pos, 3), "end": round(end, 3), "text": scene})
        pos = end
    return boundaries


def local_images(root, folder):
    if not folder:
        return []
    path = Path(folder).expanduser()
    path = (path if path.is_absolute() else root / path).resolve()
    if not inside(path, root) or not path.is_dir():
        raise ValueError("--images must be a directory inside the project")
    pictures = sorted(p for p in path.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_EXT)
    if not pictures:
        raise ValueError("No supported local images in --images directory")
    return pictures


def make_background(images, scenes, duration, temp):
    # Render from local media only. Use preencoded temporary footage for robust
    # cuts and no additional Python/video-rendering dependencies.
    must_have("ffmpeg")
    color_palette = ["0x101827", "0x1a1740", "0x122b34", "0x2a1e35"]
    parts = []
    for i, row in enumerate(scenes):
        sec = row["end"] - row["start"]
        part = temp / f"scene-{i:03d}.mp4"
        if images:
            cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
                   "-loop", "1", "-framerate", "30", "-i", str(images[i % len(images)]),
                   "-t", f"{sec:.3f}"]
            vf = video_filter("portrait", fit="crop")
        else:
            cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
                   "-f", "lavfi", "-i",
                   f"color=c={color_palette[i % len(color_palette)]}:s=1080x1920:r=30:d={sec:.3f}"]
            vf = "fps=30,format=yuv420p"
        cmd += ["-vf", vf, "-an", "-c:v", "libx264", "-preset", "ultrafast",
                "-crf", "28", "-r", "30", "-pix_fmt", "yuv420p", str(part)]
        run(cmd)
        parts.append(part)
    listfile = temp / "background-list.txt"
    listfile.write_text("".join("file '" + str(p).replace("'", "'\\''") + "'\n"
                                for p in parts), encoding="utf-8")
    background = temp / "background.mp4"
    run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
         "-f", "concat", "-safe", "0", "-i", str(listfile), "-c", "copy", str(background)])
    return background


def mode_faceless(args):
    root = project_root(args.project)
    script = local_file(root, args.script, {".txt", ".md"})
    text = script.read_text(encoding="utf-8-sig").strip()
    if not text or len(text) > 24000:
        raise ValueError("Provide a non-empty script shorter than 24k characters")
    scenes = split_scenes(text)
    images = local_images(root, args.images)
    if args.narration and args.piper_model:
        raise ValueError("Choose --narration or --piper-model")
    if args.piper_model and not args.voice_license_confirmed:
        raise ValueError("Confirm the specific voice model's permitted license with "
                         "--voice-license-confirmed before using Piper")
    voice = local_file(root, args.narration, AUDIO_EXT) if args.narration else None
    piper_model = local_file(root, args.piper_model, {".onnx"}) if args.piper_model else None
    if voice:
        total = probe(voice)["duration"]
    elif piper_model:
        total = None   # Generated voice duration will be measured before rendering.
    else:
        if not 1.5 <= args.seconds_per_scene <= 30:
            raise ValueError("--seconds-per-scene must be 1.5-30")
        total = len(scenes) * args.seconds_per_scene
    if args.plan_only:
        rows = scene_times(scenes, total) if total else [{"text": s} for s in scenes]
        plan = {"mode": "faceless", "script": script.relative_to(root).as_posix(),
                "scenes": rows, "narration": bool(voice or piper_model),
                "images": len(images), "approved": False}
        dest = safe_output(root, args.plan_out or "out/faceless-plan.json")
        write_json_new(dest, plan)
        print("Draft faceless storyboard:", dest)
        return
    dest = safe_output(root, args.output or "out/faceless.mp4")
    if dest.suffix.lower() != ".mp4":
        raise ValueError("Output must end in .mp4")
    ass = safe_output(root, dest.with_suffix(".ass"))
    srt = safe_output(root, dest.with_suffix(".srt"))
    report = safe_output(root, dest.with_suffix(".json"))
    must_have("ffmpeg", "ffprobe")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="workbench-faceless-", dir=root / "out") as td:
        temp = Path(td)
        if piper_model:
            must_have("piper")
            voice = temp / "narration.wav"
            run(["piper", "--model", str(piper_model), "--output_file", str(voice)],
                input_text=text, timeout=600)
            total = probe(voice)["duration"]
        rows = scene_times(scenes, total)
        write_srt(srt, rows)
        make_ass(ass, rows, centre=True)
        background = make_background(images, rows, total, temp)
        cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
               "-i", str(background)]
        if voice:
            cmd += ["-i", str(voice)]
        cmd += ["-map", "0:v:0"]
        if voice:
            cmd += ["-map", "1:a:0"]
        cmd += ["-vf", video_filter("portrait", burn_ass=ass),
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "22",
                "-pix_fmt", "yuv420p"]
        if voice:
            cmd += ["-c:a", "aac", "-b:a", "160k", "-shortest"]
        else:
            cmd += ["-an"]
        cmd += ["-movflags", "+faststart", str(dest)]
        run(cmd)
    metadata = ensure_video(dest)
    write_json_new(report, {"mode": "faceless", "output": dest.relative_to(root).as_posix(),
                            "scenes": rows, "images": len(images),
                            "voice": bool(voice), "probe": metadata, "approved": False,
                            "disclaimer": "Review audio/captions/rights before posting."})
    print("Created local faceless video:", dest)
    if not voice:
        print("No narration requested: video is intentionally silent. "
              "Add --narration or local --piper-model for voice.")
