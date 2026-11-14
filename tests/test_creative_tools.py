import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from creative_overlay import captions, cards, ass, srt, brief
from visual_review import events


class CreativeTests(unittest.TestCase):
    def setUp(self):
        self.prog = {"duration": 12.0, "words": [
            [0.1, .5, "Merhaba"], [.6, 1.1, "dünya!"],
            [2.0, 2.3, "Yeni"], [2.4, 2.8, "konu"],
            [7.0, 7.4, "Son"], [7.5, 8.0, "bölüm."]
        ]}

    def test_captions_follow_program_clock(self):
        cues = captions(self.prog, "short")
        self.assertEqual([x[2] for x in cues], ["Merhaba dünya!", "Yeni konu", "Son bölüm."])
        self.assertTrue(all(a < b for a, b, _ in cues))
        self.assertTrue(all(a[1] <= b[0] for a, b in zip(cues, cues[1:])))
        self.assertIn("00:00:00,100 --> 00:00:01,220", srt(cues))

    def test_cards_are_anchored_and_escaped(self):
        p = {"revision": "rev", "cards": [
            {"word": 0, "kind": "keyword", "text": r"{\pos(1,2)}", "seconds": 2},
            {"word": 4, "kind": "section", "text": "Son bölüm", "seconds": 2},
        ]}
        cues = captions(self.prog, "education")
        gfx = cards(p, "rev", self.prog, "education", cues)
        rendered = ass(self.prog, "education", cues, gfx)
        self.assertNotIn(r"{\pos", rendered)
        self.assertIn(r"{\fad(180,180)}", rendered)
        self.assertIn("Son bölüm", rendered)
        self.assertEqual(gfx[1][0], 7.0)
        with self.assertRaises(ValueError):
            cards(p, "stale", self.prog, "education", cues)
        p["cards"][1]["word"] = 1
        with self.assertRaises(ValueError):
            cards(p, "rev", self.prog, "education", cues)

    def test_brief_lists_real_anchors(self):
        packet = brief(self.prog, "rev", "short")
        self.assertEqual(packet["revision"], "rev")
        self.assertEqual([x[0] for x in packet["anchors"]], [0, 2, 4])

    def test_visual_log_parser(self):
        log = """
[Parsed_showinfo_4] n: 0 pts: 30 pts_time:1.0
[Parsed_blackdetect_1] black_start:2 black_end:3 black_duration:1
[freezedetect] freeze_start: 4.0
[silencedetect] silence_end: 8.5 | silence_duration: 1
"""
        result = events(log, ("shot_change", "black_start", "black_end", "freeze_start", "silence_end"))
        self.assertEqual([x["seconds"] for x in result], [1.0, 2, 3, 4, 8.5])
        self.assertEqual(result[0]["type"], "shot_change")


if __name__ == "__main__":
    unittest.main()
