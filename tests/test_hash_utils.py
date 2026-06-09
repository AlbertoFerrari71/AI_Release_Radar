import unittest

from radar.hash_utils import (
    content_hash_for_item_fields,
    normalize_text,
    stable_item_id,
    stable_sha256_text,
)
from radar.models import Item


class HashUtilsTests(unittest.TestCase):
    def test_normalize_text_collapses_spaces_and_newlines(self):
        self.assertEqual(normalize_text("  Alpha\r\n  Beta\t\tGamma  "), "Alpha Beta Gamma")

    def test_stable_sha256_text_is_deterministic(self):
        self.assertEqual(stable_sha256_text(" Alpha "), stable_sha256_text("Alpha"))

    def test_stable_item_id_uses_normalized_equivalent_inputs(self):
        first = stable_item_id(" offline-source ", "Codex\nCLI")
        second = stable_item_id("offline-source", "Codex CLI")
        self.assertEqual(first, second)

    def test_content_hash_changes_when_relevant_title_or_evidence_changes(self):
        base = self.content_hash(title="Title A", evidence="Evidence A")
        changed_title = self.content_hash(title="Title B", evidence="Evidence A")
        changed_evidence = self.content_hash(title="Title A", evidence="Evidence B")
        self.assertNotEqual(base, changed_title)
        self.assertNotEqual(base, changed_evidence)

    def test_content_hash_does_not_depend_on_first_seen(self):
        content_hash = self.content_hash(title="Title A", evidence="Evidence A")
        first = Item(
            item_id="item_001",
            source_id="offline-source",
            provider="openai",
            category="codex_cli",
            severity="medium",
            title="Title A",
            published_at="2026-06-01T09:00:00Z",
            url="https://example.invalid/offline/item",
            evidence="Evidence A",
            content_hash=content_hash,
            first_seen="2026-06-09T10:00:00Z",
            confidence=0.8,
        )
        second = Item.from_dict({**first.to_dict(), "first_seen": "2026-06-10T10:00:00Z"})
        self.assertEqual(first.content_hash, second.content_hash)

    def content_hash(self, *, title: str, evidence: str) -> str:
        return content_hash_for_item_fields(
            source_id="offline-source",
            provider="openai",
            category="codex_cli",
            severity="medium",
            title=title,
            published_at="2026-06-01T09:00:00Z",
            url="https://example.invalid/offline/item",
            evidence=evidence,
        )


if __name__ == "__main__":
    unittest.main()
