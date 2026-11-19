#!/usr/bin/env python3
"""Optional Lemo-Opuscar style discovery and review-first planning.

Reads an existing *local* Lemo-Opuscar checkout. Does not download, install,
execute upstream code, copy CC BY-NC style guides, or render video. Workbench
remains the rendering and approval authority for imported outputs.
"""

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

UPSTREAM = "https://github.com/lemomo-ai/lemo-opuscar"
DEFAULT_LIBRARY = Path(os.environ.get("LEMO_OPUSCAR_LIBRARY", "~/lemo-opuscar"))
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
OUTPUT_NAME = re.compile(r"[a-z0-9][a-z0-9._-]*\.json\Z")


def read_library(path):
    """Identify a local checkout, not a downloaded/assumed integration."""
    root = path.expanduser().resolve(strict=True)
    if not root.is_dir() or not (root / "styles").is_dir() or not (root / "LICENSE").is_file():
        raise ValueError("Not a Lemo-Opuscar checkout (expected styles/ and LICENSE)")
    return root


def local_styles(root):
    """Read upstream MIT-licensed JSON metadata; never copy the guides."""
    records = []
    for metadata in sorted((root / "styles").glob("*/style.json")):
        if metadata.is_symlink() or not metadata.resolve().is_relative_to(root):
            continue
        slug = metadata.parent.name
        if not SLUG.fullmatch(slug) or metadata.stat().st_size > 65536:
            continue
        guide = metadata.parent / "STYLE.md"
        if not guide.is_file() or not guide.resolve().is_relative_to(root):
            continue
        value = json.loads(metadata.read_text(encoding="utf-8"))
        if not isinstance(value, dict) or value.get("slug") != slug:
            continue
        records.append({
            "slug": slug,
            "name": str(value.get("en", slug)),
            "category": str(value.get("category_en", "")),
            "uses": value.get("uses", []) if isinstance(value.get("uses", []), list) else [],
            "style_path": f"styles/{slug}/STYLE.md",
        })
    return records

def search_styles(styles, query, limit=10):
    """Deterministic metadata keyword matches; NOT a semantic/quality rating."""
    if not query.strip() or not 1 <= limit <= 99:
        raise ValueError("Provide --query text and --limit between 1 and 99")
    terms = re.findall(r"[\w-]+", query.casefold())
    if not terms:
        raise ValueError("Query must contain a search term")
    matches = []
    for item in styles:
        name = item["name"].casefold()
        slug = item["slug"].casefold()
        category = item["category"].casefold()
        uses = " ".join(str(u) for u in item["uses"]).casefold()
        score = sum(5 * (term in name or term in slug)
                    + 3 * (term in category)
                    + 1 * (term in uses) for term in terms)
        if score:
            matches.append((score, item))
    matches.sort(key=lambda value: (-value[0], value[1]["slug"]))
    return [item for _, item in matches[:limit]]



def make_plan(project, library, style, filename=None, mode="faceless"):
    if mode not in ("long-to-shorts", "faceless", "own-footage"):
        raise ValueError("Invalid Workbench mode")
    if not SLUG.fullmatch(style):
        raise ValueError("Style must be a valid local folder slug (e.g. neon-tubes)")
    source = read_library(library)
    styles = {item["slug"]: item for item in local_styles(source)}
    if style not in styles:
        raise ValueError("Style not found; run 'list' to see available local styles")
    root = project.expanduser().resolve(strict=True)
    if not root.is_dir() or not (root / "work").is_dir():
        raise ValueError("Initialize a Workbench project first: python workbench.py init PROJECT")
    if not (root / "work").resolve().is_relative_to(root):
        raise ValueError("Unsafe project work/ path")

    name = filename or f"lemo-{style}.json"
    if not OUTPUT_NAME.fullmatch(name) or name in {".", ".."}:
        raise ValueError("--name must be a simple .json filename without directories")
    target_dir = root / "work" / "style-plans"
    if target_dir.is_symlink():
        raise ValueError("Refusing a symlinked style-plans directory")
    target_dir.mkdir(exist_ok=True)
    if not target_dir.resolve().is_relative_to(root):
        raise ValueError("Unsafe output directory")

    selected = styles[style]
    content = {
        "schema_version": 1,
        "tool": "lemo-opuscar",
        "mode": mode,
        "status": "advisory-style-plan-only",
        "approved": False,
        "rendered": False,
        "upstream": UPSTREAM,
        "local_library": str(source),
        "style": selected,
        "license": {
            "code": "MIT (upstream code only)",
            "guides": "CC BY-NC 4.0; upstream has limited film-production permissions",
            "assets": "Review individual third-party and demo asset licenses",
            "guide_copied": False,
        },
        "next_steps": [
            "Review reference/editorial-intake.md; use owned or licensed materials only.",
            "Read the selected STYLE.md locally; do not redistribute its text in this repo.",
            "Ask the user to approve the style/storyboard before using external production tools.",
            "Lemo runs separately with its own dependencies and agent requirements; this plan does not run it.",
            "Keep any rendered local MP4 in the Workbench project and register it with scripts/external_handoff.py --tool lemo-opuscar --mode MODE --kind rendered-video (MODE is the current Workbench production mode).",
            "Add a validated visual_component segment in the existing production.json, render a combined preview via scripts/produce.py, review it with the human, then approve final with preview SHA256.",
            "No automatic downloads, installs, cloud uploads, billing, model calls or source overwrites.",
        ],
    }
    target = target_dir / name
    with target.open("x", encoding="utf-8") as out:
        json.dump(content, out, indent=2, ensure_ascii=False)
        out.write("\n")
    return target


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    for command in ("doctor", "list", "search", "plan"):
        child = subs.add_parser(command)
        child.add_argument("--library", type=Path, default=DEFAULT_LIBRARY,
                           help="Existing local Lemo-Opuscar checkout (default: ~/lemo-opuscar)")
        if command in ("doctor", "list", "search"):
            child.add_argument("--json", action="store_true")
        if command == "search":
            child.add_argument("--query", required=True, help="Metadata keywords, not semantic AI search")
            child.add_argument("--limit", type=int, default=10)
        if command == "plan":
            child.add_argument("--project", type=Path, required=True)
            child.add_argument("--style", required=True, help="A slug from 'list', e.g. neon-tubes")
            child.add_argument("--name", help="Optional new .json filename in work/style-plans/")
            child.add_argument("--mode", default="faceless",
                               choices=("long-to-shorts", "faceless", "own-footage"),
                               help="Existing Workbench production mode; never starts a new renderer")
    args = parser.parse_args(argv)
    try:
        root = read_library(args.library)
        if args.command == "plan":
            path = make_plan(args.project, root, args.style, args.name, args.mode)
            print("Advisory style plan written:", path)
            return 0
        styles = local_styles(root)
        if args.command == "doctor":
            status = {
                "local_library": str(root),
                "styles_found": len(styles),
                "style_metadata_readable": bool(styles),
                "upstream_requirements_detected": {
                    "node": shutil.which("node") is not None,
                    "ffmpeg": shutil.which("ffmpeg") is not None,
                    "python": True,
                },
                "note": "Only local presence checked; upstream runtime, licenses, paid features and film generation are NOT verified",
            }
            print(json.dumps(status, indent=2, ensure_ascii=False))
            return 0 if styles else 1
        if args.command == "search":
            results = search_styles(styles, args.query, args.limit)
            if args.json:
                print(json.dumps({"query": args.query, "matches": results, "match_type": "keyword-only"},
                                 indent=2, ensure_ascii=False))
            else:
                for item in results:
                    print(f"{item['slug']:27} {item['name']} ({item['category']})")
                print(f"{len(results)} keyword matches; review upstream STYLE.md before selecting.")
            return 0
        if args.json:
            print(json.dumps({"upstream": UPSTREAM, "styles": styles}, indent=2, ensure_ascii=False))
        else:
            for item in styles:
                print(f"{item['slug']:27} {item['name']} ({item['category']})")
            print(f"{len(styles)} local styles. Nothing was downloaded, installed or rendered.")
        return 0 if styles else 1
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print("Error:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
