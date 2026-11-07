#!/usr/bin/env python3
"""Check an edit list and its local inputs without changing the project."""

import argparse
import json
import math
import re
from pathlib import Path


CLIP_ID = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*\Z")


def json_object(path, problems):
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as error:
        problems.append(f"{path.name} could not be read: {error}")
        return None
    if not isinstance(value, dict):
        problems.append(f"{path.name} must contain a JSON object.")
        return None
    return value


def seconds(value):
    try:
        return type(value) in (int, float) and math.isfinite(value) and 0 <= value <= 1e9
    except OverflowError:
        return False


def utterances(value):
    bounds = value if isinstance(value, list) else [value, value]
    if (len(bounds) == 2 and all(type(part) is int and part >= 0 for part in bounds)
            and bounds[0] <= bounds[1]):
        return bounds
    return None


def inspect_clip(root, clip_id, source, problems):
    if not isinstance(source, str) or not source.strip():
        problems.append(f"Clip {clip_id!r} needs a source file in the clip map.")
    else:
        try:
            source_path = Path(source)
            resolved = (root / source_path).resolve()
            if source_path.is_absolute() or not resolved.is_relative_to(root):
                problems.append(f"Clip {clip_id!r} must point to a file inside the project.")
            elif not resolved.is_file():
                problems.append(f"Clip {clip_id!r} source file is missing: {source}")
        except (OSError, ValueError, RuntimeError):
            problems.append(f"Clip {clip_id!r} has an invalid source path.")

    transcript = json_object(root / "work" / "transcripts" / f"{clip_id}.json", problems)
    envelope = root / "work" / "env" / f"{clip_id}.npy"
    if not envelope.is_file():
        problems.append(f"Clip {clip_id!r} has no energy envelope. Run transcribe.py.")
    if transcript is None:
        return None
    items = transcript.get("utterances")
    if not isinstance(items, list):
        problems.append(f"Clip {clip_id!r} has no utterance list. Run transcribe.py.")
        return None
    return len(items)


def inspect_edl(root):
    problems = []
    work = root / "work"
    edl = json_object(work / "edl.json", problems)
    if edl is None:
        return problems

    fps = edl.get("fps", 30)
    if type(fps) is not int or not 1 <= fps <= 1000:
        problems.append("fps must be an integer from 1 to 1000.")
        fps = None
    if edl.get("pace", "natural") not in ("natural", "tight"):
        problems.append("pace must be natural or tight.")
    clip_map = json_object(work / "clips.json", problems) if (work / "clips.json").exists() else {}
    declared = edl.get("clips", {})
    if not isinstance(declared, dict):
        problems.append("clips must map clip IDs to project-relative source files.")
        declared = {}
    sources = (clip_map or {}) | declared

    items = edl.get("items")
    if not isinstance(items, list):
        return problems + ["items must be an array."]

    counts = {}
    has_cut = False
    for index, item in enumerate(items, start=1):
        label = f"Item {index}"
        if not isinstance(item, dict):
            problems.append(f"{label} must be an object.")
            continue
        if "chapter" in item:
            if not isinstance(item["chapter"], str) or not item["chapter"].strip():
                problems.append(f"{label} needs a nonempty chapter title.")
            continue
        if item.keys() == {"note"}:
            continue
        has_cut = True
        clip_id = item.get("clip")
        if not isinstance(clip_id, str) or not CLIP_ID.fullmatch(clip_id):
            problems.append(f"{label} needs a clip ID using letters, digits, dots, hyphens, or underscores.")
            continue
        if clip_id not in counts:
            counts[clip_id] = inspect_clip(root, clip_id, sources.get(clip_id), problems)
        if "range" in item:
            bounds = item["range"]
            if "utt" in item or not isinstance(bounds, list) or len(bounds) != 2:
                problems.append(f"{label} must give either a two-value range or an utterance selector.")
            elif not all(seconds(part) for part in bounds) or bounds[0] >= bounds[1]:
                problems.append(f"{label} range needs two increasing, nonnegative times.")
            continue
        selected = utterances(item.get("utt"))
        if selected is None:
            problems.append(f"{label} needs a nonnegative utterance index or an increasing index pair.")
        elif counts[clip_id] is not None and selected[1] >= counts[clip_id]:
            problems.append(f"{label} selects an utterance outside clip {clip_id!r}.")
        start, end = item.get("start"), item.get("end")
        if any(value is not None and not seconds(value) for value in (start, end)):
            problems.append(f"{label} start and end must be nonnegative times.")
        elif start is not None and end is not None and start >= end:
            problems.append(f"{label} end must come after start.")
    if not has_cut:
        problems.append("Add at least one cut item.")
    return problems


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=Path.cwd())
    options = parser.parse_args()
    problems = inspect_edl(options.project.resolve())
    if problems:
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("Edit list and input files passed preflight.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
