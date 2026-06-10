"""Deterministic project impact mapping for scored radar items."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from radar.classification import ItemClassification
from radar.models import Item
from radar.scoring import RelevanceScore


IMPACT_LEVELS: tuple[str, ...] = ("critical", "high", "medium", "low", "none")
IMPACT_RANK: dict[str, int] = {
    "none": 0,
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}
ACTION_TYPES: tuple[str, ...] = ("direct_action", "monitor_only", "no_action")
ACTION_TYPE_RANK: dict[str, int] = {
    "no_action": 0,
    "monitor_only": 1,
    "direct_action": 2,
}

IMAGE_VISION_PROJECTS = {
    "agglodetect",
    "diamsign",
    "family_photo_organizer",
}

CODEX_AGENTS_PROJECTS = {
    "ai_software_factory",
    "codex_skills",
}
CODEX_WORKFLOW_CATEGORIES = {
    "codex_agents_md",
    "codex_app",
    "codex_cli",
    "codex_cloud",
    "codex_mcp",
    "codex_plugins",
    "codex_review",
    "codex_skills",
    "codex_windows",
}
DIRECT_ACTION_CATEGORIES_BY_PROJECT = {
    "ai_software_factory": CODEX_WORKFLOW_CATEGORIES
    | {"api_platform", "billing", "deprecation", "security"},
    "codex_skills": CODEX_WORKFLOW_CATEGORIES | {"security"},
    "family_photo_organizer": {"image_vision", "security"},
    "agglodetect": {"image_vision"},
    "diamsign": {"image_vision", "security"},
    "controllo_gestione_esolver": {"data_analysis", "security"},
    "mansionario_vivo": {"security"},
}
GENERIC_MONITOR_CATEGORIES = CODEX_WORKFLOW_CATEGORIES | {
    "api_platform",
    "deprecation",
    "gpt_models",
}


@dataclass(frozen=True)
class ProjectImpact:
    """Impact of one radar item on one target project."""

    item_id: str
    project_key: str
    project_name: str
    impact_level: str
    reasons: list[str]
    suggested_actions: list[str]
    action_type: str = "direct_action"

    def __post_init__(self) -> None:
        if self.impact_level not in IMPACT_RANK:
            raise ValueError(f"unsupported impact_level: {self.impact_level}")
        if self.action_type not in ACTION_TYPE_RANK:
            raise ValueError(f"unsupported action_type: {self.action_type}")

    def to_dict(self) -> dict[str, object]:
        return {
            "action_type": self.action_type,
            "impact_level": self.impact_level,
            "item_id": self.item_id,
            "project_key": self.project_key,
            "project_name": self.project_name,
            "reasons": list(self.reasons),
            "suggested_actions": list(self.suggested_actions),
        }


def _ensure_mapping(data: object, context: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError(f"{context} must be a dict.")
    return data


def _require_str(data: dict[str, Any], field_name: str) -> str:
    value = data.get(field_name)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _require_str_list(data: dict[str, Any], field_name: str) -> list[str]:
    value = data.get(field_name)
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field_name} must be a non-empty list.")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field_name}[{index}] must be a non-empty string.")
    return list(value)


def _optional_str_list(data: dict[str, Any], field_name: str) -> list[str]:
    value = data.get(field_name, [])
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{field_name}[{index}] must be a non-empty string.")
    return list(value)


def load_project_map(data: object) -> dict[str, object]:
    """Load and validate an offline project map."""
    raw = _ensure_mapping(data, "project map")
    projects = raw.get("projects")
    if not isinstance(projects, list) or not projects:
        raise ValueError("project map projects must be a non-empty list.")

    result: dict[str, object] = {}
    for index, project_data in enumerate(projects):
        project = _ensure_mapping(project_data, f"projects[{index}]")
        project_key = _require_str(project, "project_key")
        if project_key in result:
            raise ValueError(f"duplicate project_key: {project_key}")
        sensitive = project.get("sensitive", False)
        if not isinstance(sensitive, bool):
            raise ValueError("sensitive must be a boolean when present.")
        result[project_key] = {
            "project_key": project_key,
            "project_name": _require_str(project, "project_name"),
            "categories": sorted(set(_require_str_list(project, "categories"))),
            "keywords": sorted(set(_optional_str_list(project, "keywords"))),
            "sensitive": sensitive,
            "suggested_actions": _require_str_list(project, "suggested_actions"),
        }
    return result


def _max_level(current: str, minimum: str) -> str:
    if IMPACT_RANK[minimum] > IMPACT_RANK[current]:
        return minimum
    return current


def _min_level(current: str, maximum: str) -> str:
    if IMPACT_RANK[maximum] < IMPACT_RANK[current]:
        return maximum
    return current


def _base_impact_level(classification: ItemClassification, score: RelevanceScore) -> tuple[str, str]:
    category = classification.category
    severity = classification.severity
    if severity == "critical":
        return "critical", "critical severity on relevant project"
    if category in {"security", "deprecation"} and score.score >= 80:
        return "critical", f"{category} score {score.score} >= 80"
    if severity == "high":
        return "high", "high severity on relevant project"
    if score.score >= 70:
        return "high", f"score {score.score} >= 70"
    if severity == "medium":
        return "medium", "medium severity on relevant project"
    if score.score >= 45:
        return "medium", f"score {score.score} >= 45"
    return "low", "relevant category with low score"


def _project_relevance(
    classification: ItemClassification,
    project: dict[str, object],
) -> tuple[bool, list[str]]:
    categories = set(project["categories"])
    project_keywords = set(project["keywords"])
    matched_keywords = set(classification.matched_keywords)
    reasons: list[str] = []
    if classification.category in categories:
        reasons.append(f"category {classification.category} relevant to project")
    if classification.category == "deprecation" and "api_platform" in categories:
        reasons.append("deprecation relevant to API/platform project")
    keyword_matches = sorted(project_keywords & matched_keywords)
    if keyword_matches:
        reasons.append(f"matched project keywords: {', '.join(keyword_matches)}")
    return bool(reasons), reasons


def _apply_special_rules(
    impact_level: str,
    project: dict[str, object],
    classification: ItemClassification,
    score: RelevanceScore,
) -> tuple[str, list[str]]:
    project_key = str(project["project_key"])
    categories = set(project["categories"])
    category = classification.category
    reasons: list[str] = []

    if category == "security" and bool(project["sensitive"]):
        new_level = _max_level(impact_level, "high")
        if new_level != impact_level:
            reasons.append("security raises sensitive project impact to high")
        impact_level = new_level

    if category == "deprecation" and ("api_platform" in categories or "deprecation" in categories):
        new_level = _max_level(impact_level, "high")
        if new_level != impact_level:
            reasons.append("deprecation raises API/platform project impact to high")
        impact_level = new_level

    if category == "image_vision" and project_key in IMAGE_VISION_PROJECTS and score.score >= 40:
        new_level = _max_level(impact_level, "medium")
        if new_level != impact_level:
            reasons.append("image_vision raises image project impact to medium")
        impact_level = new_level

    if category == "codex_agents_md" and project_key in CODEX_AGENTS_PROJECTS:
        new_level = _max_level(impact_level, "high")
        if new_level != impact_level:
            reasons.append("codex_agents_md raises Codex workflow impact to high")
        impact_level = new_level

    if category == "billing" and project_key == "ai_software_factory":
        new_level = _max_level(impact_level, "medium")
        if new_level != impact_level:
            reasons.append("billing raises AI Software Factory impact to medium")
        impact_level = new_level

    return impact_level, reasons


def _action_type_for_impact(
    project: dict[str, object],
    classification: ItemClassification,
) -> tuple[str, str]:
    project_key = str(project["project_key"])
    category = classification.category
    direct_categories = DIRECT_ACTION_CATEGORIES_BY_PROJECT.get(project_key, set())
    if category in direct_categories:
        return "direct_action", f"category {category} is direct for {project_key}"
    if category == "security" and bool(project["sensitive"]):
        return "direct_action", "security is direct for sensitive project"
    if category in GENERIC_MONITOR_CATEGORIES:
        return "monitor_only", f"category {category} is monitor-only for {project_key}"
    return "no_action", f"category {category} has no direct action rule for {project_key}"


def _adjust_level_for_action_type(impact_level: str, action_type: str) -> tuple[str, list[str]]:
    if action_type == "direct_action":
        return impact_level, []
    if action_type == "monitor_only":
        adjusted = _min_level(impact_level, "low")
        if adjusted != impact_level:
            return adjusted, [f"monitor_only caps impact level from {impact_level} to low"]
        return adjusted, []
    adjusted = _min_level(impact_level, "low")
    if adjusted != impact_level:
        return adjusted, [f"no_action caps impact level from {impact_level} to low"]
    return adjusted, []


def _actions_for_impact(
    project: dict[str, object],
    classification: ItemClassification,
    action_type: str,
) -> list[str]:
    if action_type == "direct_action":
        return list(project["suggested_actions"])
    if action_type == "monitor_only":
        return [
            (
                "monitor only: keep the project visible for "
                f"{classification.category} but do not open implementation work yet"
            )
        ]
    return ["no action: keep no project task until a direct project signal appears"]


def impact_item_for_projects(
    item: Item,
    classification: ItemClassification,
    score: RelevanceScore,
    project_map: dict[str, object],
) -> list[ProjectImpact]:
    """Return non-none project impacts for one classified and scored item."""
    if not isinstance(item, Item):
        raise ValueError("item must be an Item.")
    if not isinstance(classification, ItemClassification):
        raise ValueError("classification must be an ItemClassification.")
    if not isinstance(score, RelevanceScore):
        raise ValueError("score must be a RelevanceScore.")
    if item.item_id != classification.item_id or item.item_id != score.item_id:
        raise ValueError("item, classification and score must have the same item_id.")

    impacts: list[ProjectImpact] = []
    for project_key in sorted(project_map):
        project = _ensure_mapping(project_map[project_key], f"project {project_key}")
        is_relevant, relevance_reasons = _project_relevance(classification, project)
        if not is_relevant:
            continue

        impact_level, base_reason = _base_impact_level(classification, score)
        impact_level, special_reasons = _apply_special_rules(
            impact_level,
            project,
            classification,
            score,
        )
        if impact_level == "none":
            continue

        action_type, action_reason = _action_type_for_impact(project, classification)
        impact_level, action_level_reasons = _adjust_level_for_action_type(
            impact_level,
            action_type,
        )
        reasons = relevance_reasons + [
            base_reason,
            f"score {score.score}",
            f"severity {classification.severity}",
            action_reason,
        ] + special_reasons + action_level_reasons
        actions = _actions_for_impact(project, classification, action_type)
        impacts.append(
            ProjectImpact(
                item_id=item.item_id,
                project_key=str(project["project_key"]),
                project_name=str(project["project_name"]),
                impact_level=impact_level,
                action_type=action_type,
                reasons=reasons,
                suggested_actions=actions,
            )
        )

    return _sort_impacts(impacts)


def impact_scores_for_projects(
    items_by_id: dict[str, Item],
    classifications_by_id: dict[str, ItemClassification],
    scores: list[RelevanceScore],
    project_map: dict[str, object],
) -> list[ProjectImpact]:
    """Return deterministic project impacts for a list of relevance scores."""
    impacts: list[ProjectImpact] = []
    for score in scores:
        item = items_by_id.get(score.item_id)
        classification = classifications_by_id.get(score.item_id)
        if item is None or classification is None:
            continue
        impacts.extend(impact_item_for_projects(item, classification, score, project_map))
    return _sort_impacts(impacts)


def _sort_impacts(impacts: list[ProjectImpact]) -> list[ProjectImpact]:
    return sorted(
        impacts,
        key=lambda impact: (
            impact.item_id,
            -IMPACT_RANK[impact.impact_level],
            -ACTION_TYPE_RANK[impact.action_type],
            impact.project_key,
        ),
    )
