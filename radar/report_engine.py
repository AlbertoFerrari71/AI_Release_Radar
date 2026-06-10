"""Deterministic Markdown report rendering for radar results."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from radar.classification import ItemClassification
from radar.models import DiffResult, Item
from radar.project_impact import IMPACT_RANK, ProjectImpact
from radar.scoring import RelevanceScore


REPORT_STATUSES = (
    "NO_CHANGE",
    "NO_PARSED_ITEMS",
    "CHANGES_FOUND",
    "ACTION_RECOMMENDED",
    "CRITICAL",
)
NEXT_STEP_RECOMMENDATION = "0090) CLI Dry Run"
_MISSING_SCORE = -1


@dataclass(frozen=True)
class ReportInput:
    """Fully prepared offline input for Markdown report rendering."""

    run_id: str
    generated_at: str
    source_id: str
    provider: str
    diff_result: DiffResult
    items_by_id: dict[str, Item]
    classifications_by_id: dict[str, ItemClassification]
    scores_by_id: dict[str, RelevanceScore]
    project_impacts: list[ProjectImpact]
    notes: list[str]


def render_full_markdown_report(report_input: ReportInput) -> str:
    """Render the full deterministic Markdown report."""
    _validate_report_input(report_input)
    status = render_report_status(report_input)
    top_score = _sorted_scores(report_input)[:1]
    top_score_line = (
        f"[INT] Top relevance item is `{top_score[0].item_id}` with score {top_score[0].score}."
        if top_score
        else "[INT] No relevance score is available for this report."
    )
    action_count = len(_recommended_actions(report_input))

    lines = [
        f"# AI Release Radar Report — {report_input.run_id}",
        "",
        "## 1. Executive summary",
        "",
        f"- [F] Report status: {status}.",
        f"- [F] Source `{report_input.source_id}` was provided by `{report_input.provider}`.",
        (
            "- [F] Diff contains "
            f"{len(report_input.diff_result.new_items)} new, "
            f"{len(report_input.diff_result.changed_items)} changed, "
            f"{len(report_input.diff_result.removed_items)} removed and "
            f"{report_input.diff_result.unchanged_count} unchanged item(s)."
        ),
        f"- {top_score_line}",
        f"- [PROP] Review {action_count} deterministic project action(s) before the next radar run.",
        "",
        "## 2. Source and run metadata",
        "",
        f"- [F] run_id: `{report_input.run_id}`.",
        f"- [F] generated_at: `{report_input.generated_at}`.",
        f"- [F] source_id: `{report_input.source_id}`.",
        f"- [F] provider: `{report_input.provider}`.",
    ]

    if report_input.notes:
        for note in sorted(report_input.notes):
            lines.append(f"- [F] note: {note}")
    else:
        lines.append("- [F] notes: none.")

    lines.extend(
        [
            "",
            "## 3. Diff summary",
            "",
            f"- [F] New items: {len(report_input.diff_result.new_items)}.",
            f"- [F] Changed items: {len(report_input.diff_result.changed_items)}.",
            f"- [F] Removed items: {len(report_input.diff_result.removed_items)}.",
            f"- [F] Unchanged items: {report_input.diff_result.unchanged_count}.",
            "",
            "## 4. New items",
            "",
        ]
    )
    lines.extend(_render_item_section(report_input, report_input.diff_result.new_items))
    lines.extend(["", "## 5. Changed items", ""])
    lines.extend(_render_item_section(report_input, report_input.diff_result.changed_items))
    lines.extend(["", "## 6. Removed items", ""])
    lines.extend(_render_item_section(report_input, report_input.diff_result.removed_items))
    lines.extend(["", "## 7. Top relevance scores", ""])
    lines.extend(_render_scores_section(report_input))
    lines.extend(["", "## 8. Project impacts", ""])
    lines.extend(_render_impacts_section(report_input))
    lines.extend(["", "## 9. Recommended actions", ""])
    lines.extend(_render_recommended_actions_section(report_input))
    lines.extend(
        [
            "",
            "## 10. Risks and caveats",
            "",
            "- [F] offline fixture only.",
            "- [F] no live fetch.",
            "- [F] no LLM.",
            "- [INT] report based on deterministic rules.",
            "",
            "## 11. Next step recommendation",
            "",
            f"- [PROP] {NEXT_STEP_RECOMMENDATION}.",
        ]
    )
    return _join_lines(lines)


def render_compact_markdown_report(report_input: ReportInput) -> str:
    """Render a compact deterministic Markdown report."""
    _validate_report_input(report_input)
    lines = [
        f"# AI Release Radar Compact Report — {report_input.run_id}",
        "",
        "## Summary",
        "",
        f"- [F] run_id: `{report_input.run_id}`.",
        f"- [F] source_id: `{report_input.source_id}`.",
        f"- [F] generated_at: `{report_input.generated_at}`.",
        f"- [F] status: {render_report_status(report_input)}.",
        (
            "- [F] diff: "
            f"{len(report_input.diff_result.new_items)} new, "
            f"{len(report_input.diff_result.changed_items)} changed, "
            f"{len(report_input.diff_result.removed_items)} removed, "
            f"{report_input.diff_result.unchanged_count} unchanged."
        ),
        "",
        "## Top changes",
        "",
    ]
    change_ids = _sorted_changed_item_ids(report_input)[:5]
    if change_ids:
        for index, item_id in enumerate(change_ids, start=1):
            item = report_input.items_by_id[item_id]
            classification = _classification_for_item(report_input, item)
            score = report_input.scores_by_id.get(item_id)
            lines.append(
                f"{index}. [F] `{item_id}` ({_novelty_for_item(report_input, item_id)}): "
                f"{item.title}; severity {classification.severity}; "
                f"category {classification.category}; score {_score_label(score)}."
            )
    else:
        lines.append("- [F] No new, changed or removed item.")

    lines.extend(["", "## Main project impacts", ""])
    impacts = _sorted_impacts(report_input)[:7]
    if impacts:
        for index, impact in enumerate(impacts, start=1):
            score = report_input.scores_by_id.get(impact.item_id)
            lines.append(
                f"{index}. [F] {impact.impact_level} - {impact.project_name} "
                f"for `{impact.item_id}`; score {_score_label(score)}."
            )
    else:
        lines.append("- [F] No project impact available.")

    lines.extend(["", "## Recommended next action", ""])
    actions = _recommended_actions(report_input)
    if actions:
        first_action = actions[0]
        lines.append(
            f"- [PROP] {first_action['project_name']}: {first_action['action']} "
            f"for `{first_action['item_id']}`."
        )
    else:
        lines.append("- [PROP] No project action before the next dry run.")
    lines.append(f"- [PROP] {NEXT_STEP_RECOMMENDATION}.")
    return _join_lines(lines)


def render_report_status(report_input: ReportInput) -> str:
    """Return the deterministic status label for one report input."""
    _validate_report_input(report_input)
    if any(
        _classification_for_item(report_input, item).severity == "critical"
        or item.severity == "critical"
        for item in report_input.items_by_id.values()
    ):
        return "CRITICAL"
    if any(impact.impact_level == "critical" for impact in report_input.project_impacts):
        return "CRITICAL"
    if any(impact.impact_level in {"high", "critical"} for impact in report_input.project_impacts):
        return "ACTION_RECOMMENDED"
    if any(score.score >= 70 for score in report_input.scores_by_id.values()):
        return "ACTION_RECOMMENDED"
    if (
        report_input.diff_result.new_items
        or report_input.diff_result.changed_items
        or report_input.diff_result.removed_items
    ):
        return "CHANGES_FOUND"
    return "NO_CHANGE"


def load_report_input(data: object) -> ReportInput:
    """Load a report input from an offline JSON-compatible mapping."""
    raw = _ensure_mapping(data, "ReportInput")
    diff_result = DiffResult.from_dict(raw.get("diff_result"))
    items_by_id = _load_items_by_id(raw)
    classifications_by_id = _load_classifications_by_id(raw)
    scores_by_id = _load_scores_by_id(raw)
    project_impacts = _load_project_impacts(raw.get("project_impacts", []))
    notes = _require_str_list(raw, "notes", allow_empty=True)

    run_id = _require_str(raw, "run_id")
    source_id = _require_str(raw, "source_id")
    if diff_result.source_id != source_id:
        raise ValueError("diff_result.source_id must match ReportInput.source_id.")

    _validate_referenced_ids(diff_result, items_by_id)
    return ReportInput(
        run_id=run_id,
        generated_at=_require_str(raw, "generated_at"),
        source_id=source_id,
        provider=_require_str(raw, "provider"),
        diff_result=diff_result,
        items_by_id=items_by_id,
        classifications_by_id=classifications_by_id,
        scores_by_id=scores_by_id,
        project_impacts=project_impacts,
        notes=notes,
    )


def _validate_report_input(report_input: ReportInput) -> None:
    if not isinstance(report_input, ReportInput):
        raise ValueError("report_input must be a ReportInput.")


def _ensure_mapping(data: object, context: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError(f"{context} must be a dict.")
    return data


def _require_str(data: dict[str, Any], field_name: str) -> str:
    value = data.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _require_str_list(
    data: dict[str, Any],
    field_name: str,
    *,
    allow_empty: bool = False,
) -> list[str]:
    value = data.get(field_name)
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    if not allow_empty and not value:
        raise ValueError(f"{field_name} must be a non-empty list.")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field_name}[{index}] must be a non-empty string.")
    return list(value)


def _require_int(data: dict[str, Any], field_name: str) -> int:
    value = data.get(field_name)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer.")
    return value


def _load_items_by_id(raw: dict[str, Any]) -> dict[str, Item]:
    if "items_by_id" in raw:
        source = _ensure_mapping(raw["items_by_id"], "items_by_id").values()
    else:
        items = raw.get("items")
        if not isinstance(items, list):
            raise ValueError("items must be a list when items_by_id is absent.")
        source = items
    items_by_id: dict[str, Item] = {}
    for item_data in source:
        item = Item.from_dict(item_data)
        if item.item_id in items_by_id:
            raise ValueError(f"duplicate item_id: {item.item_id}")
        items_by_id[item.item_id] = item
    return {item_id: items_by_id[item_id] for item_id in sorted(items_by_id)}


def _load_classifications_by_id(raw: dict[str, Any]) -> dict[str, ItemClassification]:
    if "classifications_by_id" in raw:
        source = _ensure_mapping(raw["classifications_by_id"], "classifications_by_id").values()
    else:
        classifications = raw.get("classifications")
        if not isinstance(classifications, list):
            raise ValueError(
                "classifications must be a list when classifications_by_id is absent."
            )
        source = classifications
    result: dict[str, ItemClassification] = {}
    for classification_data in source:
        classification_raw = _ensure_mapping(classification_data, "classification")
        classification = ItemClassification(
            item_id=_require_str(classification_raw, "item_id"),
            category=_require_str(classification_raw, "category"),
            severity=_require_str(classification_raw, "severity"),
            matched_keywords=_require_str_list(classification_raw, "matched_keywords"),
            reasons=_require_str_list(classification_raw, "reasons"),
        )
        if classification.item_id in result:
            raise ValueError(f"duplicate classification item_id: {classification.item_id}")
        result[classification.item_id] = classification
    return {item_id: result[item_id] for item_id in sorted(result)}


def _load_scores_by_id(raw: dict[str, Any]) -> dict[str, RelevanceScore]:
    if "scores_by_id" in raw:
        source = _ensure_mapping(raw["scores_by_id"], "scores_by_id").values()
    else:
        scores = raw.get("scores")
        if not isinstance(scores, list):
            raise ValueError("scores must be a list when scores_by_id is absent.")
        source = scores
    result: dict[str, RelevanceScore] = {}
    for score_data in source:
        score_raw = _ensure_mapping(score_data, "score")
        score = RelevanceScore(
            item_id=_require_str(score_raw, "item_id"),
            score=_require_int(score_raw, "score"),
            severity_score=_require_int(score_raw, "severity_score"),
            keyword_score=_require_int(score_raw, "keyword_score"),
            confidence_score=_require_int(score_raw, "confidence_score"),
            novelty_score=_require_int(score_raw, "novelty_score"),
            category_score=_require_int(score_raw, "category_score"),
            reasons=_require_str_list(score_raw, "reasons"),
        )
        if score.item_id in result:
            raise ValueError(f"duplicate score item_id: {score.item_id}")
        result[score.item_id] = score
    return {item_id: result[item_id] for item_id in sorted(result)}


def _load_project_impacts(data: object) -> list[ProjectImpact]:
    if not isinstance(data, list):
        raise ValueError("project_impacts must be a list.")
    impacts: list[ProjectImpact] = []
    for impact_data in data:
        impact_raw = _ensure_mapping(impact_data, "project impact")
        impact = ProjectImpact(
            item_id=_require_str(impact_raw, "item_id"),
            project_key=_require_str(impact_raw, "project_key"),
            project_name=_require_str(impact_raw, "project_name"),
            impact_level=_require_str(impact_raw, "impact_level"),
            reasons=_require_str_list(impact_raw, "reasons"),
            suggested_actions=_require_str_list(impact_raw, "suggested_actions"),
        )
        if impact.impact_level not in IMPACT_RANK:
            raise ValueError(f"unsupported impact_level: {impact.impact_level}")
        impacts.append(impact)
    return _sort_impacts(impacts)


def _validate_referenced_ids(diff_result: DiffResult, items_by_id: dict[str, Item]) -> None:
    for item_id in diff_result.new_items + diff_result.changed_items + diff_result.removed_items:
        if item_id not in items_by_id:
            raise ValueError(f"diff item_id missing from items: {item_id}")


def _classification_for_item(report_input: ReportInput, item: Item) -> ItemClassification:
    return report_input.classifications_by_id.get(
        item.item_id,
        ItemClassification(
            item_id=item.item_id,
            category=item.category,
            severity=item.severity,
            matched_keywords=[],
            reasons=["classification missing: item category and severity used"],
        ),
    )


def _sorted_scores(report_input: ReportInput) -> list[RelevanceScore]:
    return sorted(
        report_input.scores_by_id.values(),
        key=lambda score: (-score.score, score.item_id),
    )


def _sort_impacts(impacts: list[ProjectImpact]) -> list[ProjectImpact]:
    return sorted(
        impacts,
        key=lambda impact: (-IMPACT_RANK[impact.impact_level], impact.item_id, impact.project_key),
    )


def _sorted_impacts(report_input: ReportInput) -> list[ProjectImpact]:
    return _sort_impacts(report_input.project_impacts)


def _sorted_changed_item_ids(report_input: ReportInput) -> list[str]:
    item_ids = (
        list(report_input.diff_result.new_items)
        + list(report_input.diff_result.changed_items)
        + list(report_input.diff_result.removed_items)
    )
    return sorted(
        item_ids,
        key=lambda item_id: (
            -_score_value(report_input.scores_by_id.get(item_id)),
            item_id,
        ),
    )


def _novelty_for_item(report_input: ReportInput, item_id: str) -> str:
    if item_id in report_input.diff_result.new_items:
        return "new"
    if item_id in report_input.diff_result.changed_items:
        return "changed"
    if item_id in report_input.diff_result.removed_items:
        return "removed"
    return "unchanged"


def _score_value(score: RelevanceScore | None) -> int:
    return score.score if score is not None else _MISSING_SCORE


def _score_label(score: RelevanceScore | None) -> str:
    return str(score.score) if score is not None else "n/a"


def _render_item_section(report_input: ReportInput, item_ids: list[str]) -> list[str]:
    if not item_ids:
        return ["- [F] None."]
    lines: list[str] = []
    for item_id in sorted(item_ids):
        item = report_input.items_by_id[item_id]
        classification = _classification_for_item(report_input, item)
        score = report_input.scores_by_id.get(item_id)
        lines.extend(
            [
                f"- [F] `{item.item_id}` - {item.title}",
                f"  - [F] category: {classification.category}.",
                f"  - [F] severity: {classification.severity}.",
                f"  - [F] score: {_score_label(score)}.",
                f"  - [F] URL: {item.url}",
                f"  - [F] evidence: {item.evidence}",
            ]
        )
    return lines


def _render_scores_section(report_input: ReportInput) -> list[str]:
    scores = _sorted_scores(report_input)
    if not scores:
        return ["- [F] No relevance scores available."]
    lines: list[str] = []
    for index, score in enumerate(scores, start=1):
        item = report_input.items_by_id.get(score.item_id)
        classification = (
            _classification_for_item(report_input, item)
            if item is not None
            else report_input.classifications_by_id.get(score.item_id)
        )
        category = classification.category if classification is not None else "unknown"
        severity = classification.severity if classification is not None else "unknown"
        lines.append(
            f"{index}. [F] `{score.item_id}`: score {score.score}; "
            f"category {category}; severity {severity}."
        )
        lines.append(f"   - [INT] score reasons: {'; '.join(score.reasons)}.")
    return lines


def _render_impacts_section(report_input: ReportInput) -> list[str]:
    impacts = _sorted_impacts(report_input)
    if not impacts:
        return ["- [F] No project impacts available."]
    lines: list[str] = []
    for impact in impacts:
        lines.extend(
            [
                f"- [F] {impact.project_name} (`{impact.project_key}`)",
                f"  - [F] item_id: `{impact.item_id}`.",
                f"  - [F] impact_level: {impact.impact_level}.",
                f"  - [INT] reasons: {'; '.join(impact.reasons)}.",
                f"  - [PROP] suggested_actions: {'; '.join(impact.suggested_actions)}.",
            ]
        )
    return lines


def _recommended_actions(report_input: ReportInput) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for impact in _sorted_impacts(report_input):
        for action in impact.suggested_actions:
            key = (impact.project_key, action)
            if key in seen:
                continue
            seen.add(key)
            actions.append(
                {
                    "action": action,
                    "impact_level": impact.impact_level,
                    "item_id": impact.item_id,
                    "project_key": impact.project_key,
                    "project_name": impact.project_name,
                }
            )
    return actions


def _render_recommended_actions_section(report_input: ReportInput) -> list[str]:
    actions = _recommended_actions(report_input)
    if not actions:
        return ["- [PROP] No project action recommended by the current offline input."]
    return [
        f"{index}. [PROP] {action['project_name']}: {action['action']} "
        f"for `{action['item_id']}` ({action['impact_level']})."
        for index, action in enumerate(actions, start=1)
    ]


def _join_lines(lines: list[str]) -> str:
    return "\n".join(lines).rstrip("\n") + "\n"
