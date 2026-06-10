import unittest

from radar.action_triage import ActionTriageResult, TriageEntry
from radar.prompt_suggestions import suggest_codex_prompts


class PromptSuggestionsTests(unittest.TestCase):
    def test_generates_suggested_only_prompt_for_candidate(self):
        triage = ActionTriageResult(
            status="ACTION_REVIEW_REQUIRED",
            entries=[
                TriageEntry(
                    triage_class="codex_prompt_candidate",
                    title="Codex CLI changed",
                    target_project="AI Software Factory",
                    project_key="ai_software_factory",
                    reason="direct project signal",
                    risk_class="L1/L2",
                )
            ],
            counts={"codex_prompt_candidate": 1},
            warnings=[],
        )

        pack = suggest_codex_prompts(triage)

        self.assertEqual(len(pack.suggestions), 1)
        self.assertEqual(pack.suggestions[0].status, "suggested_only")
        self.assertIn("Do not commit", pack.suggestions[0].prompt_text)

    def test_skips_monitor_only_entries(self):
        triage = ActionTriageResult(
            status="PASS",
            entries=[
                TriageEntry(
                    triage_class="monitor",
                    title="Monitor item",
                    target_project="Mixed",
                    project_key=None,
                    reason="monitor only",
                    risk_class="L1",
                )
            ],
            counts={"monitor": 1},
            warnings=[],
        )

        pack = suggest_codex_prompts(triage)

        self.assertEqual(len(pack.suggestions), 0)
        self.assertIn("no_prompt_suggestions_generated", pack.warnings)


if __name__ == "__main__":
    unittest.main()
