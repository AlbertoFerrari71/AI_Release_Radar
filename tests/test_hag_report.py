import unittest

from radar.action_triage import ActionTriageResult
from radar.hag_report import build_hag_report
from radar.prompt_suggestions import PromptSuggestionPack


class HagReportTests(unittest.TestCase):
    def test_builds_hag_hold_for_blocked_actions(self):
        triage = ActionTriageResult(
            status="HOLD",
            entries=[],
            counts={
                "blocked_by_coverage": 2,
                "blocked_by_manual_review": 0,
                "codex_prompt_candidate": 0,
                "manual_review": 1,
            },
            warnings=[],
        )
        report = build_hag_report(
            {"result": {"status": "CHANGES_FOUND", "source_count": 11, "parsed_count": 1}},
            daily_quality_gate={"overall_daily_review_status": "ACTION_REVIEW_REQUIRED"},
            action_triage=triage,
            prompt_suggestions=PromptSuggestionPack(suggestions=[], warnings=[]),
        )

        self.assertEqual(report.status, "HOLD_FOR_HUMAN_APPROVAL")
        self.assertIn("auto_actions_executed: false", report.markdown)
        self.assertIn("A: approve one suggested prompt", report.markdown)


if __name__ == "__main__":
    unittest.main()
