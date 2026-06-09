import unittest

from radar.diff import diff_snapshots
from radar.models import Item, SourceSnapshot


class DiffTests(unittest.TestCase):
    def item(self, item_id: str, content_hash: str) -> Item:
        return Item(
            item_id=item_id,
            source_id="offline-source",
            provider="openai",
            category="codex_cli",
            severity="medium",
            title=f"Offline {item_id}",
            published_at="2026-06-01T09:00:00Z",
            url=f"https://example.invalid/offline/{item_id}",
            evidence=f"Artificial evidence for {item_id}.",
            content_hash=content_hash,
            first_seen="2026-06-09T10:00:00Z",
            confidence=0.8,
        )

    def snapshot(self, items: list[Item], page_hash: str = "page-a") -> SourceSnapshot:
        return SourceSnapshot(
            source_id="offline-source",
            provider="openai",
            fetched_at="2026-06-09T10:00:00Z",
            fetch_status="offline_fixture",
            http_status=None,
            items=items,
            page_hash=page_hash,
        )

    def test_previous_none_marks_all_current_items_as_new(self):
        current = self.snapshot([self.item("item_b", "hash-b"), self.item("item_a", "hash-a")])
        diff = diff_snapshots(None, current)
        self.assertEqual(diff.new_items, ["item_a", "item_b"])
        self.assertEqual(diff.changed_items, [])
        self.assertEqual(diff.removed_items, [])
        self.assertEqual(diff.unchanged_count, 0)

    def test_snapshot_diff_detects_new_changed_removed_and_unchanged_items(self):
        previous = self.snapshot(
            [
                self.item("item_changed", "hash-old"),
                self.item("item_removed", "hash-removed"),
                self.item("item_unchanged", "hash-same"),
            ]
        )
        current = self.snapshot(
            [
                self.item("item_new", "hash-new"),
                self.item("item_unchanged", "hash-same"),
                self.item("item_changed", "hash-new-value"),
            ]
        )
        diff = diff_snapshots(previous, current)
        self.assertEqual(diff.new_items, ["item_new"])
        self.assertEqual(diff.changed_items, ["item_changed"])
        self.assertEqual(diff.removed_items, ["item_removed"])
        self.assertEqual(diff.unchanged_count, 1)

    def test_output_lists_are_sorted_deterministically(self):
        previous = self.snapshot([self.item("item_z", "old-z"), self.item("item_a", "old-a")])
        current = self.snapshot([self.item("item_z", "new-z"), self.item("item_b", "new-b")])
        diff = diff_snapshots(previous, current)
        self.assertEqual(diff.changed_items, ["item_z"])
        self.assertEqual(diff.new_items, ["item_b"])
        self.assertEqual(diff.removed_items, ["item_a"])

    def test_page_hash_difference_does_not_mark_items_changed(self):
        items = [self.item("item_same", "hash-same")]
        previous = self.snapshot(items, page_hash="page-old")
        current = self.snapshot(items, page_hash="page-new")
        diff = diff_snapshots(previous, current)
        self.assertEqual(diff.changed_items, [])
        self.assertEqual(diff.new_items, [])
        self.assertEqual(diff.removed_items, [])
        self.assertEqual(diff.unchanged_count, 1)


if __name__ == "__main__":
    unittest.main()
