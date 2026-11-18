"""Optional real-media integration smoke test, executed in dedicated CI job.

RUN_MEDIA_SMOKE=1 python -m unittest discover -s tests -p 'test_workbench_smoke.py' -v
Requires a local FFmpeg build with libx264 and libass; no API/network/model.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from workbench import project_init


@unittest.skipUnless(os.environ.get("RUN_MEDIA_SMOKE") == "1",
                     "Enable with RUN_MEDIA_SMOKE=1 (dedicated CI/media test)")
class LocalRealMediaSmoke(unittest.TestCase):
    def test_all_three_modes_encode_own_synthetic_video(self):
        for cmd in ("ffmpeg", "ffprobe"):
            if shutil.which(cmd) is None:
                self.skipTest(f"{cmd} unavailable")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "videos"
            project_init(root)
            src = root / "src" / "recording.mp4"
            generate = [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostdin", "-n",
                "-f", "lavfi", "-i", "testsrc2=size=256x456:rate=30",
                "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=44100",
                "-t", "5", "-c:v", "libx264", "-preset", "ultrafast",
                "-crf", "29", "-c:a", "aac", str(src)
            ]
            subprocess.run(generate, check=True, timeout=90)

            srt = root / "src" / "recording.srt"
            srt.write_text(
                "1\n00:00:00,000 --> 00:00:01,500\nNeden şimdi önemli?\n\n"
                "2\n00:00:01,500 --> 00:00:03,000\nÇünkü yerel ve ücretsiz.\n\n"
                "3\n00:00:03,000 --> 00:00:04,500\nBir videoyu kesip izleyelim.\n",
                encoding="utf-8"
            )
            script = root / "src" / "script.txt"
            script.write_text(
                "Bu örnek kısa bir video.\n\n"
                "Yapay zekâ servisi yerine ücretsiz yerel araçlar kullanıyor.",
                encoding="utf-8"
            )

            def cli(*args):
                p = subprocess.run(
                    [sys.executable, str(ROOT / "workbench.py"), *args],
                    capture_output=True, text=True, timeout=180
                )
                self.assertEqual(p.returncode, 0, p.stderr[-1000:])
                return p

            cli("edit", "--project", str(root), "--input", "src/recording.mp4",
                "--format", "portrait", "--start", "0.5", "--end", "2.5")
            cli("shorts", "--project", str(root), "--input", "src/recording.mp4",
                "--srt", "src/recording.srt", "--minimum", "1",
                "--maximum", "4", "--count", "1", "--burn-captions")
            cli("faceless", "--project", str(root), "--script", "src/script.txt",
                "--seconds-per-scene", "1.8")
            expected = [
                root / "out" / "edited.mp4",
                root / "out" / "shorts-recording" / "short-01.mp4",
                root / "out" / "faceless.mp4"
            ]
            for path in expected:
                self.assertTrue(path.is_file(), str(path))
                p = subprocess.run([
                    "ffprobe", "-v", "error", "-select_streams", "v:0",
                    "-show_entries", "stream=width,height",
                    "-of", "json", str(path)
                ], capture_output=True, text=True, check=True, timeout=30)
                stream = json.loads(p.stdout)["streams"][0]
                self.assertEqual((stream["width"], stream["height"]), (1080, 1920))
            self.assertTrue((root / "src" / "recording.mp4").is_file())
            self.assertFalse((root / "out" / "faceless.json").read_text().find(
                '"approved": false') == -1)


if __name__ == "__main__":
    unittest.main()
