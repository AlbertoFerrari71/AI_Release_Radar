import unittest
from pathlib import Path

from radar.json_utils import read_json
from radar.report_engine import (
    ReportInput,
    load_report_input,
    render_compact_markdown_report,
    render_full_markdown_report,
    render_report_status,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "examples" / "fixtures"
INPUT_PATH = FIXTURES_DIR / "0080_report_input.json"
EXPECTED_FULL_PATH = FIXTURES_DIR / "0080_report_expected_full.md"
EXPECTED_COMPACT_PATH = FIXTURES_DIR / "0080_report_expected_compact.md"


class ReportEngineTests(unittest.TestCase):
    def load_report_input(self) -> ReportInput:
        return load_report_input(read_json(INPUT_PATH))

    def test_load_report_input_loads_complete_fixture(self):
        report_input = self.load_report_input()
        self.assertEqual(report_input.run_id, "0080-offline-report-fixture")
        self.assertEqual(len(report_input.items_by_id), 5)
        self.assertEqual(len(report_input.classifications_by_id), 5)
        self.assertEqual(len(report_input.scores_by_id), 5)
        self.assertEqual(len(report_input.project_impacts), 7)
        self.assertEqual(report_input.diff_result.unchanged_count, 2)

    def test_render_report_status_flags_critical_fixture(self):
        self.assertIn(render_report_status(self.load_report_input()), {"ACTION_RECOMMENDED", "CRITICAL"})

    def test_full_report_contains_required_sections(self):
        full = render_full_markdown_report(self.load_report_input())
        for section in (
            "# AI Release Radar Report — 0080-offline-report-fixture",
            "## 1. Executive summary",
            "## 2. Source and run metadata",
            "## 3. Diff summary",
            "## 4. New items",
            "## 5. Changed items",
            "## 6. Removed items",
            "## 7. Top relevance scores",
            "## 8. Project impacts",
            "## 9. Recommended actions",
            "## 10. Risks and caveats",
            "## 11. Next step recommendation",
        ):
            self.assertIn(section, full)

    def test_compact_report_contains_required_sections(self):
        compact = render_compact_markdown_report(self.load_report_input())
        for section in (
            "# AI Release Radar Compact Report — 0080-offline-report-fixture",
            "## Summary",
            "## Top changes",
            "## Main project impacts",
            "## Recommended next action",
        ):
            self.assertIn(section, compact)
        line_count = len(compact.splitlines())
        self.assertGreaterEqual(line_count, 30)
        self.assertLessEqual(line_count, 60)

    def test_full_report_matches_golden_fixture(self):
        actual = render_full_markdown_report(self.load_report_input())
        expected = EXPECTED_FULL_PATH.read_text(encoding="utf-8")
        self.assertEqual(actual, expected)

    def test_compact_report_matches_golden_fixture(self):
        actual = render_compact_markdown_report(self.load_report_input())
        expected = EXPECTED_COMPACT_PATH.read_text(encoding="utf-8")
        self.assertEqual(actual, expected)

    def test_reports_end_with_final_newline(self):
        report_input = self.load_report_input()
        self.assertTrue(render_full_markdown_report(report_input).endswith("\n"))
        self.assertTrue(render_compact_markdown_report(report_input).endswith("\n"))

    def test_output_is_deterministic(self):
        report_input = self.load_report_input()
        self.assertEqual(
            render_full_markdown_report(report_input),
            render_full_markdown_report(report_input),
        )
        self.assertEqual(
            render_compact_markdown_report(report_input),
            render_compact_markdown_report(report_input),
        )

    def test_recommended_actions_are_derived_from_project_impacts(self):
        report_input = self.load_report_input()
        full = render_full_markdown_report(report_input)
        for impact in report_input.project_impacts:
            for action in impact.suggested_actions:
                self.assertIn(action, full)

    def test_risks_and_caveats_include_offline_no_live_no_llm(self):
        full = render_full_markdown_report(self.load_report_input())
        self.assertIn("offline fixture only", full)
        self.assertIn("no live fetch", full)
        self.assertIn("no LLM", full)
        self.assertIn("report based on deterministic rules", full)

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

    def test_renderer_does_not_write_files_directly(self):
        report_input = self.load_report_input()
        before = self.repo_files()
        render_full_markdown_report(report_input)
        render_compact_markdown_report(report_input)
        after = self.repo_files()
        self.assertEqual(before, after)

    def repo_files(self) -> set[str]:
        return {
            str(path.relative_to(REPO_ROOT))
            for path in REPO_ROOT.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and "__pycache__" not in path.parts
        }


if __name__ == "__main__":
    unittest.main()
