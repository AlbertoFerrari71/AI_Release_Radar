"""Deterministic keyword-based item classification."""

from __future__ import annotations

import re
from dataclasses import dataclass

from radar.models import Item


CATEGORY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "deprecation": ("deprecat", "retirement", "sunset", "removed"),
    "security": ("security", "permission", "sandbox", "credential"),
    "billing": ("billing", "quota", "token usage", "cost"),
    "api_platform": ("api", "responses api", "admin api", "endpoint"),
    "codex_agents_md": ("agents.md", "workspace instructions"),
    "codex_cli": ("codex cli", "command", "terminal", "tui", "/app"),
    "codex_app": ("codex app", "desktop", "app handoff"),
    "codex_cloud": ("codex cloud", "cloud task", "remote task"),
    "codex_ide": ("ide", "editor", "vscode", "extension"),
    "codex_review": ("code review", "pull request", "pr review"),
    "codex_windows": ("windows", "powershell", "sandbox"),
    "codex_skills": ("skill", "skills"),
    "codex_mcp": ("mcp",),
    "codex_plugins": ("plugin", "plugins"),
    "gpt_models": ("model", "gpt", "reasoning"),
    "chatgpt": ("chatgpt",),
    "image_vision": ("image", "vision", "local file path"),
    "web_search": ("web search", "search"),
    "data_analysis": ("data analysis", "spreadsheet", "csv", "python"),
}

CATEGORY_PRIORITY: tuple[str, ...] = tuple(CATEGORY_KEYWORDS)

SEVERITY_KEYWORDS: dict[str, tuple[str, ...]] = {
    "critical": ("critical", "security vulnerability", "exploit", "data loss"),
    "high": (
        "deprecat",
        "breaking",
        "removed",
        "retirement",
        "sunset",
        "no longer",
        "security",
    ),
    "medium": (
        "added",
        "new command",
        "now available",
        "support for",
        "introduced",
        "improved sandbox",
    ),
    "low": ("fix", "improved", "better", "minor"),
    "ignored": ("chore", "typo only", "cosmetic"),
    "info": ("note", "documentation", "typo"),
}

SEVERITY_PRIORITY: tuple[str, ...] = (
    "critical",
    "high",
    "medium",
    "low",
    "ignored",
    "info",
)

SUPPORTED_CATEGORIES: tuple[str, ...] = CATEGORY_PRIORITY + ("unknown",)
SUPPORTED_SEVERITIES: tuple[str, ...] = SEVERITY_PRIORITY

_PARTIAL_KEYWORDS = {"deprecat"}


@dataclass(frozen=True, kw_only=True)
class ItemClassification:
    """Classification output kept separate from the source Item."""

    item_id: str
    category: str
    severity: str
    matched_keywords: list[str]
    reasons: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "item_id": self.item_id,
            "category": self.category,
            "severity": self.severity,
            "matched_keywords": list(self.matched_keywords),
            "reasons": list(self.reasons),
        }


def _combined_text(title: str, evidence: str) -> str:
    return f"{title}\n{evidence}".casefold()


def _keyword_matches(text: str, keyword: str) -> bool:
    normalized = keyword.casefold()
    if normalized in _PARTIAL_KEYWORDS or not normalized.replace(" ", "").isalnum():
        return normalized in text
    if " " in normalized:
        return normalized in text
    return re.search(rf"(?<![a-z0-9]){re.escape(normalized)}(?![a-z0-9])", text) is not None


def _matched_by_bucket(
    title: str,
    evidence: str,
    buckets: dict[str, tuple[str, ...]],
) -> dict[str, list[str]]:
    text = _combined_text(title, evidence)
    matches: dict[str, list[str]] = {}
    for bucket, keywords in buckets.items():
        bucket_matches = sorted(
            {keyword for keyword in keywords if _keyword_matches(text, keyword)}
        )
        if bucket_matches:
            matches[bucket] = bucket_matches
    return matches


def _first_matched_bucket(matches: dict[str, list[str]], priority: tuple[str, ...]) -> str | None:
    for bucket in priority:
        if bucket in matches:
            return bucket
    return None


def classify_category_from_text(title: str, evidence: str) -> str:
    """Classify an item category from title and evidence text."""
    matches = _matched_by_bucket(title, evidence, CATEGORY_KEYWORDS)
    return _first_matched_bucket(matches, CATEGORY_PRIORITY) or "unknown"


def classify_severity_from_text(title: str, evidence: str) -> str:
    """Classify an item severity from title and evidence text."""
    matches = _matched_by_bucket(title, evidence, SEVERITY_KEYWORDS)
    return _first_matched_bucket(matches, SEVERITY_PRIORITY) or "info"


def classify_item(item: Item) -> ItemClassification:
    """Return a deterministic classification without mutating the source item."""
    if not isinstance(item, Item):
        raise ValueError("item must be an Item.")

    category_matches = _matched_by_bucket(item.title, item.evidence, CATEGORY_KEYWORDS)
    severity_matches = _matched_by_bucket(item.title, item.evidence, SEVERITY_KEYWORDS)
    category = _first_matched_bucket(category_matches, CATEGORY_PRIORITY) or "unknown"
    severity = _first_matched_bucket(severity_matches, SEVERITY_PRIORITY) or "info"

    matched_keywords = sorted(
        {
            keyword
            for keywords in list(category_matches.values()) + list(severity_matches.values())
            for keyword in keywords
        }
    )

    reasons: list[str] = []
    if category == "unknown":
        reasons.append("category unknown: no category keyword matched")
    else:
        reasons.append(
            f"category {category}: matched {', '.join(category_matches[category])}"
        )

    if severity_matches:
        reasons.append(
            f"severity {severity}: matched {', '.join(severity_matches[severity])}"
        )
    else:
        reasons.append("severity info: no severity keyword matched")

    return ItemClassification(
        item_id=item.item_id,
        category=category,
        severity=severity,
        matched_keywords=matched_keywords,
        reasons=reasons,
    )
