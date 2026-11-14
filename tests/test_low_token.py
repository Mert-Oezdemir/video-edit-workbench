import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from low_token import snapshot, packet, make_edl, save_new
from plan_provider import validate


class LowTokenTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in ("src", "work/transcripts", "work/env"):
            (self.root / name).mkdir(parents=True, exist_ok=True)
        clips = {"a": "src/one.mp4", "b": "src/two.mp4"}
        (self.root / "work/clips.json").write_text(json.dumps(clips))
        for cid, source in clips.items():
            (self.root / source).write_bytes(b"fake-media")
            (self.root / f"work/env/{cid}.npy").write_bytes(b"fake-envelope")
            tr = {"clip": cid, "src": source, "utterances": [
                {"text": "Bu bir örnek cümle."},
                {"text": "Bu bir örnek cümle."},
                {"text": "Sonraki konu."},
            ]}
            (self.root / f"work/transcripts/{cid}.json").write_text(
                json.dumps(tr), encoding="utf-8")
        self.revision, self.sources, self.rows = snapshot(self.root, ["b", "a"])
        self.packet = packet(self.revision, self.sources, self.rows)

    def test_order_and_duplicate_hint(self):
        self.assertEqual(self.packet["clip_order"], ["b", "a"])
        self.assertEqual(self.packet["possible_exact_retakes"], [["b:0", "b:1"], ["a:0", "a:1"]])
        self.assertEqual(self.packet["utterances"][0][0], "b:0")

    def test_plan_preserves_other_utterances(self):
        d = {"revision": self.revision, "drop": ["b:0"]}
        edl = make_edl(self.revision, self.sources, self.rows, d, 30, "natural")
        self.assertEqual(edl["items"][0], {"clip": "b", "utt": 1})
        self.assertEqual(len(edl["items"]), 5)

    def test_reject_unknown_stale_duplicate_and_empty(self):
        cases = [{"revision": "old", "drop": []},
                 {"revision": self.revision, "drop": ["x:0"]},
                 {"revision": self.revision, "drop": ["a:0", "a:0"]},
                 {"revision": self.revision, "drop": [u[0] for u in self.packet["utterances"]]}]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                validate(self.packet, json.dumps(case))

    def test_clip_order_and_changed_transcript_invalidate(self):
        self.assertNotEqual(snapshot(self.root)[0], self.revision)
        tp = self.root / "work/transcripts/b.json"
        tr = json.loads(tp.read_text())
        tr["utterances"][0]["text"] = "changed"
        tp.write_text(json.dumps(tr))
        self.assertNotEqual(snapshot(self.root, ["b", "a"])[0], self.revision)

    def test_no_overwrite(self):
        p = self.root / "existing"
        save_new(p, "first")
        with self.assertRaises(FileExistsError):
            save_new(p, "second")
        self.assertEqual(p.read_text(), "first")

    def test_keep_all_and_cli_adapters(self):
        p = self.root / "packet.json"
        p.write_text(json.dumps(self.packet))
        base = [sys.executable, str(SCRIPTS / "plan_provider.py"), "--packet", str(p)]
        out = self.root / "no-ai.json"
        subprocess.run(base + ["--out", str(out), "keep-all"], check=True, capture_output=True)
        self.assertEqual(json.loads(out.read_text())["drop"], [])
        out = self.root / "cli.json"
        fake = [sys.executable, "-c",
                "import sys,json; sys.stdin.read(); print(json.dumps(" +
                repr({"revision": self.revision, "drop": ["a:0"]}) + "))"]
        subprocess.run(base + ["--out", str(out), "cli", "--argv", json.dumps(fake)],
                       check=True, capture_output=True)
        self.assertEqual(json.loads(out.read_text())["drop"], ["a:0"])

    def test_remote_requires_explicit_opt_in(self):
        p = self.root / "packet.json"
        p.write_text(json.dumps(self.packet))
        out = self.root / "remote.json"
        proc = subprocess.run([sys.executable, str(SCRIPTS / "plan_provider.py"),
            "--packet", str(p), "--out", str(out), "api", "--endpoint",
            "https://example.invalid/v1/chat/completions", "--model", "unused"],
            capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("allow-remote", proc.stderr)
        self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
