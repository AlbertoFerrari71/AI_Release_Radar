import tempfile
import unittest
from pathlib import Path

from radar.run_index import (
    append_run_index_entry,
    get_last_run_index_entry,
    read_run_index,
    validate_run_index,
)
from radar.models import RunIndexEntry


class RunIndexTests(unittest.TestCase):
    def entry(self, run_id: str, status: str) -> RunIndexEntry:
        return RunIndexEntry(
            run_id=run_id,
            step="0030",
            status=status,
            started_at="2026-06-09T10:00:00Z",
            finished_at="2026-06-09T10:00:01Z",
            duration_seconds=1.0,
            report_full=None,
            report_compact=None,
            snapshot_dir="examples/snapshots",
            notes="Artificial offline test entry.",
            source_count=2,
            parsed_count=1,
            item_count=3,
            failed_count=0,
            skipped_count=1,
            timestamp="2026-06-09T10:00:01Z",
        )

    def test_append_two_entries_creates_two_lines(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "runs_index.jsonl"
            append_run_index_entry(index_path, self.entry("run-001", "success"))
            append_run_index_entry(index_path, self.entry("run-002", "failed"))
            lines = index_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)
            self.assertIn('"source_count":2', lines[0])
            self.assertIn('"parsed_count":1', lines[0])
            self.assertIn('"item_count":3', lines[0])
            self.assertIn('"failed_count":0', lines[0])
            self.assertIn('"skipped_count":1', lines[0])
            self.assertIn('"timestamp":"2026-06-09T10:00:01Z"', lines[0])

    def test_read_run_index_reads_all_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "runs_index.jsonl"
            first = self.entry("run-001", "success")
            second = self.entry("run-002", "failed")
            append_run_index_entry(index_path, first)
            append_run_index_entry(index_path, second)
            self.assertEqual(read_run_index(index_path), [first, second])
            self.assertEqual(validate_run_index(index_path), [])

    def test_get_last_run_index_entry_returns_last_valid_entry(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "runs_index.jsonl"
            first = self.entry("run-001", "success")
            second = self.entry("run-002", "failed")
            append_run_index_entry(index_path, first)
            append_run_index_entry(index_path, second)
            self.assertEqual(get_last_run_index_entry(index_path), second)

    def test_missing_file_is_handled_without_crash(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "runs_index.jsonl"
            self.assertEqual(read_run_index(index_path), [])
            self.assertIsNone(get_last_run_index_entry(index_path))
            self.assertEqual(validate_run_index(index_path), [])

    def test_no_last_or_latest_files_created(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "runs_index.jsonl"
            append_run_index_entry(index_path, self.entry("run-001", "success"))
            forbidden = [
                path
                for path in Path(tmpdir).iterdir()
                if path.name.startswith("LAST-") or path.name.startswith("latest-")
            ]
            self.assertEqual(forbidden, [])

    def test_validate_run_index_reports_incomplete_line(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "runs_index.jsonl"
            index_path.write_text('{"schema_version":1,"status":"partial"}\n', encoding="utf-8")

            issues = validate_run_index(index_path)

            self.assertEqual(len(issues), 1)
            self.assertIn("line 1", issues[0])
            self.assertIn("run_id", issues[0])

    def test_partial_run_index_entry_is_valid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "runs_index.jsonl"
            partial = self.entry("run-partial", "partial")
            append_run_index_entry(index_path, partial)

            self.assertEqual(validate_run_index(index_path), [])
            self.assertEqual(read_run_index(index_path), [partial])

    def test_no_parsed_items_and_changes_found_entries_are_valid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "runs_index.jsonl"
            no_parsed = self.entry("run-no-parsed", "NO_PARSED_ITEMS")
            changes = self.entry("run-changes", "CHANGES_FOUND")
            append_run_index_entry(index_path, no_parsed)
            append_run_index_entry(index_path, changes)

            entries = read_run_index(index_path)

            self.assertEqual(validate_run_index(index_path), [])
            self.assertEqual(
                [entry.status for entry in entries],
                ["NO_PARSED_ITEMS", "CHANGES_FOUND"],
            )


if __name__ == "__main__":
    unittest.main()
