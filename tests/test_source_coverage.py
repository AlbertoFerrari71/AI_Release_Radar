import unittest

from radar.source_coverage import (
    build_source_coverage_matrix,
    evaluate_source_coverage_final_gate,
    render_source_coverage_final_gate_markdown,
    render_source_coverage_matrix_markdown,
    summarize_source_coverage_matrix,
)


class SourceCoverageTests(unittest.TestCase):
    def test_matrix_classifies_parsed_unsupported_failed_and_manual_review_sources(self):
        matrix = build_source_coverage_matrix(
            [
                {
                    "source_id": "github_api_openai_codex_releases",
                    "provider": "github",
                    "coverage_priority": "P0",
                    "diagnostic_status": "parsed",
                    "fetch_status": "fetched",
                    "parser_status": "parsed",
                    "http_status_code": 200,
                    "item_count": 10,
                    "manual_review_required": False,
                    "scheduler_readiness": "ready",
                    "recommended_follow_up": "use_parsed_items",
                    "parser_strategy": "github_api_releases",
                    "final_v1_status": "parsed",
                    "final_v1_reason": "Structured JSON parsed.",
                    "maintenance_backlog_category": "none",
                },
                {
                    "source_id": "openai_codex_changelog",
                    "provider": "openai",
                    "coverage_priority": "P1",
                    "diagnostic_status": "fetched_but_unsupported",
                    "fetch_status": "fetched",
                    "parser_status": "parser_skipped_unsupported_source",
                    "http_status_code": 200,
                    "item_count": 0,
                    "manual_review_required": False,
                    "scheduler_readiness": "hold",
                    "machine_readable_preferred": True,
                    "registry_recommended_follow_up": "evaluate_structured_endpoint",
                    "parser_strategy": "unsupported_diagnostic",
                    "final_v1_status": "unsupported_documented",
                    "final_v1_reason": "No structured endpoint selected for V1.",
                    "maintenance_backlog_category": "parser_candidate",
                },
                {
                    "source_id": "openai_release_notes_hub",
                    "provider": "openai",
                    "coverage_priority": "P2",
                    "diagnostic_status": "manual_review_required",
                    "fetch_status": "rejected",
                    "parser_status": "fetch_failed",
                    "http_status_code": 403,
                    "item_count": 0,
                    "manual_review_required": True,
                    "scheduler_readiness": "hold",
                    "error_code": "unexpected_status",
                    "recommended_follow_up": "manual_review_source",
                    "parser_strategy": "manual_review_only",
                    "final_v1_status": "manual_review_403",
                    "final_v1_reason": "403 requires manual review.",
                    "maintenance_backlog_category": "manual_review",
                },
                {
                    "source_id": "openai_model_release_notes",
                    "provider": "openai",
                    "coverage_priority": "P2",
                    "diagnostic_status": "fetch_failed",
                    "fetch_status": "failed",
                    "parser_status": "fetch_failed",
                    "http_status_code": 500,
                    "item_count": 0,
                    "manual_review_required": True,
                    "scheduler_readiness": "hold",
                    "error": "server_error",
                    "parser_strategy": "manual_review_only",
                    "final_v1_status": "manual_review_403",
                    "final_v1_reason": "Fetch failure remains manual review.",
                    "maintenance_backlog_category": "manual_review",
                },
            ]
        )
        summary = summarize_source_coverage_matrix(matrix)
        markdown = render_source_coverage_matrix_markdown(matrix)
        gate = evaluate_source_coverage_final_gate(matrix, parsed_count_target=1)
        gate_markdown = render_source_coverage_final_gate_markdown(gate)

        self.assertEqual(summary["source_count"], 4)
        self.assertEqual(summary["parsed_count"], 1)
        self.assertEqual(summary["unsupported_source_count"], 1)
        self.assertEqual(summary["unsupported_explained_count"], 1)
        self.assertEqual(summary["manual_review_required_count"], 2)
        self.assertEqual(summary["manual_review_explained_count"], 2)
        self.assertEqual(summary["failed_count"], 2)
        self.assertEqual(summary["http_403_count"], 1)
        self.assertEqual(summary["fragile_parser_count"], 0)
        self.assertTrue(summary["coverage_warning"])
        self.assertTrue(summary["final_classification_complete"])
        self.assertEqual(matrix[1]["machine_readable_alternative"], "evaluate_structured_endpoint")
        self.assertEqual(matrix[1]["final_v1_status"], "unsupported_documented")
        self.assertEqual(matrix[2]["http_status"], 403)
        self.assertEqual(gate["status"], "SOURCE_COVERAGE_FINAL_PASS_WITH_WARNINGS")
        self.assertIn("openai_codex_changelog", markdown)
        self.assertIn("Source Coverage Closure Gate", gate_markdown)


if __name__ == "__main__":
    unittest.main()
