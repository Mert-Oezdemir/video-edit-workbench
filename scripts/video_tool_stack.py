#!/usr/bin/env python3
"""Read-only inventory and zero-extra-spend planning for optional video tools.

This module NEVER installs dependencies, calls AI APIs, uploads media, renders,
or executes programs. It only reads the tracked registry and optionally writes
an exclusive new plan file. Existing editing scripts remain the engine.
"""
import argparse
import importlib.util
import json
import shutil
import sys
from pathlib import Path

REGISTRY = Path(__file__).resolve().parents[1] / "reference" / "video-tool-registry.json"
# Entirely local means no billing or cloud call. Other entries require a review.
LOCAL_POLICIES = {"local-free", "local-free-hardware"}
REVIEW_POLICIES = {"existing-subscription", "mixed-providers",
                   "free-core-pro-extras", "restricted-license"}
BLOCKED_POLICIES = {"paid-service-disabled"}


def registry():
    data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported tool registry schema")
    tools = data["tools"]
    names = [tool["id"] for tool in tools]
    if len(names) != len(set(names)):
        raise ValueError("Duplicate tool IDs")
    if not set(names).issuperset(name for stages in data["routes"].values()
                                for stage in stages for name in stage["tools"]):
        raise ValueError("Route references unknown tool")
    if not set(data["routes"]).issubset(set(data["modes"])):
        raise ValueError("Unknown mode in routes")
    for tool in tools:
        if tool["policy"] not in LOCAL_POLICIES | REVIEW_POLICIES | BLOCKED_POLICIES:
            raise ValueError("Unknown policy for " + tool["id"])
        if tool["enabled_by_default"] and tool["policy"] not in LOCAL_POLICIES:
            raise ValueError("Non-local tool enabled by default")
    if any(data["policy"][key] for key in (
            "extra_api_spend_allowed", "cloud_generation_allowed",
            "cloud_render_allowed", "paid_features_allowed",
            "auto_install_optional_tools", "send_private_media_off_device")):
        raise ValueError("Registry cost or privacy guards must default to false")
    return data


def probe(tool):
    check = tool["availability"]
    kind = check["type"]
    if kind == "binary":
        return "present" if shutil.which(check["name"]) else "not-found"
    if kind == "python_module":
        try:
            return "present" if importlib.util.find_spec(check["name"]) else "not-found"
        except (ImportError, ValueError):
            return "not-found"
    if kind == "manual":
        return "not-checked"
    raise ValueError("Unknown availability check")


def eligibility(tool):
    if tool["policy"] in BLOCKED_POLICIES:
        return "blocked-no-extra-spend"
    if tool["policy"] in REVIEW_POLICIES:
        return "optional-review-required"
    return "local-eligible"


def selected_tools(data, mode=None):
    return [tool for tool in data["tools"] if mode is None or mode in tool["modes"]]


def plan(data, mode):
    by_id = {tool["id"]: tool for tool in data["tools"]}
    stages = []
    for stage in data["routes"][mode]:
        stages.append({
            "step": stage["step"],
            "action": stage["action"],
            "choices": [{
                "id": tool_id,
                "eligibility": eligibility(by_id[tool_id]),
                "availability": probe(by_id[tool_id]),
                "reason": by_id[tool_id]["note"]
            } for tool_id in stage["tools"]]
        })
    return {
        "mode": mode,
        "status": "advisory-plan-only",
        "plan_is_not_execution": True,
        "zero_extra_spend_guards": data["policy"],
        "instructions": [
            "Follow reference/editorial-intake.md and ask for approval of substantive changes.",
            "Start with existing FFmpeg/Whisper scripts; use at most one optional tool per unmet need.",
            "An optional-review-required tool is not preapproved for paid/cloud features.",
            "Never automatically install, upload private media, buy credits, or call an external API.",
            "Keep raw footage unchanged, review rights/model licenses and preview before final output.",
            "Inspect reference/free-video-tool-stack.md for exact handoff and fallback rules."
        ],
        "stages": stages
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("list", "doctor"):
        p = sub.add_parser(name, help="Read-only catalog and local availability")
        p.add_argument("--mode", choices=["long-to-shorts", "faceless", "own-footage"])
        p.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p = sub.add_parser("plan", help="Write or print an advisory mode plan; never run tools")
    p.add_argument("--mode", choices=["long-to-shorts", "faceless", "own-footage"],
                   required=True)
    p.add_argument("--out", type=Path, help="Exclusive new JSON file; never overwrite")
    args = parser.parse_args(argv)
    try:
        data = registry()
        if args.command == "plan":
            output = plan(data, args.mode)
            rendered = json.dumps(output, indent=2, ensure_ascii=False) + "\n"
            if args.out:
                with args.out.open("x", encoding="utf-8") as f:
                    f.write(rendered)
                print("Advisory plan written:", args.out)
            else:
                print(rendered, end="")
            return 0
        entries = []
        for item in selected_tools(data, args.mode):
            entries.append({
                "id": item["id"], "name": item["name"], "url": item["url"],
                "policy": item["policy"], "eligibility": eligibility(item),
                "modes": item["modes"], "installed": probe(item),
                "enabled_by_default": item["enabled_by_default"]
            })
        if args.json:
            print(json.dumps({"tools": entries, "cost_policy": data["policy"]},
                             indent=2, ensure_ascii=False))
        else:
            for item in entries:
                print("{:<19} {:<24} {:<25} {}".format(
                    item["id"], item["installed"], item["eligibility"], item["url"]))
            print("Presence is not an execution, API, license or compatibility test.")
        return 0
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        print("Error:", exc, file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
