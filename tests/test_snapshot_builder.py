import json
import unittest
from pathlib import Path

from radar.hash_utils import stable_sha256_text
from radar.json_utils import read_json
from radar.models import SourceSnapshot
from radar.parsers import (
    parse_json_items_fixture,
    parse_simple_html_release_fixture,
    parse_simple_text_release_fixture,
)
from radar.snapshot_builder import build_source_snapshot_from_items


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "examples" / "fixtures"
SNAPSHOTS_DIR = REPO_ROOT / "examples" / "snapshots"


class SnapshotBuilderTests(unittest.TestCase):
    def github_items(self):
        data = read_json(FIXTURES_DIR / "0040_github_releases_fixture.json")
        return parse_json_items_fixture("offline-github-releases-fixture", "github", data)

    def test_build_snapshot_from_items(self):
        items = list(reversed(self.github_items()))
        snapshot = build_source_snapshot_from_items(
            source_id="offline-github-releases-fixture",
            provider="github",
            fetched_at="2026-06-09T12:05:00Z",
            fetch_status="offline_fixture",
            http_status=None,
            items=items,
            page_hash="page-hash",
        )
        self.assertEqual(snapshot.source_id, "offline-github-releases-fixture")
        self.assertEqual(snapshot.provider, "github")
        self.assertEqual(len(snapshot.items), 2)

    def test_snapshot_metadata_for_offline_fixture(self):
        snapshot = build_source_snapshot_from_items(
            source_id="offline-github-releases-fixture",
            provider="github",
            fetched_at="2026-06-09T12:05:00Z",
            fetch_status="offline_fixture",
            http_status=None,
            items=self.github_items(),
        )
        self.assertEqual(snapshot.schema_version, 1)
        self.assertEqual(snapshot.fetch_status, "offline_fixture")
        self.assertIsNone(snapshot.http_status)

    def test_items_are_sorted_deterministically(self):
        snapshot = build_source_snapshot_from_items(
            source_id="offline-github-releases-fixture",
            provider="github",
            fetched_at="2026-06-09T12:05:00Z",
            fetch_status="offline_fixture",
            http_status=None,
            items=list(reversed(self.github_items())),
        )
        keys = [(item.published_at, item.title, item.item_id) for item in snapshot.items]
        self.assertEqual(keys, sorted(keys))

    def test_snapshot_serializes_and_deserializes(self):
        snapshot = build_source_snapshot_from_items(
            source_id="offline-github-releases-fixture",
            provider="github",
            fetched_at="2026-06-09T12:05:00Z",
            fetch_status="offline_fixture",
            http_status=None,
            items=self.github_items(),
            page_hash="page-hash",
        )
        encoded = json.dumps(snapshot.to_dict(), sort_keys=True)
        decoded = SourceSnapshot.from_dict(json.loads(encoded))
        self.assertEqual(decoded, snapshot)

    def test_expected_snapshot_fixtures_match_parsers(self):
        html_text = (FIXTURES_DIR / "0040_codex_changelog_fixture.html").read_text(
            encoding="utf-8"
        )
        html_items = parse_simple_html_release_fixture(
            "offline-codex-changelog-fixture",
            "openai_codex",
            html_text,
        )
        self.assert_snapshot_matches(
            "0040_codex_changelog_snapshot.json",
            build_source_snapshot_from_items(
                source_id="offline-codex-changelog-fixture",
                provider="openai_codex",
                fetched_at="2026-06-09T12:00:00Z",
                fetch_status="offline_fixture",
                http_status=None,
                items=html_items,
                page_hash=stable_sha256_text(html_text),
            ),
        )

        json_data = read_json(FIXTURES_DIR / "0040_github_releases_fixture.json")
        json_items = parse_json_items_fixture(
            "offline-github-releases-fixture",
            "github",
            json_data,
        )
        self.assert_snapshot_matches(
            "0040_github_releases_snapshot.json",
            build_source_snapshot_from_items(
                source_id="offline-github-releases-fixture",
                provider="github",
                fetched_at="2026-06-09T12:05:00Z",
                fetch_status="offline_fixture",
                http_status=None,
                items=json_items,
                page_hash=stable_sha256_text(
                    json.dumps(json_data, ensure_ascii=False, sort_keys=True)
                ),
            ),
        )

        text = (FIXTURES_DIR / "0040_api_deprecations_fixture.txt").read_text(
            encoding="utf-8"
        )
        text_items = parse_simple_text_release_fixture(
            "offline-api-deprecations-fixture",
            "openai_api",
            text,
        )
        self.assert_snapshot_matches(
            "0040_api_deprecations_snapshot.json",
            build_source_snapshot_from_items(
                source_id="offline-api-deprecations-fixture",
                provider="openai_api",
                fetched_at="2026-06-09T12:10:00Z",
                fetch_status="offline_fixture",
                http_status=None,
                items=text_items,
                page_hash=stable_sha256_text(text),
            ),
        )

    def test_page_hash_difference_does_not_influence_items(self):
        items = self.github_items()
        snapshot_a = build_source_snapshot_from_items(
            source_id="offline-github-releases-fixture",
            provider="github",
            fetched_at="2026-06-09T12:05:00Z",
            fetch_status="offline_fixture",
            http_status=None,
            items=items,
            page_hash="page-a",
        )
        snapshot_b = build_source_snapshot_from_items(
            source_id="offline-github-releases-fixture",
            provider="github",
            fetched_at="2026-06-09T12:05:00Z",
            fetch_status="offline_fixture",
            http_status=None,
            items=items,
            page_hash="page-b",
        )
        self.assertNotEqual(snapshot_a.page_hash, snapshot_b.page_hash)
        self.assertEqual(
            [item.to_dict() for item in snapshot_a.items],
            [item.to_dict() for item in snapshot_b.items],
        )

    def assert_snapshot_matches(self, expected_file_name: str, actual_snapshot: SourceSnapshot):
        expected = SourceSnapshot.from_dict(read_json(SNAPSHOTS_DIR / expected_file_name))
        self.assertEqual(actual_snapshot, expected)


if __name__ == "__main__":
    unittest.main()
