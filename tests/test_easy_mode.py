import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from radar_web.app import create_app
from radar_web.config import DashboardConfig
from radar_web.easy_mode import (
    build_easy_days,
    build_easy_run_detail,
    calculate_easy_semaphore,
)


class EasyModeTests(unittest.TestCase):
    def create_bridge(
        self,
        root: Path,
        *,
        run_id: str = "0320_0400_daily_sim_20260613_064418",
        status: str = "PASS",
        direct_count: int = 0,
        monitor_count: int = 0,
        blocked_count: int = 0,
        manual_count: int = 0,
        source_diagnostics: list[dict[str, object]] | None = None,
    ) -> Path:
        bridge = root / "bridge"
        run_dir = bridge / "runs" / run_id
        run_dir.mkdir(parents=True)
        source_diagnostics = source_diagnostics or []
        action_entries = []
        if blocked_count:
            action_entries.append(
                {
                    "triage_class": "blocked_by_coverage",
                    "title": "Aggregate direct actions",
                    "target_project": "Mixed project targets",
                    "reason": "direct actions exist, but source coverage is below full-pass threshold",
                    "risk_class": "L1/L2",
                    "count": blocked_count,
                }
            )
        if manual_count:
            action_entries.append(
                {
                    "triage_class": "manual_review",
                    "title": "Manual review: openai_api_deprecations",
                    "target_project": "Radar source coverage",
                    "reason": "direct_actions_present",
                    "risk_class": "L1/L2",
                    "severity": "high",
                }
            )
        summary = {
            "status": status,
            "automation_gate_status": "PASS" if status == "PASS" else "ACTION_REVIEW_REQUIRED",
            "scheduler_readiness_recommendation": "READY" if status == "PASS" else "HOLD",
            "hag_status": "NO_ACTION_REQUIRED" if not blocked_count else "HOLD_FOR_HUMAN_APPROVAL",
            "manual_review_queue_count": manual_count,
            "prompt_suggestions_count": 0,
            "daily_quality_gate_v2": {
                "overall_daily_review_status": "PASS" if status == "PASS" else "ACTION_REVIEW_REQUIRED",
                "source_coverage_status": "PASS" if not source_diagnostics else "WARN",
            },
            "real_run": {
                "status": status,
                "source_count": max(len(source_diagnostics), 1),
                "parsed_count": max(len(source_diagnostics) - 1, 1),
                "item_count": direct_count,
                "direct_action_count": direct_count,
                "monitor_only_action_count": monitor_count,
                "source_diagnostics": source_diagnostics,
            },
            "action_triage": {
                "status": "PASS" if not action_entries else "HOLD",
                "counts": {
                    "blocked_by_coverage": blocked_count,
                    "blocked_by_manual_review": 0,
                    "manual_review": manual_count,
                    "monitor": monitor_count,
                },
                "entries": action_entries,
            },
            "prompt_suggestions": {
                "status": "NO_DATA",
                "suggestions_count": 0,
                "suggestions": [],
            },
        }
        (run_dir / "0180-Report_Compact.md").write_text("# Compact\n", encoding="utf-8")
        (run_dir / "0180-Run_Summary.json").write_text(
            json.dumps({"result": summary["real_run"]}),
            encoding="utf-8",
        )
        (run_dir / "0350-Daily_Sim_Summary.json").write_text(
            json.dumps(summary),
            encoding="utf-8",
        )
        (run_dir / "0350-Daily_Sim_Gate.json").write_text(
            json.dumps({"status": summary["automation_gate_status"]}),
            encoding="utf-8",
        )
        (run_dir / "0350-Daily_Sim_Gate.md").write_text("# Gate\n", encoding="utf-8")
        (run_dir / "0630-Daily_Quality_Gate_V2.json").write_text(
            json.dumps(summary["daily_quality_gate_v2"]),
            encoding="utf-8",
        )
        (run_dir / "0630-Daily_Quality_Gate_V2.md").write_text("# Quality\n", encoding="utf-8")
        (run_dir / "0650-Action_Triage.json").write_text(
            json.dumps(summary["action_triage"]),
            encoding="utf-8",
        )
        (run_dir / "0660-Codex_Prompt_Suggestions.json").write_text(
            json.dumps(summary["prompt_suggestions"]),
            encoding="utf-8",
        )
        (run_dir / "0660-Codex_Prompt_Suggestions.md").write_text(
            "# Suggestions\n",
            encoding="utf-8",
        )
        (run_dir / "0680-Human_Approval_Gate_Report.md").write_text(
            "# Human approval\n",
            encoding="utf-8",
        )
        (run_dir / "0710-Daily_Operator_Dashboard.md").write_text(
            "# Dashboard\n",
            encoding="utf-8",
        )
        (run_dir / "0730-Supervised_Action_Loop_Dry_Run.md").write_text(
            "# Dry run\n",
            encoding="utf-8",
        )
        return bridge

    def test_easy_semaphore_is_deterministic(self):
        self.assertEqual(
            calculate_easy_semaphore(
                {
                    "status": "CRITICAL",
                    "important_count": 1,
                    "manual_review_count": 0,
                    "source_warning_count": 0,
                }
            ),
            "red",
        )
        self.assertEqual(
            calculate_easy_semaphore(
                {
                    "status": "PASS",
                    "important_count": 1,
                    "manual_review_count": 0,
                    "source_warning_count": 0,
                }
            ),
            "yellow",
        )
        self.assertEqual(
            calculate_easy_semaphore(
                {
                    "status": "PASS",
                    "important_count": 0,
                    "manual_review_count": 0,
                    "source_warning_count": 0,
                }
            ),
            "green",
        )
        self.assertEqual(
            calculate_easy_semaphore(
                {
                    "status": "NO_DATA",
                    "important_count": 0,
                    "manual_review_count": 0,
                    "source_warning_count": 0,
                    "warnings": ["missing_json:0350-Daily_Sim_Summary.json"],
                }
            ),
            "gray",
        )

    def test_easy_builder_summarizes_days_and_detail(self):
        source_warning = {
            "source_id": "openai_api_deprecations",
            "provider": "openai",
            "diagnostic_status": "manual_review_required",
            "fetch_status": "fetched",
            "parser_status": "parsed",
            "http_status_code": 403,
            "item_count": 0,
            "manual_review_required": True,
            "scheduler_readiness": "hold",
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = self.create_bridge(
                Path(tmpdir),
                status="CRITICAL",
                direct_count=3,
                monitor_count=5,
                blocked_count=3,
                manual_count=1,
                source_diagnostics=[source_warning],
            )
            payload = build_easy_days(bridge / "runs")
            detail = build_easy_run_detail(bridge / "runs", payload["latest"]["run_id"])

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["latest"]["semaphore"], "red")
        self.assertEqual(payload["latest"]["important_count"], 3)
        self.assertEqual(payload["latest"]["monitor_count"], 5)
        self.assertEqual(payload["latest"]["source_warning_count"], 1)
        self.assertIsNotNone(detail)
        self.assertGreaterEqual(detail["cards_count"], 1)
        self.assertEqual(detail["links"]["action_center"], "/actions")

    def test_easy_routes_api_and_no_dominant_technical_terms(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = self.create_bridge(Path(tmpdir), direct_count=1)
            run_id = next((bridge / "runs").iterdir()).name
            client = TestClient(create_app(DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)))
            with patch("radar_web.app.read_scheduler_status", return_value={"status": "NO_DATA"}):
                root = client.get("/")
                detail = client.get(f"/easy/runs/{run_id}")
                days = client.get("/api/easy/days").json()
                latest = client.get("/api/easy/latest").json()
                api_detail = client.get(f"/api/easy/days/{run_id}")
                expert = client.get("/expert")

        self.assertEqual(root.status_code, 200)
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(api_detail.status_code, 200)
        self.assertEqual(expert.status_code, 200)
        self.assertEqual(days["latest"]["run_id"], run_id)
        self.assertEqual(latest["run_id"], run_id)
        self.assertIn("Modalita semplice", root.text)
        self.assertIn("Cosa e successo", detail.text)
        for forbidden in ("parsed_count", "fixture", "HAG"):
            self.assertNotIn(forbidden, root.text)
            self.assertNotIn(forbidden, detail.text)

    def test_easy_mode_fallback_without_runs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = Path(tmpdir) / "bridge"
            (bridge / "runs").mkdir(parents=True)
            client = TestClient(create_app(DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)))
            root = client.get("/")
            days = client.get("/api/easy/days").json()
            latest = client.get("/api/easy/latest").json()

        self.assertEqual(root.status_code, 200)
        self.assertIn("Nessun giorno disponibile", root.text)
        self.assertEqual(days["count"], 0)
        self.assertEqual(latest["semaphore"], "gray")


if __name__ == "__main__":
    unittest.main()
