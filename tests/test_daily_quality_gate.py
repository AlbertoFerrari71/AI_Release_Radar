import unittest

from radar.daily_quality_gate import evaluate_daily_quality_gate


class DailyQualityGateTests(unittest.TestCase):
    def test_separates_readability_coverage_and_actionability(self):
        gate = {
            "status": "ACTION_REVIEW_REQUIRED",
            "metrics": {
                "source_count": 11,
                "parsed_count": 1,
                "direct_action_count": 10,
                "monitor_only_action_count": 50,
                "manual_review_queue_count": 11,
                "unsupported_source_count": 10,
                "report_scorecard_status": "PASS",
            },
            "warnings": ["low_source_coverage: parsed_count/source_count=1/11"],
            "failures": [],
            "manual_review_queue": [{"reason": "direct_actions_present"}],
        }

        result = evaluate_daily_quality_gate(gate)

        self.assertEqual(result.report_readability_status, "PASS")
        self.assertEqual(result.source_coverage_status, "WARN")
        self.assertEqual(result.actionability_status, "ACTION_REVIEW_REQUIRED")
        self.assertEqual(result.overall_daily_review_status, "ACTION_REVIEW_REQUIRED")
        self.assertIn("direct_actions_require_human_approval", result.warnings)

    def test_no_overall_pass_when_dimension_fails(self):
        gate = {
            "status": "FAIL",
            "metrics": {
                "source_count": 11,
                "parsed_count": 0,
                "direct_action_count": 0,
                "report_scorecard_status": "PASS",
            },
            "warnings": [],
            "failures": ["parsed_count_zero"],
            "manual_review_queue": [],
        }

        result = evaluate_daily_quality_gate(gate)

        self.assertEqual(result.source_coverage_status, "FAIL")
        self.assertEqual(result.overall_daily_review_status, "FAIL")


if __name__ == "__main__":
    unittest.main()
