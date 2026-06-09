import json
import tempfile
import unittest
from pathlib import Path

from radar.diff import diff_snapshots
from radar.hash_utils import stable_sha256_text
from radar.json_utils import read_json, write_json
from radar.models import SourceSnapshot
from radar.offline_workflow import (
    build_diff_from_snapshot_files,
    build_snapshot_and_diff_from_item_fixtures,
    load_items_fixture_snapshot,
    read_diff_result,
    read_snapshot,
    write_diff_result,
    write_snapshot,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "examples" / "fixtures"
SNAPSHOTS_DIR = REPO_ROOT / "examples" / "snapshots"
SOURCE_ID = "offline-0050-diff-workflow-fixture"
PROVIDER = "openai_fixture"
PREVIOUS_FETCHED_AT = "2026-06-09T13:00:00Z"
CURRENT_FETCHED_AT = "2026-06-09T13:05:00Z"


def _previous_fixture_path() -> Path:
    return FIXTURES_DIR / "0050_previous_items_fixture.json"


def _current_fixture_path() -> Path:
    return FIXTURES_DIR / "0050_current_items_fixture.json"


def _fixture_page_hash(path: Path) -> str:
    return stable_sha256_text(path.read_text(encoding="utf-8"))


class OfflineWorkflowTests(unittest.TestCase):
    def build_expected_workflow(self):
        return build_snapshot_and_diff_from_item_fixtures(
            previous_fixture_path=str(_previous_fixture_path()),
            current_fixture_path=str(_current_fixture_path()),
            source_id=SOURCE_ID,
            provider=PROVIDER,
            previous_fetched_at=PREVIOUS_FETCHED_AT,
            current_fetched_at=CURRENT_FETCHED_AT,
            previous_page_hash=_fixture_page_hash(_previous_fixture_path()),
            current_page_hash=_fixture_page_hash(_current_fixture_path()),
        )

    def test_loads_previous_and_current_fixtures_as_snapshots(self):
        previous_snapshot = load_items_fixture_snapshot(
            str(_previous_fixture_path()),
            SOURCE_ID,
            PROVIDER,
            PREVIOUS_FETCHED_AT,
            _fixture_page_hash(_previous_fixture_path()),
        )
        current_snapshot = load_items_fixture_snapshot(
            str(_current_fixture_path()),
            SOURCE_ID,
            PROVIDER,
            CURRENT_FETCHED_AT,
            _fixture_page_hash(_current_fixture_path()),
        )
        self.assertEqual(len(previous_snapshot.items), 4)
        self.assertEqual(len(current_snapshot.items), 4)
        self.assertEqual(previous_snapshot.fetch_status, "offline_fixture")
        self.assertIsNone(current_snapshot.http_status)

    def test_complete_diff_counts_new_changed_removed_and_unchanged(self):
        previous_snapshot, current_snapshot, diff_result = self.build_expected_workflow()
        self.assertIsNotNone(previous_snapshot)
        self.assertEqual(len(current_snapshot.items), 4)
        self.assertEqual(len(diff_result.new_items), 1)
        self.assertEqual(len(diff_result.changed_items), 1)
        self.assertEqual(len(diff_result.removed_items), 1)
        self.assertEqual(diff_result.unchanged_count, 2)

    def test_previous_none_marks_all_current_items_as_new(self):
        previous_snapshot, current_snapshot, diff_result = build_snapshot_and_diff_from_item_fixtures(
            previous_fixture_path=None,
            current_fixture_path=str(_current_fixture_path()),
            source_id=SOURCE_ID,
            provider=PROVIDER,
            previous_fetched_at=None,
            current_fetched_at=CURRENT_FETCHED_AT,
            current_page_hash=_fixture_page_hash(_current_fixture_path()),
        )
        self.assertIsNone(previous_snapshot)
        self.assertEqual(len(diff_result.new_items), len(current_snapshot.items))
        self.assertEqual(diff_result.changed_items, [])
        self.assertEqual(diff_result.removed_items, [])
        self.assertEqual(diff_result.unchanged_count, 0)

    def test_page_hash_difference_does_not_mark_items_changed(self):
        snapshot_a = load_items_fixture_snapshot(
            str(_current_fixture_path()),
            SOURCE_ID,
            PROVIDER,
            CURRENT_FETCHED_AT,
            "page-a",
        )
        snapshot_b = load_items_fixture_snapshot(
            str(_current_fixture_path()),
            SOURCE_ID,
            PROVIDER,
            CURRENT_FETCHED_AT,
            "page-b",
        )
        diff_result = diff_snapshots(snapshot_a, snapshot_b)
        self.assertNotEqual(snapshot_a.page_hash, snapshot_b.page_hash)
        self.assertEqual(diff_result.new_items, [])
        self.assertEqual(diff_result.changed_items, [])
        self.assertEqual(diff_result.removed_items, [])
        self.assertEqual(diff_result.unchanged_count, len(snapshot_a.items))

    def test_diff_output_is_deterministic_with_items_in_different_order(self):
        previous_snapshot, current_snapshot, expected_diff = self.build_expected_workflow()
        self.assertIsNotNone(previous_snapshot)
        previous_reordered = SourceSnapshot(
            source_id=previous_snapshot.source_id,
            provider=previous_snapshot.provider,
            fetched_at=previous_snapshot.fetched_at,
            fetch_status=previous_snapshot.fetch_status,
            http_status=previous_snapshot.http_status,
            items=list(reversed(previous_snapshot.items)),
            page_hash=previous_snapshot.page_hash,
        )
        current_reordered = SourceSnapshot(
            source_id=current_snapshot.source_id,
            provider=current_snapshot.provider,
            fetched_at=current_snapshot.fetched_at,
            fetch_status=current_snapshot.fetch_status,
            http_status=current_snapshot.http_status,
            items=list(reversed(current_snapshot.items)),
            page_hash=current_snapshot.page_hash,
        )
        self.assertEqual(diff_snapshots(previous_reordered, current_reordered), expected_diff)

    def test_snapshot_write_and_read_round_trip(self):
        _, current_snapshot, _ = self.build_expected_workflow()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "0050_current_snapshot.json"
            write_snapshot(str(path), current_snapshot)
            self.assertEqual(read_snapshot(str(path)), current_snapshot)

    def test_diff_write_and_read_round_trip(self):
        _, _, diff_result = self.build_expected_workflow()
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "0050_diff_result.json"
            write_diff_result(str(path), diff_result)
            self.assertEqual(read_diff_result(str(path)), diff_result)

    def test_expected_snapshot_and_diff_fixtures_match_generated_workflow(self):
        previous_snapshot, current_snapshot, diff_result = self.build_expected_workflow()
        self.assertEqual(
            previous_snapshot,
            read_snapshot(str(SNAPSHOTS_DIR / "0050_previous_snapshot.json")),
        )
        self.assertEqual(
            current_snapshot,
            read_snapshot(str(SNAPSHOTS_DIR / "0050_current_snapshot.json")),
        )
        self.assertEqual(
            diff_result,
            read_diff_result(str(SNAPSHOTS_DIR / "0050_diff_result.json")),
        )

    def test_diff_fixture_matches_diff_from_snapshot_files(self):
        diff_result = build_diff_from_snapshot_files(
            str(SNAPSHOTS_DIR / "0050_previous_snapshot.json"),
            str(SNAPSHOTS_DIR / "0050_current_snapshot.json"),
        )
        self.assertEqual(
            diff_result,
            read_diff_result(str(SNAPSHOTS_DIR / "0050_diff_result.json")),
        )

    def test_diff_from_snapshot_files_with_previous_none_marks_all_current_as_new(self):
        diff_result = build_diff_from_snapshot_files(
            None,
            str(SNAPSHOTS_DIR / "0050_current_snapshot.json"),
        )
        current_snapshot = read_snapshot(str(SNAPSHOTS_DIR / "0050_current_snapshot.json"))
        self.assertEqual(len(diff_result.new_items), len(current_snapshot.items))
        self.assertEqual(diff_result.changed_items, [])
        self.assertEqual(diff_result.removed_items, [])
        self.assertEqual(diff_result.unchanged_count, 0)

    def test_duplicate_item_ids_in_snapshot_raise_clear_error(self):
        duplicate_fixture = {
            "items": [
                {
                    "natural_key": "duplicate-natural-key",
                    "category": "codex_cli",
                    "severity": "info",
                    "title": "Duplicate fixture item A",
                    "published_at": "2026-06-09T10:00:00Z",
                    "url": "https://example.invalid/0050/duplicate-a",
                    "evidence": "Offline fixture: first duplicate item.",
                    "first_seen": "2026-06-09",
                    "confidence": 0.8,
                },
                {
                    "natural_key": "duplicate-natural-key",
                    "category": "codex_cli",
                    "severity": "medium",
                    "title": "Duplicate fixture item B",
                    "published_at": "2026-06-09T11:00:00Z",
                    "url": "https://example.invalid/0050/duplicate-b",
                    "evidence": "Offline fixture: second duplicate item.",
                    "first_seen": "2026-06-09",
                    "confidence": 0.8,
                },
            ]
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "0050_duplicate_items_fixture.json"
            write_json(path, duplicate_fixture)
            with self.assertRaisesRegex(ValueError, "duplicate item_id in snapshot"):
                load_items_fixture_snapshot(
                    str(path),
                    SOURCE_ID,
                    PROVIDER,
                    CURRENT_FETCHED_AT,
                )

    def test_workflow_does_not_create_forbidden_last_or_latest_files(self):
        before = self.forbidden_files()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            _, current_snapshot, diff_result = self.build_expected_workflow()
            write_snapshot(str(temp_path / "0050_current_snapshot.json"), current_snapshot)
            write_diff_result(str(temp_path / "0050_diff_result.json"), diff_result)
            created_names = {path.name for path in temp_path.iterdir()}
        after = self.forbidden_files()
        self.assertEqual(before, after)
        self.assertFalse(any(name.startswith("LAST-") for name in created_names))
        self.assertFalse(any(name.startswith("latest-") for name in created_names))

    def test_missing_previous_fetched_at_raises_clear_error(self):
        with self.assertRaisesRegex(
            ValueError,
            "previous_fetched_at is required when previous_fixture_path is set",
        ):
            build_snapshot_and_diff_from_item_fixtures(
                previous_fixture_path=str(_previous_fixture_path()),
                current_fixture_path=str(_current_fixture_path()),
                source_id=SOURCE_ID,
                provider=PROVIDER,
                previous_fetched_at=None,
                current_fetched_at=CURRENT_FETCHED_AT,
            )

    def test_current_snapshot_fixture_is_valid_json_object(self):
        data = read_json(SNAPSHOTS_DIR / "0050_current_snapshot.json")
        encoded = json.dumps(data, sort_keys=True)
        self.assertIsInstance(json.loads(encoded), dict)

    def forbidden_files(self) -> set[Path]:
        return {
            path.relative_to(REPO_ROOT)
            for path in REPO_ROOT.rglob("*")
            if path.is_file()
            and (path.name.startswith("LAST-") or path.name.startswith("latest-"))
            and ".git" not in path.parts
        }


if __name__ == "__main__":
    unittest.main()
