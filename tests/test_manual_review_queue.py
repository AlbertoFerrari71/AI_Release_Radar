import unittest

from radar.manual_review_queue import build_manual_review_queue


class ManualReviewQueueTests(unittest.TestCase):
    def test_builds_source_queue_for_manual_review_and_unsupported_sources(self):
        queue = build_manual_review_queue(
            result={"source_count": 3},
            source_diagnostics=[
                self.source("github_api_openai_codex_releases", "parsed"),
                self.source(
                    "openai_release_notes_hub",
                    "manual_review_required",
                    registry_recommended_follow_up="manual_review_source",
                    scheduler_readiness="hold",
                ),
                self.source(
                    "openai_codex_changelog",
                    "fetched_but_unsupported",
                    coverage_priority="P1",
                    registry_recommended_follow_up="evaluate_structured_endpoint",
                    scheduler_readiness="warn",
                ),
            ],
            metrics={
                "source_count": 3,
                "parsed_count": 1,
                "direct_action_count": 0,
            },
        )

        self.assertEqual([entry["source_id"] for entry in queue], [
            "openai_codex_changelog",
            "openai_release_notes_hub",
        ])
        self.assertEqual(queue[0]["severity"], "high")
        self.assertEqual(queue[0]["recommended_follow_up"], "evaluate_structured_endpoint")
        self.assertTrue(queue[0]["blocking_for_scheduler"])
        self.assertEqual(queue[1]["reason"], "manual_review_required")

    def test_adds_action_queue_entry_for_direct_actions(self):
        queue = build_manual_review_queue(
            result={"source_count": 1},
            source_diagnostics=[self.source("github_api_openai_codex_releases", "parsed")],
            metrics={
                "source_count": 1,
                "parsed_count": 1,
                "direct_action_count": 2,
            },
        )

        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["type"], "action")
        self.assertEqual(queue[0]["reason"], "direct_actions_present")
        self.assertEqual(queue[0]["count"], 2)
        self.assertTrue(queue[0]["blocking_for_scheduler"])

    def test_adds_critical_queue_entry_for_zero_parsed_sources(self):
        queue = build_manual_review_queue(
            result={"source_count": 2},
            source_diagnostics=[
                self.source("openai_api_changelog", "fetched_but_unsupported"),
                self.source("openai_api_deprecations", "fetched_but_unsupported"),
            ],
            metrics={
                "source_count": 2,
                "parsed_count": 0,
                "direct_action_count": 0,
            },
        )

        self.assertTrue(any(entry["reason"] == "parsed_count_zero" for entry in queue))
        zero_entry = next(entry for entry in queue if entry["reason"] == "parsed_count_zero")
        self.assertEqual(zero_entry["severity"], "critical")
        self.assertTrue(zero_entry["blocking_for_scheduler"])

    def source(
        self,
        source_id: str,
        diagnostic_status: str,
        *,
        coverage_priority: str = "P3",
        registry_recommended_follow_up: str = "keep_diagnostic_no_parser",
        scheduler_readiness: str = "hold",
    ):
        return {
            "source_id": source_id,
            "diagnostic_status": diagnostic_status,
            "coverage_priority": coverage_priority,
            "registry_recommended_follow_up": registry_recommended_follow_up,
            "scheduler_readiness": scheduler_readiness,
        }


if __name__ == "__main__":
    unittest.main()
