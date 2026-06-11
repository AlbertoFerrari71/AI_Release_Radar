"""Bridge-only prompt pack generation for dynamic news translations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from radar.json_utils import write_json
from radar.news_translation import (
    DEFAULT_TRANSLATION_PROFILE,
    SUPPORTED_TRANSLATION_LOCALES,
    TRANSLATION_MODEL_PROFILES,
    normalize_translation_locale,
    translation_run_root,
)


DEFAULT_GLOSSARY_TERMS = (
    "AI Release Radar",
    "Action Center",
    "Action Inbox",
    "Bridge",
    "Codex",
    "Prompt",
    "Gate",
    "HAG",
    "Backlog",
    "Scheduler",
    "Dry report",
    "Manual trigger",
    "No auto-action",
    "Human approval",
)


def build_translation_prompt(
    *,
    run_id: str,
    target_locale: object,
    items: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    profile: str = DEFAULT_TRANSLATION_PROFILE,
    glossary_terms: list[str] | tuple[str, ...] = DEFAULT_GLOSSARY_TERMS,
) -> str:
    """Render one controlled translation prompt without executing it."""
    locale = normalize_translation_locale(target_locale)
    profile_name = _normalize_profile(profile)
    payload = {
        "run_id": run_id,
        "target_locale": locale,
        "source_locale": "en",
        "translation_model_profile": profile_name,
        "items": [_prompt_item(item) for item in items],
    }
    lines = [
        f"# 1200) Translation Prompt - {locale.upper()} - {profile_name}",
        "",
        "## Scope",
        "",
        "- [F] Translate only `title` and `summary` fields.",
        "- [F] Return valid JSON only for the translated items.",
        "- [F] Do not call external services.",
        "- [F] Do not add information that is not present in the source.",
        "- [F] Preserve `source_item_id` exactly.",
        "- [F] If uncertain, set `translation_status` to `needs_review` and `review_required` to true.",
        "",
        "## Preservation Rules",
        "",
        "- [F] Do not translate links.",
        "- [F] Do not translate file paths.",
        "- [F] Do not translate CLI commands.",
        "- [F] Do not translate model names, product names, or version numbers.",
        "- [F] Preserve all version numbers exactly.",
        "",
        "## Glossary",
        "",
    ]
    for term in glossary_terms:
        lines.append(f"- {term}")
    lines.extend(
        [
            "",
            "## Required Output Schema",
            "",
            "Return a JSON array. Each item must contain:",
            "",
            "```json",
            json.dumps(
                {
                    "run_id": run_id,
                    "source_item_id": "...",
                    "target_locale": locale,
                    "source_locale": "en",
                    "title_translated": "...",
                    "summary_translated": "...",
                    "technical_terms_preserved": True,
                    "links_preserved": True,
                    "version_numbers_preserved": True,
                    "translation_model_profile": profile_name,
                    "translation_status": "translated|missing|needs_review|failed",
                    "review_required": False,
                    "created_at": "...",
                },
                ensure_ascii=False,
                indent=2,
            ),
            "```",
            "",
            "## Source Items",
            "",
            "```json",
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True),
            "```",
        ]
    )
    return "\n".join(lines).rstrip("\n") + "\n"


def write_translation_prompt_pack(
    *,
    run_id: str,
    items: list[dict[str, Any]] | tuple[dict[str, Any], ...],
    bridge_root: str | Path,
    locales: list[str] | tuple[str, ...] = SUPPORTED_TRANSLATION_LOCALES,
    profile: str = DEFAULT_TRANSLATION_PROFILE,
) -> dict[str, Any]:
    """Write controlled translation prompts into the Bridge and return an index."""
    profile_name = _normalize_profile(profile)
    root = translation_run_root(run_id, bridge_root)
    root.mkdir(parents=True, exist_ok=True)
    prompt_paths: dict[str, str] = {}
    for locale in locales:
        normalized_locale = normalize_translation_locale(locale)
        prompt_path = root / f"1200-Translation_Prompt_{normalized_locale}_{profile_name}.md"
        prompt_path.write_text(
            build_translation_prompt(
                run_id=run_id,
                target_locale=normalized_locale,
                items=items,
                profile=profile_name,
            ),
            encoding="utf-8",
            newline="\n",
        )
        prompt_paths[normalized_locale] = str(prompt_path)
    index = {
        "schema_version": 1,
        "run_id": run_id,
        "profile": profile_name,
        "prompt_paths": prompt_paths,
        "target_locales": sorted(prompt_paths),
        "bridge_only": True,
        "llm_executed": False,
        "no_external_services": True,
    }
    index_path = root / "1200-Translation_Prompt_Index.json"
    write_json(index_path, index)
    index["index_path"] = str(index_path)
    return index


def _prompt_item(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "source_item_id": str(item.get("source_item_id") or item.get("item_id") or ""),
        "title": str(item.get("title") or ""),
        "summary": str(item.get("summary") or ""),
        "links": list(item.get("links") or []),
        "source_url": str(item.get("source_url") or ""),
    }


def _normalize_profile(profile: str) -> str:
    value = str(profile or DEFAULT_TRANSLATION_PROFILE).strip().lower()
    if value not in TRANSLATION_MODEL_PROFILES:
        raise ValueError(f"unsupported translation profile: {profile}")
    return value
