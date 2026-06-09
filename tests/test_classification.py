import unittest

from radar.classification import (
    classify_category_from_text,
    classify_item,
    classify_severity_from_text,
)
from radar.models import Item


class ClassificationTests(unittest.TestCase):
    def item(self, title: str, evidence: str, item_id: str = "item_001") -> Item:
        return Item(
            item_id=item_id,
            source_id="offline-0060-classification-test",
            provider="openai_fixture",
            category="unknown",
            severity="info",
            title=title,
            published_at="2026-06-09T10:00:00Z",
            url="https://example.invalid/0060/classification",
            evidence=evidence,
            content_hash=f"hash-{item_id}",
            first_seen="2026-06-09",
            confidence=0.8,
        )

    def test_codex_cli_keyword_maps_to_codex_cli(self):
        category = classify_category_from_text(
            "Codex CLI added new command",
            "Offline fixture evidence for terminal users.",
        )
        self.assertEqual(category, "codex_cli")

    def test_agents_md_keyword_maps_to_codex_agents_md(self):
        category = classify_category_from_text(
            "AGENTS.md workspace instructions changed",
            "Offline fixture evidence.",
        )
        self.assertEqual(category, "codex_agents_md")

    def test_windows_sandbox_keyword_maps_to_expected_category(self):
        category = classify_category_from_text(
            "Windows PowerShell sandbox note",
            "Offline fixture evidence for sandbox behavior.",
        )
        self.assertIn(category, {"codex_windows", "security"})

    def test_deprecation_keyword_maps_to_deprecation_and_high_severity(self):
        title = "Responses API deprecation notice"
        evidence = "Offline fixture: endpoint sunset and retirement guidance."
        self.assertEqual(classify_category_from_text(title, evidence), "deprecation")
        self.assertIn(classify_severity_from_text(title, evidence), {"high", "critical"})

    def test_security_vulnerability_maps_to_critical(self):
        severity = classify_severity_from_text(
            "Critical security vulnerability",
            "Offline fixture: exploit could cause data loss.",
        )
        self.assertEqual(severity, "critical")

    def test_unrecognized_text_defaults_to_unknown_and_info(self):
        title = "Neutral release note"
        evidence = "Offline fixture with unrelated wording."
        self.assertEqual(classify_category_from_text(title, evidence), "unknown")
        self.assertEqual(classify_severity_from_text(title, evidence), "info")

    def test_matched_keywords_are_sorted_and_deterministic(self):
        item = self.item(
            "Codex CLI terminal command",
            "Offline fixture: command introduced for TUI and /app users.",
        )
        first = classify_item(item)
        second = classify_item(item)
        self.assertEqual(first.matched_keywords, sorted(first.matched_keywords))
        self.assertEqual(first.matched_keywords, second.matched_keywords)

    def test_reasons_are_not_empty(self):
        classification = classify_item(
            self.item(
                "Codex CLI added new command",
                "Offline fixture: command introduced for terminal users.",
            )
        )
        self.assertTrue(classification.reasons)

    def test_classify_item_does_not_modify_item(self):
        item = self.item(
            "AGENTS.md breaking workspace instructions",
            "Offline fixture: breaking guidance for AGENTS.md loading.",
        )
        before = item.to_dict()
        classification = classify_item(item)
        self.assertEqual(item.to_dict(), before)
        self.assertEqual(classification.item_id, item.item_id)
        self.assertEqual(item.category, "unknown")
        self.assertEqual(item.severity, "info")


if __name__ == "__main__":
    unittest.main()
