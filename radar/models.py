"""Persistent data models for AI Release Radar."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


SCHEMA_VERSION = 1


def _ensure_mapping(data: object, model_name: str) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError(f"{model_name}.from_dict expected a dict.")
    return data


def _require_schema_version(data: dict[str, Any], model_name: str) -> int:
    value = data.get("schema_version")
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{model_name}.schema_version must be a positive integer.")
    return value


def _require_str(data: dict[str, Any], field_name: str) -> str:
    value = data.get(field_name)
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")
    if not value.strip():
        raise ValueError(f"{field_name} must not be empty.")
    return value


def _require_str_allow_empty(data: dict[str, Any], field_name: str) -> str:
    value = data.get(field_name)
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")
    return value


def _optional_str(data: dict[str, Any], field_name: str) -> str | None:
    value = data.get(field_name)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string or null.")
    return value


def _optional_int(data: dict[str, Any], field_name: str) -> int | None:
    value = data.get(field_name)
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer or null.")
    return value


def _require_int(data: dict[str, Any], field_name: str) -> int:
    value = data.get(field_name)
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer.")
    return value


def _require_float(data: dict[str, Any], field_name: str) -> float:
    value = data.get(field_name)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be a number.")
    return float(value)


def _require_str_list(data: dict[str, Any], field_name: str) -> list[str]:
    value = data.get(field_name)
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a list.")
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise ValueError(f"{field_name}[{index}] must be a string.")
    return list(value)


def _validate_str_attr(value: object, field_name: str, *, allow_empty: bool = False) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{field_name} must be a string.")
    if not allow_empty and not value.strip():
        raise ValueError(f"{field_name} must not be empty.")


def _validate_schema_attr(value: object, model_name: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise ValueError(f"{model_name}.schema_version must be a positive integer.")


def _validate_optional_non_negative_int(value: object, field_name: str) -> None:
    if value is None:
        return
    if not isinstance(value, int) or isinstance(value, bool):
        raise ValueError(f"{field_name} must be an integer or None.")
    if value < 0:
        raise ValueError(f"{field_name} must not be negative.")


@dataclass(frozen=True, kw_only=True)
class Item:
    """A normalized release-radar item observed from one source."""

    schema_version: int = SCHEMA_VERSION
    item_id: str
    source_id: str
    provider: str
    category: str
    severity: str
    title: str
    published_at: str
    url: str
    evidence: str
    content_hash: str
    first_seen: str
    confidence: float

    def __post_init__(self) -> None:
        _validate_schema_attr(self.schema_version, "Item")
        for field_name in (
            "item_id",
            "source_id",
            "provider",
            "category",
            "severity",
            "title",
            "published_at",
            "evidence",
            "content_hash",
            "first_seen",
        ):
            _validate_str_attr(getattr(self, field_name), field_name)
        _validate_str_attr(self.url, "url", allow_empty=True)
        if not isinstance(self.confidence, (int, float)) or isinstance(self.confidence, bool):
            raise ValueError("confidence must be a number.")
        confidence = float(self.confidence)
        if confidence < 0.0 or confidence > 1.0:
            raise ValueError("confidence must be between 0 and 1.")
        object.__setattr__(self, "confidence", confidence)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "item_id": self.item_id,
            "source_id": self.source_id,
            "provider": self.provider,
            "category": self.category,
            "severity": self.severity,
            "title": self.title,
            "published_at": self.published_at,
            "url": self.url,
            "evidence": self.evidence,
            "content_hash": self.content_hash,
            "first_seen": self.first_seen,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: object) -> "Item":
        raw = _ensure_mapping(data, "Item")
        return cls(
            schema_version=_require_schema_version(raw, "Item"),
            item_id=_require_str(raw, "item_id"),
            source_id=_require_str(raw, "source_id"),
            provider=_require_str(raw, "provider"),
            category=_require_str(raw, "category"),
            severity=_require_str(raw, "severity"),
            title=_require_str(raw, "title"),
            published_at=_require_str(raw, "published_at"),
            url=_require_str_allow_empty(raw, "url"),
            evidence=_require_str(raw, "evidence"),
            content_hash=_require_str(raw, "content_hash"),
            first_seen=_require_str(raw, "first_seen"),
            confidence=_require_float(raw, "confidence"),
        )


@dataclass(frozen=True, kw_only=True)
class SourceSnapshot:
    """Deterministic snapshot of one source at one observation time."""

    schema_version: int = SCHEMA_VERSION
    source_id: str
    provider: str
    fetched_at: str
    fetch_status: str
    http_status: int | None
    items: list[Item]
    page_hash: str | None

    def __post_init__(self) -> None:
        _validate_schema_attr(self.schema_version, "SourceSnapshot")
        for field_name in ("source_id", "provider", "fetched_at", "fetch_status"):
            _validate_str_attr(getattr(self, field_name), field_name)
        if self.http_status is not None and (
            not isinstance(self.http_status, int) or isinstance(self.http_status, bool)
        ):
            raise ValueError("http_status must be an integer or None.")
        if not isinstance(self.items, list):
            raise ValueError("items must be a list of Item.")
        seen_item_ids: set[str] = set()
        for index, item in enumerate(self.items):
            if not isinstance(item, Item):
                raise ValueError(f"items[{index}] must be an Item.")
            if item.item_id in seen_item_ids:
                raise ValueError(f"duplicate item_id in snapshot: {item.item_id}")
            seen_item_ids.add(item.item_id)
        if self.page_hash is not None:
            _validate_str_attr(self.page_hash, "page_hash")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "source_id": self.source_id,
            "provider": self.provider,
            "fetched_at": self.fetched_at,
            "fetch_status": self.fetch_status,
            "http_status": self.http_status,
            "items": [item.to_dict() for item in self.items],
            "page_hash": self.page_hash,
        }

    @classmethod
    def from_dict(cls, data: object) -> "SourceSnapshot":
        raw = _ensure_mapping(data, "SourceSnapshot")
        items = raw.get("items")
        if not isinstance(items, list):
            raise ValueError("items must be a list.")
        return cls(
            schema_version=_require_schema_version(raw, "SourceSnapshot"),
            source_id=_require_str(raw, "source_id"),
            provider=_require_str(raw, "provider"),
            fetched_at=_require_str(raw, "fetched_at"),
            fetch_status=_require_str(raw, "fetch_status"),
            http_status=_optional_int(raw, "http_status"),
            items=[Item.from_dict(item) for item in items],
            page_hash=_optional_str(raw, "page_hash"),
        )


@dataclass(frozen=True, kw_only=True)
class DiffResult:
    """Item-level diff between two source snapshots."""

    schema_version: int = SCHEMA_VERSION
    source_id: str
    new_items: list[str]
    changed_items: list[str]
    removed_items: list[str]
    unchanged_count: int

    def __post_init__(self) -> None:
        _validate_schema_attr(self.schema_version, "DiffResult")
        _validate_str_attr(self.source_id, "source_id")
        for field_name in ("new_items", "changed_items", "removed_items"):
            value = getattr(self, field_name)
            if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
                raise ValueError(f"{field_name} must be a list of strings.")
            object.__setattr__(self, field_name, sorted(value))
        if not isinstance(self.unchanged_count, int) or isinstance(self.unchanged_count, bool):
            raise ValueError("unchanged_count must be an integer.")
        if self.unchanged_count < 0:
            raise ValueError("unchanged_count must not be negative.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "source_id": self.source_id,
            "new_items": list(self.new_items),
            "changed_items": list(self.changed_items),
            "removed_items": list(self.removed_items),
            "unchanged_count": self.unchanged_count,
        }

    @classmethod
    def from_dict(cls, data: object) -> "DiffResult":
        raw = _ensure_mapping(data, "DiffResult")
        return cls(
            schema_version=_require_schema_version(raw, "DiffResult"),
            source_id=_require_str(raw, "source_id"),
            new_items=_require_str_list(raw, "new_items"),
            changed_items=_require_str_list(raw, "changed_items"),
            removed_items=_require_str_list(raw, "removed_items"),
            unchanged_count=_require_int(raw, "unchanged_count"),
        )


@dataclass(frozen=True, kw_only=True)
class RunIndexEntry:
    """Append-only index entry for one radar run."""

    schema_version: int = SCHEMA_VERSION
    run_id: str
    step: str
    status: str
    started_at: str
    finished_at: str
    duration_seconds: float
    report_full: str | None
    report_compact: str | None
    snapshot_dir: str | None
    notes: str | None
    source_count: int | None = None
    parsed_count: int | None = None
    item_count: int | None = None
    failed_count: int | None = None
    skipped_count: int | None = None
    timestamp: str | None = None

    def __post_init__(self) -> None:
        _validate_schema_attr(self.schema_version, "RunIndexEntry")
        for field_name in ("run_id", "step", "status", "started_at", "finished_at"):
            _validate_str_attr(getattr(self, field_name), field_name)
        if not isinstance(self.duration_seconds, (int, float)) or isinstance(
            self.duration_seconds, bool
        ):
            raise ValueError("duration_seconds must be a number.")
        duration = float(self.duration_seconds)
        if duration < 0.0:
            raise ValueError("duration_seconds must not be negative.")
        object.__setattr__(self, "duration_seconds", duration)
        for field_name in ("report_full", "report_compact", "snapshot_dir", "notes"):
            value = getattr(self, field_name)
            if value is not None and not isinstance(value, str):
                raise ValueError(f"{field_name} must be a string or None.")
        for field_name in (
            "source_count",
            "parsed_count",
            "item_count",
            "failed_count",
            "skipped_count",
        ):
            _validate_optional_non_negative_int(getattr(self, field_name), field_name)
        if self.timestamp is not None:
            _validate_str_attr(self.timestamp, "timestamp")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "run_id": self.run_id,
            "step": self.step,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_seconds": self.duration_seconds,
            "report_full": self.report_full,
            "report_compact": self.report_compact,
            "snapshot_dir": self.snapshot_dir,
            "notes": self.notes,
            "source_count": self.source_count,
            "parsed_count": self.parsed_count,
            "item_count": self.item_count,
            "failed_count": self.failed_count,
            "skipped_count": self.skipped_count,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: object) -> "RunIndexEntry":
        raw = _ensure_mapping(data, "RunIndexEntry")
        return cls(
            schema_version=_require_schema_version(raw, "RunIndexEntry"),
            run_id=_require_str(raw, "run_id"),
            step=_require_str(raw, "step"),
            status=_require_str(raw, "status"),
            started_at=_require_str(raw, "started_at"),
            finished_at=_require_str(raw, "finished_at"),
            duration_seconds=_require_float(raw, "duration_seconds"),
            report_full=_optional_str(raw, "report_full"),
            report_compact=_optional_str(raw, "report_compact"),
            snapshot_dir=_optional_str(raw, "snapshot_dir"),
            notes=_optional_str(raw, "notes"),
            source_count=_optional_int(raw, "source_count"),
            parsed_count=_optional_int(raw, "parsed_count"),
            item_count=_optional_int(raw, "item_count"),
            failed_count=_optional_int(raw, "failed_count"),
            skipped_count=_optional_int(raw, "skipped_count"),
            timestamp=_optional_str(raw, "timestamp"),
        )
