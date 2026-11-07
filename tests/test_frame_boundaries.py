"""Regression checks for outward frame rounding and short audio pieces."""
import json
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build
import cuts
from preflight import inspect_edl


class FrameBoundaries(unittest.TestCase):
    def test_fractional_end_keeps_the_last_frame(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for child in ("src", "work/env", "work/transcripts"):
                (root / child).mkdir(parents=True)
            (root / "src/take.mp4").touch()
            np.save(root / "work/env/a.npy", np.full(100, -20))
            (root / "work/transcripts/a.json").write_text(json.dumps({
                "src": "src/take.mp4", "regions": [[0, 1]], "utterances": [],
            }))
            edl = {"fps": 30, "clips": {"a": "src/take.mp4"},
                   "items": [{"clip": "a", "range": [0.01, 0.041]}]}
            (root / "work/edl.json").write_text(json.dumps(edl))
            self.assertEqual(inspect_edl(root), [])
            cuts.build(directory)
            program = json.loads((root / "work/program.json").read_text())
            self.assertEqual(program["pieces"][0]["a"], 0)
            self.assertEqual(program["pieces"][0]["b"], 2)

    def test_one_high_fps_frame_can_have_a_short_fade(self):
        program = {"fps": 120, "clips": {"a": "take.wav"},
                   "pieces": [{"clip": "a", "a": 0, "b": 1}]}
        options = SimpleNamespace(target=-14, ceiling=-1, highpass=None, limiter=False)
        with patch.object(build, "decode", return_value=np.ones((1000, 2), np.float32)), \
                patch.object(build, "write_wav") as writer, \
                patch.object(build, "loudness", return_value=(-14, -3, 0)), \
                patch.object(build, "ffmpeg"):
            build.build_audio(".", ".", program, options)
        samples = writer.call_args.args[1]
        self.assertEqual(samples.shape, (400, 2))
        self.assertTrue(np.isfinite(samples).all())
        self.assertEqual(samples[-1, 0], 0)


if __name__ == "__main__":
    unittest.main()
