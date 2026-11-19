import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from lemo_opuscar import local_styles, make_plan, read_library, search_styles


class LemoOpuscarTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.library = root / "lemo"
        style = self.library / "styles" / "neon-tubes"
        style.mkdir(parents=True)
        (self.library / "LICENSE").write_text("fixture", encoding="utf-8")
        (style / "STYLE.md").write_text("NC style fixture", encoding="utf-8")
        (style / "style.json").write_text(json.dumps({
            "slug": "neon-tubes", "en": "Neon Tubes", "category_en": "Light & Lines",
            "uses": ["Example"]
        }), encoding="utf-8")
        self.project = root / "project"
        (self.project / "work").mkdir(parents=True)

    def test_keyword_search_is_local_and_not_a_semantic_recommendation(self):
        styles = local_styles(read_library(self.library))
        self.assertEqual([s["slug"] for s in search_styles(styles, "neon")],
                         ["neon-tubes"])
        self.assertEqual([s["slug"] for s in search_styles(styles, "Light")],
                         ["neon-tubes"])
        self.assertEqual(search_styles(styles, "watercolor"), [])
        with self.assertRaises(ValueError):
            search_styles(styles, "")
        with self.assertRaises(ValueError):
            search_styles(styles, "neon", 0)

        cmd = [sys.executable, str(SCRIPTS / "lemo_opuscar.py"), "search",
               "--library", str(self.library), "--query", "neon", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        response = json.loads(result.stdout)
        self.assertEqual(response["match_type"], "keyword-only")
        self.assertEqual(response["matches"][0]["slug"], "neon-tubes")

    def test_local_style_index_and_non_destructive_plan(self):
        lib = read_library(self.library)
        items = local_styles(lib)
        self.assertEqual([item["slug"] for item in items], ["neon-tubes"])
        output = make_plan(self.project, lib, "neon-tubes")
        plan = json.loads(output.read_text(encoding="utf-8"))
        self.assertFalse(plan["approved"])
        self.assertFalse(plan["rendered"])
        self.assertEqual(plan["mode"], "faceless")
        self.assertFalse(plan["license"]["guide_copied"])
        self.assertEqual(plan["style"]["style_path"], "styles/neon-tubes/STYLE.md")
        self.assertNotIn("NC style fixture", output.read_text(encoding="utf-8"))
        with self.assertRaises(FileExistsError):
            make_plan(self.project, lib, "neon-tubes")
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")), plan)

    def test_style_plan_targets_existing_workbench_mode(self):
        filename = make_plan(self.project, self.library, "neon-tubes",
                             "intro.json", mode="own-footage")
        data = json.loads(filename.read_text(encoding="utf-8"))
        self.assertEqual(data["mode"], "own-footage")
        self.assertFalse(data["approved"])
        self.assertTrue(any("production.json" in x for x in data["next_steps"]))
        with self.assertRaises(ValueError):
            make_plan(self.project, self.library, "neon-tubes",
                      "wrong.json", mode="alternate-mode")

    def test_reject_traversal_unknown_style_and_missing_project(self):
        for style in ("../../outside", "neon-tubes/../../outside", "missing"):
            with self.assertRaises(ValueError):
                make_plan(self.project, self.library, style)
        with self.assertRaises(ValueError):
            make_plan(self.project, self.library, "neon-tubes", "../escape.json")
        with self.assertRaises(OSError):
            make_plan(self.project.parent / "absent", self.library, "neon-tubes")

    def test_reject_symlinked_output_directory(self):
        external = Path(self.tmp.name) / "other"
        external.mkdir()
        (self.project / "work" / "style-plans").symlink_to(external, target_is_directory=True)
        with self.assertRaises(ValueError):
            make_plan(self.project, self.library, "neon-tubes")
        self.assertEqual(list(external.iterdir()), [])

    def test_cli_list_doctor_plan_no_installation(self):
        script = SCRIPTS / "lemo_opuscar.py"
        for command in ("list", "doctor"):
            p = subprocess.run([sys.executable, str(script), command,
                                "--library", str(self.library), "--json"],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("neon-tubes" if command == "list" else "styles_found", p.stdout)
        p = subprocess.run([sys.executable, str(script), "plan",
                            "--library", str(self.library), "--project", str(self.project),
                            "--style", "neon-tubes", "--name", "custom.json", "--mode", "own-footage"],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue((self.project / "work" / "style-plans" / "custom.json").is_file())


if __name__ == "__main__":
    unittest.main()
