import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from produce import digest, load_job, local_file, main, probe, render
from spend_policy import require_paid_opt_in


class PolicyTests(unittest.TestCase):
    def test_remote_requires_both_switches(self):
        for environment, flag in (("1", True), ("0", False), ("unexpected", True)):
            with patch.dict(os.environ, {"VIDEO_WORKBENCH_ZERO_SPEND": environment}):
                with self.assertRaises(ValueError):
                    require_paid_opt_in(flag)
        with patch.dict(os.environ, {"VIDEO_WORKBENCH_ZERO_SPEND": "0"}):
            require_paid_opt_in(True)

    def test_local_paths_reject_remote_and_escape(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for path in ("https://example.com/a.mp4", "../missing", str(root)):
                with self.assertRaises((ValueError, OSError)):
                    local_file(root, path)

    def test_init_never_overwrites(self):
        with tempfile.TemporaryDirectory() as temp:
            args = ["--project", temp, "init", "--mode", "faceless"]
            self.assertEqual(main(args), 0)
            original = (Path(temp) / "production.json").read_bytes()
            self.assertEqual(main(args), 1)
            self.assertEqual((Path(temp) / "production.json").read_bytes(), original)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg required")
class RealMediaTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "src").mkdir()
        self.video = self.root / "src/test.mp4"
        self.image = self.root / "src/test.png"
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-f", "lavfi", "-i",
                        "testsrc2=s=160x90:r=30:d=1", "-f", "lavfi", "-i",
                        "sine=frequency=440:duration=1", "-c:v", "libx264", "-c:a", "aac",
                        "-shortest", str(self.video)], check=True, capture_output=True)
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-i", str(self.video),
                        "-frames:v", "1", str(self.image)], check=True, capture_output=True)
        self.spec = {"schema_version": 1, "mode": "own-footage", "segments": [
            {"source": "src/test.mp4", "start": .1, "duration": .4}],
            "captions": [{"start": 0, "end": .3, "text": "Türkçe {test} \\ kontrol"}]}

    def tearDown(self):
        self.temp.cleanup()

    def job(self):
        (self.root / "production.json").write_text(json.dumps(self.spec), encoding="utf-8")
        return load_job(self.root)

    def test_three_modes_real_render_and_approval(self):
        original = digest(self.video)
        for mode in ("long-to-shorts", "own-footage", "faceless"):
            with self.subTest(mode=mode):
                self.spec["mode"] = mode
                if mode == "faceless":
                    self.spec["segments"] = [{"source": "src/test.png", "duration": .4}]
                    self.spec["narration"] = "src/test.mp4"
                else:
                    self.spec["segments"] = [
                        {"source": "src/test.mp4", "start": .1, "duration": .2},
                        {"source": "src/test.mp4", "start": .6, "duration": .2}]
                job = self.job()
                render(self.root, job, "preview")
                approval = digest(self.root / "out/preview.mp4")
                with self.assertRaises(ValueError):
                    render(self.root, job, "final", "wrong")
                altered = copy.deepcopy(job)
                altered["identity"]["manifest_sha256"] = "changed"
                with self.assertRaises(ValueError):
                    render(self.root, altered, "final", approval)
                render(self.root, job, "final", approval)
                info = probe(self.root / "out/final.mp4")
                video = next(s for s in info["streams"] if s["codec_type"] == "video")
                self.assertEqual((video["width"], video["height"]), (1080, 1920))
                self.assertTrue(any(s["codec_type"] == "audio" for s in info["streams"]))
                with self.assertRaises(ValueError):
                    render(self.root, job, "preview")
                shutil.rmtree(self.root / "out")
        self.assertEqual(digest(self.video), original)

    def test_bad_ranges_and_unknown_fields(self):
        for change in ({"duration": -1}, {"start": 3}, {"duration": True}):
            original = copy.deepcopy(self.spec)
            self.spec["segments"][0].update(change)
            with self.assertRaises(ValueError):
                self.job()
            self.spec = original
        self.spec["provider"] = "paid"
        with self.assertRaises(ValueError):
            self.job()

    def test_doctor_reports_bad_project(self):
        self.spec["segments"][0]["source"] = "src/missing.mp4"
        (self.root / "production.json").write_text(json.dumps(self.spec))
        self.assertEqual(main(["--project", str(self.root), "doctor"]), 1)


if __name__ == "__main__":
    unittest.main()
