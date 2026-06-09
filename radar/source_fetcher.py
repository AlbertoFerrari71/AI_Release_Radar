"""Read-only source content fetcher without live parsing."""

from __future__ import annotations

from dataclasses import dataclass
import socket
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from radar.source_registry import SourceDefinition


SCHEMA_VERSION = 1
DEFAULT_TIMEOUT_SECONDS = 10.0
_USER_AGENT = "AI-Release-Radar-0130/1.0"


@dataclass(frozen=True)
class FetchedSourceContent:
    """Small diagnostic fetch result for one source without parsing content."""

    source_id: str
    url: str
    ok: bool
    status_code: int | None
    final_url: str | None
    content_type: str | None
    content_length: int | None
    body_sample: str | None
    truncated: bool
    error: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "url": self.url,
            "ok": self.ok,
            "status_code": self.status_code,
            "final_url": self.final_url,
            "content_type": self.content_type,
            "content_length": self.content_length,
            "body_sample": self.body_sample,
            "truncated": self.truncated,
            "error": self.error,
        }


def fetch_source_content(
    source: SourceDefinition,
    timeout_seconds: float | None = None,
    max_bytes: int = 4096,
) -> FetchedSourceContent:
    """Fetch a bounded body sample for one source without parsing it."""
    if not isinstance(source, SourceDefinition):
        raise ValueError("source must be a SourceDefinition.")
    _validate_max_bytes(max_bytes)

    if not source.live_check_enabled:
        return FetchedSourceContent(
            source_id=source.source_id,
            url=source.url,
            ok=False,
            status_code=None,
            final_url=None,
            content_type=None,
            content_length=None,
            body_sample=None,
            truncated=False,
            error="live_check_disabled",
        )

    effective_timeout = _effective_timeout(source, timeout_seconds)
    request = Request(
        source.url,
        method="GET",
        headers={"User-Agent": _USER_AGENT},
    )
    try:
        with urlopen(request, timeout=effective_timeout) as response:
            return _result_from_response(source, response, max_bytes)
    except HTTPError as exc:
        try:
            return _result_from_response(source, exc, max_bytes, status_code=exc.code)
        finally:
            exc.close()
    except (TimeoutError, URLError, OSError, socket.timeout) as exc:
        return _result_from_error(source, exc)


def fetch_sources_content(
    sources: list[SourceDefinition],
    timeout_seconds: float | None = None,
    max_sources: int | None = None,
    max_bytes: int = 4096,
) -> list[FetchedSourceContent]:
    """Fetch bounded source samples one source at a time."""
    if not isinstance(sources, list):
        raise ValueError("sources must be a list.")
    _validate_max_sources(max_sources)
    _validate_max_bytes(max_bytes)

    selected_sources = sources[:max_sources] if max_sources is not None else list(sources)
    results: list[FetchedSourceContent] = []
    for source in selected_sources:
        if not isinstance(source, SourceDefinition):
            raise ValueError("sources must contain SourceDefinition entries.")
        try:
            result = fetch_source_content(
                source,
                timeout_seconds=timeout_seconds,
                max_bytes=max_bytes,
            )
        except Exception as exc:  # Defensive boundary around one source only.
            result = _result_from_error(source, exc)
        results.append(result)
    return _ordered_results(results)


def summarize_fetched_sources(
    results: list[FetchedSourceContent],
) -> dict[str, object]:
    """Summarize fetched source content results deterministically."""
    ordered = _ordered_results(_validate_results(results))
    status_code_counts: dict[str, int] = {}
    content_type_counts: dict[str, int] = {}
    for result in ordered:
        status_key = str(result.status_code) if result.status_code is not None else "none"
        status_code_counts[status_key] = status_code_counts.get(status_key, 0) + 1
        type_key = result.content_type if result.content_type is not None else "none"
        content_type_counts[type_key] = content_type_counts.get(type_key, 0) + 1

    ok_source_ids = [result.source_id for result in ordered if result.ok]
    failed_source_ids = [result.source_id for result in ordered if not result.ok]
    disabled_source_ids = [
        result.source_id for result in ordered if result.error == "live_check_disabled"
    ]
    truncated_source_ids = [result.source_id for result in ordered if result.truncated]
    unexpected_status_source_ids = [
        result.source_id
        for result in ordered
        if result.error is not None and result.error.startswith("unexpected_status:")
    ]
    redirect_not_allowed_source_ids = [
        result.source_id for result in ordered if result.error == "redirect_not_allowed"
    ]
    return {
        "total": len(ordered),
        "ok": len(ok_source_ids),
        "failed": len(failed_source_ids),
        "disabled": len(disabled_source_ids),
        "truncated": len(truncated_source_ids),
        "unexpected_status": len(unexpected_status_source_ids),
        "redirect_not_allowed": len(redirect_not_allowed_source_ids),
        "ok_source_ids": ok_source_ids,
        "failed_source_ids": failed_source_ids,
        "disabled_source_ids": disabled_source_ids,
        "truncated_source_ids": truncated_source_ids,
        "unexpected_status_source_ids": unexpected_status_source_ids,
        "redirect_not_allowed_source_ids": redirect_not_allowed_source_ids,
        "status_code_counts": dict(sorted(status_code_counts.items())),
        "content_type_counts": dict(sorted(content_type_counts.items())),
    }


def fetched_sources_to_dict(
    results: list[FetchedSourceContent],
) -> dict[str, object]:
    """Serialize fetched source content results into a stable JSON shape."""
    ordered = _ordered_results(_validate_results(results))
    return {
        "schema_version": SCHEMA_VERSION,
        "summary": summarize_fetched_sources(ordered),
        "results": [result.to_dict() for result in ordered],
    }


def _result_from_response(
    source: SourceDefinition,
    response: object,
    max_bytes: int,
    *,
    status_code: int | None = None,
) -> FetchedSourceContent:
    raw_sample = response.read(max_bytes)
    body_sample = raw_sample.decode("utf-8", errors="replace")
    response_status = _response_status(response, status_code)
    final_url = _response_url(response, source.url)
    content_type = _header_value(response, "content-type")
    content_length = _parse_content_length(_header_value(response, "content-length"))
    truncated = _is_truncated(raw_sample, max_bytes, content_length)
    unexpected_status = not _is_expected_status(source, response_status)
    redirect_not_allowed = final_url != source.url and not source.allow_redirects
    ok = not unexpected_status and not redirect_not_allowed
    return FetchedSourceContent(
        source_id=source.source_id,
        url=source.url,
        ok=ok,
        status_code=response_status,
        final_url=final_url,
        content_type=content_type,
        content_length=content_length,
        body_sample=body_sample,
        truncated=truncated,
        error=_build_error(response_status, unexpected_status, redirect_not_allowed),
    )


def _result_from_error(
    source: SourceDefinition,
    exc: BaseException,
) -> FetchedSourceContent:
    return FetchedSourceContent(
        source_id=source.source_id,
        url=source.url,
        ok=False,
        status_code=None,
        final_url=None,
        content_type=None,
        content_length=None,
        body_sample=None,
        truncated=False,
        error=f"{exc.__class__.__name__}: {exc}",
    )


def _effective_timeout(
    source: SourceDefinition,
    timeout_seconds: float | None,
) -> float:
    candidate = (
        source.timeout_seconds
        if source.timeout_seconds is not None
        else timeout_seconds
        if timeout_seconds is not None
        else DEFAULT_TIMEOUT_SECONDS
    )
    if (
        not isinstance(candidate, (int, float))
        or isinstance(candidate, bool)
        or candidate <= 0
    ):
        raise ValueError("timeout_seconds must be a positive number.")
    return float(candidate)


def _validate_max_bytes(max_bytes: int) -> None:
    if not isinstance(max_bytes, int) or isinstance(max_bytes, bool):
        raise ValueError("max_bytes must be an integer.")
    if max_bytes < 1:
        raise ValueError("max_bytes must be >= 1.")


def _validate_max_sources(max_sources: int | None) -> None:
    if max_sources is None:
        return
    if not isinstance(max_sources, int) or isinstance(max_sources, bool):
        raise ValueError("max_sources must be an integer or None.")
    if max_sources < 1:
        raise ValueError("max_sources must be >= 1.")


def _validate_results(results: list[FetchedSourceContent]) -> list[FetchedSourceContent]:
    if not isinstance(results, list):
        raise ValueError("results must be a list.")
    for result in results:
        if not isinstance(result, FetchedSourceContent):
            raise ValueError("results must contain FetchedSourceContent entries.")
    return list(results)


def _ordered_results(results: list[FetchedSourceContent]) -> list[FetchedSourceContent]:
    return sorted(results, key=lambda result: result.source_id)


def _response_status(response: object, fallback: int | None) -> int:
    if fallback is not None:
        return int(fallback)
    getcode = getattr(response, "getcode")
    return int(getcode())


def _response_url(response: object, fallback: str) -> str:
    geturl = getattr(response, "geturl", None)
    if not callable(geturl):
        return fallback
    return str(geturl())


def _header_value(response: object, name: str) -> str | None:
    headers = getattr(response, "headers", None)
    if headers is None:
        info = getattr(response, "info", None)
        headers = info() if callable(info) else None
    if headers is None:
        return None
    value = headers.get(name)
    return str(value) if value is not None else None


def _parse_content_length(value: str | None) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(value)
    except ValueError:
        return None
    return parsed if parsed >= 0 else None


def _is_truncated(
    raw_sample: bytes,
    max_bytes: int,
    content_length: int | None,
) -> bool:
    if content_length is not None:
        return content_length > max_bytes
    return len(raw_sample) >= max_bytes


def _is_expected_status(source: SourceDefinition, status_code: int) -> bool:
    if source.expected_status_codes is None:
        return 200 <= status_code < 400
    return status_code in source.expected_status_codes


def _build_error(
    status_code: int,
    unexpected_status: bool,
    redirect_not_allowed: bool,
) -> str | None:
    if redirect_not_allowed:
        return "redirect_not_allowed"
    if unexpected_status:
        return f"unexpected_status:{status_code}"
    return None
