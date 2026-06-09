"""Deterministic hashing helpers for radar items."""

from __future__ import annotations

import hashlib
import json
import re
from typing import Any


_WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(value: str) -> str:
    """Normalize text for stable comparisons and hashes."""
    if not isinstance(value, str):
        raise TypeError(f"Expected str, got {type(value).__name__}.")
    normalized = value.replace("\r\n", "\n").replace("\r", "\n")
    normalized = _WHITESPACE_RE.sub(" ", normalized)
    return normalized.strip()


def stable_json_dumps(data: object) -> str:
    """Serialize JSON-compatible data with stable key ordering."""
    return json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def stable_sha256_text(value: str) -> str:
    """Return a SHA-256 hex digest for normalized UTF-8 text."""
    normalized = normalize_text(value)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def stable_item_id(source_id: str, natural_key: str) -> str:
    """Build a stable item id from a source id and natural key."""
    if not normalize_text(source_id):
        raise ValueError("source_id must not be empty.")
    if not normalize_text(natural_key):
        raise ValueError("natural_key must not be empty.")
    payload = {
        "natural_key": normalize_text(natural_key),
        "source_id": normalize_text(source_id),
    }
    return "item_" + hashlib.sha256(
        stable_json_dumps(payload).encode("utf-8")
    ).hexdigest()


def content_hash_for_item_fields(
    *,
    source_id: str,
    provider: str,
    category: str,
    severity: str,
    title: str,
    published_at: str,
    url: str,
    evidence: str,
) -> str:
    """Hash stable item content fields, excluding volatile observation metadata."""
    payload: dict[str, Any] = {
        "category": normalize_text(category),
        "evidence": normalize_text(evidence),
        "provider": normalize_text(provider),
        "published_at": normalize_text(published_at),
        "severity": normalize_text(severity),
        "source_id": normalize_text(source_id),
        "title": normalize_text(title),
        "url": normalize_text(url),
    }
    return hashlib.sha256(stable_json_dumps(payload).encode("utf-8")).hexdigest()
