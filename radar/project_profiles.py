"""Project-specific impact profile loading for supervised daily review."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from radar.json_utils import read_json


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PROJECT_PROFILES_PATH = REPO_ROOT / "config" / "projects" / "project_profiles.json"


@dataclass(frozen=True)
class ProjectProfile:
    """Validated project-specific profile used by triage and prompt suggestions."""

    project_key: str
    project_name: str
    direct_categories: list[str]
    monitor_categories: list[str]
    ignored_categories: list[str]
    keywords_positive: list[str]
    keywords_negative: list[str]
    review_threshold: int
    prompt_generation_allowed: bool

    def __post_init__(self) -> None:
        if not self.project_key.strip():
            raise ValueError("project_key must not be empty.")
        if not self.project_name.strip():
            raise ValueError("project_name must not be empty.")
        if self.review_threshold < 0 or self.review_threshold > 100:
            raise ValueError("review_threshold must be between 0 and 100.")

    def to_dict(self) -> dict[str, object]:
        return {
            "project_key": self.project_key,
            "project_name": self.project_name,
            "direct_categories": list(self.direct_categories),
            "monitor_categories": list(self.monitor_categories),
            "ignored_categories": list(self.ignored_categories),
            "keywords_positive": list(self.keywords_positive),
            "keywords_negative": list(self.keywords_negative),
            "review_threshold": self.review_threshold,
            "prompt_generation_allowed": self.prompt_generation_allowed,
        }


def load_project_profiles(path: str | Path | None = None) -> dict[str, ProjectProfile]:
    """Load project profiles, using a deterministic fallback when the config is absent."""
    profile_path = Path(path) if path is not None else DEFAULT_PROJECT_PROFILES_PATH
    if not profile_path.exists():
        return fallback_project_profiles()
    raw = read_json(profile_path)
    data = _mapping(raw, "project profiles")
    projects = data.get("projects")
    if not isinstance(projects, list) or not projects:
        raise ValueError("project profiles projects must be a non-empty list.")
    profiles: dict[str, ProjectProfile] = {}
    for index, project_data in enumerate(projects):
        project = _mapping(project_data, f"projects[{index}]")
        profile = ProjectProfile(
            project_key=_required_str(project, "project_key"),
            project_name=_required_str(project, "project_name"),
            direct_categories=sorted(set(_str_list(project, "direct_categories"))),
            monitor_categories=sorted(set(_str_list(project, "monitor_categories"))),
            ignored_categories=sorted(set(_str_list(project, "ignored_categories"))),
            keywords_positive=sorted(set(_str_list(project, "keywords_positive"))),
            keywords_negative=sorted(set(_str_list(project, "keywords_negative"))),
            review_threshold=_required_int(project, "review_threshold"),
            prompt_generation_allowed=_required_bool(project, "prompt_generation_allowed"),
        )
        if profile.project_key in profiles:
            raise ValueError(f"duplicate project_key: {profile.project_key}")
        profiles[profile.project_key] = profile
    return profiles


def fallback_project_profiles() -> dict[str, ProjectProfile]:
    """Return deterministic built-in profiles when the config file is unavailable."""
    return {
        profile.project_key: profile
        for profile in [
            ProjectProfile(
                project_key="ai_software_factory",
                project_name="AI Software Factory",
                direct_categories=[
                    "api_platform",
                    "codex_agents_md",
                    "codex_cli",
                    "codex_mcp",
                    "codex_plugins",
                    "codex_review",
                    "codex_skills",
                    "codex_windows",
                    "deprecation",
                    "security",
                ],
                monitor_categories=["billing", "gpt_models"],
                ignored_categories=[],
                keywords_positive=["agents.md", "codex", "sandbox", "workflow"],
                keywords_negative=[],
                review_threshold=60,
                prompt_generation_allowed=True,
            ),
            ProjectProfile(
                project_key="codex_skills",
                project_name="Codex_Skills",
                direct_categories=[
                    "codex_agents_md",
                    "codex_cli",
                    "codex_mcp",
                    "codex_plugins",
                    "codex_skills",
                    "codex_windows",
                ],
                monitor_categories=["deprecation", "security"],
                ignored_categories=[],
                keywords_positive=["skill", "skills", "validator"],
                keywords_negative=[],
                review_threshold=60,
                prompt_generation_allowed=True,
            ),
            ProjectProfile(
                project_key="family_photo_organizer",
                project_name="Family Photo Organizer",
                direct_categories=["image_vision", "security"],
                monitor_categories=["api_platform", "codex_cli", "codex_review"],
                ignored_categories=["billing"],
                keywords_positive=["image", "privacy", "vision"],
                keywords_negative=[],
                review_threshold=70,
                prompt_generation_allowed=False,
            ),
            ProjectProfile(
                project_key="mansionario_vivo",
                project_name="Mansionario_Vivo",
                direct_categories=["api_platform", "deprecation", "security"],
                monitor_categories=["codex_cli", "codex_review", "data_analysis"],
                ignored_categories=["image_vision"],
                keywords_positive=["api", "fastapi", "security"],
                keywords_negative=[],
                review_threshold=70,
                prompt_generation_allowed=True,
            ),
            ProjectProfile(
                project_key="agglodetect",
                project_name="AggloDetect",
                direct_categories=["image_vision"],
                monitor_categories=["api_platform", "codex_cli", "data_analysis", "gpt_models"],
                ignored_categories=["billing"],
                keywords_positive=["image", "vision", "csv"],
                keywords_negative=[],
                review_threshold=65,
                prompt_generation_allowed=True,
            ),
            ProjectProfile(
                project_key="diamsign",
                project_name="DiamSign",
                direct_categories=["image_vision", "security"],
                monitor_categories=["api_platform", "codex_cli", "gpt_models"],
                ignored_categories=["billing"],
                keywords_positive=["image", "security", "vision"],
                keywords_negative=[],
                review_threshold=70,
                prompt_generation_allowed=True,
            ),
            ProjectProfile(
                project_key="controllo_gestione_esolver",
                project_name="ControlloGestioneExcel / eSolver",
                direct_categories=["data_analysis", "deprecation", "security"],
                monitor_categories=["api_platform", "codex_cli"],
                ignored_categories=["image_vision", "billing"],
                keywords_positive=["api", "csv", "spreadsheet"],
                keywords_negative=[],
                review_threshold=75,
                prompt_generation_allowed=False,
            ),
            ProjectProfile(
                project_key="ai_release_radar",
                project_name="AI Release Radar",
                direct_categories=[
                    "api_platform",
                    "codex_cli",
                    "codex_review",
                    "deprecation",
                    "security",
                ],
                monitor_categories=["billing", "gpt_models", "image_vision"],
                ignored_categories=[],
                keywords_positive=["radar", "dashboard", "scheduler", "release"],
                keywords_negative=[],
                review_threshold=60,
                prompt_generation_allowed=True,
            ),
        ]
    }


def profile_to_dicts(profiles: dict[str, ProjectProfile]) -> dict[str, dict[str, object]]:
    """Convert loaded profiles to plain dictionaries for JSON output."""
    return {key: profiles[key].to_dict() for key in sorted(profiles)}


def _mapping(value: object, context: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{context} must be a dict.")
    return value


def _required_str(data: dict[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string.")
    return value


def _str_list(data: dict[str, Any], key: str) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list):
        raise ValueError(f"{key} must be a list.")
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{key}[{index}] must be a non-empty string.")
        result.append(item)
    return result


def _required_int(data: dict[str, Any], key: str) -> int:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{key} must be an integer.")
    return value


def _required_bool(data: dict[str, Any], key: str) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise ValueError(f"{key} must be a boolean.")
    return value
