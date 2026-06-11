import tempfile
import unittest
from pathlib import Path

from radar.json_utils import read_json
from radar.translation_prompt_pack import (
    DEFAULT_GLOSSARY_TERMS,
    build_translation_prompt,
    write_translation_prompt_pack,
)


class TranslationPromptPackTests(unittest.TestCase):
    def sample_items(self):
        return [
            {
                "source_item_id": "item-1",
                "title": "OpenAI Codex CLI v1.2.3 release",
                "summary": "Run python -m radar.cli daily-sim and keep https://example.test unchanged.",
                "source_url": "https://example.test",
            }
        ]

    def test_build_translation_prompt_contains_contract_and_glossary(self):
        prompt = build_translation_prompt(
            run_id="run-1",
            target_locale="it",
            items=self.sample_items(),
            profile="balanced",
        )

        self.assertIn("Translate only `title` and `summary` fields", prompt)
        self.assertIn("Do not call external services", prompt)
        self.assertIn("AI Release Radar", prompt)
        self.assertIn("Human approval", prompt)
        self.assertIn("source_item_id", prompt)
        self.assertIn("OpenAI Codex CLI v1.2.3 release", prompt)

    def test_write_translation_prompt_pack_writes_bridge_only_index(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = Path(tmpdir) / "bridge"
            index = write_translation_prompt_pack(
                run_id="run-1",
                items=self.sample_items(),
                bridge_root=bridge,
                locales=["it", "de"],
                profile="balanced",
            )
            index_path = Path(index["index_path"])
            loaded_index = read_json(index_path)
            prompt_text = Path(index["prompt_paths"]["it"]).read_text(encoding="utf-8")

            self.assertTrue(index_path.name.endswith("1200-Translation_Prompt_Index.json"))
            for term in DEFAULT_GLOSSARY_TERMS:
                self.assertIn(term, prompt_text)
        self.assertFalse(loaded_index["llm_executed"])
        self.assertTrue(loaded_index["bridge_only"])
        self.assertEqual(loaded_index["profile"], "balanced")
        self.assertEqual(loaded_index["target_locales"], ["de", "it"])

    def test_unsupported_profile_is_refused(self):
        with self.assertRaises(ValueError):
            build_translation_prompt(
                run_id="run-1",
                target_locale="it",
                items=self.sample_items(),
                profile="expensive",
            )


if __name__ == "__main__":
    unittest.main()
