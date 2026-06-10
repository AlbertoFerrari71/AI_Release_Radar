import tempfile
import unittest
from pathlib import Path

from radar.automation_gate import (
    ACTION_REVIEW_REQUIRED,
    FAIL,
    PASS,
    PASS_WITH_WARNINGS,
    evaluate_automation_gate,
    render_automation_gate_markdown,
)
from radar.json_utils import write_json
from radar.models import RunIndexEntry
from radar.run_index import append_run_index_entry


REPO_ROOT = Path(__file__).resolve().parents[1]


class AutomationGateTests(unittest.TestCase):
    def test_gate_pass_when_outputs_coverage_and_scorecard_are_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = self.write_run_output(
                Path(tmp),
                result_overrides={
                    "source_count": 4,
                    "parsed_count": 4,
                    "unsupported_source_count": 0,
                    "no_action_count": 2,
                },
                diagnostics=[self.diagnostic("parsed") for _ in range(4)],
            )

            gate = evaluate_automation_gate(output_dir)

            self.assertEqual(gate.status, PASS)
            self.assertEqual(gate.failures, [])
            self.assertEqual(gate.warnings, [])
            self.assertIn("automation_gate_status: PASS", render_automation_gate_markdown(gate))

    def test_gate_pass_with_warnings_for_low_coverage(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = self.write_run_output(
                Path(tmp),
                result_overrides={
                    "source_count": 11,
                    "parsed_count": 1,
                    "unsupported_source_count": 10,
                },
                diagnostics=[
                    self.diagnostic("parsed"),
                    *[self.diagnostic("fetched_but_unsupported") for _ in range(10)],
                ],
            )

            gate = evaluate_automation_gate(output_dir)

            self.assertEqual(gate.status, PASS_WITH_WARNINGS)
            self.assertTrue(
                any(warning.startswith("low_source_coverage") for warning in gate.warnings)
            )
            self.assertTrue(
                any(warning.startswith("unsupported_source_count_high") for warning in gate.warnings)
            )

    def test_gate_fail_when_no_source_is_parsed(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = self.write_run_output(
                Path(tmp),
                result_overrides={
                    "status": "NO_PARSED_ITEMS",
                    "source_count": 2,
                    "parsed_count": 0,
                    "item_count": 0,
                    "unsupported_source_count": 2,
                },
                diagnostics=[self.diagnostic("fetched_but_unsupported") for _ in range(2)],
            )

            gate = evaluate_automation_gate(output_dir)

            self.assertEqual(gate.status, FAIL)
            self.assertIn("parsed_count_zero", gate.failures)

    def test_gate_fail_when_compact_report_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = self.write_run_output(
                Path(tmp),
                result_overrides={"source_count": 2, "parsed_count": 2},
                diagnostics=[self.diagnostic("parsed") for _ in range(2)],
                missing={"report_compact"},
            )

            gate = evaluate_automation_gate(output_dir)

            self.assertEqual(gate.status, FAIL)
            self.assertIn("report_compact_missing", gate.failures)

    def test_gate_warns_when_manual_review_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = self.write_run_output(
                Path(tmp),
                result_overrides={
                    "source_count": 4,
                    "parsed_count": 3,
                    "manual_review_required_count": 1,
                },
                diagnostics=[
                    self.diagnostic("parsed"),
                    self.diagnostic("parsed"),
                    self.diagnostic("parsed"),
                    self.diagnostic("manual_review_required", manual=True, http_status_code=403),
                ],
            )

            gate = evaluate_automation_gate(output_dir)

            self.assertEqual(gate.status, PASS_WITH_WARNINGS)
            self.assertIn("manual_review_required_present: count=1", gate.warnings)

    def test_gate_requires_action_review_when_direct_actions_exist(self):
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = self.write_run_output(
                Path(tmp),
                result_overrides={
                    "source_count": 4,
                    "parsed_count": 4,
                    "direct_action_count": 1,
                    "monitor_only_action_count": 0,
                    "no_action_count": 1,
                },
                diagnostics=[self.diagnostic("parsed") for _ in range(4)],
            )

            gate = evaluate_automation_gate(output_dir)

            self.assertEqual(gate.status, ACTION_REVIEW_REQUIRED)
            self.assertEqual(gate.failures, [])

    def write_run_output(
        self,
        root: Path,
        *,
        result_overrides: dict[str, object] | None = None,
        diagnostics: list[dict[str, object]] | None = None,
        missing: set[str] | None = None,
    ) -> Path:
        missing = missing or set()
        output_dir = root / "run"
        output_dir.mkdir()
        result = self.base_result(output_dir)
        if result_overrides:
            result.update(result_overrides)
        diagnostics = diagnostics if diagnostics is not None else [self.diagnostic("parsed")]
        if "manual_review_required_count" not in result:
            result["manual_review_required_count"] = sum(
                1
                for diagnostic in diagnostics
                if diagnostic.get("diagnostic_status") == "manual_review_required"
                or diagnostic.get("manual_review_required") is True
            )

        if "report_full" not in missing:
            Path(result["report_full"]).write_text("full report\n", encoding="utf-8")
        if "report_compact" not in missing:
            Path(result["report_compact"]).write_text("compact report\n", encoding="utf-8")
        if "run_index_entry" not in missing:
            write_json(result["run_index_entry"], self.run_index_entry(output_dir, result))
        if "runs_index" not in missing:
            append_run_index_entry(result["runs_index"], self.run_index_entry(output_dir, result))
        if "run_summary" not in missing:
            write_json(
                result["run_summary"],
                {
                    "schema_version": 1,
                    "result": result,
                    "source_diagnostics": diagnostics,
                    "report_scorecard": {"status": result["report_scorecard_status"]},
                },
            )
        return output_dir

    def base_result(self, output_dir: Path) -> dict[str, object]:
        return {
            "run_id": "0180-gate-test",
            "status": "CHANGES_FOUND",
            "output_dir": str(output_dir),
            "report_full": str(output_dir / "0180-Report_Full.md"),
            "report_compact": str(output_dir / "0180-Report_Compact.md"),
            "run_summary": str(output_dir / "0180-Run_Summary.json"),
            "run_index_entry": str(output_dir / "0180-Run_Index_Entry.json"),
            "runs_index": str(output_dir / "runs_index.jsonl"),
            "source_count": 1,
            "parsed_count": 1,
            "item_count": 1,
            "failed_count": 0,
            "skipped_count": 0,
            "unsupported_source_count": 0,
            "manual_review_required_count": 0,
            "direct_action_count": 0,
            "monitor_only_action_count": 0,
            "no_action_count": 1,
            "report_scorecard_status": "PASS",
        }

    def run_index_entry(self, output_dir: Path, result: dict[str, object]) -> RunIndexEntry:
        return RunIndexEntry(
            run_id=str(result["run_id"]),
            step="0180",
            status=str(result["status"]),
            started_at="2026-06-10T12:00:00Z",
            finished_at="2026-06-10T12:00:00Z",
            duration_seconds=0.0,
            report_full=str(result["report_full"]),
            report_compact=str(result["report_compact"]),
            snapshot_dir=str(output_dir),
            notes="Automation gate test fixture.",
            source_count=int(result["source_count"]),
            parsed_count=int(result["parsed_count"]),
            item_count=int(result["item_count"]),
            failed_count=int(result["failed_count"]),
            skipped_count=int(result["skipped_count"]),
            timestamp="2026-06-10T12:00:00Z",
        )

    def diagnostic(
        self,
        status: str,
        *,
        manual: bool = False,
        http_status_code: int = 200,
    ) -> dict[str, object]:
        return {
            "source_id": f"source_{status}",
            "provider": "test",
            "source_type": "test",
            "manual_review_required": manual,
            "diagnostic_status": status,
            "fetch_status": "fetched" if status != "fetch_failed" else "failed",
            "http_status_code": http_status_code,
            "parser_status": "parsed" if status == "parsed" else "parser_skipped",
            "error_code": None,
            "item_count": 1 if status == "parsed" else 0,
            "recommended_follow_up": "test",
            "error": None,
        }


if __name__ == "__main__":
    unittest.main()
