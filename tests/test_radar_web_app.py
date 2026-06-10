import json
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from radar_web.app import create_app
from radar_web.config import DashboardConfig
from radar_web.manual_trigger import DailySimTrigger


SCHEDULER_NO_DATA = {
    "status": "NO_DATA",
    "task_name": "AIReleaseRadar_DailyDryReport",
    "read_only": True,
    "warnings": [],
}


class RadarWebAppTests(unittest.TestCase):
    def create_bridge(self, root: Path) -> Path:
        bridge = root / "bridge"
        run_dir = bridge / "runs" / "0320_0400_daily_sim_20260610_090000"
        run_dir.mkdir(parents=True)
        (run_dir / "0180-Report_Compact.md").write_text("# Compact\n", encoding="utf-8")
        (run_dir / "0350-Daily_Sim_Summary.json").write_text(
            json.dumps(
                {
                    "status": "PASS",
                    "automation_gate_status": "PASS",
                    "daily_quality_gate_v2": {
                        "overall_daily_review_status": "PASS",
                        "source_coverage_status": "PASS",
                    },
                    "real_run": {
                        "status": "PASS",
                        "source_count": 2,
                        "parsed_count": 1,
                        "direct_action_count": 0,
                        "monitor_only_action_count": 1,
                    },
                    "prompt_suggestions": {
                        "status": "suggested_only",
                        "suggestions_count": 0,
                        "suggestions": [],
                    },
                    "prompt_suggestions_count": 0,
                    "manual_review_queue_count": 0,
                    "hag_status": "NO_ACTION_REQUIRED",
                }
            ),
            encoding="utf-8",
        )
        return bridge

    def test_health_status_and_runs_endpoints(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = self.create_bridge(Path(tmpdir))
            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            with patch("radar_web.app.read_scheduler_status", return_value=SCHEDULER_NO_DATA):
                client = TestClient(create_app(config))

                self.assertEqual(client.get("/health").json()["status"], "ok")
                self.assertEqual(client.get("/api/status").json()["status"], "PASS")
                runs = client.get("/api/runs").json()["runs"]
                self.assertEqual(len(runs), 1)
                self.assertIn("AI Release Radar", client.get("/").text)

    def test_operator_smoke_covers_run_detail_and_sub_endpoints(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = self.create_bridge(Path(tmpdir))
            run_id = next((bridge / "runs").iterdir()).name
            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            with patch("radar_web.app.read_scheduler_status", return_value=SCHEDULER_NO_DATA):
                client = TestClient(create_app(config))

                endpoints = [
                    "/",
                    "/health",
                    "/api/status",
                    "/api/runs",
                    f"/runs/{run_id}",
                    f"/api/runs/{run_id}",
                    f"/api/runs/{run_id}/compact",
                    f"/api/runs/{run_id}/gate",
                    f"/api/runs/{run_id}/hag",
                    f"/api/runs/{run_id}/dashboard",
                    "/api/scheduler",
                ]
                for endpoint in endpoints:
                    with self.subTest(endpoint=endpoint):
                        response = client.get(endpoint)
                        self.assertEqual(response.status_code, 200)

    def test_home_formats_scheduler_dates_and_manual_trigger_note(self):
        scheduler = {
            "status": "Ready",
            "task_name": "AIReleaseRadar_DailyDryReport",
            "read_only": True,
            "last_run_time": "2026-06-10T19:01:02.0000000+02:00",
            "last_task_result": 0,
            "next_run_time": "2026-06-11T07:15:00.0000000+02:00",
            "number_of_missed_runs": 0,
            "warnings": [],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = self.create_bridge(Path(tmpdir))
            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            with patch("radar_web.app.read_scheduler_status", return_value=scheduler):
                html = TestClient(create_app(config)).get("/").text

        self.assertIn("Manual only / no auto-action", html)
        self.assertIn("10/06/2026 19:01", html)
        self.assertIn("11/06/2026 07:15", html)
        self.assertIn("Yes", html)

    def test_run_detail_highlights_hold_warnings_and_prompt_suggestions(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = self.create_bridge(Path(tmpdir))
            run_dir = next((bridge / "runs").iterdir())
            summary_path = run_dir / "0350-Daily_Sim_Summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary.update(
                {
                    "status": "ACTION_REVIEW_REQUIRED",
                    "hag_status": "HOLD_FOR_HUMAN_APPROVAL",
                    "action_triage": {
                        "status": "HOLD",
                        "counts": {
                            "blocked_by_coverage": 1,
                            "blocked_by_manual_review": 0,
                        },
                        "entries": [
                            {
                                "triage_class": "blocked_by_coverage",
                                "title": "Coverage blocked action",
                                "target_project": "Radar",
                                "reason": "coverage",
                                "risk_class": "L1/L2",
                            }
                        ],
                    },
                    "prompt_suggestions": {
                        "status": "suggested_only",
                        "suggestions_count": 1,
                        "suggestions": [
                            {
                                "suggested_step_number": "PS-001",
                                "title": "Review dashboard",
                                "status": "suggested_only",
                                "target_project": "Radar",
                                "risk_class": "L1/L2",
                            }
                        ],
                    },
                    "prompt_suggestions_count": 1,
                }
            )
            summary_path.write_text(json.dumps(summary), encoding="utf-8")
            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            with patch("radar_web.app.read_scheduler_status", return_value=SCHEDULER_NO_DATA):
                html = TestClient(create_app(config)).get(f"/runs/{run_dir.name}").text

        self.assertIn("operator attention", html)
        self.assertIn("HOLD_FOR_HUMAN_APPROVAL", html)
        self.assertIn("Coverage blocked action", html)
        self.assertIn("SUGGESTED ONLY - not executed", html)
        self.assertIn("Review dashboard", html)
        self.assertIn("<summary>", html)

    def test_manual_trigger_uses_only_daily_sim_command(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = Path(tmpdir) / "bridge"
            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            calls = []

            def fake_runner(command, **kwargs):
                calls.append((command, kwargs))
                output_dir = bridge / "runs" / "0320_0400_daily_sim_20260610_090000"
                output_dir.mkdir(parents=True)
                (output_dir / "0350-Daily_Sim_Summary.json").write_text(
                    json.dumps(
                        {
                            "status": "PASS",
                            "automation_gate_status": "PASS",
                            "hag_status": "NO_ACTION_REQUIRED",
                        }
                    ),
                    encoding="utf-8",
                )
                return subprocess.CompletedProcess(
                    command,
                    0,
                    stdout=(
                        "Output dir: "
                        f"{output_dir}\n"
                    ),
                    stderr="",
                )

            trigger = DailySimTrigger(config, runner=fake_runner)
            with patch("radar_web.app.read_scheduler_status", return_value=SCHEDULER_NO_DATA):
                response = TestClient(create_app(config, daily_sim_trigger=trigger)).post(
                    "/api/daily-sim/run"
                )

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "PASS")
            self.assertTrue(response.json()["manual_only"])
            self.assertTrue(response.json()["writes_to_bridge"])
            self.assertTrue(response.json()["no_auto_action"])
            self.assertTrue(response.json()["dashboard_updated"])
            self.assertEqual(response.json()["automation_gate_status"], "PASS")
            self.assertEqual(response.json()["hag_status"], "NO_ACTION_REQUIRED")
            self.assertEqual(
                calls[0][0],
                [
                    "python",
                    "-m",
                    "radar.cli",
                    "daily-sim",
                    "--output-root",
                    str(bridge / "runs"),
                ],
            )
            self.assertEqual(calls[0][1]["cwd"], str(Path.cwd()))
            self.assertEqual(calls[0][1]["env"]["PYTHONDONTWRITEBYTECODE"], "1")

    def test_manual_trigger_lock_returns_conflict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = Path(tmpdir) / "bridge"
            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            lock = threading.Lock()
            lock.acquire()
            trigger = DailySimTrigger(
                config,
                runner=lambda command, **kwargs: subprocess.CompletedProcess(command, 0),
                lock=lock,
            )
            try:
                response = TestClient(create_app(config, daily_sim_trigger=trigger)).post(
                    "/api/daily-sim/run"
                )
            finally:
                lock.release()

            self.assertEqual(response.status_code, 409)
            self.assertEqual(response.json()["status"], "ALREADY_RUNNING")

    def test_manual_trigger_refuses_repo_output_root(self):
        config = DashboardConfig(repo_root=Path.cwd(), bridge_root=Path.cwd() / "bridge")
        calls = []
        trigger = DailySimTrigger(
            config,
            runner=lambda command, **kwargs: calls.append(command)
            or subprocess.CompletedProcess(command, 0),
        )

        response = TestClient(create_app(config, daily_sim_trigger=trigger)).post(
            "/api/daily-sim/run"
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "REFUSED")
        self.assertIn("output_root_inside_repository", response.json()["warnings"])
        self.assertEqual(calls, [])

    def test_manual_trigger_refuses_last_latest_output_root(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            config = DashboardConfig(
                repo_root=Path.cwd(),
                bridge_root=Path(tmpdir) / "latest-bridge",
            )
            trigger = DailySimTrigger(
                config,
                runner=lambda command, **kwargs: subprocess.CompletedProcess(command, 0),
            )

            response = TestClient(create_app(config, daily_sim_trigger=trigger)).post(
                "/api/daily-sim/run"
            )

            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json()["status"], "REFUSED")
            self.assertIn("forbidden_path_name:latest-bridge", response.json()["warnings"])


if __name__ == "__main__":
    unittest.main()
