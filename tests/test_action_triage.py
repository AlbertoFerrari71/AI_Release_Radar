import unittest

from radar.action_triage import triage_daily_actions


class ActionTriageTests(unittest.TestCase):
    def test_blocks_direct_actions_by_low_coverage(self):
        result = {
            "source_count": 11,
            "parsed_count": 1,
            "direct_action_count": 10,
            "monitor_only_action_count": 50,
        }
        gate = {
            "status": "ACTION_REVIEW_REQUIRED",
            "metrics": result,
            "manual_review_queue": [{"source_id": "x", "reason": "direct_actions_present"}],
        }
        quality = {
            "source_coverage_status": "WARN",
            "actionability_status": "ACTION_REVIEW_REQUIRED",
        }

        triage = triage_daily_actions(
            {"result": result},
            automation_gate=gate,
            daily_quality_gate=quality,
        )

        self.assertEqual(triage.status, "HOLD")
        self.assertEqual(triage.counts["blocked_by_coverage"], 10)
        self.assertEqual(triage.counts["monitor"], 50)
        self.assertGreater(triage.counts["manual_review"], 0)

    def test_explicit_direct_impact_can_be_prompt_candidate(self):
        result = {
            "source_count": 2,
            "parsed_count": 2,
            "direct_action_count": 1,
            "project_impacts": [
                {
                    "title": "Codex CLI changed",
                    "project_key": "ai_software_factory",
                    "project_name": "AI Software Factory",
                    "action_type": "direct_action",
                    "category": "codex_cli",
                    "score": 80,
                }
            ],
        }

        triage = triage_daily_actions(
            {"result": result},
            automation_gate={"status": "PASS", "metrics": result, "manual_review_queue": []},
            daily_quality_gate={"source_coverage_status": "PASS", "actionability_status": "PASS"},
        )

        self.assertEqual(triage.counts["codex_prompt_candidate"], 1)
        self.assertEqual(triage.status, "ACTION_REVIEW_REQUIRED")


if __name__ == "__main__":
    unittest.main()
