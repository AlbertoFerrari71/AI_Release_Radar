"""Deterministic relevance scoring for classified radar items."""

from __future__ import annotations

from dataclasses import dataclass

from radar.classification import ItemClassification
from radar.models import DiffResult, Item


SEVERITY_SCORES: dict[str, int] = {
    "critical": 50,
    "high": 40,
    "medium": 25,
    "low": 10,
    "info": 5,
    "ignored": 0,
}

NOVELTY_SCORES: dict[str, int] = {
    "new": 15,
    "changed": 10,
    "removed": 12,
    "unchanged": 0,
}

HIGH_IMPACT_CATEGORY_SCORES = {
    "deprecation",
    "security",
    "billing",
    "api_platform",
    "codex_cli",
    "codex_agents_md",
    "codex_windows",
}

MEDIUM_IMPACT_CATEGORY_SCORES = {
    "image_vision",
    "data_analysis",
    "gpt_models",
    "chatgpt",
}


@dataclass(frozen=True, kw_only=True)
class RelevanceScore:
    """Auditable score with component-level reasons."""

    item_id: str
    score: int
    severity_score: int
    keyword_score: int
    confidence_score: int
    novelty_score: int
    category_score: int
    reasons: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "item_id": self.item_id,
            "score": self.score,
            "severity_score": self.severity_score,
            "keyword_score": self.keyword_score,
            "confidence_score": self.confidence_score,
            "novelty_score": self.novelty_score,
            "category_score": self.category_score,
            "reasons": list(self.reasons),
        }


def _category_score(category: str) -> int:
    if category in HIGH_IMPACT_CATEGORY_SCORES:
        return 10
    if category in MEDIUM_IMPACT_CATEGORY_SCORES:
        return 7
    if category == "unknown":
        return 0
    return 5


def score_item(
    item: Item,
    classification: ItemClassification,
    novelty: str = "unchanged",
) -> RelevanceScore:
    """Score one item using a deterministic integer-only formula."""
    if not isinstance(item, Item):
        raise ValueError("item must be an Item.")
    if not isinstance(classification, ItemClassification):
        raise ValueError("classification must be an ItemClassification.")
    if item.item_id != classification.item_id:
        raise ValueError("item and classification must have the same item_id.")
    if novelty not in NOVELTY_SCORES:
        raise ValueError(f"unsupported novelty: {novelty}")

    severity_score = SEVERITY_SCORES.get(classification.severity, 0)
    keyword_count = len(set(classification.matched_keywords))
    keyword_score = min(20, keyword_count * 4)
    confidence_score = round(item.confidence * 10)
    novelty_score = NOVELTY_SCORES[novelty]
    category_score = _category_score(classification.category)
    score = (
        severity_score
        + keyword_score
        + confidence_score
        + novelty_score
        + category_score
    )

    reasons = [
        f"severity {classification.severity}: {severity_score}",
        f"keywords {keyword_count}: {keyword_score}",
        f"confidence {item.confidence:.2f}: {confidence_score}",
        f"novelty {novelty}: {novelty_score}",
        f"category {classification.category}: {category_score}",
        f"total: {score}",
    ]

    return RelevanceScore(
        item_id=item.item_id,
        score=score,
        severity_score=severity_score,
        keyword_score=keyword_score,
        confidence_score=confidence_score,
        novelty_score=novelty_score,
        category_score=category_score,
        reasons=reasons,
    )


def score_diff_items(
    items_by_id: dict[str, Item],
    diff_result: DiffResult,
    classifications_by_id: dict[str, ItemClassification],
) -> list[RelevanceScore]:
    """Score new, changed and removed diff items, sorted by relevance."""
    if not isinstance(diff_result, DiffResult):
        raise ValueError("diff_result must be a DiffResult.")

    scores: list[RelevanceScore] = []
    for novelty, item_ids in (
        ("new", diff_result.new_items),
        ("changed", diff_result.changed_items),
        ("removed", diff_result.removed_items),
    ):
        for item_id in item_ids:
            item = items_by_id.get(item_id)
            classification = classifications_by_id.get(item_id)
            if item is None or classification is None:
                continue
            scores.append(score_item(item, classification, novelty))

    return sorted(scores, key=lambda relevance: (-relevance.score, relevance.item_id))
