import json
import tempfile
import unittest
from pathlib import Path

from radar.news_translation import (
    apply_translation_cache_to_actions,
    load_translation_cache,
    preservation_report,
    save_translation_cache,
    translation_cache_status,
    validate_translation_item,
)


class NewsTranslationTests(unittest.TestCase):
    def test_translation_item_schema_and_cache_round_trip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = Path(tmpdir) / "bridge"
            item = {
                "run_id": "run-1",
                "source_item_id": "item-1",
                "target_locale": "it",
                "source_locale": "en",
                "title_translated": "Titolo tradotto",
                "summary_translated": "Sintesi tradotta",
                "technical_terms_preserved": True,
                "links_preserved": True,
                "version_numbers_preserved": True,
                "translation_model_profile": "balanced",
                "translation_status": "translated",
                "review_required": False,
                "created_at": "2026-06-11T07:15:00Z",
            }

            path = save_translation_cache("run-1", "it", [item], bridge)
            self.assertTrue(path.is_file())
            self.assertEqual(path.name, "translated_items.it.json")
            loaded = load_translation_cache("run-1", "it", bridge)

        self.assertEqual(len(loaded), 1)
        self.assertEqual(validate_translation_item(loaded[0]), [])
        self.assertEqual(loaded[0]["source_item_id"], "item-1")

    def test_translation_cache_status_is_robust_for_missing_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            status = translation_cache_status(
                "run-1",
                ["en", "it", "fr", "de", "es"],
                Path(tmpdir) / "bridge",
            )

        self.assertEqual(status["locales"]["it"]["status"], "missing")
        self.assertEqual(status["locales"]["it"]["item_count"], 0)

    def test_missing_translation_falls_back_to_original_action(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            actions = [
                {
                    "source_item_id": "item-1",
                    "title": "Original title",
                    "summary": "Original summary",
                }
            ]
            localized = apply_translation_cache_to_actions(
                actions,
                run_id="run-1",
                locale="de",
                bridge_root=Path(tmpdir) / "bridge",
            )

        self.assertEqual(localized[0]["localized_title"], "Original title")
        self.assertEqual(localized[0]["translation"]["badge"], "missing")

    def test_existing_cache_is_used_by_action_view_model(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = Path(tmpdir) / "bridge"
            save_translation_cache(
                "run-1",
                "it",
                [
                    {
                        "source_item_id": "item-1",
                        "target_locale": "it",
                        "title_translated": "Titolo",
                        "summary_translated": "Sintesi",
                    }
                ],
                bridge,
            )
            localized = apply_translation_cache_to_actions(
                [
                    {
                        "source_item_id": "item-1",
                        "title": "Original title",
                        "summary": "Original summary",
                    }
                ],
                run_id="run-1",
                locale="it",
                bridge_root=bridge,
            )

        self.assertEqual(localized[0]["localized_title"], "Titolo")
        self.assertEqual(localized[0]["localized_summary"], "Sintesi")
        self.assertEqual(localized[0]["translation"]["badge"], "cached")

    def test_preservation_rules_for_versions_links_commands_and_paths(self):
        source = (
            "Use python -m radar.cli daily-sim --output-root D:\\Bridge\\runs "
            "for https://example.test/release v1.2.3."
        )
        translated = (
            "Usare python -m radar.cli daily-sim --output-root D:\\Bridge\\runs "
            "per https://example.test/release v1.2.3."
        )
        report = preservation_report(source, translated)

        self.assertTrue(report["version_numbers_preserved"])
        self.assertTrue(report["links_preserved"])
        self.assertTrue(report["commands_preserved"])
        self.assertTrue(report["paths_preserved"])
        self.assertTrue(report["preservation_pass"])

    def test_cache_writes_runtime_outputs_only_under_bridge_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = Path(tmpdir) / "bridge"
            save_translation_cache("run-1", "fr", [], bridge)
            files = sorted(path.relative_to(bridge).as_posix() for path in bridge.rglob("*") if path.is_file())

        self.assertEqual(
            files,
            [
                "translations/run-1/translated_items.fr.json",
                "translations/run-1/translation_index.json",
                "translations/run-1/translation_report.md",
            ],
        )
        self.assertNotIn("LAST-", json.dumps(files))
        self.assertNotIn("latest-", json.dumps(files))


if __name__ == "__main__":
    unittest.main()
