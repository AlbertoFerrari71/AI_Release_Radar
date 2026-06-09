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
    parse_json_items_fixture,
    parse_simple_html_release_fixture,
    parse_simple_text_release_fixture,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "examples" / "fixtures"


def _load_json_fixture() -> dict:
    return json.loads((FIXTURES_DIR / "0040_github_releases_fixture.json").read_text())


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
        self.assert_items_sorted(json_items)
        self.assert_items_sorted(html_items)
        self.assert_items_sorted(text_items)
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
            parse_simple_html_release_fixture("html-source", "provider", html_fixture)
            parse_simple_text_release_fixture("text-source", "provider", text_fixture)


if __name__ == "__main__":
    unittest.main()
