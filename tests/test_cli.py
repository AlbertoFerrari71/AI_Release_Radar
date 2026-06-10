import inspect
import io
import tempfile
import unittest
import unittest.mock
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import radar.cli as cli
from radar.json_utils import read_json, write_json
from radar.models import RunIndexEntry
from radar.run_index import append_run_index_entry
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
        self.assertIn("live-snapshot", parser.format_help())
        self.assertIn("real-run", parser.format_help())
        self.assertIn("daily-sim", parser.format_help())
        stdout = io.StringIO()
        with redirect_stdout(stdout), self.assertRaises(SystemExit) as exc:
            parser.parse_args(["dry-run", "--help"])
        self.assertEqual(exc.exception.code, 0)
        self.assertIn("--output-dir", stdout.getvalue())
        stdout = io.StringIO()
        with redirect_stdout(stdout), self.assertRaises(SystemExit) as exc:
            parser.parse_args(["live-snapshot", "--help"])
        self.assertEqual(exc.exception.code, 0)
        self.assertIn("--source-registry", stdout.getvalue())
        stdout = io.StringIO()
        with redirect_stdout(stdout), self.assertRaises(SystemExit) as exc:
            parser.parse_args(["real-run", "--help"])
        self.assertEqual(exc.exception.code, 0)
        self.assertIn("--project-map", stdout.getvalue())
        self.assertIn("--profile", stdout.getvalue())
        stdout = io.StringIO()
        with redirect_stdout(stdout), self.assertRaises(SystemExit) as exc:
            parser.parse_args(["daily-sim", "--help"])
        self.assertEqual(exc.exception.code, 0)
        self.assertIn("--output-root", stdout.getvalue())

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

    def test_main_live_snapshot_with_mock_returns_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            with unittest.mock.patch.object(
                cli,
                "run_live_snapshot",
                return_value={
                    "run_id": "0170-test",
                    "status": "success",
                    "source_count": 1,
                    "snapshot_count": 1,
                    "parsed_count": 1,
                    "skipped_count": 0,
                    "failed_count": 0,
                    "output_dir": tmp,
                    "run_summary_path": str(Path(tmp) / "0170-Live_Snapshot_Run_Summary.json"),
                    "run_index_entry_path": str(
                        Path(tmp) / "0170-Live_Snapshot_Run_Index_Entry.json"
                    ),
                    "runs_index_path": str(Path(tmp) / "runs_index.jsonl"),
                },
            ):
                with redirect_stdout(stdout):
                    code = cli.main(
                        [
                            "live-snapshot",
                            "--source-registry",
                            str(REPO_ROOT / "config" / "sources" / "openai_sources.json"),
                            "--output-dir",
                            tmp,
                            "--max-sources",
                            "1",
                        ]
                    )
            self.assertEqual(code, 0)
            self.assertIn("AI Release Radar live snapshot completed", stdout.getvalue())

    def test_main_real_run_with_mock_returns_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            with unittest.mock.patch.object(
                cli,
                "run_real_run",
                return_value={
                    "run_id": "0180-test",
                    "status": "ACTION_RECOMMENDED",
                    "source_count": 1,
                    "item_count": 1,
                    "new_count": 1,
                    "changed_count": 0,
                    "removed_count": 0,
                    "project_impact_count": 1,
                    "report_full": str(Path(tmp) / "0180-Report_Full.md"),
                    "report_compact": str(Path(tmp) / "0180-Report_Compact.md"),
                    "run_summary": str(Path(tmp) / "0180-Run_Summary.json"),
                    "runs_index": str(Path(tmp) / "runs_index.jsonl"),
                },
            ) as run_mock:
                with redirect_stdout(stdout):
                    code = cli.main(
                        [
                            "real-run",
                            "--source-registry",
                            str(REPO_ROOT / "config" / "sources" / "openai_sources.json"),
                            "--output-dir",
                            tmp,
                            "--max-sources",
                            "1",
                        ]
            )
            self.assertEqual(code, 0)
            self.assertIn("AI Release Radar real run completed", stdout.getvalue())
            self.assertEqual(
                run_mock.call_args.kwargs["max_bytes"],
                cli.DEFAULT_REAL_RUN_MAX_BYTES,
            )

    def test_main_real_run_manual_profile_with_mock_returns_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            with unittest.mock.patch.object(
                cli,
                "run_real_run",
                return_value={
                    "run_id": "0210-manual",
                    "status": "CHANGES_FOUND",
                    "source_count": 11,
                    "item_count": 10,
                    "new_count": 10,
                    "changed_count": 0,
                    "removed_count": 0,
                    "project_impact_count": 60,
                    "report_full": str(Path(tmp) / "0180-Report_Full.md"),
                    "report_compact": str(Path(tmp) / "0180-Report_Compact.md"),
                    "run_summary": str(Path(tmp) / "0180-Run_Summary.json"),
                    "runs_index": str(Path(tmp) / "runs_index.jsonl"),
                },
            ) as run_mock:
                with redirect_stdout(stdout):
                    code = cli.main(["real-run", "--profile", "manual", "--output-dir", tmp])

            self.assertEqual(code, 0)
            self.assertIn("AI Release Radar real run completed", stdout.getvalue())
            self.assertIn(cli.REAL_RUN_NEXT_STEP_RECOMMENDATION, stdout.getvalue())
            self.assertNotIn("0190) Review first real radar output", stdout.getvalue())
            self.assertEqual(run_mock.call_args.args[0], str(cli.DEFAULT_SOURCE_REGISTRY_PATH))
            self.assertEqual(run_mock.call_args.kwargs["timeout_seconds"], 30.0)
            self.assertEqual(run_mock.call_args.kwargs["max_sources"], 11)
            self.assertEqual(run_mock.call_args.kwargs["max_bytes"], 2_000_000)

    def test_run_daily_sim_with_mock_creates_dated_output_summary(self):
        with tempfile.TemporaryDirectory() as tmp:
            with unittest.mock.patch.object(
                cli,
                "run_real_run",
                return_value={
                    "run_id": "0180-daily-sim",
                    "status": "CHANGES_FOUND",
                    "source_count": 11,
                    "parsed_count": 1,
                    "item_count": 10,
                    "direct_action_count": 10,
                    "monitor_only_action_count": 50,
                    "unsupported_source_count": 10,
                    "report_full": str(Path(tmp) / "run" / "0180-Report_Full.md"),
                    "report_compact": str(Path(tmp) / "run" / "0180-Report_Compact.md"),
                    "run_summary": str(Path(tmp) / "run" / "0180-Run_Summary.json"),
                    "runs_index": str(Path(tmp) / "run" / "runs_index.jsonl"),
                },
            ) as run_mock:
                result = cli.run_daily_sim(
                    output_root=tmp,
                    stamp="20260610_120000",
                )

            self.assertEqual(result["status"], "CHANGES_FOUND")
            self.assertEqual(result["automation_gate_status"], "FAIL")
            self.assertIn("0320_0400_daily_sim_20260610_120000", result["output_dir"])
            self.assertTrue(Path(result["daily_sim_summary"]).is_file())
            self.assertTrue(Path(result["automation_gate_json"]).is_file())
            self.assertTrue(Path(result["automation_gate_markdown"]).is_file())
            self.assertTrue(Path(result["daily_quality_gate_v2_json"]).is_file())
            self.assertTrue(Path(result["action_triage_json"]).is_file())
            self.assertTrue(Path(result["prompt_suggestions_markdown"]).is_file())
            self.assertTrue(Path(result["hag_report_markdown"]).is_file())
            self.assertTrue(Path(result["dashboard_path"]).is_file())
            self.assertTrue(Path(result["supervised_action_loop_dry_run"]).is_file())
            self.assertEqual(run_mock.call_args.args[0], str(cli.DEFAULT_SOURCE_REGISTRY_PATH))
            self.assertIn(
                "0320_0400_daily_sim_20260610_120000",
                run_mock.call_args.args[1],
            )
            self.assertEqual(run_mock.call_args.kwargs["timeout_seconds"], 30.0)
            self.assertEqual(run_mock.call_args.kwargs["max_sources"], 11)
            self.assertEqual(run_mock.call_args.kwargs["max_bytes"], 2_000_000)

    def test_run_daily_sim_propagates_gate_warnings_and_manual_review_queue(self):
        with tempfile.TemporaryDirectory() as tmp:
            with unittest.mock.patch.object(
                cli,
                "run_real_run",
                side_effect=self.write_action_review_required_real_run,
            ):
                result = cli.run_daily_sim(
                    output_root=tmp,
                    stamp="20260610_130000",
                )

            self.assertEqual(result["automation_gate_status"], "ACTION_REVIEW_REQUIRED")
            self.assertEqual(result["scheduler_activated"], False)
            self.assertEqual(result["windows_task_created"], False)
            self.assertEqual(result["llm_called"], False)
            self.assertEqual(result["scheduler_readiness_recommendation"], "HOLD")
            self.assertGreater(result["manual_review_queue_count"], 0)
            self.assertTrue(Path(result["daily_sim_summary"]).is_file())
            self.assertTrue(Path(result["automation_gate_json"]).is_file())
            self.assertTrue(Path(result["automation_gate_markdown"]).is_file())
            gate = read_json(result["automation_gate_json"])
            self.assertEqual(gate["status"], "ACTION_REVIEW_REQUIRED")
            self.assertGreater(gate["metrics"]["manual_review_queue_count"], 0)
            self.assertTrue(
                any(
                    warning.startswith("low_source_coverage")
                    for warning in gate["warnings"]
                )
            )
            self.assertTrue(
                any(
                    entry["reason"] == "direct_actions_present"
                    for entry in gate["manual_review_queue"]
                )
            )
            summary = read_json(result["daily_sim_summary"])
            self.assertEqual(summary["manual_review_queue_count"], result["manual_review_queue_count"])
            self.assertEqual(
                summary["scheduler_readiness_recommendation"],
                "HOLD",
            )
            self.assertEqual(
                summary["daily_quality_gate_v2"]["overall_daily_review_status"],
                "ACTION_REVIEW_REQUIRED",
            )
            self.assertEqual(summary["action_triage_status"], "HOLD")
            self.assertIn("prompt_suggestions_count", summary)
            self.assertEqual(summary["auto_action_executed"], False)
            self.assertEqual(summary["other_repository_touched"], False)
            self.assertEqual(summary["email_sent"], False)

    def test_main_daily_sim_with_mock_returns_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            with unittest.mock.patch.object(
                cli,
                "run_daily_sim",
                return_value={
                    "status": "CHANGES_FOUND",
                    "automation_gate_status": "ACTION_REVIEW_REQUIRED",
                    "recommendation": "Manual review required before acting on direct actions; no auto-action.",
                    "output_dir": str(Path(tmp) / "run"),
                    "daily_sim_summary": str(
                        Path(tmp) / "run" / cli.DAILY_SIM_SUMMARY_FILENAME
                    ),
                    "automation_gate_markdown": str(
                        Path(tmp) / "run" / cli.DAILY_SIM_GATE_MARKDOWN_FILENAME
                    ),
                    "next_step": cli.DAILY_SIM_NEXT_STEP_RECOMMENDATION,
                    "automation_gate": {
                        "metrics": {
                            "manual_review_required_count": 0,
                        }
                    },
                    "real_run": {
                        "run_id": "0180-daily-sim",
                        "source_count": 11,
                        "parsed_count": 1,
                        "item_count": 10,
                        "direct_action_count": 10,
                        "monitor_only_action_count": 50,
                        "unsupported_source_count": 10,
                        "run_summary": str(Path(tmp) / "run" / "0180-Run_Summary.json"),
                    },
                },
            ):
                with redirect_stdout(stdout):
                    code = cli.main(["daily-sim", "--output-root", tmp])

            self.assertEqual(code, 0)
            self.assertIn("AI Release Radar daily simulation completed", stdout.getvalue())
            self.assertIn("No scheduler: confirmed", stdout.getvalue())

    def test_daily_sim_rejects_output_root_inside_repo(self):
        with self.assertRaisesRegex(ValueError, "outside repository"):
            cli.run_daily_sim(
                output_root=str(REPO_ROOT / "tmp_daily_sim_output"),
                stamp="20260610_120000",
            )

    def test_main_real_run_requires_source_registry_without_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                code = cli.main(["real-run", "--output-dir", tmp])

            self.assertNotEqual(code, 0)
            self.assertIn("--source-registry", stderr.getvalue())

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

    def write_action_review_required_real_run(self, source_registry, output_dir, **kwargs):
        target_dir = Path(output_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        result = {
            "run_id": "0180-daily-sim-action-review",
            "status": "CHANGES_FOUND",
            "output_dir": str(target_dir),
            "report_full": str(target_dir / "0180-Report_Full.md"),
            "report_compact": str(target_dir / "0180-Report_Compact.md"),
            "run_summary": str(target_dir / "0180-Run_Summary.json"),
            "run_index_entry": str(target_dir / "0180-Run_Index_Entry.json"),
            "runs_index": str(target_dir / "runs_index.jsonl"),
            "live_snapshot_status": "success",
            "source_count": 11,
            "parsed_count": 1,
            "skipped_count": 10,
            "failed_count": 0,
            "item_count": 10,
            "new_count": 10,
            "changed_count": 0,
            "removed_count": 0,
            "unchanged_count": 0,
            "project_impact_count": 60,
            "direct_action_count": 10,
            "monitor_only_action_count": 50,
            "no_action_count": 0,
            "unsupported_source_count": 9,
            "manual_review_required_count": 1,
            "report_scorecard_status": "PASS",
        }
        diagnostics = [
            {
                "source_id": "github_api_openai_codex_releases",
                "provider": "github",
                "source_type": "github_api",
                "manual_review_required": False,
                "diagnostic_status": "parsed",
                "fetch_status": "fetched",
                "http_status_code": 200,
                "parser_status": "parsed",
                "error_code": None,
                "item_count": 10,
                "recommended_follow_up": "use_parsed_items",
                "registry_recommended_follow_up": "use_parsed_items_after_gate",
                "coverage_priority": "P0",
                "scheduler_readiness": "ready",
                "error": None,
            },
            {
                "source_id": "openai_release_notes_hub",
                "provider": "openai",
                "source_type": "official_release_notes",
                "manual_review_required": True,
                "diagnostic_status": "manual_review_required",
                "fetch_status": "rejected",
                "http_status_code": 403,
                "parser_status": "fetch_failed",
                "error_code": "unexpected_status",
                "item_count": 0,
                "recommended_follow_up": "manual_review_source",
                "registry_recommended_follow_up": "manual_review_source",
                "coverage_priority": "P2",
                "scheduler_readiness": "hold",
                "error": "unexpected_status:403",
            },
            *[
                {
                    "source_id": f"unsupported_source_{index}",
                    "provider": "openai",
                    "source_type": "official_docs",
                    "manual_review_required": False,
                    "diagnostic_status": "fetched_but_unsupported",
                    "fetch_status": "fetched",
                    "http_status_code": 200,
                    "parser_status": "parser_skipped_unsupported_source",
                    "error_code": None,
                    "item_count": 0,
                    "recommended_follow_up": "keep_diagnostic_no_parser",
                    "registry_recommended_follow_up": "keep_diagnostic_no_parser",
                    "coverage_priority": "P3",
                    "scheduler_readiness": "hold",
                    "error": None,
                }
                for index in range(1, 10)
            ],
        ]
        Path(result["report_full"]).write_text("full report\n", encoding="utf-8")
        Path(result["report_compact"]).write_text("compact report\n", encoding="utf-8")
        entry = RunIndexEntry(
            run_id=str(result["run_id"]),
            step="0180",
            status=str(result["status"]),
            started_at="2026-06-10T13:00:00Z",
            finished_at="2026-06-10T13:00:00Z",
            duration_seconds=0.0,
            report_full=str(result["report_full"]),
            report_compact=str(result["report_compact"]),
            snapshot_dir=str(target_dir),
            notes="Daily sim CLI test fixture.",
            source_count=int(result["source_count"]),
            parsed_count=int(result["parsed_count"]),
            item_count=int(result["item_count"]),
            failed_count=int(result["failed_count"]),
            skipped_count=int(result["skipped_count"]),
            timestamp="2026-06-10T13:00:00Z",
        )
        write_json(result["run_index_entry"], entry)
        append_run_index_entry(result["runs_index"], entry)
        write_json(
            result["run_summary"],
            {
                "schema_version": 1,
                "result": result,
                "source_diagnostics": diagnostics,
                "report_scorecard": {"status": "PASS"},
            },
        )
        return result


if __name__ == "__main__":
    unittest.main()
