import tempfile
import unittest
from pathlib import Path

from radar.run_index import (
    append_run_index_entry,
    get_last_run_index_entry,
    read_run_index,
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
        )

    def test_append_two_entries_creates_two_lines(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "runs_index.jsonl"
            append_run_index_entry(index_path, self.entry("run-001", "success"))
            append_run_index_entry(index_path, self.entry("run-002", "failed"))
            lines = index_path.read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 2)

    def test_read_run_index_reads_all_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            index_path = Path(tmpdir) / "runs_index.jsonl"
            first = self.entry("run-001", "success")
            second = self.entry("run-002", "failed")
            append_run_index_entry(index_path, first)
            append_run_index_entry(index_path, second)
            self.assertEqual(read_run_index(index_path), [first, second])

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


if __name__ == "__main__":
    unittest.main()
