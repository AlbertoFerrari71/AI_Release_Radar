import inspect
import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import radar.cli as cli
from radar.url_verifier import UrlVerificationResult


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "examples" / "fixtures"
EXPECTED_SUMMARY_PATH = FIXTURES_DIR / "0090_cli_expected_summary.txt"
EXPECTED_FULL_PATH = FIXTURES_DIR / "0090_cli_expected_full.md"
EXPECTED_COMPACT_PATH = FIXTURES_DIR / "0090_cli_expected_compact.md"


class CliTests(unittest.TestCase):
    def test_build_arg_parser_help_does_not_crash(self):
        parser = cli.build_arg_parser()
        self.assertIn("dry-run", parser.format_help())
        self.assertIn("check-urls", parser.format_help())
        stdout = io.StringIO()
        with redirect_stdout(stdout), self.assertRaises(SystemExit) as exc:
            parser.parse_args(["dry-run", "--help"])
        self.assertEqual(exc.exception.code, 0)
        self.assertIn("--output-dir", stdout.getvalue())

    def test_main_dry_run_returns_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                code = cli.main(["dry-run", "--output-dir", tmp])
            self.assertEqual(code, 0)
            self.assertIn("AI Release Radar dry-run completed", stdout.getvalue())

    def test_main_check_urls_with_mock_returns_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            with unittest.mock.patch.object(
                cli,
                "check_sources_live",
                return_value=[self.sample_url_result()],
            ):
                with redirect_stdout(stdout):
                    code = cli.main(
                        [
                            "check-urls",
                            "--registry",
                            str(REPO_ROOT / "config" / "sources" / "openai_sources.json"),
                            "--output-dir",
                            tmp,
                            "--max-sources",
                            "1",
                        ]
                    )
            self.assertEqual(code, 0)
            self.assertIn("AI Release Radar live URL check completed", stdout.getvalue())

    def test_dry_run_creates_full_compact_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            result = cli.run_dry_run(str(output_dir))
            self.assertEqual(
                set(result),
                {"full_report", "compact_report", "summary"},
            )
            self.assertTrue((output_dir / cli.FULL_REPORT_FILENAME).is_file())
            self.assertTrue((output_dir / cli.COMPACT_REPORT_FILENAME).is_file())
            self.assertTrue((output_dir / cli.SUMMARY_FILENAME).is_file())

    def test_check_urls_with_mock_writes_results_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            with unittest.mock.patch.object(
                cli,
                "check_sources_live",
                return_value=[self.sample_url_result()],
            ):
                result = cli.run_check_urls(
                    str(REPO_ROOT / "config" / "sources" / "openai_sources.json"),
                    str(output_dir),
                    timeout_seconds=1.0,
                    max_sources=1,
                )
            self.assertEqual(set(result), {"results_json", "summary"})
            self.assertTrue((output_dir / cli.CHECK_URLS_RESULTS_FILENAME).is_file())
            self.assertTrue((output_dir / cli.CHECK_URLS_SUMMARY_FILENAME).is_file())
            summary = (output_dir / cli.CHECK_URLS_SUMMARY_FILENAME).read_text(
                encoding="utf-8"
            )
            self.assertIn("Total: 1", summary)
            self.assertIn("Recommendation: registry_ok", summary)

    def test_full_report_matches_expected_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            cli.run_dry_run(str(output_dir))
            actual = (output_dir / cli.FULL_REPORT_FILENAME).read_text(encoding="utf-8")
            expected = EXPECTED_FULL_PATH.read_text(encoding="utf-8")
            self.assertEqual(actual, expected)

    def test_compact_report_matches_expected_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            cli.run_dry_run(str(output_dir))
            actual = (output_dir / cli.COMPACT_REPORT_FILENAME).read_text(encoding="utf-8")
            expected = EXPECTED_COMPACT_PATH.read_text(encoding="utf-8")
            self.assertEqual(actual, expected)

    def test_summary_normalized_matches_expected_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            cli.run_dry_run(str(output_dir))
            actual = (output_dir / cli.SUMMARY_FILENAME).read_text(encoding="utf-8")
            expected = EXPECTED_SUMMARY_PATH.read_text(encoding="utf-8")
            self.assertEqual(self.normalize_summary(actual, output_dir), expected)

    def test_compact_only_creates_only_compact_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            result = cli.run_dry_run(str(output_dir), full=False, compact=True)
            self.assertEqual(result["full_report"], "skipped")
            self.assertTrue((output_dir / cli.COMPACT_REPORT_FILENAME).is_file())
            self.assertTrue((output_dir / cli.SUMMARY_FILENAME).is_file())
            self.assertFalse((output_dir / cli.FULL_REPORT_FILENAME).exists())
            summary = (output_dir / cli.SUMMARY_FILENAME).read_text(encoding="utf-8")
            self.assertIn("Full report: skipped", summary)

    def test_full_only_creates_only_full_and_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            result = cli.run_dry_run(str(output_dir), full=True, compact=False)
            self.assertEqual(result["compact_report"], "skipped")
            self.assertTrue((output_dir / cli.FULL_REPORT_FILENAME).is_file())
            self.assertTrue((output_dir / cli.SUMMARY_FILENAME).is_file())
            self.assertFalse((output_dir / cli.COMPACT_REPORT_FILENAME).exists())
            summary = (output_dir / cli.SUMMARY_FILENAME).read_text(encoding="utf-8")
            self.assertIn("Compact report: skipped", summary)

    def test_compact_only_and_full_only_together_return_nonzero(self):
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = cli.main(
                    [
                        "dry-run",
                        "--output-dir",
                        tmp,
                        "--compact-only",
                        "--full-only",
                    ]
                )
            self.assertNotEqual(code, 0)
            self.assertIn("cannot be used together", stderr.getvalue())

    def test_output_dir_is_created_when_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "nested" / "out"
            self.assertFalse(output_dir.exists())
            cli.run_dry_run(str(output_dir))
            self.assertTrue(output_dir.is_dir())

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

    def test_dry_run_does_not_write_files_outside_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            output_dir = temp_root / "out"
            repo_before = self.repo_files()
            cli.run_dry_run(str(output_dir))
            repo_after = self.repo_files()
            self.assertEqual(repo_before, repo_after)

            created = {
                path.relative_to(temp_root).as_posix()
                for path in temp_root.rglob("*")
                if path.is_file()
            }
            self.assertEqual(
                created,
                {
                    f"out/{cli.FULL_REPORT_FILENAME}",
                    f"out/{cli.COMPACT_REPORT_FILENAME}",
                    f"out/{cli.SUMMARY_FILENAME}",
                },
            )

    def test_outputs_are_deterministic_on_two_runs(self):
        with tempfile.TemporaryDirectory() as tmp:
            first_dir = Path(tmp) / "first"
            second_dir = Path(tmp) / "second"
            cli.run_dry_run(str(first_dir))
            cli.run_dry_run(str(second_dir))
            self.assertEqual(
                (first_dir / cli.FULL_REPORT_FILENAME).read_text(encoding="utf-8"),
                (second_dir / cli.FULL_REPORT_FILENAME).read_text(encoding="utf-8"),
            )
            self.assertEqual(
                (first_dir / cli.COMPACT_REPORT_FILENAME).read_text(encoding="utf-8"),
                (second_dir / cli.COMPACT_REPORT_FILENAME).read_text(encoding="utf-8"),
            )
            first_summary = (first_dir / cli.SUMMARY_FILENAME).read_text(encoding="utf-8")
            second_summary = (second_dir / cli.SUMMARY_FILENAME).read_text(encoding="utf-8")
            self.assertEqual(
                self.normalize_summary(first_summary, first_dir),
                self.normalize_summary(second_summary, second_dir),
            )

    def test_cli_introduces_no_fetch_live_or_network_client(self):
        source = inspect.getsource(cli)
        for forbidden in (
            "requ" + "ests",
            "ur" + "llib",
            "ht" + "tpx",
            "aio" + "http",
            "url" + "open",
            "fet" + "ch(",
        ):
            self.assertNotIn(forbidden, source)

    def normalize_summary(self, text: str, output_dir: Path) -> str:
        return text.replace(str(output_dir.resolve()), "<OUTPUT_DIR>").replace("\\", "/")

    def repo_files(self) -> set[str]:
        return {
            str(path.relative_to(REPO_ROOT))
            for path in REPO_ROOT.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and "__pycache__" not in path.parts
        }

    def sample_url_result(self) -> UrlVerificationResult:
        return UrlVerificationResult(
            source_id="openai_codex_changelog",
            url="https://developers.openai.com/codex/changelog",
            ok=True,
            status_code=200,
            final_url="https://developers.openai.com/codex/changelog",
            error=None,
        )


if __name__ == "__main__":
    unittest.main()
