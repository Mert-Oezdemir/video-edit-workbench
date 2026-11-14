#!/usr/bin/env python3
"""Check the lightweight pipeline without installing, downloading or starting anything."""
import importlib.util
import json
import shutil
import sys


def report():
    python_ok = sys.version_info >= (3, 10)
    core = {"python_3_10_plus": python_ok,
            "numpy": importlib.util.find_spec("numpy") is not None,
            "ffmpeg": shutil.which("ffmpeg") is not None,
            "ffprobe": shutil.which("ffprobe") is not None}
    backends = {"faster_whisper": importlib.util.find_spec("faster_whisper") is not None,
                "whisperkit_cli": shutil.which("whisperkit-cli") is not None}
    optional = {"node": shutil.which("node") is not None,
                "ollama": shutil.which("ollama") is not None}
    return {"ready": all(core.values()) and any(backends.values()),
            "core": core, "whisper_backend": backends, "optional": optional,
            "note": "Presence only; no model, codec, GPU or compatibility test was run. Optional tools are not required."}


def main():
    result = report()
    print(json.dumps(result, indent=2))
    return 0 if result["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
