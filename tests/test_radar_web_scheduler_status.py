import json
import subprocess
import unittest
from unittest.mock import patch

from radar_web.scheduler_status import read_scheduler_status


class RadarWebSchedulerStatusTests(unittest.TestCase):
    def test_non_windows_returns_no_data(self):
        with patch("radar_web.scheduler_status.platform.system", return_value="Linux"):
            status = read_scheduler_status("AIReleaseRadar_DailyDryReport")

        self.assertEqual(status["status"], "NO_DATA")
        self.assertIn("scheduler_status_not_windows", status["warnings"])

    def test_windows_runner_success_parses_payload(self):
        payload = {
            "status": "Ready",
            "task_name": "AIReleaseRadar_DailyDryReport",
            "task_path": "\\",
            "last_run_time": "2026-06-10T19:01:02.0000000+02:00",
            "last_task_result": 0,
            "next_run_time": "2026-06-11T07:15:00.0000000+02:00",
            "number_of_missed_runs": 0,
            "warnings": [],
        }

        def fake_runner(command, **kwargs):
            return subprocess.CompletedProcess(command, 0, json.dumps(payload), "")

        with patch("radar_web.scheduler_status.platform.system", return_value="Windows"):
            status = read_scheduler_status(
                "AIReleaseRadar_DailyDryReport",
                runner=fake_runner,
            )

        self.assertEqual(status["status"], "Ready")
        self.assertEqual(status["last_task_result"], 0)
        self.assertTrue(status["read_only"])

    def test_windows_runner_failure_is_no_data(self):
        def fake_runner(command, **kwargs):
            return subprocess.CompletedProcess(command, 1, "", "boom")

        with patch("radar_web.scheduler_status.platform.system", return_value="Windows"):
            status = read_scheduler_status(
                "AIReleaseRadar_DailyDryReport",
                runner=fake_runner,
            )

        self.assertEqual(status["status"], "NO_DATA")
        self.assertEqual(status["warnings"], ["boom"])


if __name__ == "__main__":
    unittest.main()
