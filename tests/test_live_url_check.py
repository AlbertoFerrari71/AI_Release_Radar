import os
import unittest
from pathlib import Path
from unittest.mock import patch

from radar.json_utils import read_json
from radar.live_url_check import (
    check_sources_live,
    summarize_url_verification_results,
    verification_results_to_dict,
)
from radar.source_registry import SourceDefinition, load_source_registry_file
from radar.url_verifier import UrlVerificationResult


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "examples" / "fixtures"
CONFIG_PATH = REPO_ROOT / "config" / "sources" / "openai_sources.json"
SAMPLE_RESULTS_PATH = FIXTURES_DIR / "0110_live_url_check_sample_results.json"
EXPECTED_PATH = FIXTURES_DIR / "0110_live_url_check_expected.json"


class LiveUrlCheckTests(unittest.TestCase):
    def test_summarize_counts_ok_failed_and_total(self):
        summary = summarize_url_verification_results(self.sample_results())
        self.assertEqual(summary["total"], 4)
        self.assertEqual(summary["ok"], 2)
        self.assertEqual(summary["failed"], 2)

    def test_verification_results_to_dict_is_deterministic(self):
        results = list(reversed(self.sample_results()))
        serialized = verification_results_to_dict(results)
        source_ids = [result["source_id"] for result in serialized["results"]]
        self.assertEqual(source_ids, sorted(source_ids))
        self.assertEqual(serialized, verification_results_to_dict(results))

    def test_check_sources_live_uses_mock_and_handles_mixed_results(self):
        sources = [
            self.source("source_c"),
            self.source("source_a"),
            self.source("source_b"),
        ]

        def fake_verify(source, timeout_seconds):
            if source.source_id == "source_b":
                return UrlVerificationResult(
                    source_id=source.source_id,
                    url=source.url,
                    ok=False,
                    status_code=503,
                    final_url=source.url,
                    error="http_error:503",
                )
            return UrlVerificationResult(
                source_id=source.source_id,
                url=source.url,
                ok=True,
                status_code=200,
                final_url=source.url,
                error=None,
            )

        with patch("radar.live_url_check.verify_url_live", side_effect=fake_verify):
            results = check_sources_live(sources, timeout_seconds=2.0)

        self.assertEqual([result.source_id for result in results], ["source_a", "source_b", "source_c"])
        self.assertEqual(summarize_url_verification_results(results)["failed"], 1)

    def test_single_source_exception_does_not_block_others(self):
        sources = [self.source("source_a"), self.source("source_b")]

        def fake_verify(source, timeout_seconds):
            if source.source_id == "source_a":
                raise RuntimeError("simulated failure")
            return UrlVerificationResult(
                source_id=source.source_id,
                url=source.url,
                ok=True,
                status_code=200,
                final_url=source.url,
                error=None,
            )

        with patch("radar.live_url_check.verify_url_live", side_effect=fake_verify):
            results = check_sources_live(sources, timeout_seconds=2.0)

        self.assertEqual(len(results), 2)
        errors = {result.source_id: result.error for result in results}
        self.assertEqual(errors["source_a"], "RuntimeError: simulated failure")
        self.assertIsNone(errors["source_b"])

    def test_max_sources_limits_checked_sources(self):
        sources = [self.source("source_c"), self.source("source_b"), self.source("source_a")]

        def fake_verify(source, timeout_seconds):
            return UrlVerificationResult(
                source_id=source.source_id,
                url=source.url,
                ok=True,
                status_code=200,
                final_url=source.url,
                error=None,
            )

        with patch("radar.live_url_check.verify_url_live", side_effect=fake_verify) as mocked:
            results = check_sources_live(sources, timeout_seconds=2.0, max_sources=2)

        self.assertEqual(mocked.call_count, 2)
        self.assertEqual([result.source_id for result in results], ["source_b", "source_c"])

    def test_fixture_sample_results_match_expected_summary(self):
        expected = read_json(EXPECTED_PATH)
        serialized = verification_results_to_dict(self.sample_results())
        self.assertEqual(serialized["summary"], expected["summary"])

    def test_no_last_or_latest_files_exist(self):
        forbidden = [
            path
            for path in REPO_ROOT.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and "__pycache__" not in path.parts
            and (path.name.startswith("LAST-") or path.name.startswith("latest-"))
        ]
        self.assertEqual(forbidden, [])

    @unittest.skipUnless(
        os.environ.get("AI_RELEASE_RADAR_RUN_LIVE_TESTS") == "1",
        "live URL tests require AI_RELEASE_RADAR_RUN_LIVE_TESTS=1",
    )
    def test_live_check_sources_is_opt_in(self):
        sources = load_source_registry_file(str(CONFIG_PATH))
        results = check_sources_live(sources, timeout_seconds=8.0, max_sources=2)
        self.assertLessEqual(len(results), 2)
        for result in results:
            self.assertTrue(result.url.startswith("https://"))
            self.assertIsInstance(result.ok, bool)

    def sample_results(self):
        fixture = read_json(SAMPLE_RESULTS_PATH)
        return [UrlVerificationResult(**result) for result in fixture["results"]]

    def source(self, source_id: str) -> SourceDefinition:
        return SourceDefinition(
            source_id=source_id,
            provider="openai",
            name=source_id.replace("_", " ").title(),
            url=f"https://example.invalid/{source_id}",
            source_type="official_docs",
            priority=1,
            reliability="primary",
            machine_readable=False,
            category_hints=["codex_cli"],
            verification_status="verified_url_format",
            notes="Offline test source.",
        )


if __name__ == "__main__":
    unittest.main()
