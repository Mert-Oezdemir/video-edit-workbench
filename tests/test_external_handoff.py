import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from external_handoff import make_handoff


class ExternalHandoffTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "project"
        (self.root / "work" / "external" / "hyperframes").mkdir(parents=True)
        (self.root / "work" / "reference").mkdir()
        self.video = self.root / "work" / "external" / "hyperframes" / "test.mp4"
        self.video.write_bytes(b"simulated video - ffprobe mocked")
        self.report = self.root / "work" / "reference" / "VIDEO.md"
        self.report.write_text("# Local video analysis", encoding="utf-8")

    def test_reference_handoff_never_runs_commands(self):
        with patch("external_handoff.subprocess.run", side_effect=AssertionError("no subprocess")):
            result = make_handoff(
                self.root, "rea-video", "faceless",
                Path("work/reference/VIDEO.md"), "reference-report",
                "owned reference")
        self.assertEqual(result["review_status"], "pending-human-review")
        self.assertFalse(result["approved"])
        self.assertEqual(result["file"], "work/reference/VIDEO.md")
        self.assertEqual(result["metadata"], {})

    def test_video_probes_without_shell_and_is_unapproved(self):
        stdout = json.dumps({"streams": [
            {"codec_type": "audio", "codec_name": "aac"},
            {"codec_type": "video", "width": 1080, "height": 1920,
             "codec_name": "h264"}
        ], "format": {"duration": "29.97"}})
        with patch("external_handoff.subprocess.run",
                   return_value=Mock(returncode=0, stdout=stdout, stderr="")) as fake:
            result = make_handoff(self.root, "hyperframes", "faceless",
                                  self.video, "rendered-video")
        args = fake.call_args.args[0]
        self.assertEqual(args[0], "ffprobe")
        self.assertNotIn("sh", args)
        self.assertFalse(fake.call_args.kwargs.get("shell", False))
        self.assertEqual(result["metadata"]["height"], 1920)
        self.assertFalse(result["approved"])

    def test_rejects_unknown_paid_or_wrong_mode(self):
        for tool, mode, path, kind in [
            ("higgsfield-skills", "faceless", self.report, "reference-report"),
            ("no-such-repo", "faceless", self.report, "reference-report"),
            ("claude-shorts", "own-footage", self.report, "reference-report")
        ]:
            with self.subTest(tool=tool), self.assertRaises(ValueError):
                make_handoff(self.root, tool, mode, path, kind)

    def test_rejects_escape_and_bad_filetype(self):
        with tempfile.TemporaryDirectory() as other:
            external = Path(other) / "private.mp4"
            external.write_bytes(b"private")
            with self.assertRaises(ValueError):
                make_handoff(self.root, "hyperframes", "faceless",
                             external, "rendered-video")
        with self.assertRaises(ValueError):
            make_handoff(self.root, "rea-video", "faceless",
                         self.report, "rendered-video")

    def test_cli_creates_manifest_once(self):
        cmd = [sys.executable, str(SCRIPTS / "external_handoff.py"),
               "--project", str(self.root),
               "--tool", "rea-video", "--mode", "faceless",
               "--kind", "reference-report",
               "--asset", "work/reference/VIDEO.md",
               "--out", "work/handoffs/reference.json"]
        first = subprocess.run(cmd, text=True, capture_output=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        p = self.root / "work" / "handoffs" / "reference.json"
        self.assertEqual(json.loads(p.read_text())["approved"], False)
        second = subprocess.run(cmd, text=True, capture_output=True)
        self.assertNotEqual(second.returncode, 0)

    def test_cli_refuses_manifest_outside_work(self):
        cmd = [sys.executable, str(SCRIPTS / "external_handoff.py"),
               "--project", str(self.root),
               "--tool", "rea-video", "--mode", "faceless",
               "--kind", "reference-report",
               "--asset", "work/reference/VIDEO.md", "--out", "src/unsafe.json"]
        result = subprocess.run(cmd, text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((self.root / "src" / "unsafe.json").exists())


if __name__ == "__main__":
    unittest.main()
