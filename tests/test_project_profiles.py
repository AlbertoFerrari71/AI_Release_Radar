import tempfile
import unittest
from pathlib import Path

from radar.json_utils import write_json
from radar.project_profiles import fallback_project_profiles, load_project_profiles


class ProjectProfilesTests(unittest.TestCase):
    def test_loads_default_profiles(self):
        profiles = load_project_profiles()

        self.assertIn("ai_software_factory", profiles)
        self.assertIn("codex_skills", profiles)
        self.assertIn("family_photo_organizer", profiles)
        self.assertIn("mansionario_vivo", profiles)
        self.assertIn("agglodetect", profiles)
        self.assertIn("diamsign", profiles)
        self.assertIn("controllo_gestione_esolver", profiles)
        self.assertIn("ai_release_radar", profiles)
        self.assertFalse(profiles["family_photo_organizer"].prompt_generation_allowed)
        self.assertTrue(profiles["ai_release_radar"].prompt_generation_allowed)

    def test_fallback_when_config_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            profiles = load_project_profiles(Path(tmp) / "missing.json")

        self.assertEqual(
            profiles["controllo_gestione_esolver"].project_name,
            "ControlloGestioneExcel / eSolver",
        )
        self.assertEqual(
            set(fallback_project_profiles()),
            set(profiles),
        )

    def test_rejects_duplicate_project_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "profiles.json"
            project = {
                "project_key": "x",
                "project_name": "X",
                "direct_categories": ["security"],
                "monitor_categories": ["api_platform"],
                "ignored_categories": [],
                "keywords_positive": ["x"],
                "keywords_negative": [],
                "review_threshold": 50,
                "prompt_generation_allowed": True,
            }
            write_json(path, {"schema_version": 1, "projects": [project, project]})

            with self.assertRaisesRegex(ValueError, "duplicate project_key"):
                load_project_profiles(path)


if __name__ == "__main__":
    unittest.main()
