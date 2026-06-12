import json
import tempfile
import unittest
from pathlib import Path

from radar.action_inbox import (
    append_decision_log,
    build_action_inbox,
    export_backlog,
    generate_prompt_pack,
    read_decision_log,
)


def run_detail(title="Codex dashboard release", score=72):
    return {
        "run": {
            "run_id": "0320_0400_daily_sim_20260611_071500",
            "run_dir": r"D:\Bridge\runs\0320_0400_daily_sim_20260611_071500",
            "sort_key": "2026-06-11T07:15:00+00:00",
            "source_count": 4,
            "parsed_count": 3,
            "hag_status": "HOLD_FOR_HUMAN_APPROVAL",
            "files": {
                "action_triage_json": r"D:\Bridge\runs\run\0650-Action_Triage.json",
                "hag_report_markdown": r"D:\Bridge\runs\run\0680-Human_Approval_Gate_Report.md",
            },
        },
        "direct_actions": [
            {
                "triage_class": "codex_prompt_candidate",
                "title": title,
                "target_project": "AI Release Radar",
                "project_key": "ai_release_radar",
                "reason": "direct project signal can become a suggested-only Codex prompt",
                "risk_class": "L1/L2",
                "item_category": "codex_cli",
                "score": score,
                "item_id": "item-codex-dashboard",
            }
        ],
        "blocked_actions": [],
        "monitor_only_summary": [],
        "manual_review_queue": [],
        "prompt_suggestions": [],
    }


class ActionInboxTests(unittest.TestCase):
    def test_action_inbox_scores_routes_and_blocks_auto_action(self):
        inbox = build_action_inbox([run_detail()], now="2026-06-11T08:00:00Z")

        self.assertEqual(inbox.run_id, "0320_0400_daily_sim_20260611_071500")
        self.assertEqual(len(inbox.actions), 1)
        action = inbox.actions[0]
        self.assertEqual(action.project_key, "ai_release_radar")
        self.assertEqual(action.project_name, "AI Release Radar")
        self.assertEqual(action.action_type, "prepare_prompt")
        self.assertEqual(action.priority, "high")
        self.assertGreaterEqual(action.priority_score, 80)
        self.assertEqual(action.decision_status, "undecided")
        self.assertEqual(action.safety_status, "requires_human_approval")
        self.assertFalse(action.prompt_generation_allowed)
        self.assertIn("external_repo_write", action.blocked_outputs)
        self.assertIn("llm_call", action.blocked_outputs)
        self.assertIn("scheduler_change", action.blocked_outputs)

    def test_decision_log_enables_prompt_pack_generation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatch_root = Path(tmpdir) / "bridge" / "action_dispatch"
            action = build_action_inbox([run_detail()]).actions[0]

            refused = generate_prompt_pack(dispatch_root, action)
            self.assertEqual(refused.status, "REFUSED")
            self.assertIn("prompt_generation_requires_human_decision", refused.warnings)

            decision = append_decision_log(
                dispatch_root,
                action,
                decision="approve_prompt",
                reason="approved in test",
            )
            self.assertEqual(decision.status, "PASS")

            records = read_decision_log(dispatch_root)
            approved = build_action_inbox([run_detail()], decision_records=records).actions[0]
            self.assertEqual(approved.decision_status, "approved_for_prompt")
            self.assertTrue(approved.prompt_generation_allowed)

            result = generate_prompt_pack(dispatch_root, approved, timestamp="2026-06-11T08:30:00Z")
            self.assertEqual(result.status, "PASS")
            self.assertEqual(len(result.paths), 1)
            prompt_path = Path(result.paths[0])
            self.assertEqual(prompt_path.suffix, ".md")
            text = prompt_path.read_text(encoding="utf-8")
            self.assertIn("prompt_status: suggested_only", text)
            self.assertIn("Non chiamare LLM", text)
            self.assertIn("Non modificare scheduler", text)

    def test_decision_log_records_are_scoped_to_the_current_run(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatch_root = Path(tmpdir) / "bridge" / "action_dispatch"
            historical = run_detail()
            historical["run"]["run_id"] = "0320_0400_daily_sim_20260610_071500"
            historical["run"]["sort_key"] = "2026-06-10T07:15:00+00:00"
            historical_action = build_action_inbox([historical]).actions[0]
            append_decision_log(
                dispatch_root,
                historical_action,
                decision="approve_prompt",
                reason="approved in a previous run",
            )

            records = read_decision_log(dispatch_root)
            current_action = build_action_inbox(
                [run_detail()],
                decision_records=records,
            ).actions[0]

            self.assertEqual(historical_action.action_key, current_action.action_key)
            self.assertNotEqual(historical_action.run_id, current_action.run_id)
            self.assertEqual(current_action.decision_status, "undecided")
            self.assertFalse(current_action.prompt_generation_allowed)

    def test_previous_decision_suppresses_noise_and_backlog_export_writes_bridge_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            dispatch_root = Path(tmpdir) / "bridge" / "action_dispatch"
            action = build_action_inbox([run_detail()]).actions[0]
            append_decision_log(dispatch_root, action, decision="ignore", reason="too noisy")

            records = read_decision_log(dispatch_root)
            inbox = build_action_inbox(
                [run_detail(), run_detail(title="Codex dashboard release", score=60)],
                decision_records=records,
            )
            suppressed = inbox.actions[0]
            self.assertEqual(suppressed.decision_status, "ignored")
            self.assertEqual(suppressed.trend_status, "previously_ignored")
            self.assertEqual(suppressed.priority, "monitor")
            self.assertEqual(suppressed.noise_status, "suppressed")

            result = export_backlog(dispatch_root, inbox.run_id, inbox.actions)
            self.assertEqual(result.status, "PASS")
            self.assertEqual({Path(path).name for path in result.paths}, {
                "1040-Action_Backlog.md",
                "1040-Action_Backlog.json",
            })
            markdown = Path(result.paths[0]).read_text(encoding="utf-8")
            data = json.loads(Path(result.paths[1]).read_text(encoding="utf-8"))
            self.assertIn("Ignored", markdown)
            self.assertTrue(data["no_auto_action"])

    def test_monitor_only_recurring_low_score_is_downgraded_to_monitor(self):
        latest = run_detail(title="Patch release already seen", score=45)
        latest["direct_actions"] = []
        latest["monitor_only_summary"] = [
            {
                "triage_class": "monitor",
                "title": "Patch release already seen",
                "target_project": "Codex_Skills",
                "project_key": "codex_skills",
                "reason": "monitor-only recurring patch",
                "risk_class": "L1",
                "score": 45,
                "item_id": "patch-item",
            }
        ]
        previous = run_detail(title="Patch release already seen", score=45)
        previous["direct_actions"] = []
        previous["monitor_only_summary"] = list(latest["monitor_only_summary"])

        action = build_action_inbox([latest, previous]).actions[0]

        self.assertEqual(action.action_type, "monitor_only")
        self.assertEqual(action.trend_status, "recurring")
        self.assertEqual(action.priority, "monitor")
        self.assertIn(action.noise_status, {"downgraded", "visible"})


if __name__ == "__main__":
    unittest.main()
