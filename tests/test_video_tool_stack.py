import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from video_tool_stack import (
    BLOCKED_POLICIES, eligibility, plan, probe, registry, selected_tools
)

ALL_NAMED = {
    "ffmpeg", "faster-whisper", "ffmpeg-skill", "auto-editor",
    "claude-shorts", "ghost-editor", "openmontage", "rea-video",
    "hyperframes", "remotion", "piper", "comfyui", "higgsfield-skills",
    "lemo-opuscar"
}
MODES = {"long-to-shorts", "faceless", "own-footage"}


class FreeVideoToolStackTests(unittest.TestCase):
    def setUp(self):
        self.data = registry()
        self.tools = {tool["id"]: tool for tool in self.data["tools"]}

    def test_all_named_repositories_included(self):
        self.assertEqual(set(self.tools), ALL_NAMED)
        self.assertEqual(set(self.data["modes"]), MODES)
        for tool in self.data["tools"]:
            self.assertTrue(tool["url"].startswith("https://"))
            self.assertTrue(tool["license"])
            self.assertTrue(tool["note"])
            self.assertTrue(set(tool["modes"]).issubset(MODES))

    def test_guards_are_fail_closed(self):
        for field in (
            "extra_api_spend_allowed", "cloud_generation_allowed",
            "cloud_render_allowed", "paid_features_allowed",
            "auto_install_optional_tools", "send_private_media_off_device"
        ):
            self.assertIs(self.data["policy"][field], False)
        self.assertEqual(eligibility(self.tools["higgsfield-skills"]),
                         "blocked-no-extra-spend")
        self.assertEqual(self.tools["higgsfield-skills"]["policy"],
                         "paid-service-disabled")
        self.assertEqual(self.tools["openmontage"]["license"], "AGPL-3.0")
        self.assertEqual(self.tools["hyperframes"]["license"], "Apache-2.0")
        self.assertEqual(self.tools["remotion"]["policy"], "restricted-license")
        self.assertTrue("archived" in self.tools["piper"]["note"].lower())

    def test_only_core_entries_enabled_by_default(self):
        enabled = {id for id, tool in self.tools.items()
                   if tool["enabled_by_default"]}
        self.assertEqual(enabled, {"ffmpeg", "faster-whisper"})
        self.assertTrue(all(self.tools[id]["policy"] == "local-free"
                            for id in enabled))

    def test_each_mode_has_stages_with_known_tools(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                p = plan(self.data, mode)
                self.assertEqual(p["status"], "advisory-plan-only")
                self.assertTrue(p["plan_is_not_execution"])
                self.assertTrue(p["stages"])
                for stage in p["stages"]:
                    self.assertTrue(stage["choices"])
                    for choice in stage["choices"]:
                        self.assertIn(choice["id"], self.tools)
                        self.assertIn(mode, self.tools[choice["id"]]["modes"])
                        self.assertIn(choice["eligibility"], (
                            "blocked-no-extra-spend", "optional-review-required",
                            "local-eligible"))

    def test_availability_only_checks_local_presence(self):
        for tool in self.data["tools"]:
            self.assertIn(probe(tool), ("present", "not-found", "not-checked"))
        self.assertEqual(probe(self.tools["higgsfield-skills"]), "not-checked")

    def test_filter_by_mode(self):
        for mode in MODES:
            for tool in selected_tools(self.data, mode):
                self.assertIn(mode, tool["modes"])

    def test_cli_plan_exclusive_write_and_readback(self):
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "plan.json"
            cmd = [sys.executable, str(SCRIPTS / "video_tool_stack.py"),
                   "plan", "--mode", "long-to-shorts", "--out", str(destination)]
            first = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, first.stderr)
            output = json.loads(destination.read_text(encoding="utf-8"))
            self.assertEqual(output["mode"], "long-to-shorts")
            self.assertTrue(output["zero_extra_spend_guards"]["protect_originals"])
            second = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertEqual(json.loads(destination.read_text()), output)

    def test_cli_list_json(self):
        cmd = [sys.executable, str(SCRIPTS / "video_tool_stack.py"),
               "list", "--mode", "faceless", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(any(t["id"] == "comfyui" for t in data["tools"]))
        self.assertTrue(any(t["eligibility"] == "blocked-no-extra-spend"
                            for t in data["tools"]))


if __name__ == "__main__":
    unittest.main()
