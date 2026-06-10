"""Source registry model and validation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any
from urllib.parse import urlparse

from radar.json_utils import read_json


SCHEMA_VERSION = 1

ALLOWED_SOURCE_TYPES = {
    "official_changelog",
    "official_docs",
    "official_release_notes",
    "github_releases",
    "github_api",
    "status_page",
    "candidate",
}
ALLOWED_RELIABILITY = {"primary", "secondary", "candidate"}
ALLOWED_VERIFICATION_STATUS = {
    "verified_url_format",
    "live_verified",
    "pending_manual_review",
    "unreachable",
    "disabled",
}

MANDATORY_SOURCE_FIELDS = (
    "source_id",
    "provider",
    "name",
    "url",
    "source_type",
    "priority",
    "reliability",
    "machine_readable",
    "category_hints",
    "verification_status",
    "notes",
)
OPTIONAL_SOURCE_FIELDS = (
    "expected_status_codes",
    "allow_redirects",
    "timeout_seconds",
    "max_bytes",
    "live_check_enabled",
    "manual_review_required",
)

_SOURCE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")


def _ensure_mapping(data: object, name: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError(f"{name} must be a dict.")
    return data


def _require_field(data: dict[str, Any], field_name: str) -> object:
    if field_name not in data:
        raise ValueError(f"{field_name} is required.")
    return data[field_name]


def _require_str(data: dict[str, Any], field_name: str) -> str:
    value = _require_field(data, field_name)
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty.")
    return value


def _require_int(data: dict[str, Any], field_name: str) -> int:
    value = _require_field(data, field_name)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer.")
    return value


def _require_bool(data: dict[str, Any], field_name: str) -> bool:
    value = _require_field(data, field_name)
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean.")
    return value


def _require_str_list(data: dict[str, Any], field_name: str) -> list[str]:
    value = _require_field(data, field_name)
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    if not value:
        raise ValueError(f"{field_name} must not be empty.")
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise ValueError(f"{field_name}[{index}] must be a string.")
        if not item.strip():
            raise ValueError(f"{field_name}[{index}] must not be empty.")
    return list(value)


def _optional_int_list(data: dict[str, Any], field_name: str) -> list[int] | None:
    value = data.get(field_name)
    if value is None:
        return None
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list or null.")
    if not value:
        raise ValueError(f"{field_name} must not be empty when provided.")
    items: list[int] = []
    for index, item in enumerate(value):
        if not isinstance(item, int) or isinstance(item, bool):
            raise ValueError(f"{field_name}[{index}] must be an integer.")
        items.append(item)
    return sorted(set(items))


def _optional_bool(data: dict[str, Any], field_name: str, default: bool) -> bool:
    value = data.get(field_name, default)
    if not isinstance(value, bool):
        raise ValueError(f"{field_name} must be a boolean.")
    return value


def _optional_float(data: dict[str, Any], field_name: str) -> float | None:
    value = data.get(field_name)
    if value is None:
        return None
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be a number or null.")
    return float(value)


def _optional_positive_int(data: dict[str, Any], field_name: str) -> int | None:
    value = data.get(field_name)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer or null.")
    if value < 1:
        raise ValueError(f"{field_name} must be >= 1 when provided.")
    return value


def _validate_https_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError("url must be an https:// URL.")


@dataclass(frozen=True, kw_only=True)
class SourceDefinition:
    """One source entry in the OpenAI release-radar registry."""

    source_id: str
    provider: str
    name: str
    url: str
    source_type: str
    priority: int
    reliability: str
    machine_readable: bool
    category_hints: list[str]
    verification_status: str
    notes: str
    expected_status_codes: list[int] | None = None
    allow_redirects: bool = True
    timeout_seconds: float | None = None
    max_bytes: int | None = None
    live_check_enabled: bool = True
    manual_review_required: bool = False

    def __post_init__(self) -> None:
        validate_source_definition(self)
        if self.expected_status_codes is not None:
            object.__setattr__(
                self,
                "expected_status_codes",
                sorted(set(self.expected_status_codes)),
            )
        if self.timeout_seconds is not None:
            object.__setattr__(self, "timeout_seconds", float(self.timeout_seconds))

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "provider": self.provider,
            "name": self.name,
            "url": self.url,
            "source_type": self.source_type,
            "priority": self.priority,
            "reliability": self.reliability,
            "machine_readable": self.machine_readable,
            "category_hints": list(self.category_hints),
            "verification_status": self.verification_status,
            "notes": self.notes,
            "expected_status_codes": (
                list(self.expected_status_codes)
                if self.expected_status_codes is not None
                else None
            ),
            "allow_redirects": self.allow_redirects,
            "timeout_seconds": self.timeout_seconds,
            "max_bytes": self.max_bytes,
            "live_check_enabled": self.live_check_enabled,
            "manual_review_required": self.manual_review_required,
        }

    @classmethod
    def from_dict(cls, data: object) -> "SourceDefinition":
        raw = _ensure_mapping(data, "SourceDefinition")
        return cls(
            source_id=_require_str(raw, "source_id"),
            provider=_require_str(raw, "provider"),
            name=_require_str(raw, "name"),
            url=_require_str(raw, "url"),
            source_type=_require_str(raw, "source_type"),
            priority=_require_int(raw, "priority"),
            reliability=_require_str(raw, "reliability"),
            machine_readable=_require_bool(raw, "machine_readable"),
            category_hints=_require_str_list(raw, "category_hints"),
            verification_status=_require_str(raw, "verification_status"),
            notes=_require_str(raw, "notes"),
            expected_status_codes=_optional_int_list(raw, "expected_status_codes"),
            allow_redirects=_optional_bool(raw, "allow_redirects", True),
            timeout_seconds=_optional_float(raw, "timeout_seconds"),
            max_bytes=_optional_positive_int(raw, "max_bytes"),
            live_check_enabled=_optional_bool(raw, "live_check_enabled", True),
            manual_review_required=_optional_bool(raw, "manual_review_required", False),
        )


def validate_source_definition(source: SourceDefinition) -> None:
    """Validate one source definition."""
    if not isinstance(source, SourceDefinition):
        raise ValueError("source must be a SourceDefinition.")
    for field_name in ("source_id", "provider", "name", "url", "notes"):
        value = getattr(source, field_name)
        if not isinstance(value, str):
            raise ValueError(f"{field_name} must be a string.")
        if not value.strip():
            raise ValueError(f"{field_name} must not be empty.")
    if not _SOURCE_ID_PATTERN.match(source.source_id):
        raise ValueError("source_id must be non-empty snake_case.")
    _validate_https_url(source.url)
    if source.source_type not in ALLOWED_SOURCE_TYPES:
        raise ValueError(f"source_type must be one of {sorted(ALLOWED_SOURCE_TYPES)}.")
    if source.reliability not in ALLOWED_RELIABILITY:
        raise ValueError(f"reliability must be one of {sorted(ALLOWED_RELIABILITY)}.")
    if source.verification_status not in ALLOWED_VERIFICATION_STATUS:
        raise ValueError(
            "verification_status must be one of "
            f"{sorted(ALLOWED_VERIFICATION_STATUS)}."
        )
    if not isinstance(source.priority, int) or isinstance(source.priority, bool):
        raise ValueError("priority must be an integer.")
    if source.priority < 1:
        raise ValueError("priority must be >= 1.")
    if not isinstance(source.machine_readable, bool):
        raise ValueError("machine_readable must be a boolean.")
    if not isinstance(source.category_hints, list):
        raise ValueError("category_hints must be a list.")
    if not source.category_hints:
        raise ValueError("category_hints must not be empty.")
    for index, hint in enumerate(source.category_hints):
        if not isinstance(hint, str):
            raise ValueError(f"category_hints[{index}] must be a string.")
        if not hint.strip():
            raise ValueError(f"category_hints[{index}] must not be empty.")
    if source.expected_status_codes is not None:
        if not isinstance(source.expected_status_codes, list):
            raise ValueError("expected_status_codes must be a list or None.")
        if not source.expected_status_codes:
            raise ValueError("expected_status_codes must not be empty when provided.")
        for index, status_code in enumerate(source.expected_status_codes):
            if not isinstance(status_code, int) or isinstance(status_code, bool):
                raise ValueError(f"expected_status_codes[{index}] must be an integer.")
            if status_code < 100 or status_code > 599:
                raise ValueError(
                    f"expected_status_codes[{index}] must be between 100 and 599."
                )
    if not isinstance(source.allow_redirects, bool):
        raise ValueError("allow_redirects must be a boolean.")
    if source.timeout_seconds is not None:
        if (
            not isinstance(source.timeout_seconds, (int, float))
            or isinstance(source.timeout_seconds, bool)
        ):
            raise ValueError("timeout_seconds must be a number or None.")
        if source.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive when provided.")
    if source.max_bytes is not None:
        if not isinstance(source.max_bytes, int) or isinstance(source.max_bytes, bool):
            raise ValueError("max_bytes must be an integer or None.")
        if source.max_bytes < 1:
            raise ValueError("max_bytes must be >= 1 when provided.")
    if not isinstance(source.live_check_enabled, bool):
        raise ValueError("live_check_enabled must be a boolean.")
    if not isinstance(source.manual_review_required, bool):
        raise ValueError("manual_review_required must be a boolean.")


def _ordered_sources(sources: list[SourceDefinition]) -> list[SourceDefinition]:
    return sorted(sources, key=lambda source: (source.priority, source.source_id))


def load_source_registry(data: object) -> list[SourceDefinition]:
    """Load and validate a source registry mapping."""
    raw = _ensure_mapping(data, "source registry")
    schema_version = raw.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        raise ValueError(f"schema_version must be {SCHEMA_VERSION}.")
    provider = raw.get("provider")
    if not isinstance(provider, str) or not provider.strip():
        raise ValueError("provider must be a non-empty string.")
    entries = raw.get("sources")
    if not isinstance(entries, list):
        raise ValueError("sources must be a list.")
    if not entries:
        raise ValueError("sources must not be empty.")

    sources = [SourceDefinition.from_dict(entry) for entry in entries]
    seen_source_ids: set[str] = set()
    for source in sources:
        if source.source_id in seen_source_ids:
            raise ValueError(f"duplicate source_id: {source.source_id}")
        seen_source_ids.add(source.source_id)
    return _ordered_sources(sources)


def load_source_registry_file(path: str) -> list[SourceDefinition]:
    """Load a source registry JSON file."""
    return load_source_registry(read_json(Path(path)))


def source_registry_to_dict(sources: list[SourceDefinition]) -> dict[str, Any]:
    """Serialize sources into the stable registry JSON shape."""
    if not isinstance(sources, list):
        raise ValueError("sources must be a list.")
    if not sources:
        raise ValueError("sources must not be empty.")
    for source in sources:
        validate_source_definition(source)
    ordered = _ordered_sources(sources)
    return {
        "schema_version": SCHEMA_VERSION,
        "provider": ordered[0].provider,
        "sources": [source.to_dict() for source in ordered],
    }
