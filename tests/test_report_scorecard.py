import unittest
from dataclasses import replace
from pathlib import Path

from radar.json_utils import read_json
from radar.project_impact import ProjectImpact
from radar.report_engine import ReportInput, load_report_input
from radar.report_scorecard import (
    ReportScorecard,
    evaluate_report_scorecard,
    render_scorecard_markdown,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "examples" / "fixtures"
INPUT_PATH = FIXTURES_DIR / "0080_report_input.json"


class ReportScorecardTests(unittest.TestCase):
    def load_report_input(self) -> ReportInput:
        return load_report_input(read_json(INPUT_PATH))

    def live_result(self):
        return {
            "parsed_count": 1,
            "source_count": 2,
        }

    def source_diagnostics(self):
        return [
            {
                "source_id": "github_api_openai_codex_releases",
                "diagnostic_status": "parsed",
            },
            {
                "source_id": "openai_codex_changelog",
                "diagnostic_status": "fetched_but_unsupported",
            },
        ]

    def test_scorecard_passes_when_report_has_required_quality_signals(self):
        scorecard = evaluate_report_scorecard(
            self.load_report_input(),
            live_result=self.live_result(),
            source_diagnostics=self.source_diagnostics(),
            next_step="0300) Manual review.",
        )

        self.assertEqual(scorecard.status, "PASS")
        self.assertEqual(
            [finding.check for finding in scorecard.findings],
            [
                "has_readable_titles",
                "has_source_links",
                "has_parsed_source_count",
                "has_source_diagnostics",
                "has_actionable_project_actions",
                "has_no_item_id_only_top_actions",
                "has_noise_control",
                "has_next_step",
            ],
        )

    def test_scorecard_warns_when_optional_live_evidence_is_missing(self):
        scorecard = evaluate_report_scorecard(self.load_report_input())

        self.assertEqual(scorecard.status, "WARN")
        warnings = {
            finding.check
            for finding in scorecard.findings
            if finding.status == "WARN"
        }
        self.assertIn("has_parsed_source_count", warnings)
        self.assertIn("has_source_diagnostics", warnings)
        self.assertIn("has_next_step", warnings)

    def test_scorecard_fails_item_id_only_actions(self):
        report_input = self.load_report_input()
        bad_impact = ProjectImpact(
            item_id="0080_new_api_deprecation",
            project_key="sample",
            project_name="Sample",
            impact_level="medium",
            reasons=["test reason"],
            suggested_actions=["0080_new_api_deprecation"],
            action_type="direct_action",
        )
        report_input = replace(report_input, project_impacts=[bad_impact])

        scorecard = evaluate_report_scorecard(
            report_input,
            live_result=self.live_result(),
            source_diagnostics=self.source_diagnostics(),
            next_step="0300) Manual review.",
        )

        self.assertEqual(scorecard.status, "FAIL")
        failures = {
            finding.check
            for finding in scorecard.findings
            if finding.status == "FAIL"
        }
        self.assertIn("has_no_item_id_only_top_actions", failures)

    def test_render_scorecard_markdown_is_deterministic(self):
        scorecard = ReportScorecard(
            status="PASS",
            findings=[
                finding
                for finding in evaluate_report_scorecard(
                    self.load_report_input(),
                    live_result=self.live_result(),
                    source_diagnostics=self.source_diagnostics(),
                    next_step="0300) Manual review.",
                ).findings[:2]
            ],
        )

        self.assertEqual(
            render_scorecard_markdown(scorecard),
            [
                "- [F] Scorecard status: PASS.",
                "- [F] has_readable_titles: PASS - 3 changed item title(s) are readable",
                "- [F] has_source_links: PASS - changed items include source links",
            ],
        )

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


if __name__ == "__main__":
    unittest.main()
