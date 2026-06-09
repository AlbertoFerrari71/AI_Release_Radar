import unittest
from pathlib import Path

from radar.classification import ItemClassification, classify_item
from radar.json_utils import read_json
from radar.models import DiffResult, Item
from radar.scoring import score_diff_items, score_item


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "examples" / "fixtures"


class ScoringTests(unittest.TestCase):
    def item(
        self,
        item_id: str = "item_001",
        confidence: float = 0.8,
        title: str = "Offline scoring item",
        evidence: str = "Offline fixture evidence.",
    ) -> Item:
        return Item(
            item_id=item_id,
            source_id="offline-0060-scoring-test",
            provider="openai_fixture",
            category="unknown",
            severity="info",
            title=title,
            published_at="2026-06-09T10:00:00Z",
            url="https://example.invalid/0060/scoring",
            evidence=evidence,
            content_hash=f"hash-{item_id}",
            first_seen="2026-06-09",
            confidence=confidence,
        )

    def classification(
        self,
        severity: str = "medium",
        category: str = "codex_cli",
        keywords: list[str] | None = None,
        item_id: str = "item_001",
    ) -> ItemClassification:
        return ItemClassification(
            item_id=item_id,
            category=category,
            severity=severity,
            matched_keywords=keywords if keywords is not None else ["codex cli"],
            reasons=["test classification"],
        )

    def test_score_severity_ordering(self):
        item = self.item()
        scores = [
            score_item(item, self.classification(severity=severity)).score
            for severity in ("critical", "high", "medium", "low", "info")
        ]
        self.assertGreater(scores[0], scores[1])
        self.assertGreater(scores[1], scores[2])
        self.assertGreater(scores[2], scores[3])
        self.assertGreater(scores[3], scores[4])

    def test_novelty_new_scores_higher_than_changed_and_unchanged(self):
        item = self.item()
        classification = self.classification()
        new_score = score_item(item, classification, novelty="new").score
        changed_score = score_item(item, classification, novelty="changed").score
        unchanged_score = score_item(item, classification, novelty="unchanged").score
        self.assertGreater(new_score, changed_score)
        self.assertGreater(changed_score, unchanged_score)

    def test_confidence_changes_score(self):
        low_item = self.item(item_id="low_confidence", confidence=0.1)
        high_item = self.item(item_id="high_confidence", confidence=0.9)
        low_classification = self.classification(item_id=low_item.item_id)
        high_classification = self.classification(item_id=high_item.item_id)
        self.assertGreater(
            score_item(high_item, high_classification).score,
            score_item(low_item, low_classification).score,
        )

    def test_keyword_score_is_capped_at_20(self):
        item = self.item()
        classification = self.classification(
            keywords=["a", "b", "c", "d", "e", "f"],
        )
        score = score_item(item, classification)
        self.assertEqual(score.keyword_score, 20)

    def test_high_impact_category_score_is_10(self):
        item = self.item()
        score = score_item(item, self.classification(category="security"))
        self.assertEqual(score.category_score, 10)

    def test_total_score_is_sum_of_components(self):
        item = self.item(confidence=0.83)
        score = score_item(item, self.classification(), novelty="changed")
        self.assertEqual(
            score.score,
            score.severity_score
            + score.keyword_score
            + score.confidence_score
            + score.novelty_score
            + score.category_score,
        )

    def test_score_diff_items_output_is_sorted_by_score_desc_then_item_id(self):
        items_by_id = {
            "item_a": self.item("item_a", confidence=0.7),
            "item_b": self.item("item_b", confidence=0.9),
            "item_c": self.item("item_c", confidence=0.8),
        }
        classifications_by_id = {
            "item_a": self.classification("medium", item_id="item_a"),
            "item_b": self.classification("critical", "security", item_id="item_b"),
            "item_c": self.classification("high", "deprecation", item_id="item_c"),
        }
        diff_result = DiffResult(
            source_id="offline-0060-scoring-test",
            new_items=["item_a", "item_b"],
            changed_items=["item_c"],
            removed_items=[],
            unchanged_count=0,
        )
        scores = score_diff_items(items_by_id, diff_result, classifications_by_id)
        sort_keys = [(-score.score, score.item_id) for score in scores]
        self.assertEqual(sort_keys, sorted(sort_keys))

    def test_expected_fixture_matches_generated_scores(self):
        item_data = read_json(FIXTURES_DIR / "0060_scoring_items.json")
        diff_data = read_json(FIXTURES_DIR / "0060_scoring_diff.json")
        expected = read_json(FIXTURES_DIR / "0060_scoring_expected.json")
        items = [Item.from_dict(raw_item) for raw_item in item_data["items"]]
        diff_result = DiffResult.from_dict(diff_data)

        novelty_by_id = {item.item_id: "unchanged" for item in items}
        novelty_by_id.update({item_id: "new" for item_id in diff_result.new_items})
        novelty_by_id.update({item_id: "changed" for item_id in diff_result.changed_items})
        novelty_by_id.update({item_id: "removed" for item_id in diff_result.removed_items})

        actual = []
        for item in items:
            classification = classify_item(item)
            relevance = score_item(item, classification, novelty_by_id[item.item_id])
            actual.append(
                {
                    "category": classification.category,
                    "item_id": item.item_id,
                    "reasons": relevance.reasons,
                    "score": relevance.score,
                    "severity": classification.severity,
                }
            )
        actual.sort(key=lambda row: (-row["score"], row["item_id"]))
        self.assertEqual(actual, expected["items"])

    def test_removed_item_without_available_item_does_not_crash(self):
        diff_result = DiffResult(
            source_id="offline-0060-scoring-test",
            new_items=[],
            changed_items=[],
            removed_items=["missing_removed_item"],
            unchanged_count=0,
        )
        self.assertEqual(score_diff_items({}, diff_result, {}), [])

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
