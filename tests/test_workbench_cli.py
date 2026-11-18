"""Tests for the human/agent CLI, file safety and deterministic planning."""
import argparse
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

import workbench
from workbench_media import (
    make_ass, parse_srt, safe_output, sliced_subtitles, srt_time, video_cmd
)
from workbench_modes import (
    scene_times, score_text, split_scenes, suggest_clips,
    validate_selections
)


class WorkbenchCliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "project"
        workbench.project_init(self.root)

    def test_init_creates_three_dirs_and_never_overwrites(self):
        self.assertEqual(json.loads((self.root / "video-workbench.json").read_text())[
            "extra_api_spend"], False)
        self.assertTrue(all((self.root / name).is_dir() for name in ("src", "out", "work")))
        with self.assertRaises(ValueError):
            workbench.project_init(self.root)

    def test_parses_and_slices_srt(self):
        data = ("1\n00:00:01,500 --> 00:00:03,000\nMerhaba dünya\n\n"
                "2\n00:00:03,000 --> 00:00:05,500\nNasıl çalışır?\n")
        items = parse_srt(data)
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["start"], 1.5)
        self.assertEqual(srt_time(3661.512), "01:01:01,512")
        cut = sliced_subtitles(items, 2.0, 4.0)
        self.assertEqual(cut[0]["start"], 0)
        self.assertEqual(cut[-1]["end"], 2.0)

    def test_ass_escapes_user_braces_not_instructions(self):
        path = self.root / "work" / "captions.ass"
        make_ass(path, [{"start": 0, "end": 2, "text": "{\\pos(0,0)} test"}])
        output = path.read_text()
        self.assertNotIn("{\\pos(0,0)}", output)
        self.assertIn("Dialogue: 0,", output)

    def test_short_candidates_nonoverlapping_and_heuristic(self):
        rows = [{"start": i * 2.5, "end": (i + 1) * 2.5,
                 "text": ("Neden şimdi bunu yapıyoruz?" if i % 2 == 0
                          else "Açıklaması çok basit ve anlaşılır.")}
                for i in range(20)]
        clips = suggest_clips(rows, 50.0, count=3, low=8, high=18)
        self.assertGreaterEqual(len(clips), 2)
        for c in clips:
            self.assertGreaterEqual(c["end"] - c["start"], 8)
            self.assertLessEqual(c["end"] - c["start"], 18)
            self.assertTrue(c["reason"])
        for i, c in enumerate(clips):
            for d in clips[i + 1:]:
                self.assertTrue(c["end"] <= d["start"] or c["start"] >= d["end"])

    def test_selection_validation_fails_on_wrong_source_and_invalid_span(self):
        f = self.root / "src" / "a.mp4"
        f.write_bytes(b"dummy")
        good = {"source": "src/a.mp4", "clips": [
            {"start": 1, "end": 4, "title": "Test"}]}
        self.assertEqual(len(validate_selections(good, f, self.root, 10)), 1)
        with self.assertRaises(ValueError):
            validate_selections({**good, "source": "src/other.mp4"}, f, self.root, 10)
        with self.assertRaises(ValueError):
            validate_selections({"clips": [{"start": -1, "end": 4}]}, f, self.root, 10)
        with self.assertRaises(ValueError):
            validate_selections({"clips": [{"start": float("nan"), "end": 4}]}, f, self.root, 10)

    def test_output_path_rejects_existing_or_escape(self):
        safe = safe_output(self.root, "out/test.mp4")
        self.assertEqual(safe, self.root / "out" / "test.mp4")
        safe.parent.mkdir(exist_ok=True)
        safe.write_bytes(b"sample")
        with self.assertRaises(ValueError):
            safe_output(self.root, "out/test.mp4")
        with self.assertRaises(ValueError):
            safe_output(self.root, "../outside.mp4")
        with self.assertRaises(ValueError):
            safe_output(self.root, "src/overwrite.mp4")

    def test_source_media_command_never_overwrites(self):
        cmd = video_cmd(self.root / "src/a.mp4", self.root / "out/a.mp4",
                        start=1, end=3, orientation="portrait")
        self.assertIn("-n", cmd)
        self.assertNotIn("-y", cmd)
        self.assertEqual(cmd[0], "ffmpeg")
        self.assertNotIn("bash", cmd)
        self.assertTrue(any("1080:1920" in part for part in cmd))

    def test_scene_splits_and_timing(self):
        scenes = split_scenes("Merhaba arkadaşlar.\n\nBu ikinci sahnemiz.")
        self.assertEqual(len(scenes), 2)
        times = scene_times(scenes, 8)
        self.assertEqual(times[0]["start"], 0)
        self.assertEqual(times[-1]["end"], 8)
        with self.assertRaises(ValueError):
            scene_times(scenes, 1)

    def test_help_and_tool_catalog_do_not_run_external_executables(self):
        with patch("workbench.run", side_effect=AssertionError("No execution")):
            self.assertEqual(workbench.main(["tools", "--mode", "faceless"]), 0)
            self.assertEqual(workbench.main(["tools", "--json"]), 0)
        p = subprocess.run([sys.executable, str(ROOT / "workbench.py"), "shorts", "--help"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertIn("--selections", p.stdout)


if __name__ == "__main__":
    unittest.main()
