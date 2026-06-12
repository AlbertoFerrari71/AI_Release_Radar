import json
import tempfile
import unittest
from pathlib import Path

from radar.v1_readiness import (
    AI_RADAR_V1_FINAL_READY_WITH_WARNINGS,
    BLOCKED,
    MICRO_FIX_REQUIRED_BEFORE_V1,
    evaluate_v1_final_readiness,
    V1_OPERATOR_READY_WITH_WARNINGS,
    evaluate_v1_operator_readiness,
    write_v1_final_readiness_gate,
    write_v1_operator_readiness_gate,
)


class V1ReadinessTests(unittest.TestCase):
    def test_ready_with_warnings_when_smoke_and_safety_pass_but_coverage_is_low(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = self.create_run(root / "run")
            scheduler_log = self.create_scheduler_log(root / "scheduler.log")

            gate = evaluate_v1_operator_readiness(
                run_dir,
                scheduler_log_path=scheduler_log,
                dashboard_smoke_status="PASS",
                action_center_smoke_status="PASS",
                action_center_run_scope_status="PASS",
            )

            self.assertEqual(gate["classification"], V1_OPERATOR_READY_WITH_WARNINGS)
            self.assertEqual(gate["blockers"], [])
            self.assertEqual(gate["micro_fixes"], [])
            self.assertIn("source_coverage_low", gate["warnings"])
            self.assertTrue(gate["checks"]["safety_ok"])

    def test_not_run_smoke_requires_micro_fix_before_v1(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = self.create_run(root / "run")

            gate = evaluate_v1_operator_readiness(run_dir)

            self.assertEqual(gate["classification"], MICRO_FIX_REQUIRED_BEFORE_V1)
            self.assertIn("dashboard_smoke_not_pass", gate["micro_fixes"])

    def test_failed_dashboard_smoke_blocks_v1(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = self.create_run(root / "run")

            gate = evaluate_v1_operator_readiness(
                run_dir,
                dashboard_smoke_status="FAIL",
                action_center_smoke_status="PASS",
                action_center_run_scope_status="PASS",
            )

            self.assertEqual(gate["classification"], BLOCKED)
            self.assertIn("dashboard_smoke_failed", gate["blockers"])

    def test_write_readiness_gate_is_bridge_only_and_uses_fixed_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = self.create_run(root / "run")
            output_dir = root / "codex_command"

            result = write_v1_operator_readiness_gate(
                run_dir,
                output_dir,
                dashboard_smoke_status="PASS",
                action_center_smoke_status="PASS",
                action_center_run_scope_status="PASS",
            )

            self.assertEqual(result["classification"], V1_OPERATOR_READY_WITH_WARNINGS)
            self.assertEqual(
                {path.name for path in output_dir.iterdir()},
                {
                    "1450-V1_Operator_Readiness_Gate.json",
                    "1450-V1_Operator_Readiness_Gate.md",
                },
            )

    def test_v1_final_readiness_accepts_pass_with_documented_source_warnings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = self.create_run(root / "run")
            source_gate = {
                "status": "SOURCE_COVERAGE_FINAL_PASS_WITH_WARNINGS",
                "parsed_count": 4,
                "parsed_count_target": 3,
                "final_classification_complete": True,
                "warnings": ["manual_review_sources_present:3"],
            }
            safety_gate = {"status": "SAFETY_FINAL_PASS", "warnings": []}

            gate = evaluate_v1_final_readiness(
                run_dir=run_dir,
                source_coverage_gate=source_gate,
                safety_gate=safety_gate,
                dashboard_smoke_status="PASS",
                action_center_status="PASS",
                daily_review_pack_status="PASS",
                hag_status="HOLD_FOR_HUMAN_APPROVAL",
                tests_status="PASS",
                docs_status="PASS",
            )

            self.assertEqual(gate["classification"], AI_RADAR_V1_FINAL_READY_WITH_WARNINGS)
            self.assertEqual(gate["blockers"], [])
            self.assertTrue(gate["checks"]["source_coverage_target_reached"])
            self.assertIn("manual_review_sources_present:3", gate["warnings"])

    def test_write_v1_final_readiness_gate_uses_1810_names(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = self.create_run(root / "run")
            output_dir = root / "codex_command"

            result = write_v1_final_readiness_gate(
                output_dir,
                run_dir=run_dir,
                source_coverage_gate={
                    "status": "SOURCE_COVERAGE_FINAL_PASS",
                    "parsed_count": 3,
                    "parsed_count_target": 3,
                    "final_classification_complete": True,
                    "warnings": [],
                },
                safety_gate={"status": "SAFETY_FINAL_PASS", "warnings": []},
                dashboard_smoke_status="PASS",
                action_center_status="PASS",
                daily_review_pack_status="PASS",
                hag_status="HOLD_FOR_HUMAN_APPROVAL",
                tests_status="PASS",
                docs_status="PASS",
            )

            self.assertEqual(result["classification"], "AI_RADAR_V1_FINAL_READY")
            self.assertEqual(
                {path.name for path in output_dir.iterdir()},
                {
                    "1810-V1_Final_Readiness_Gate.json",
                    "1810-V1_Final_Readiness_Gate.md",
                },
            )

    def create_run(self, run_dir: Path) -> Path:
        run_dir.mkdir(parents=True)
        result = {
            "run_id": "0180-20260612-051505Z",
            "status": "CHANGES_FOUND",
            "source_count": 3,
            "parsed_count": 1,
            "direct_action_count": 1,
            "monitor_only_action_count": 1,
            "no_action_count": 0,
            "source_diagnostics": [
                {
                    "source_id": "parsed",
                    "diagnostic_status": "parsed",
                    "manual_review_required": False,
                    "scheduler_readiness": "ready",
                    "item_count": 1,
                },
                {
                    "source_id": "manual",
                    "diagnostic_status": "manual_review_required",
                    "manual_review_required": True,
                    "scheduler_readiness": "hold",
                    "http_status_code": 403,
                },
                {
                    "source_id": "unsupported",
                    "diagnostic_status": "fetched_but_unsupported",
                    "manual_review_required": False,
                    "scheduler_readiness": "hold",
                },
            ],
        }
        (run_dir / "0180-Run_Summary.json").write_text(
            json.dumps({"result": result}),
            encoding="utf-8",
        )
        (run_dir / "0350-Daily_Sim_Summary.json").write_text(
            json.dumps(
                {
                    "status": "CHANGES_FOUND",
                    "automation_gate_status": "ACTION_REVIEW_REQUIRED",
                    "hag_status": "HOLD_FOR_HUMAN_APPROVAL",
                    "auto_action_executed": False,
                    "email_sent": False,
                    "llm_called": False,
                    "scheduler_activated": False,
                    "manual_review_queue_count": 1,
                    "real_run": result,
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "0630-Daily_Quality_Gate_V2.json").write_text(
            json.dumps({"overall_daily_review_status": "ACTION_REVIEW_REQUIRED"}),
            encoding="utf-8",
        )
        (run_dir / "0650-Action_Triage.json").write_text(
            json.dumps({"status": "HOLD", "counts": {}}),
            encoding="utf-8",
        )
        (run_dir / "0660-Codex_Prompt_Suggestions.json").write_text(
            json.dumps({"status": "suggested_only", "suggestions_count": 0, "suggestions": []}),
            encoding="utf-8",
        )
        return run_dir

    def create_scheduler_log(self, path: Path) -> Path:
        path.write_text(
            "\n".join(
                [
                    "2026-06-12T05:15:02 script_exit_code=0",
                    "2026-06-12T05:15:02 no_auto_action=confirmed",
                    "2026-06-12T05:15:02 no_email=confirmed",
                    "2026-06-12T05:15:02 no_external_notification=confirmed",
                    "2026-06-12T05:15:02 no_llm=confirmed",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return path


if __name__ == "__main__":
    unittest.main()
