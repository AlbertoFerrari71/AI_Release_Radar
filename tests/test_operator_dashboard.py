import unittest

from radar.operator_dashboard import render_operator_dashboard


class OperatorDashboardTests(unittest.TestCase):
    def test_renders_required_dashboard_fields(self):
        dashboard = render_operator_dashboard(
            {
                "result": {
                    "status": "CHANGES_FOUND",
                    "source_count": 11,
                    "parsed_count": 1,
                    "item_count": 10,
                    "direct_action_count": 10,
                    "monitor_only_action_count": 50,
                }
            },
            daily_quality_gate={
                "overall_daily_review_status": "ACTION_REVIEW_REQUIRED",
                "source_coverage_status": "WARN",
            },
            action_triage={"counts": {"manual_review": 11}},
            prompt_suggestions={"suggestions_count": 2},
            hag_status="HUMAN_APPROVAL_REQUIRED",
        )

        self.assertIn("run_status: CHANGES_FOUND", dashboard)
        self.assertIn("prompt_suggestions: 2", dashboard)
        self.assertIn("no_auto_action: confirmed", dashboard)


if __name__ == "__main__":
    unittest.main()
