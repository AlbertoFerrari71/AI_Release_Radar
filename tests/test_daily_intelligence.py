import json
import tempfile
import unittest
from pathlib import Path

from radar.daily_intelligence import (
    FORBIDDEN_ACTIONS,
    build_daily_intelligence,
    load_project_impact_map,
    write_daily_intelligence_outputs,
)
from radar.json_utils import read_json


REPO_ROOT = Path(__file__).resolve().parents[1]
PROJECT_MAP_PATH = REPO_ROOT / "config" / "project_impact_map.json"


class DailyIntelligenceTests(unittest.TestCase):
    def create_bridge(self, root: Path) -> tuple[Path, Path]:
        bridge = root / "bridge"
        run_dir = bridge / "runs" / "0320_0400_daily_sim_20260614_070000"
        run_dir.mkdir(parents=True)
        daily_summary = {
            "status": "CHANGES_FOUND",
            "automation_gate_status": "ACTION_REVIEW_REQUIRED",
            "scheduler_readiness_recommendation": "HOLD",
            "manual_review_queue_count": 1,
            "prompt_suggestions_count": 1,
            "hag_status": "HOLD_FOR_HUMAN_APPROVAL",
            "daily_quality_gate_v2": {
                "overall_daily_review_status": "ACTION_REVIEW_REQUIRED",
                "source_coverage_status": "WARN",
            },
            "real_run": {
                "status": "CHANGES_FOUND",
                "source_count": 3,
                "parsed_count": 2,
                "item_count": 2,
                "direct_action_count": 1,
                "monitor_only_action_count": 1,
                "source_diagnostics": [
                    {
                        "source_id": "openai_release_notes_hub",
                        "provider": "openai",
                        "diagnostic_status": "manual_review_required",
                        "manual_review_required": True,
                        "http_status_code": 403,
                        "item_count": 0,
                        "recommended_follow_up": "manual_review_source",
                    },
                    {
                        "source_id": "github_api_openai_codex_releases",
                        "provider": "github",
                        "diagnostic_status": "parsed",
                        "manual_review_required": False,
                        "http_status_code": 200,
                        "item_count": 2,
                        "recommended_follow_up": "use_parsed_items",
                    },
                ],
            },
            "action_triage": {
                "status": "HOLD",
                "entries": [
                    {
                        "triage_class": "blocked_by_coverage",
                        "title": "Review Codex CLI workflow change",
                        "target_project": "AI Software Factory",
                        "project_key": "ai_software_factory",
                        "reason": "direct project signal can affect Codex workflow",
                        "risk_class": "L1/L2",
                        "item_category": "codex_cli",
                        "score": 82,
                    }
                ],
            },
            "prompt_suggestions": {
                "status": "suggested_only",
                "suggestions_count": 1,
                "suggestions": [
                    {
                        "suggested_step_number": "PS-001",
                        "title": "Review AI Release Radar Easy Mode copy",
                        "status": "suggested_only",
                        "target_project": "AI Release Radar",
                        "project_key": "ai_release_radar",
                        "risk_class": "L1",
                    }
                ],
            },
            "auto_action_executed": False,
            "email_sent": False,
            "llm_called": False,
        }
        files = {
            "0180-Report_Compact.md": "# Compact\n",
            "0180-Run_Summary.json": json.dumps(
                {"schema_version": 1, "result": daily_summary["real_run"]},
            ),
            "0350-Daily_Sim_Summary.json": json.dumps(daily_summary),
            "0630-Daily_Quality_Gate_V2.json": json.dumps(daily_summary["daily_quality_gate_v2"]),
            "0650-Action_Triage.json": json.dumps(daily_summary["action_triage"]),
            "0660-Codex_Prompt_Suggestions.json": json.dumps(daily_summary["prompt_suggestions"]),
            "0680-Human_Approval_Gate_Report.md": "# HAG\n",
        }
        for name, text in files.items():
            (run_dir / name).write_text(text, encoding="utf-8")
        return bridge, run_dir

    def test_builds_human_brief_and_ai_model_packet_from_fixture(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _bridge, run_dir = self.create_bridge(Path(tmpdir))
            packet = build_daily_intelligence(
                run_dir,
                project_map_path=PROJECT_MAP_PATH,
                generated_at_utc="2026-06-14T08:00:00Z",
            )

        human = packet["human_brief"]
        ai_packet = packet["ai_model_packet"]
        self.assertEqual(human["date"], "2026-06-14")
        self.assertEqual(human["traffic_light"]["color"], "red")
        self.assertIn("decisione", human["one_sentence_summary"])
        self.assertTrue(human["hag_status"]["preserved"])
        self.assertTrue(human["manual_only"])
        self.assertTrue(ai_packet["facts"])
        self.assertTrue(ai_packet["inferences"])
        self.assertNotEqual(ai_packet["facts"], ai_packet["inferences"])

    def test_project_impact_map_is_configurable_and_explains_matches(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _bridge, run_dir = self.create_bridge(Path(tmpdir))
            packet = build_daily_intelligence(run_dir, project_map_path=PROJECT_MAP_PATH)

        impacts = {
            impact["project_id"]: impact
            for impact in packet["project_impact_map"]["impacts"]
        }
        self.assertEqual(impacts["ai_software_factory"]["impact_level"], "high")
        self.assertEqual(impacts["ai_software_factory"]["certainty"], "certain")
        self.assertIn(impacts["ai_release_radar"]["impact_level"], {"medium", "high"})
        self.assertIn("default_action", impacts["codex_skills"])

    def test_forbidden_actions_are_explicit_and_not_executed(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            _bridge, run_dir = self.create_bridge(Path(tmpdir))
            packet = build_daily_intelligence(run_dir, project_map_path=PROJECT_MAP_PATH)

        human = packet["human_brief"]
        self.assertEqual(tuple(human["forbidden_actions"]), FORBIDDEN_ACTIONS)
        for action in human["suggested_manual_actions"]:
            self.assertTrue(action["manual_only"])
            self.assertTrue(action["not_executed"])
            self.assertTrue(action["forbidden_to_execute_automatically"])
        self.assertTrue(packet["ai_model_packet"]["no_runtime_llm"])

    def test_write_outputs_creates_json_markdown_and_no_last_latest(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge, _run_dir = self.create_bridge(Path(tmpdir))
            result = write_daily_intelligence_outputs(
                bridge_root=bridge,
                run_id="latest",
                project_map_path=PROJECT_MAP_PATH,
                generated_at_utc="2026-06-14T08:00:00Z",
            )
            output_dir = Path(result["output_dir"])
            created = sorted(path.name for path in output_dir.iterdir())
            human_json = read_json(result["human_brief_json"])

        self.assertEqual(result["status"], "PASS")
        self.assertEqual(len(created), 5)
        self.assertTrue(any(name.endswith("-Human_Brief.md") for name in created))
        self.assertTrue(any(name.endswith("-AI_Model_Packet.json") for name in created))
        self.assertFalse(any(name.startswith(("LAST-", "latest-")) for name in created))
        self.assertEqual(human_json["brief_type"], "human_daily_brief")

    def test_project_impact_map_schema_loads(self):
        project_map = load_project_impact_map(PROJECT_MAP_PATH)

        self.assertEqual(project_map["schema_version"], 1)
        self.assertEqual(len(project_map["projects"]), 6)
        self.assertEqual(project_map["projects"][0]["project_id"], "ai_software_factory")


if __name__ == "__main__":
    unittest.main()
