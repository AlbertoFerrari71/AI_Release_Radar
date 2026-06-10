import unittest
from pathlib import Path
from types import SimpleNamespace

from radar.classification import ItemClassification
from radar.json_utils import read_json
from radar.models import Item
from radar.project_impact import (
    ACTION_TYPE_RANK,
    IMPACT_RANK,
    ProjectImpact,
    _readable_action_item_title,
    impact_item_for_projects,
    impact_scores_for_projects,
    load_project_map,
)
from radar.scoring import RelevanceScore


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "examples" / "fixtures"


class ProjectImpactTests(unittest.TestCase):
    def load_project_map(self):
        return load_project_map(read_json(FIXTURES_DIR / "0070_project_map.json"))

    def load_items_by_id(self) -> dict[str, Item]:
        data = read_json(FIXTURES_DIR / "0070_impact_items.json")
        return {item.item_id: item for item in (Item.from_dict(raw) for raw in data["items"])}

    def load_classifications_by_id(self) -> dict[str, ItemClassification]:
        data = read_json(FIXTURES_DIR / "0070_impact_classifications.json")
        return {
            classification.item_id: classification
            for classification in (
                ItemClassification(
                    item_id=raw["item_id"],
                    category=raw["category"],
                    severity=raw["severity"],
                    matched_keywords=raw["matched_keywords"],
                    reasons=raw["reasons"],
                )
                for raw in data["classifications"]
            )
        }

    def load_scores_by_id(self) -> dict[str, RelevanceScore]:
        data = read_json(FIXTURES_DIR / "0070_impact_scores.json")
        return {
            score.item_id: score
            for score in (
                RelevanceScore(
                    item_id=raw["item_id"],
                    score=raw["score"],
                    severity_score=raw["severity_score"],
                    keyword_score=raw["keyword_score"],
                    confidence_score=raw["confidence_score"],
                    novelty_score=raw["novelty_score"],
                    category_score=raw["category_score"],
                    reasons=raw["reasons"],
                )
                for raw in data["scores"]
            )
        }

    def impacts_for_item(self, item_id: str) -> list[ProjectImpact]:
        project_map = self.load_project_map()
        items_by_id = self.load_items_by_id()
        classifications_by_id = self.load_classifications_by_id()
        scores_by_id = self.load_scores_by_id()
        return impact_item_for_projects(
            items_by_id[item_id],
            classifications_by_id[item_id],
            scores_by_id[item_id],
            project_map,
        )

    def test_project_map_loads_successfully(self):
        project_map = self.load_project_map()
        self.assertEqual(len(project_map), 7)
        self.assertIn("ai_software_factory", project_map)
        self.assertIn("controllo_gestione_esolver", project_map)

    def test_codex_cli_impacts_ai_software_factory(self):
        impacts = self.impacts_for_item("0070_codex_cli_command")
        by_project = {impact.project_key: impact for impact in impacts}
        self.assertIn("ai_software_factory", by_project)
        self.assertIn(by_project["ai_software_factory"].impact_level, {"high", "medium"})
        self.assertEqual(by_project["ai_software_factory"].action_type, "direct_action")
        self.assertEqual(by_project["codex_skills"].action_type, "direct_action")
        self.assertEqual(by_project["agglodetect"].action_type, "monitor_only")
        self.assertEqual(by_project["agglodetect"].impact_level, "low")

    def test_codex_agents_md_impacts_asf_and_codex_skills_at_least_high(self):
        impacts = self.impacts_for_item("0070_agents_md_loading")
        by_project = {impact.project_key: impact for impact in impacts}
        self.assertGreaterEqual(IMPACT_RANK[by_project["ai_software_factory"].impact_level], 3)
        self.assertGreaterEqual(IMPACT_RANK[by_project["codex_skills"].impact_level], 3)
        self.assertEqual(by_project["ai_software_factory"].action_type, "direct_action")
        self.assertEqual(by_project["codex_skills"].action_type, "direct_action")

    def test_image_vision_impacts_image_projects(self):
        impacts = self.impacts_for_item("0070_image_vision")
        by_project = {impact.project_key: impact for impact in impacts}
        self.assertTrue({"agglodetect", "diamsign", "family_photo_organizer"} <= set(by_project))
        for project_key in ("agglodetect", "diamsign", "family_photo_organizer"):
            self.assertEqual(by_project[project_key].action_type, "direct_action")

    def test_data_analysis_impacts_controllo_gestione_esolver(self):
        impacts = self.impacts_for_item("0070_data_analysis")
        by_project = {impact.project_key: impact for impact in impacts}
        self.assertIn("controllo_gestione_esolver", by_project)
        self.assertEqual(by_project["controllo_gestione_esolver"].action_type, "direct_action")

    def test_deprecation_impacts_api_platform_projects_at_least_high(self):
        impacts = self.impacts_for_item("0070_api_deprecation")
        project_map = self.load_project_map()
        api_project_keys = {
            project_key
            for project_key, raw_project in project_map.items()
            if "api_platform" in raw_project["categories"] or "deprecation" in raw_project["categories"]
        }
        by_project = {impact.project_key: impact for impact in impacts}
        self.assertTrue(api_project_keys <= set(by_project))
        self.assertGreaterEqual(IMPACT_RANK[by_project["ai_software_factory"].impact_level], 3)
        self.assertEqual(by_project["ai_software_factory"].action_type, "direct_action")
        for project_key in api_project_keys - {"ai_software_factory"}:
            self.assertEqual(by_project[project_key].action_type, "monitor_only")
            self.assertEqual(by_project[project_key].impact_level, "low")

    def test_security_generates_high_or_critical_sensitive_project_impacts(self):
        impacts = self.impacts_for_item("0070_security_sandbox")
        sensitive_projects = {
            "ai_software_factory",
            "family_photo_organizer",
            "mansionario_vivo",
            "diamsign",
            "controllo_gestione_esolver",
        }
        by_project = {impact.project_key: impact for impact in impacts}
        self.assertTrue(sensitive_projects <= set(by_project))
        for project_key in sensitive_projects:
            self.assertGreaterEqual(IMPACT_RANK[by_project[project_key].impact_level], 3)
            self.assertEqual(by_project[project_key].action_type, "direct_action")

    def test_non_relevant_item_produces_no_impacts(self):
        item = Item(
            item_id="non_relevant_web_search",
            source_id="offline-0070-impact-test",
            provider="openai_fixture",
            category="unknown",
            severity="info",
            title="Web search note",
            published_at="2026-06-09T12:00:00Z",
            url="https://example.invalid/0070/non-relevant",
            evidence="Offline fixture: search note unrelated to project map.",
            content_hash="hash-non-relevant",
            first_seen="2026-06-09",
            confidence=0.5,
        )
        classification = ItemClassification(
            item_id=item.item_id,
            category="web_search",
            severity="info",
            matched_keywords=["web search"],
            reasons=["test classification"],
        )
        score = RelevanceScore(
            item_id=item.item_id,
            score=20,
            severity_score=5,
            keyword_score=4,
            confidence_score=5,
            novelty_score=0,
            category_score=6,
            reasons=["test score"],
        )
        self.assertEqual(impact_item_for_projects(item, classification, score, self.load_project_map()), [])

    def test_reasons_and_suggested_actions_are_not_empty(self):
        impacts = self.impacts_for_item("0070_security_sandbox")
        self.assertTrue(impacts)
        for impact in impacts:
            self.assertTrue(impact.reasons)
            self.assertTrue(impact.suggested_actions)
            self.assertIn(impact.action_type, {"direct_action", "monitor_only", "no_action"})

    def test_direct_action_mentions_title_reason_and_next_step(self):
        impacts = self.impacts_for_item("0070_codex_cli_command")
        action = {
            impact.project_key: impact.suggested_actions[0]
            for impact in impacts
        }["ai_software_factory"]

        self.assertIn("Codex CLI command update detected.", action)
        self.assertIn("Direct action for AI Software Factory", action)
        self.assertIn("Reason: codex_cli matches this project", action)
        self.assertIn("Next step:", action)

    def test_monitor_only_action_avoids_unrelated_project_action(self):
        impacts = self.impacts_for_item("0070_codex_cli_command")
        action = {
            impact.project_key: impact.suggested_actions[0]
            for impact in impacts
        }["agglodetect"]

        self.assertIn("Codex CLI command update detected.", action)
        self.assertIn("Monitor-only for AggloDetect", action)
        self.assertIn("do not open implementation work", action)
        self.assertNotIn("review image pipeline", action)

    def test_no_action_recommendation_is_explicit_for_category_without_direct_rule(self):
        item = Item(
            item_id="experimental_item",
            source_id="offline-0270-impact-test",
            provider="openai_fixture",
            category="experimental",
            severity="info",
            title="Experimental platform note",
            published_at="2026-06-10T12:00:00Z",
            url="https://example.invalid/0270/experimental",
            evidence="Offline fixture: experimental note.",
            content_hash="hash-experimental",
            first_seen="2026-06-10",
            confidence=0.7,
        )
        classification = ItemClassification(
            item_id=item.item_id,
            category="experimental",
            severity="info",
            matched_keywords=[],
            reasons=["test classification"],
        )
        score = RelevanceScore(
            item_id=item.item_id,
            score=35,
            severity_score=5,
            keyword_score=0,
            confidence_score=7,
            novelty_score=15,
            category_score=8,
            reasons=["test score"],
        )
        project_map = {
            "sample_project": {
                "project_key": "sample_project",
                "project_name": "Sample Project",
                "categories": ["experimental"],
                "keywords": [],
                "sensitive": False,
                "suggested_actions": ["update sample project"],
            }
        }

        impacts = impact_item_for_projects(item, classification, score, project_map)

        self.assertEqual(len(impacts), 1)
        self.assertEqual(impacts[0].action_type, "no_action")
        self.assertEqual(impacts[0].impact_level, "low")
        self.assertIn("No project action for Sample Project", impacts[0].suggested_actions[0])

    def test_action_title_fallback_is_readable(self):
        item = SimpleNamespace(title="", item_id="missing_title_item")

        self.assertEqual(
            _readable_action_item_title(item),
            "Untitled radar item missing_title_item",
        )

    def test_output_is_sorted_deterministically(self):
        items_by_id = self.load_items_by_id()
        classifications_by_id = self.load_classifications_by_id()
        scores = list(reversed(list(self.load_scores_by_id().values())))
        impacts = impact_scores_for_projects(
            items_by_id,
            classifications_by_id,
            scores,
            self.load_project_map(),
        )
        sort_keys = [
            (
                impact.item_id,
                -IMPACT_RANK[impact.impact_level],
                -ACTION_TYPE_RANK[impact.action_type],
                impact.project_key,
            )
            for impact in impacts
        ]
        self.assertEqual(sort_keys, sorted(sort_keys))

    def test_expected_fixture_matches_generated_output(self):
        items_by_id = self.load_items_by_id()
        classifications_by_id = self.load_classifications_by_id()
        scores = list(self.load_scores_by_id().values())
        actual = [
            impact.to_dict()
            for impact in impact_scores_for_projects(
                items_by_id,
                classifications_by_id,
                scores,
                self.load_project_map(),
            )
        ]
        expected = read_json(FIXTURES_DIR / "0070_impact_expected.json")
        self.assertEqual(actual, expected["impacts"])

    def test_no_last_or_latest_files_exist(self):
        forbidden = [
            path
            for path in REPO_ROOT.rglob("*")
            if path.is_file()
            and ".git" not in path.parts
            and (path.name.startswith("LAST-") or path.name.startswith("latest-"))
        ]
        self.assertEqual(forbidden, [])


if __name__ == "__main__":
    unittest.main()
