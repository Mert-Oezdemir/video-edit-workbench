#!/usr/bin/env python3
"""Provider-neutral rough-cut planning; local tools perform the media work."""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

from preflight import CLIP_ID, inspect_edl

HERE = Path(__file__).resolve().parent


def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save_new(path, data):
    # Exclusive creation: never silently overwrite an approved edit or decision.
    with path.open("x", encoding="utf-8") as f:
        f.write(data)


def snapshot(root, selected=None):
    work = root / "work"
    clips = load(work / "clips.json")
    ids = list(clips) if selected is None else selected
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("Select unique clip IDs in recording order")
    rows, sources, fingerprints = [], {}, {}
    for cid in ids:
        if cid not in clips or not CLIP_ID.fullmatch(cid):
            raise ValueError(f"Unknown clip: {cid}")
        src = clips[cid]
        media = (root / src).resolve()
        if Path(src).is_absolute() or not media.is_relative_to(root) or not media.is_file():
            raise ValueError(f"{cid}: source must be a file inside the project")
        tp = work / "transcripts" / f"{cid}.json"
        ep = work / "env" / f"{cid}.npy"
        tr = load(tp)
        if tr.get("clip") != cid or tr.get("src") != src or not tr.get("utterances"):
            raise ValueError(f"{cid}: missing or mismatched transcript")
        stat = media.stat()
        fingerprints[cid] = [src, stat.st_size, stat.st_mtime_ns,
                             hashlib.sha256(tp.read_bytes()).hexdigest(),
                             hashlib.sha256(ep.read_bytes()).hexdigest()]
        sources[cid] = src
        for i, utt in enumerate(tr["utterances"]):
            rows.append((cid, i, " ".join(utt["text"].split())))
    revision = hashlib.sha256(json.dumps([ids, fingerprints], sort_keys=True).encode()).hexdigest()
    return revision, sources, rows


def hints(rows):
    last, result = {}, []
    for cid, i, text in rows:
        normalized = " ".join(re.findall(r"\w+", text.casefold()))
        if len(normalized.split()) < 4:
            continue
        key = (cid, normalized)
        if key in last and i - last[key] <= 3:
            result.append([f"{cid}:{last[key]}", f"{cid}:{i}"])
        last[key] = i
    return result


def packet(revision, sources, rows):
    return {"revision": revision, "clip_order": list(sources),
            "utterances": [[f"{cid}:{i}", text] for cid, i, text in rows],
            "possible_exact_retakes": hints(rows)}


def make_edl(revision, sources, rows, decision, fps, pace):
    if not isinstance(decision, dict) or set(decision) != {"revision", "drop"}:
        raise ValueError("Expected JSON object with revision and drop only")
    if decision["revision"] != revision:
        raise ValueError("Stale decisions: regenerate the packet")
    drops = decision["drop"]
    if not isinstance(drops, list) or not all(isinstance(x, str) for x in drops):
        raise ValueError("drop must be a list of utterance IDs")
    known = {f"{cid}:{i}" for cid, i, _ in rows}
    if len(set(drops)) != len(drops) or set(drops) - known:
        raise ValueError("Unknown or duplicate drop IDs")
    removed = set(drops)
    if removed == known:
        raise ValueError("Refusing to remove all footage")
    items = [{"clip": cid, "utt": i} for cid, i, _ in rows if f"{cid}:{i}" not in removed]
    # Keep each utterance separate: merging across pauses may change the measured cut.
    return {"fps": fps, "pace": pace, "clips": sources, "items": items}


def preview(root, args):
    problems = inspect_edl(root)
    if problems:
        raise ValueError("Preflight failed:\n" + "\n".join(problems))
    work = root / "work"
    if (work / "proxy.mp4").exists() and not args.rebuild:
        raise ValueError("Preview exists. Close the player, back up the edit and use --rebuild.")
    logs = work / "low-token-logs"
    logs.mkdir(exist_ok=True)
    verify = ["--model", args.model, "--backend", args.backend, "--device", args.device]
    if args.lang:
        verify += ["--lang", args.lang]
    for script, extra in [("cuts.py", []), ("build.py", ["audio", "video"]),
                          ("verify.py", verify)]:
        log = logs / (script + ".log")
        with log.open("w", encoding="utf-8") as f:
            result = subprocess.run([sys.executable, str(HERE / script),
                                     "--project", str(root), *extra], cwd=root,
                                    stdout=f, stderr=subprocess.STDOUT)
        if result.returncode:
            raise ValueError(f"{script} failed ({result.returncode}); inspect {log}")
    program = load(work / "program.json")
    report = (work / "verify.txt").read_text(encoding="utf-8")
    flagged = sum(line.startswith("!") for line in report.splitlines())
    print(f"work/proxy.mp4: {program['duration']:.2f}s, "
          f"{len(program['pieces'])} pieces, {flagged} flagged joins")
    print("Review work/verify.txt and listen to the preview. Not final approval.")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, default=Path.cwd())
    sub = ap.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare", help="Create compact JSON for any planner")
    p.add_argument("--clips", nargs="+", help="Explicit order; default: clips.json order")
    p.add_argument("--out", type=Path, required=True)
    p = sub.add_parser("apply", help="Validate reviewed decisions and create a new EDL")
    p.add_argument("--clips", nargs="+", help="Same IDs/order as prepare")
    p.add_argument("--decisions", type=Path, required=True)
    p.add_argument("--fps", type=int, required=True, choices=range(1, 121), metavar="1..120")
    p.add_argument("--pace", choices=["natural", "tight"], default="natural")
    p = sub.add_parser("preview", help="Run existing local tools with compact output")
    p.add_argument("--model", default="large-v3")
    p.add_argument("--backend", default="auto")
    p.add_argument("--device", choices=["cpu", "cuda", "auto"], default="cpu")
    p.add_argument("--lang")
    p.add_argument("--rebuild", action="store_true")
    args = ap.parse_args()
    root = args.project.resolve()
    try:
        if args.command == "preview":
            preview(root, args)
            return 0
        revision, sources, rows = snapshot(root, args.clips)
        if args.command == "prepare":
            p = packet(revision, sources, rows)
            save_new(args.out, json.dumps(p, ensure_ascii=False, separators=(",", ":")) + "\n")
            print(f"{len(rows)} utterances, {len(p['possible_exact_retakes'])} hints -> {args.out}")
        else:
            edl = make_edl(revision, sources, rows, load(args.decisions), args.fps, args.pace)
            save_new(root / "work" / "edl.json", json.dumps(edl, ensure_ascii=False, indent=2) + "\n")
            print("Created work/edl.json. Review before running preview.")
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
