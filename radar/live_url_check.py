"""Controlled live URL checks for source registry entries."""

from __future__ import annotations

from typing import Any

from radar.source_registry import SourceDefinition
from radar.url_verifier import UrlVerificationResult, verify_url_live


SCHEMA_VERSION = 1


def check_sources_live(
    sources: list[SourceDefinition],
    timeout_seconds: float = 10.0,
    max_sources: int | None = None,
) -> list[UrlVerificationResult]:
    """Run read-only live URL checks for source definitions.

    This function delegates one URL at a time to ``verify_url_live``. A failure
    on one source is converted into that source result and does not stop checks
    for the remaining sources.
    """
    if not isinstance(sources, list):
        raise ValueError("sources must be a list.")
    _validate_timeout(timeout_seconds)
    _validate_max_sources(max_sources)

    selected_sources = sources[:max_sources] if max_sources is not None else list(sources)
    results: list[UrlVerificationResult] = []
    for source in selected_sources:
        if not isinstance(source, SourceDefinition):
            raise ValueError("sources must contain SourceDefinition entries.")
        try:
            result = verify_url_live(source, timeout_seconds=float(timeout_seconds))
        except Exception as exc:  # Defensive boundary around one source only.
            result = UrlVerificationResult(
                source_id=source.source_id,
                url=source.url,
                ok=False,
                status_code=None,
                final_url=None,
                error=f"{exc.__class__.__name__}: {exc}",
            )
        results.append(result)
    return _ordered_results(results)


def summarize_url_verification_results(
    results: list[UrlVerificationResult],
) -> dict[str, object]:
    """Summarize URL verification results deterministically."""
    ordered = _ordered_results(_validate_results(results))
    status_code_counts: dict[str, int] = {}
    for result in ordered:
        key = str(result.status_code) if result.status_code is not None else "none"
        status_code_counts[key] = status_code_counts.get(key, 0) + 1

    ok_source_ids = [result.source_id for result in ordered if result.ok]
    failed_source_ids = [result.source_id for result in ordered if not result.ok]
    return {
        "total": len(ordered),
        "ok": len(ok_source_ids),
        "failed": len(failed_source_ids),
        "ok_source_ids": ok_source_ids,
        "failed_source_ids": failed_source_ids,
        "status_code_counts": dict(sorted(status_code_counts.items())),
    }


def verification_results_to_dict(
    results: list[UrlVerificationResult],
) -> dict[str, object]:
    """Serialize URL verification results into a stable JSON shape."""
    ordered = _ordered_results(_validate_results(results))
    return {
        "schema_version": SCHEMA_VERSION,
        "summary": summarize_url_verification_results(ordered),
        "results": [result.to_dict() for result in ordered],
    }


def _validate_timeout(timeout_seconds: float) -> None:
    if (
        not isinstance(timeout_seconds, (int, float))
        or isinstance(timeout_seconds, bool)
        or timeout_seconds <= 0
    ):
        raise ValueError("timeout_seconds must be a positive number.")


def _validate_max_sources(max_sources: int | None) -> None:
    if max_sources is None:
        return
    if not isinstance(max_sources, int) or isinstance(max_sources, bool):
        raise ValueError("max_sources must be an integer or None.")
    if max_sources < 1:
        raise ValueError("max_sources must be >= 1.")


def _validate_results(results: list[UrlVerificationResult]) -> list[UrlVerificationResult]:
    if not isinstance(results, list):
        raise ValueError("results must be a list.")
    for result in results:
        if not isinstance(result, UrlVerificationResult):
            raise ValueError("results must contain UrlVerificationResult entries.")
    return list(results)


def _ordered_results(results: list[UrlVerificationResult]) -> list[UrlVerificationResult]:
    return sorted(results, key=lambda result: result.source_id)
