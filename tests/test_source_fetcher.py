import inspect
import tempfile
import unittest
from pathlib import Path
from urllib.error import URLError

import radar.cli as cli
import radar.source_fetcher as source_fetcher
from radar.json_utils import read_json
from radar.source_fetcher import (
    FetchedSourceContent,
    fetched_sources_to_dict,
    fetch_source_content,
    fetch_sources_content,
    summarize_fetched_sources,
)
from radar.source_registry import SourceDefinition


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "examples" / "fixtures"
SAMPLE_RESULTS_PATH = FIXTURES_DIR / "0130_fetcher_sample_results.json"
EXPECTED_SUMMARY_PATH = FIXTURES_DIR / "0130_fetcher_expected_summary.json"


class SourceFetcherTests(unittest.TestCase):
    def test_fetched_source_content_converts_to_dict(self):
        result = self.result("source_ok", ok=True, status_code=200)

        self.assertEqual(
            result.to_dict(),
            {
                "source_id": "source_ok",
                "url": "https://example.invalid/source_ok",
                "ok": True,
                "status_code": 200,
                "final_url": "https://example.invalid/source_ok",
                "content_type": "text/plain",
                "content_length": 5,
                "body_sample": "hello",
                "truncated": False,
                "error": None,
            },
        )

    def test_fetch_single_source_ok_with_mock_response(self):
        response = FakeResponse(
            b"hello world",
            url="https://example.invalid/source_ok",
            headers={"content-type": "text/plain", "content-length": "11"},
        )

        with unittest.mock.patch("radar.source_fetcher.urlopen", return_value=response):
            result = fetch_source_content(self.source("source_ok"), timeout_seconds=2.0)

        self.assertTrue(result.ok)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.content_type, "text/plain")
        self.assertEqual(result.content_length, 11)
        self.assertEqual(result.body_sample, "hello world")
        self.assertFalse(result.truncated)

    def test_fetch_single_source_error_with_mock_exception(self):
        with unittest.mock.patch(
            "radar.source_fetcher.urlopen",
            side_effect=URLError("simulated offline"),
        ):
            result = fetch_source_content(self.source("source_failed"), timeout_seconds=2.0)

        self.assertFalse(result.ok)
        self.assertIsNone(result.status_code)
        self.assertIsNone(result.body_sample)
        self.assertIn("URLError", result.error)

    def test_max_bytes_limits_body_sample(self):
        response = FakeResponse(
            b"abcdef",
            headers={"content-type": "text/plain", "content-length": "6"},
        )

        with unittest.mock.patch("radar.source_fetcher.urlopen", return_value=response):
            result = fetch_source_content(
                self.source("source_limited"),
                timeout_seconds=2.0,
                max_bytes=3,
            )

        self.assertEqual(result.body_sample, "abc")
        self.assertEqual(len(result.body_sample), 3)

    def test_truncated_true_when_content_exceeds_max_bytes(self):
        response = FakeResponse(
            b"abcdef",
            headers={"content-type": "text/plain", "content-length": "6"},
        )

        with unittest.mock.patch("radar.source_fetcher.urlopen", return_value=response):
            result = fetch_source_content(
                self.source("source_truncated"),
                timeout_seconds=2.0,
                max_bytes=3,
            )

        self.assertTrue(result.truncated)

    def test_disabled_source_returns_disabled_result_without_network(self):
        with unittest.mock.patch("radar.source_fetcher.urlopen") as mocked:
            result = fetch_source_content(self.source("source_disabled", live=False))

        mocked.assert_not_called()
        self.assertFalse(result.ok)
        self.assertEqual(result.error, "live_check_disabled")
        self.assertIsNone(result.body_sample)

    def test_fetch_sources_content_does_not_crash_when_one_source_fails(self):
        sources = [
            self.source("source_b"),
            self.source("source_a"),
        ]

        def fake_fetch(source, timeout_seconds=None, max_bytes=4096):
            if source.source_id == "source_a":
                raise RuntimeError("simulated source failure")
            return self.result(source.source_id, ok=True, status_code=200)

        with unittest.mock.patch(
            "radar.source_fetcher.fetch_source_content",
            side_effect=fake_fetch,
        ):
            results = fetch_sources_content(sources, timeout_seconds=2.0)

        errors = {result.source_id: result.error for result in results}
        self.assertEqual(errors["source_a"], "RuntimeError: simulated source failure")
        self.assertIsNone(errors["source_b"])

    def test_fetch_sources_content_sorts_results_by_source_id(self):
        sources = [
            self.source("source_c"),
            self.source("source_a"),
            self.source("source_b"),
        ]

        def fake_fetch(source, timeout_seconds=None, max_bytes=4096):
            return self.result(source.source_id, ok=True, status_code=200)

        with unittest.mock.patch(
            "radar.source_fetcher.fetch_source_content",
            side_effect=fake_fetch,
        ):
            results = fetch_sources_content(sources, timeout_seconds=2.0)

        self.assertEqual(
            [result.source_id for result in results],
            ["source_a", "source_b", "source_c"],
        )

    def test_summarize_fetched_sources_counts_core_outcomes(self):
        summary = summarize_fetched_sources(self.sample_results())

        self.assertEqual(summary["total"], 4)
        self.assertEqual(summary["ok"], 2)
        self.assertEqual(summary["failed"], 2)
        self.assertEqual(summary["disabled"], 1)
        self.assertEqual(summary["truncated"], 1)

    def test_fetched_sources_to_dict_is_deterministic(self):
        results = list(reversed(self.sample_results()))
        serialized = fetched_sources_to_dict(results)

        self.assertEqual(
            [result["source_id"] for result in serialized["results"]],
            sorted(result.source_id for result in results),
        )
        self.assertEqual(serialized, fetched_sources_to_dict(results))

    def test_fixture_sample_results_match_expected_summary(self):
        expected = read_json(EXPECTED_SUMMARY_PATH)
        serialized = fetched_sources_to_dict(self.fixture_results())

        self.assertEqual(serialized["summary"], expected)

    def test_cli_fetch_sources_with_mock_writes_results_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            with unittest.mock.patch.object(
                cli,
                "fetch_sources_content",
                return_value=[self.result("source_ok", ok=True, status_code=200)],
            ):
                result = cli.run_fetch_sources(
                    str(REPO_ROOT / "config" / "sources" / "openai_sources.json"),
                    str(output_dir),
                    timeout_seconds=1.0,
                    max_sources=1,
                    max_bytes=16,
                )

            self.assertEqual(set(result), {"results_json", "summary"})
            self.assertTrue((output_dir / cli.FETCH_SOURCES_RESULTS_FILENAME).is_file())
            self.assertTrue((output_dir / cli.FETCH_SOURCES_SUMMARY_FILENAME).is_file())
            summary = (output_dir / cli.FETCH_SOURCES_SUMMARY_FILENAME).read_text(
                encoding="utf-8"
            )
            self.assertIn("AI Release Radar source fetch completed", summary)
            self.assertIn("Parsing: not performed", summary)
            self.assertIn("Snapshot: not created", summary)

    def test_cli_fetch_sources_rejects_output_inside_repo(self):
        with self.assertRaisesRegex(ValueError, "outside repository"):
            cli.run_fetch_sources(
                str(REPO_ROOT / "config" / "sources" / "openai_sources.json"),
                str(REPO_ROOT / "tmp_fetch_sources_output"),
                timeout_seconds=1.0,
                max_sources=1,
                max_bytes=16,
            )

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

    def test_source_fetcher_does_not_import_parser_or_snapshot_models(self):
        source = inspect.getsource(source_fetcher)
        self.assertNotIn("radar.parsers", source)
        self.assertNotIn("parse_json_items_fixture", source)
        self.assertNotIn("SourceSnapshot", source)
        self.assertNotIn("Item", source)

    def sample_results(self):
        return [
            self.result("source_ok", ok=True, status_code=200),
            self.result(
                "source_failed",
                ok=False,
                status_code=503,
                error="unexpected_status:503",
            ),
            self.result("source_disabled", ok=False, status_code=None, error="live_check_disabled"),
            self.result("source_truncated", ok=True, status_code=200, truncated=True),
        ]

    def fixture_results(self):
        fixture = read_json(SAMPLE_RESULTS_PATH)
        return [FetchedSourceContent(**result) for result in fixture["results"]]

    def source(
        self,
        source_id: str,
        *,
        live: bool = True,
        expected_status_codes: list[int] | None = None,
    ) -> SourceDefinition:
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
            expected_status_codes=expected_status_codes or [200],
            live_check_enabled=live,
        )

    def result(
        self,
        source_id: str,
        *,
        ok: bool,
        status_code: int | None,
        error: str | None = None,
        truncated: bool = False,
    ) -> FetchedSourceContent:
        return FetchedSourceContent(
            source_id=source_id,
            url=f"https://example.invalid/{source_id}",
            ok=ok,
            status_code=status_code,
            final_url=(
                f"https://example.invalid/{source_id}" if status_code is not None else None
            ),
            content_type="text/plain" if status_code is not None else None,
            content_length=5 if status_code is not None else None,
            body_sample="hello" if status_code is not None else None,
            truncated=truncated,
            error=error,
        )


class FakeResponse:
    def __init__(
        self,
        body: bytes,
        *,
        status_code: int = 200,
        url: str = "https://example.invalid/source",
        headers: dict[str, str] | None = None,
    ):
        self._body = body
        self._status_code = status_code
        self._url = url
        self.headers = headers or {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self, size: int = -1) -> bytes:
        if size < 0:
            return self._body
        return self._body[:size]

    def getcode(self) -> int:
        return self._status_code

    def geturl(self) -> str:
        return self._url


if __name__ == "__main__":
    unittest.main()
