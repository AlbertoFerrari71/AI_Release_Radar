import json
import tempfile
import unittest
from pathlib import Path

from radar_web.bridge_reader import load_json, load_text
from radar_web.run_locator import (
    find_latest_run,
    inspect_runs_root,
    list_recent_runs,
    load_run_detail,
)


class RadarWebRunLocatorTests(unittest.TestCase):
    def write_json(self, path: Path, data: object) -> None:
        path.write_text(json.dumps(data), encoding="utf-8")

    def create_run(
        self,
        runs_root: Path,
        stamp: str,
        *,
        status: str = "PASS",
        prompt_suggestions_count: int = 0,
    ) -> Path:
        run_dir = runs_root / f"0320_0400_daily_sim_{stamp}"
        run_dir.mkdir(parents=True)
        (run_dir / "0180-Report_Compact.md").write_text("# Compact\n", encoding="utf-8")
        self.write_json(
            run_dir / "0350-Daily_Sim_Summary.json",
            {
                "status": status,
                "automation_gate_status": status,
                "daily_quality_gate_v2": {
                    "overall_daily_review_status": status,
                    "source_coverage_status": status,
                },
                "real_run": {
                    "status": status,
                    "source_count": 2,
                    "parsed_count": 1,
                    "direct_action_count": 1,
                    "monitor_only_action_count": 1,
                    "source_diagnostics": [
                        {"diagnostic_status": "parsed"},
                        {"diagnostic_status": "manual_review_required"},
                    ],
                },
                "action_triage": {
                    "status": "HOLD",
                    "counts": {
                        "blocked_by_coverage": 1,
                        "blocked_by_manual_review": 0,
                        "manual_review": 1,
                    },
                    "entries": [
                        {
                            "triage_class": "blocked_by_coverage",
                            "title": "Blocked",
                            "target_project": "Radar",
                            "reason": "coverage",
                            "risk_class": "L1/L2",
                        },
                        {
                            "triage_class": "manual_review",
                            "title": "Manual",
                            "target_project": "Radar",
                            "reason": "source review",
                            "risk_class": "L1/L2",
                        },
                    ],
                },
                "prompt_suggestions": {
                    "status": "suggested_only",
                    "suggestions_count": prompt_suggestions_count,
                    "suggestions": [
                        {
                            "suggested_step_number": "PS-001",
                            "title": "Review",
                            "status": "suggested_only",
                            "target_project": "Radar",
                            "risk_class": "L1/L2",
                        }
                    ][:prompt_suggestions_count],
                },
                "hag_status": "HOLD_FOR_HUMAN_APPROVAL",
                "manual_review_queue_count": 1,
                "prompt_suggestions_count": prompt_suggestions_count,
            },
        )
        return run_dir

    def test_find_latest_run_prefers_newest_dated_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            runs_root = Path(tmpdir) / "runs"
            self.create_run(runs_root, "20260610_080000", status="PASS")
            latest_dir = self.create_run(
                runs_root,
                "20260610_090000",
                status="ACTION_REVIEW_REQUIRED",
                prompt_suggestions_count=1,
            )

            latest = find_latest_run(runs_root)

            self.assertIsNotNone(latest)
            self.assertEqual(latest.run_dir, str(latest_dir))
            self.assertEqual(latest.status, "ACTION_REVIEW_REQUIRED")
            self.assertEqual(latest.prompt_suggestions_count, 1)
            self.assertEqual(latest.blocked_action_count, 1)

    def test_missing_files_are_reported_as_warnings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            runs_root = Path(tmpdir) / "runs"
            run_dir = runs_root / "0320_0400_daily_sim_20260610_080000"
            run_dir.mkdir(parents=True)

            runs = list_recent_runs(runs_root)

            self.assertEqual(len(runs), 1)
            self.assertIn("missing_json:0350-Daily_Sim_Summary.json", runs[0].warnings)
            self.assertIn("missing_json:0180-Run_Summary.json", runs[0].warnings)

    def test_inspect_runs_root_reports_missing_and_invalid_index(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            runs_root = Path(tmpdir) / "runs"

            self.assertEqual(inspect_runs_root(runs_root), ["runs_root_missing"])

            runs_root.mkdir()
            (runs_root / "runs_index.jsonl").write_text("{not-json}\n", encoding="utf-8")
            warnings = inspect_runs_root(runs_root)

            self.assertTrue(any(warning.startswith("runs_index:line 1:") for warning in warnings))

    def test_load_run_detail_extracts_hag_prompt_and_review_data(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            runs_root = Path(tmpdir) / "runs"
            run_dir = self.create_run(
                runs_root,
                "20260610_090000",
                status="ACTION_REVIEW_REQUIRED",
                prompt_suggestions_count=1,
            )

            detail = load_run_detail(runs_root, run_dir.name)

            self.assertIsNotNone(detail)
            self.assertEqual(detail["source_diagnostics_summary"]["parsed"], 1)
            self.assertEqual(len(detail["blocked_actions"]), 1)
            self.assertEqual(len(detail["manual_review_queue"]), 1)
            self.assertEqual(detail["prompt_suggestions_status"], "suggested_only")
            self.assertTrue(detail["no_auto_action"])

    def test_forbidden_last_latest_names_are_not_used(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            forbidden = root / "latest-runs"
            forbidden.mkdir()
            self.create_run(forbidden, "20260610_080000")

            self.assertEqual(list_recent_runs(forbidden), [])
            self.assertIn(
                "forbidden_path_name:LAST-Run.json",
                load_json(root / "LAST-Run.json").warnings,
            )
            self.assertIn(
                "forbidden_path_name:latest-report.md",
                load_text(root / "latest-report.md").warnings,
            )


if __name__ == "__main__":
    unittest.main()
