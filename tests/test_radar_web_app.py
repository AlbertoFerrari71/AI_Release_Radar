import json
from html.parser import HTMLParser
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urlsplit

from fastapi.testclient import TestClient

from radar_web.app import create_app
from radar_web.config import DashboardConfig
from radar_web.manual_trigger import DailySimTrigger
from radar.action_inbox import append_decision_log, build_action_inbox
from radar_web.run_locator import load_run_detail


SCHEDULER_NO_DATA = {
    "status": "NO_DATA",
    "task_name": "AIReleaseRadar_DailyDryReport",
    "read_only": True,
    "interpretation": "NO_DATA",
    "warnings": [],
}


class InternalLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.buttons = []
        self.selects = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a" and values.get("href"):
            self.links.append(values["href"])
        if tag == "button":
            self.buttons.append(values)
        if tag == "select":
            self.selects.append(values)


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
                    "action_triage": {
                        "status": "ACTION_REVIEW_REQUIRED",
                        "counts": {
                            "codex_prompt_candidate": 1,
                            "monitor": 0,
                            "ignore": 0,
                            "manual_review": 0,
                            "blocked_by_coverage": 0,
                            "blocked_by_manual_review": 0,
                        },
                        "entries": [
                            {
                                "triage_class": "codex_prompt_candidate",
                                "title": "Review Action Center candidate",
                                "target_project": "AI Release Radar",
                                "project_key": "ai_release_radar",
                                "reason": "direct project signal can become a suggested-only Codex prompt",
                                "risk_class": "L1/L2",
                                "item_category": "codex_cli",
                                "score": 82,
                                "item_id": "action-center-candidate",
                            }
                        ],
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
                html = client.get("/").text
                self.assertIn("AI Release Radar", html)
                self.assertIn("Modalita semplice", html)
                self.assertIn("Leggi", html)
                self.assertNotIn("parsed_count", html)
                expert_html = client.get("/expert?lang=en").text
                self.assertIn("SUGGESTED ONLY - not executed", expert_html)

    def test_operator_smoke_covers_run_detail_and_sub_endpoints(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = self.create_bridge(Path(tmpdir))
            run_id = next((bridge / "runs").iterdir()).name
            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            with patch("radar_web.app.read_scheduler_status", return_value=SCHEDULER_NO_DATA):
                client = TestClient(create_app(config))

                endpoints = [
                    "/",
                    "/easy",
                    "/easy-mode",
                    "/expert",
                    "/dashboard",
                    "/sources",
                    "/health",
                    "/api/status",
                    "/api/runs",
                    "/api/easy/days",
                    "/api/easy/latest",
                    "/api/preferences/ui",
                    f"/api/easy/days/{run_id}",
                    f"/easy/runs/{run_id}",
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

    def test_easy_alias_redirect_is_safe(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = self.create_bridge(Path(tmpdir))
            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            with patch("radar_web.app.read_scheduler_status", return_value=SCHEDULER_NO_DATA):
                client = TestClient(create_app(config))
                response = client.get("/easy-mode?lang=fr", follow_redirects=False)

        self.assertEqual(response.status_code, 307)
        self.assertEqual(response.headers["location"], "/easy?lang=fr")

    def test_ui_preferences_language_resolution_and_save_are_local_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo_root = root / "repo"
            bridge = self.create_bridge(root)
            repo_root.mkdir()
            config = DashboardConfig(repo_root=repo_root, bridge_root=bridge)
            preferences_path = bridge / "config" / "ui_preferences.ini"
            with patch("radar_web.app.read_scheduler_status", return_value=SCHEDULER_NO_DATA):
                client = TestClient(create_app(config))

                self.assertIn(
                    '<html lang="fr">',
                    client.get("/", headers={"accept-language": "fr-FR,fr;q=0.9"}).text,
                )
                self.assertIn(
                    '<html lang="de">',
                    client.get("/?lang=de", headers={"accept-language": "fr-FR"}).text,
                )
                self.assertIn(
                    '<html lang="it">',
                    client.get("/", headers={"accept-language": "pt-BR,pt;q=0.9"}).text,
                )

                before_files = {
                    path.relative_to(bridge).as_posix()
                    for path in bridge.rglob("*")
                    if path.is_file()
                }
                saved = client.post(
                    "/api/preferences/ui",
                    json={"language": "en", "start_mode": "expert"},
                )
                after_files = {
                    path.relative_to(bridge).as_posix()
                    for path in bridge.rglob("*")
                    if path.is_file()
                }
                preference_response = client.get("/api/preferences/ui").json()
                html_after_save = client.get("/").text
                preferences_file_exists = preferences_path.is_file()

        self.assertEqual(saved.status_code, 200)
        self.assertTrue(saved.json()["no_scheduler_mutation"])
        self.assertTrue(saved.json()["no_action_mutation"])
        self.assertEqual(after_files - before_files, {"config/ui_preferences.ini"})
        self.assertTrue(preferences_file_exists)
        with self.assertRaises(ValueError):
            preferences_path.resolve().relative_to(repo_root.resolve())
        self.assertEqual(preference_response["preferences"]["language"], "en")
        self.assertEqual(preference_response["preferences"]["start_mode"], "expert")
        self.assertEqual(preference_response["effective_language"], "en")
        self.assertIn('<html lang="en">', html_after_save)

    def test_ui_preferences_reject_operational_or_repo_writes(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            bridge = self.create_bridge(root)
            config = DashboardConfig(repo_root=root / "repo", bridge_root=bridge)
            config.repo_root.mkdir()
            with patch("radar_web.app.read_scheduler_status", return_value=SCHEDULER_NO_DATA):
                client = TestClient(create_app(config))
                refused = client.post(
                    "/api/preferences/ui",
                    json={"language": "it", "scheduler": "mutate"},
                )

            inside_repo = root / "repo"
            inside_config = DashboardConfig(repo_root=inside_repo, bridge_root=inside_repo / "bridge")
            with patch("radar_web.app.read_scheduler_status", return_value=SCHEDULER_NO_DATA):
                inside_client = TestClient(create_app(inside_config))
                inside_refused = inside_client.post(
                    "/api/preferences/ui",
                    json={"language": "it"},
                )

        self.assertEqual(refused.status_code, 400)
        self.assertIn("unsupported_ui_preference_field:scheduler", refused.text)
        self.assertFalse((bridge / "config" / "ui_preferences.ini").exists())
        self.assertEqual(inside_refused.status_code, 400)
        self.assertIn("ui_preferences_inside_repository", inside_refused.text)
        self.assertFalse((inside_repo / "bridge" / "config" / "ui_preferences.ini").exists())

    def test_ui_navigation_audit_safe_get_links_and_controls(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = self.create_bridge(Path(tmpdir))
            run_id = next((bridge / "runs").iterdir()).name
            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            with patch("radar_web.app.read_scheduler_status", return_value=SCHEDULER_NO_DATA):
                client = TestClient(create_app(config))
                pages = [
                    "/",
                    "/easy",
                    "/easy-mode",
                    "/expert",
                    "/actions",
                    "/sources",
                    f"/easy/runs/{run_id}",
                    f"/runs/{run_id}",
                ]
                visited = set()
                excluded_buttons = set()
                select_names = set()
                for page in pages:
                    response = client.get(page)
                    self.assertEqual(response.status_code, 200)
                    parser = InternalLinkParser()
                    parser.feed(response.text)
                    for attrs in parser.selects:
                        if attrs.get("aria-label"):
                            select_names.add(attrs["aria-label"])
                        if attrs.get("id"):
                            select_names.add(attrs["id"])
                    for attrs in parser.buttons:
                        button_class = attrs.get("class", "")
                        if "decision-button" in button_class or "prompt-button" in button_class:
                            excluded_buttons.add(button_class)
                    for href in parser.links:
                        target = urlsplit(href)
                        if target.scheme or target.netloc or href.startswith("#"):
                            continue
                        safe_path = target.path or "/"
                        if safe_path.startswith("/api/actions") and safe_path != "/api/actions":
                            continue
                        if safe_path.startswith("/api/daily-sim"):
                            continue
                        if safe_path in visited:
                            continue
                        visited.add(safe_path)
                        link_response = client.get(href)
                        self.assertLess(link_response.status_code, 400, href)

        self.assertIn("language-select", select_names)
        self.assertIn("start-mode-select", select_names)
        self.assertTrue(any("decision-button" in value for value in excluded_buttons))
        self.assertTrue(any("prompt-button" in value for value in excluded_buttons))

    def test_action_center_get_is_run_scoped_and_read_only(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = self.create_bridge(Path(tmpdir))
            run_dir = next((bridge / "runs").iterdir())
            run_id = run_dir.name
            (run_dir / "0660-Codex_Prompt_Suggestions.md").write_text(
                "# Suggested only\n",
                encoding="utf-8",
            )
            (run_dir / "0680-Human_Approval_Gate_Report.md").write_text(
                "# HOLD\n",
                encoding="utf-8",
            )
            summary_path = run_dir / "0350-Daily_Sim_Summary.json"
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            summary["hag_status"] = "HOLD_FOR_HUMAN_APPROVAL"
            summary_path.write_text(json.dumps(summary), encoding="utf-8")
            current_detail = load_run_detail(bridge / "runs", run_id)
            self.assertIsNotNone(current_detail)
            historical_detail = json.loads(json.dumps(current_detail))
            historical_detail["run"]["run_id"] = "0320_0400_daily_sim_20260609_090000"
            historical_action = build_action_inbox([historical_detail]).actions[0]
            append_decision_log(
                bridge / "action_dispatch",
                historical_action,
                decision="approve_prompt",
                reason="historical approval",
            )
            dispatch_files_before = {
                path.relative_to(bridge / "action_dispatch").as_posix()
                for path in (bridge / "action_dispatch").rglob("*")
                if path.is_file()
            }

            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            with patch("radar_web.app.read_scheduler_status", return_value=SCHEDULER_NO_DATA):
                client = TestClient(create_app(config))
                actions = client.get("/api/actions").json()
                html = client.get("/actions?lang=it").text
                matrix_response = client.get(f"/api/runs/{run_id}/source-matrix")

            dispatch_files_after = {
                path.relative_to(bridge / "action_dispatch").as_posix()
                for path in (bridge / "action_dispatch").rglob("*")
                if path.is_file()
            }
            self.assertEqual(actions["run_scope_status"], "RUN_OUTPUT_ONLY")
            self.assertEqual(actions["current_run_decision_count"], 0)
            self.assertEqual(actions["historical_decision_count"], 1)
            self.assertEqual(actions["actions"][0]["decision_status"], "undecided")
            self.assertIn("In attesa di approvazione umana", html)
            self.assertEqual(matrix_response.status_code, 200)
            self.assertEqual(dispatch_files_after, dispatch_files_before)

    def test_home_formats_scheduler_dates_and_manual_trigger_note(self):
        scheduler = {
            "status": "Ready",
            "task_name": "AIReleaseRadar_DailyDryReport",
            "read_only": True,
            "last_run_time": "2026-06-10T19:01:02.0000000+02:00",
            "last_task_result": 0,
            "next_run_time": "2026-06-11T07:15:00.0000000+02:00",
            "number_of_missed_runs": 0,
            "interpretation": "OK",
            "warnings": [],
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = self.create_bridge(Path(tmpdir))
            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            with patch("radar_web.app.read_scheduler_status", return_value=scheduler):
                html = TestClient(create_app(config)).get("/expert?lang=en").text

        self.assertIn("Manual only / no auto-action", html)
        self.assertIn("2026-06-10 19:01", html)
        self.assertIn("2026-06-11 07:15", html)
        self.assertIn("Yes", html)

    def test_status_and_home_report_data_completeness_warnings(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = Path(tmpdir) / "bridge"
            run_dir = bridge / "runs" / "0320_0400_daily_sim_20260610_090000"
            run_dir.mkdir(parents=True)
            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            with patch("radar_web.app.read_scheduler_status", return_value=SCHEDULER_NO_DATA):
                client = TestClient(create_app(config))
                status = client.get("/api/status").json()
                html = client.get("/expert?lang=en").text

        self.assertEqual(status["data_completeness_status"], "PASS_WITH_WARNINGS")
        self.assertIn(
            "missing_json:0350-Daily_Sim_Summary.json",
            status["data_completeness_warnings"],
        )
        self.assertIn("Data Completeness Warnings", html)
        self.assertIn("missing_json:0180-Run_Summary.json", html)

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
                html = TestClient(create_app(config)).get(f"/runs/{run_dir.name}?lang=en").text

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

    def test_action_center_decision_prompt_and_backlog_flow(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = self.create_bridge(Path(tmpdir))
            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            with patch("radar_web.app.read_scheduler_status", return_value=SCHEDULER_NO_DATA):
                client = TestClient(create_app(config))

                html = client.get("/actions?lang=en").text
                self.assertIn("Action Center", html)
                self.assertIn("Approve prompt", html)
                self.assertIn("Review Action Center candidate", html)

                actions_response = client.get("/api/actions").json()
                self.assertEqual(actions_response["actions_count"], 1)
                action_id = actions_response["actions"][0]["action_id"]
                self.assertEqual(client.get(f"/api/actions/{action_id}").status_code, 200)

                refused = client.post(f"/api/actions/{action_id}/generate-prompt")
                self.assertEqual(refused.status_code, 400)
                self.assertEqual(refused.json()["status"], "REFUSED")

                decision = client.post(
                    f"/api/actions/{action_id}/decision",
                    json={
                        "decision": "approve_prompt",
                        "reason": "operator approved prompt pack",
                        "operator": "Alberto",
                    },
                )
                self.assertEqual(decision.status_code, 200)
                self.assertEqual(decision.json()["status"], "PASS")

                generated = client.post(f"/api/actions/{action_id}/generate-prompt")
                self.assertEqual(generated.status_code, 200)
                prompt_paths = generated.json()["paths"]
                self.assertEqual(len(prompt_paths), 1)
                self.assertTrue(Path(prompt_paths[0]).is_file())
                self.assertEqual(Path(prompt_paths[0]).suffix, ".md")

                backlog = client.post("/api/actions/export-backlog")
                self.assertEqual(backlog.status_code, 200)
                self.assertEqual(backlog.json()["status"], "PASS")
                for raw_path in backlog.json()["paths"]:
                    self.assertTrue(Path(raw_path).is_file())

                decision_log = bridge / "action_dispatch" / "decision_log.jsonl"
                self.assertTrue(decision_log.is_file())
                self.assertIn("approve_prompt", decision_log.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
