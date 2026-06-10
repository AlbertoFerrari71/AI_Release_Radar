import unittest

from radar.models import DiffResult, Item, RunIndexEntry, SourceSnapshot


class ModelTests(unittest.TestCase):
    def sample_item(self) -> Item:
        return Item(
            item_id="item_001",
            source_id="offline-source",
            provider="openai",
            category="codex_cli",
            severity="medium",
            title="Offline item",
            published_at="2026-06-01T09:00:00Z",
            url="https://example.invalid/offline/item",
            evidence="Artificial offline evidence.",
            content_hash="abc123",
            first_seen="2026-06-09T10:00:00Z",
            confidence=0.8,
        )

    def test_item_serializes_and_deserializes(self):
        item = self.sample_item()
        self.assertEqual(Item.from_dict(item.to_dict()), item)

    def test_item_confidence_out_of_range_raises(self):
        with self.assertRaises(ValueError):
            Item(
                item_id="item_001",
                source_id="offline-source",
                provider="openai",
                category="codex_cli",
                severity="medium",
                title="Offline item",
                published_at="2026-06-01T09:00:00Z",
                url="https://example.invalid/offline/item",
                evidence="Artificial offline evidence.",
                content_hash="abc123",
                first_seen="2026-06-09T10:00:00Z",
                confidence=1.2,
            )

    def test_source_snapshot_serializes_and_deserializes(self):
        snapshot = SourceSnapshot(
            source_id="offline-source",
            provider="openai",
            fetched_at="2026-06-09T10:00:00Z",
            fetch_status="offline_fixture",
            http_status=None,
            items=[self.sample_item()],
            page_hash="pagehash",
        )
        self.assertEqual(SourceSnapshot.from_dict(snapshot.to_dict()), snapshot)

    def test_diff_result_serializes_and_deserializes(self):
        diff = DiffResult(
            source_id="offline-source",
            new_items=["item_002"],
            changed_items=["item_003"],
            removed_items=["item_004"],
            unchanged_count=1,
        )
        self.assertEqual(DiffResult.from_dict(diff.to_dict()), diff)

    def test_run_index_entry_serializes_and_deserializes(self):
        entry = RunIndexEntry(
            run_id="2026-06-09_100000_0030",
            step="0030",
            status="failed",
            started_at="2026-06-09T10:00:00Z",
            finished_at="2026-06-09T10:00:02Z",
            duration_seconds=2,
            report_full=None,
            report_compact=None,
            snapshot_dir="examples/snapshots",
            notes="Artificial offline test entry.",
            source_count=2,
            parsed_count=1,
            item_count=3,
            failed_count=0,
            skipped_count=1,
            timestamp="2026-06-09T10:00:02Z",
        )
        self.assertEqual(RunIndexEntry.from_dict(entry.to_dict()), entry)

    def test_run_index_entry_rejects_negative_counts(self):
        with self.assertRaises(ValueError):
            RunIndexEntry(
                run_id="2026-06-09_100000_0030",
                step="0030",
                status="failed",
                started_at="2026-06-09T10:00:00Z",
                finished_at="2026-06-09T10:00:02Z",
                duration_seconds=2,
                report_full=None,
                report_compact=None,
                snapshot_dir="examples/snapshots",
                notes="Artificial offline test entry.",
                source_count=-1,
            )


if __name__ == "__main__":
    unittest.main()
