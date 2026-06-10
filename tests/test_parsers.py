import inspect
import json
import os
import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import radar.parsers as parsers_module
from radar.parsers import (
    parse_codex_changelog_fixture,
    parse_github_releases_api_fixture,
    parse_json_items_fixture,
    parse_simple_html_release_fixture,
    parse_simple_text_release_fixture,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "examples" / "fixtures"


def _load_json_fixture() -> dict:
    return json.loads((FIXTURES_DIR / "0040_github_releases_fixture.json").read_text())


def _load_github_releases_api_fixture() -> list:
    return json.loads(
        (FIXTURES_DIR / "0150_github_releases_api_fixture.json").read_text()
    )


def _load_codex_changelog_fixture() -> str:
    return (FIXTURES_DIR / "0160_codex_changelog_fixture.md").read_text(
        encoding="utf-8"
    )


def _load_html_fixture() -> str:
    return (FIXTURES_DIR / "0040_codex_changelog_fixture.html").read_text(encoding="utf-8")


def _load_text_fixture() -> str:
    return (FIXTURES_DIR / "0040_api_deprecations_fixture.txt").read_text(encoding="utf-8")


class ParserTests(unittest.TestCase):
    def assert_items_have_ids_and_hashes(self, items):
        for item in items:
            self.assertTrue(item.item_id)
            self.assertTrue(item.content_hash)

    def assert_items_sorted(self, items):
        keys = [(item.published_at, item.title, item.item_id) for item in items]
        self.assertEqual(keys, sorted(keys))

    def test_json_fixture_produces_items(self):
        items = parse_json_items_fixture(
            "offline-github-releases-fixture",
            "github",
            _load_json_fixture(),
        )
        self.assertEqual(len(items), 2)
        self.assertEqual({item.category for item in items}, {"codex_cli"})
        self.assert_items_have_ids_and_hashes(items)

    def test_github_releases_api_fixture_produces_unique_items(self):
        items = parse_github_releases_api_fixture(
            "github_codex_releases",
            "github",
            _load_github_releases_api_fixture(),
        )
        self.assertEqual(len(items), 3)
        self.assertEqual({item.category for item in items}, {"codex_cli"})
        self.assertEqual({item.severity for item in items}, {"info", "low"})
        self.assertIn("Codex CLI v0.140.0", {item.title for item in items})
        self.assertIn("v0.139.0-beta.1", {item.title for item in items})
        self.assert_items_have_ids_and_hashes(items)

    def test_github_releases_api_parser_handles_empty_list(self):
        self.assertEqual(
            parse_github_releases_api_fixture("github_codex_releases", "github", []),
            [],
        )

    def test_github_releases_api_parser_accepts_releases_mapping(self):
        items = parse_github_releases_api_fixture(
            "github_codex_releases",
            "github",
            {"releases": _load_github_releases_api_fixture()},
        )
        self.assertEqual(len(items), 3)

    def test_github_releases_api_parser_handles_missing_name_and_null_body(self):
        items = parse_github_releases_api_fixture(
            "github_codex_releases",
            "github",
            _load_github_releases_api_fixture(),
        )
        prerelease = next(item for item in items if item.title == "v0.139.0-beta.1")
        self.assertIn("No release body provided", prerelease.evidence)
        self.assertIn("prerelease=true", prerelease.evidence)

    def test_github_releases_api_parser_deduplicates_by_stable_release_key(self):
        items = parse_github_releases_api_fixture(
            "github_codex_releases",
            "github",
            _load_github_releases_api_fixture(),
        )
        release = next(item for item in items if item.title == "Codex CLI v0.140.0")
        self.assertIn("github_release_id=140", release.evidence)
        self.assertNotIn("duplicate older copy", release.title)
        self.assertNotIn("Older duplicate fixture entry", release.evidence)

    def test_github_releases_api_parser_rejects_invalid_dates(self):
        fixture = [
            {
                "id": 1,
                "tag_name": "v0.invalid",
                "published_at": "not-a-date",
                "draft": False,
                "prerelease": False,
            }
        ]
        with self.assertRaisesRegex(ValueError, "published_at must be an ISO timestamp"):
            parse_github_releases_api_fixture("github_codex_releases", "github", fixture)

    def test_codex_changelog_fixture_produces_items(self):
        items = parse_codex_changelog_fixture(
            "openai_codex_changelog",
            "openai",
            _load_codex_changelog_fixture(),
        )
        self.assertEqual(len(items), 4)
        self.assertEqual(
            {item.category for item in items},
            {"codex_agents_md", "codex_cli", "codex_general", "codex_windows"},
        )
        self.assert_items_have_ids_and_hashes(items)

    def test_codex_changelog_parser_merges_duplicate_sections(self):
        items = parse_codex_changelog_fixture(
            "openai_codex_changelog",
            "openai",
            _load_codex_changelog_fixture(),
        )
        cli_item = next(item for item in items if item.category == "codex_cli")
        self.assertIn("Added deterministic release radar fixture support", cli_item.evidence)
        self.assertIn("Tightened fetch safety warnings", cli_item.evidence)
        self.assertEqual(cli_item.published_at, "2026-06-10T00:00:00Z")

    def test_codex_changelog_parser_handles_version_without_date(self):
        items = parse_codex_changelog_fixture(
            "openai_codex_changelog",
            "openai",
            _load_codex_changelog_fixture(),
        )
        undated = next(item for item in items if item.title == "Codex 0.138.0 - General")
        self.assertEqual(undated.published_at, "undated")
        self.assertIn("date=missing", undated.evidence)

    def test_codex_changelog_parser_handles_empty_changelog(self):
        self.assertEqual(
            parse_codex_changelog_fixture("openai_codex_changelog", "openai", ""),
            [],
        )

    def test_codex_changelog_parser_decodes_bytes(self):
        items = parse_codex_changelog_fixture(
            "openai_codex_changelog",
            "openai",
            _load_codex_changelog_fixture().encode("utf-8"),
        )
        self.assertEqual(len(items), 4)

    def test_codex_changelog_parser_rejects_bad_encoding(self):
        with self.assertRaisesRegex(ValueError, "encoding is invalid"):
            parse_codex_changelog_fixture(
                "openai_codex_changelog",
                "openai",
                b"\xff",
            )

    def test_codex_changelog_parser_rejects_too_long_content(self):
        with self.assertRaisesRegex(ValueError, "too long"):
            parse_codex_changelog_fixture(
                "openai_codex_changelog",
                "openai",
                "## v0.1.0\n- change",
                max_chars=5,
            )

    def test_codex_changelog_parser_rejects_invalid_heading_date(self):
        with self.assertRaisesRegex(ValueError, "invalid date"):
            parse_codex_changelog_fixture(
                "openai_codex_changelog",
                "openai",
                "## v0.1.0 - 2026-13-99\n- Broken fixture date.",
            )

    def test_html_fixture_produces_three_items(self):
        items = parse_simple_html_release_fixture(
            "offline-codex-changelog-fixture",
            "openai_codex",
            _load_html_fixture(),
        )
        self.assertEqual(len(items), 3)
        self.assertEqual(
            {item.category for item in items},
            {"codex_agents_md", "codex_cli", "codex_windows"},
        )
        self.assertEqual({item.severity for item in items}, {"high", "info", "medium"})
        self.assert_items_have_ids_and_hashes(items)

    def test_text_fixture_produces_two_items(self):
        items = parse_simple_text_release_fixture(
            "offline-api-deprecations-fixture",
            "openai_api",
            _load_text_fixture(),
        )
        self.assertEqual(len(items), 2)
        self.assertEqual({item.category for item in items}, {"api_platform", "deprecation"})
        self.assertIn("high", {item.severity for item in items})
        self.assert_items_have_ids_and_hashes(items)

    def test_json_parser_requires_mandatory_fields(self):
        broken_fixture = {
            "items": [
                {
                    "natural_key": "missing-title",
                    "category": "codex_cli",
                    "severity": "medium",
                    "published_at": "2026-06-08T00:00:00Z",
                    "url": "https://example.invalid/missing-title",
                    "evidence": "Offline fixture with a missing title.",
                    "first_seen": "2026-06-09",
                    "confidence": 0.9,
                }
            ]
        }
        with self.assertRaisesRegex(ValueError, r"items\[0\]\.title is required"):
            parse_json_items_fixture("source", "provider", broken_fixture)

    def test_parser_outputs_are_sorted_deterministically(self):
        json_items = parse_json_items_fixture(
            "offline-github-releases-fixture",
            "github",
            _load_json_fixture(),
        )
        html_items = parse_simple_html_release_fixture(
            "offline-codex-changelog-fixture",
            "openai_codex",
            _load_html_fixture(),
        )
        text_items = parse_simple_text_release_fixture(
            "offline-api-deprecations-fixture",
            "openai_api",
            _load_text_fixture(),
        )
        github_release_api_items = parse_github_releases_api_fixture(
            "github_codex_releases",
            "github",
            _load_github_releases_api_fixture(),
        )
        codex_changelog_items = parse_codex_changelog_fixture(
            "openai_codex_changelog",
            "openai",
            _load_codex_changelog_fixture(),
        )
        self.assert_items_sorted(json_items)
        self.assert_items_sorted(html_items)
        self.assert_items_sorted(text_items)
        self.assert_items_sorted(github_release_api_items)
        self.assert_items_sorted(codex_changelog_items)
        self.assertEqual(json_items[0].title, "Codex CLI v0.138.0 fixture release")

    def test_parsers_do_not_create_files(self):
        json_fixture = _load_json_fixture()
        html_fixture = _load_html_fixture()
        text_fixture = _load_text_fixture()
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                before = sorted(Path(temp_dir).iterdir())
                parse_json_items_fixture("json-source", "provider", json_fixture)
                parse_github_releases_api_fixture(
                    "github-release-source",
                    "github",
                    _load_github_releases_api_fixture(),
                )
                parse_codex_changelog_fixture(
                    "codex-changelog-source",
                    "openai",
                    _load_codex_changelog_fixture(),
                )
                parse_simple_html_release_fixture("html-source", "provider", html_fixture)
                parse_simple_text_release_fixture("text-source", "provider", text_fixture)
                after = sorted(Path(temp_dir).iterdir())
            finally:
                os.chdir(original_cwd)
        self.assertEqual(before, after)

    def test_parsers_do_not_use_network_modules_or_calls(self):
        source = inspect.getsource(parsers_module)
        self.assertNotIn("requests", source)
        self.assertNotIn("urllib", source)
        self.assertNotIn("http.client", source)

        json_fixture = _load_json_fixture()
        html_fixture = _load_html_fixture()
        text_fixture = _load_text_fixture()
        with patch.object(socket, "create_connection", side_effect=AssertionError("network")):
            parse_json_items_fixture("json-source", "provider", json_fixture)
            parse_github_releases_api_fixture(
                "github-release-source",
                "github",
                _load_github_releases_api_fixture(),
            )
            parse_codex_changelog_fixture(
                "codex-changelog-source",
                "openai",
                _load_codex_changelog_fixture(),
            )
            parse_simple_html_release_fixture("html-source", "provider", html_fixture)
            parse_simple_text_release_fixture("text-source", "provider", text_fixture)


if __name__ == "__main__":
    unittest.main()
