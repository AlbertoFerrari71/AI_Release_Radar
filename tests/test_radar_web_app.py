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

    def test_manual_trigger_uses_only_daily_sim_command(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = Path(tmpdir) / "bridge"
            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            calls = []

            def fake_runner(command, **kwargs):
                calls.append((command, kwargs))
                return subprocess.CompletedProcess(
                    command,
                    0,
                    stdout=(
                        "Output dir: "
                        f"{bridge / 'runs' / '0320_0400_daily_sim_20260610_090000'}\n"
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
