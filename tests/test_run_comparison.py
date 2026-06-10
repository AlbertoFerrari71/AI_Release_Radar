import unittest
from pathlib import Path

from radar.run_comparison import (
    compare_run_summaries,
    render_run_comparison_markdown,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


class RunComparisonTests(unittest.TestCase):
    def test_compare_run_summaries_reports_required_metrics(self):
        before = self.summary(
            source_count=11,
            parsed_count=1,
            item_count=10,
            project_impact_count=60,
            direct_action_count=60,
            monitor_only_action_count=0,
            failed_count=2,
            unsupported_source_count=8,
            scorecard="WARN",
        )
        after = self.summary(
            source_count=11,
            parsed_count=1,
            item_count=10,
            project_impact_count=60,
            direct_action_count=12,
            monitor_only_action_count=48,
            failed_count=1,
            unsupported_source_count=7,
            scorecard="PASS",
        )

        comparison = compare_run_summaries(before, after)

        self.assertEqual(comparison.status, "PASS")
        by_metric = {metric.metric: metric for metric in comparison.metrics}
        self.assertEqual(by_metric["sources_checked"].after, 11)
        self.assertEqual(by_metric["parsed_sources"].after, 1)
        self.assertEqual(by_metric["items"].after, 10)
        self.assertEqual(by_metric["project_impacts"].after, 60)
        self.assertEqual(by_metric["direct_actions"].delta, -48)
        self.assertEqual(by_metric["monitor_only_actions"].delta, 48)
        self.assertEqual(by_metric["failed_sources"].delta, -1)
        self.assertEqual(by_metric["unsupported_sources"].delta, -1)
        self.assertEqual(by_metric["scorecard_result"].before, "WARN")
        self.assertEqual(by_metric["scorecard_result"].after, "PASS")

    def test_compare_run_summaries_falls_back_to_source_diagnostics(self):
        before = {
            "result": {
                "source_count": 1,
                "parsed_count": 0,
                "item_count": 0,
                "project_impact_count": 0,
                "failed_count": 0,
            },
            "source_diagnostics": [
                {
                    "source_id": "openai_codex_skills",
                    "parser_status": "parser_skipped_unsupported_source",
                }
            ],
        }
        after = self.summary(unsupported_source_count=0)

        comparison = compare_run_summaries(before, after)

        by_metric = {metric.metric: metric for metric in comparison.metrics}
        self.assertEqual(by_metric["unsupported_sources"].before, 1)
        self.assertEqual(by_metric["unsupported_sources"].after, 0)
        self.assertEqual(comparison.status, "WARN")

    def test_render_run_comparison_markdown_is_deterministic(self):
        comparison = compare_run_summaries(self.summary(), self.summary(direct_action_count=2))
        markdown = render_run_comparison_markdown(comparison)

        self.assertIn("# AI Release Radar Run Comparison", markdown)
        self.assertIn("| direct_actions | 1 | 2 | 1 |", markdown)
        self.assertTrue(markdown.endswith("\n"))

    def test_no_last_or_latest_files_exist(self):
        forbidden = [
            path
            for path in REPO_ROOT.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and "__pycache__" not in path.parts
            and (path.name.startswith("LAST-") or path.name.startswith("latest-"))
        ]
        self.assertEqual(forbidden, [])

    def summary(
        self,
        *,
        source_count: int = 1,
        parsed_count: int = 1,
        item_count: int = 1,
        project_impact_count: int = 1,
        direct_action_count: int = 1,
        monitor_only_action_count: int = 0,
        failed_count: int = 0,
        unsupported_source_count: int = 0,
        scorecard: str = "PASS",
    ):
        return {
            "result": {
                "source_count": source_count,
                "parsed_count": parsed_count,
                "item_count": item_count,
                "project_impact_count": project_impact_count,
                "direct_action_count": direct_action_count,
                "monitor_only_action_count": monitor_only_action_count,
                "failed_count": failed_count,
                "unsupported_source_count": unsupported_source_count,
                "report_scorecard_status": scorecard,
            },
            "report_scorecard": {"status": scorecard},
        }


if __name__ == "__main__":
    unittest.main()
