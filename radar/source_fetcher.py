"""Read-only source content fetcher without live parsing."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import socket
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from radar.source_registry import SourceDefinition


SCHEMA_VERSION = 1
DEFAULT_TIMEOUT_SECONDS = 10.0
MAX_ERROR_MESSAGE_LENGTH = 240
_USER_AGENT = "AI-Release-Radar-0130/1.0"
_TEXTUAL_CONTENT_TYPES = {
    "application/atom+xml",
    "application/javascript",
    "application/json",
    "application/rss+xml",
    "application/vnd.github+json",
    "application/x-ndjson",
    "application/xhtml+xml",
    "application/xml",
}
_HTML_CONTENT_TYPES = {"text/html", "application/xhtml+xml"}


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
    status: str | None = None
    http_status_code: int | None = None
    encoding: str | None = None
    fetched_at: str | None = None
    error_code: str | None = None
    error_message_sanitized: str | None = None
    content_preview_or_path_policy: str | None = None

    def to_dict(self) -> dict[str, Any]:
        http_status_code = (
            self.http_status_code
            if self.http_status_code is not None
            else self.status_code
        )
        return {
            "source_id": self.source_id,
            "url": self.url,
            "status": self.status if self.status is not None else _status_from_ok(self.ok),
            "ok": self.ok,
            "http_status_code": http_status_code,
            "status_code": self.status_code,
            "final_url": self.final_url,
            "content_type": self.content_type,
            "encoding": self.encoding,
            "content_length": self.content_length,
            "fetched_at": self.fetched_at,
            "content_preview_or_path_policy": self.content_preview_or_path_policy,
            "body_sample": self.body_sample,
            "truncated": self.truncated,
            "error_code": self.error_code,
            "error_message_sanitized": self.error_message_sanitized,
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
    fetched_at = _utc_now_iso()

    if not source.live_check_enabled:
        return _result_from_policy_error(
            source,
            fetched_at=fetched_at,
            error_code="live_check_disabled",
            error="live_check_disabled",
            error_message="Source live_check_enabled is false.",
            content_preview_or_path_policy="not_fetched_disabled",
        )

    effective_timeout = _effective_timeout(source, timeout_seconds)
    request = Request(
        source.url,
        method="GET",
        headers={"User-Agent": _USER_AGENT},
    )
    try:
        with urlopen(request, timeout=effective_timeout) as response:
            return _result_from_response(
                source,
                response,
                max_bytes,
                fetched_at=fetched_at,
            )
    except HTTPError as exc:
        try:
            return _result_from_response(
                source,
                exc,
                max_bytes,
                fetched_at=fetched_at,
                status_code=exc.code,
            )
        finally:
            exc.close()
    except (TimeoutError, URLError, OSError, socket.timeout) as exc:
        return _result_from_error(source, exc, fetched_at=fetched_at)


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
        if _effective_error_code(result) == "unexpected_status"
    ]
    redirect_not_allowed_source_ids = [
        result.source_id
        for result in ordered
        if _effective_error_code(result) == "redirect_not_allowed"
    ]
    content_type_rejected_source_ids = [
        result.source_id
        for result in ordered
        if _effective_error_code(result)
        in {"missing_content_type", "unsupported_content_type"}
    ]
    binary_content_source_ids = [
        result.source_id
        for result in ordered
        if _effective_error_code(result) in {"binary_content", "unsupported_content_type"}
    ]
    empty_content_source_ids = [
        result.source_id
        for result in ordered
        if _effective_error_code(result) == "empty_content"
    ]
    oversized_content_source_ids = [
        result.source_id
        for result in ordered
        if _effective_error_code(result) in {"response_too_large", "html_too_large"}
    ]
    network_error_source_ids = [
        result.source_id
        for result in ordered
        if _effective_error_code(result) in {"network_error", "timeout", "url_error"}
    ]
    return {
        "total": len(ordered),
        "ok": len(ok_source_ids),
        "failed": len(failed_source_ids),
        "disabled": len(disabled_source_ids),
        "truncated": len(truncated_source_ids),
        "unexpected_status": len(unexpected_status_source_ids),
        "redirect_not_allowed": len(redirect_not_allowed_source_ids),
        "content_type_rejected": len(content_type_rejected_source_ids),
        "binary_content": len(binary_content_source_ids),
        "empty_content": len(empty_content_source_ids),
        "oversized_content": len(oversized_content_source_ids),
        "network_error": len(network_error_source_ids),
        "ok_source_ids": ok_source_ids,
        "failed_source_ids": failed_source_ids,
        "disabled_source_ids": disabled_source_ids,
        "truncated_source_ids": truncated_source_ids,
        "unexpected_status_source_ids": unexpected_status_source_ids,
        "redirect_not_allowed_source_ids": redirect_not_allowed_source_ids,
        "content_type_rejected_source_ids": content_type_rejected_source_ids,
        "binary_content_source_ids": binary_content_source_ids,
        "empty_content_source_ids": empty_content_source_ids,
        "oversized_content_source_ids": oversized_content_source_ids,
        "network_error_source_ids": network_error_source_ids,
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
    fetched_at: str,
    status_code: int | None = None,
) -> FetchedSourceContent:
    raw_sample = response.read(max_bytes + 1)
    response_status = _response_status(response, status_code)
    final_url = _response_url(response, source.url)
    raw_content_type = _header_value(response, "content-type")
    content_type, encoding = _parse_content_type(raw_content_type)
    content_length = _content_length_from_response(response, raw_sample, max_bytes)
    truncated = _is_truncated(raw_sample, max_bytes, content_length)
    unexpected_status = not _is_expected_status(source, response_status)
    redirect_not_allowed = final_url != source.url and not source.allow_redirects
    error_code = _response_error_code(
        raw_sample=raw_sample,
        max_bytes=max_bytes,
        content_type=content_type,
        response_status=response_status,
        unexpected_status=unexpected_status,
        redirect_not_allowed=redirect_not_allowed,
        truncated=truncated,
    )
    if error_code is not None:
        return _response_error_result(
            source,
            fetched_at=fetched_at,
            status_code=response_status,
            final_url=final_url,
            content_type=content_type,
            encoding=encoding,
            content_length=content_length,
            truncated=truncated,
            error_code=error_code,
        )
    decoded_sample, decode_error = _decode_text_sample(raw_sample, encoding)
    if decode_error is not None:
        return _response_error_result(
            source,
            fetched_at=fetched_at,
            status_code=response_status,
            final_url=final_url,
            content_type=content_type,
            encoding=encoding,
            content_length=content_length,
            truncated=truncated,
            error_code=decode_error,
        )
    body_sample = _content_preview(decoded_sample)
    return FetchedSourceContent(
        source_id=source.source_id,
        url=source.url,
        ok=True,
        status_code=response_status,
        http_status_code=response_status,
        final_url=final_url,
        content_type=content_type,
        encoding=encoding,
        content_length=content_length,
        fetched_at=fetched_at,
        content_preview_or_path_policy="inline_preview_only",
        body_sample=body_sample,
        truncated=truncated,
        error_code=None,
        error_message_sanitized=None,
        error=None,
        status="fetched",
    )


def _result_from_error(
    source: SourceDefinition,
    exc: BaseException,
    *,
    fetched_at: str | None = None,
) -> FetchedSourceContent:
    fetched_at = fetched_at if fetched_at is not None else _utc_now_iso()
    error_code = _classify_exception(exc)
    return FetchedSourceContent(
        source_id=source.source_id,
        url=source.url,
        ok=False,
        status_code=None,
        http_status_code=None,
        final_url=None,
        content_type=None,
        encoding=None,
        content_length=None,
        fetched_at=fetched_at,
        content_preview_or_path_policy="preview_omitted_error",
        body_sample=None,
        truncated=False,
        error_code=error_code,
        error_message_sanitized=_sanitize_error_message(
            f"{exc.__class__.__name__}: {exc}",
            source,
        ),
        error=error_code,
        status="network_error" if error_code in {"timeout", "url_error", "network_error"} else "failed",
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


def _result_from_policy_error(
    source: SourceDefinition,
    *,
    fetched_at: str,
    error_code: str,
    error: str,
    error_message: str,
    content_preview_or_path_policy: str,
) -> FetchedSourceContent:
    return FetchedSourceContent(
        source_id=source.source_id,
        url=source.url,
        ok=False,
        status_code=None,
        http_status_code=None,
        final_url=None,
        content_type=None,
        encoding=None,
        content_length=None,
        fetched_at=fetched_at,
        content_preview_or_path_policy=content_preview_or_path_policy,
        body_sample=None,
        truncated=False,
        error_code=error_code,
        error_message_sanitized=_sanitize_error_message(error_message, source),
        error=error,
        status="disabled" if error_code == "live_check_disabled" else "failed",
    )


def _response_error_result(
    source: SourceDefinition,
    *,
    fetched_at: str,
    status_code: int,
    final_url: str,
    content_type: str | None,
    encoding: str | None,
    content_length: int | None,
    truncated: bool,
    error_code: str,
) -> FetchedSourceContent:
    return FetchedSourceContent(
        source_id=source.source_id,
        url=source.url,
        ok=False,
        status_code=status_code,
        http_status_code=status_code,
        final_url=final_url,
        content_type=content_type,
        encoding=encoding,
        content_length=content_length,
        fetched_at=fetched_at,
        content_preview_or_path_policy=_preview_policy_for_error(error_code),
        body_sample=None,
        truncated=truncated,
        error_code=error_code,
        error_message_sanitized=_sanitize_error_message(
            _response_error_message(
                error_code,
                status_code=status_code,
                final_url=final_url,
                content_type=content_type,
            ),
            source,
        ),
        error=_legacy_error_for_code(error_code, status_code),
        status="rejected",
    )


def _response_error_code(
    *,
    raw_sample: bytes,
    max_bytes: int,
    content_type: str | None,
    response_status: int,
    unexpected_status: bool,
    redirect_not_allowed: bool,
    truncated: bool,
) -> str | None:
    if redirect_not_allowed:
        return "redirect_not_allowed"
    if unexpected_status:
        return "unexpected_status"
    if not raw_sample:
        return "empty_content"
    if content_type is None:
        return "missing_content_type"
    if not _is_textual_content_type(content_type):
        return "unsupported_content_type"
    if _is_binary_sample(raw_sample):
        return "binary_content"
    if truncated or len(raw_sample) > max_bytes:
        return "html_too_large" if content_type in _HTML_CONTENT_TYPES else "response_too_large"
    return None


def _header_value(response: object, name: str) -> str | None:
    headers = getattr(response, "headers", None)
    if headers is None:
        info = getattr(response, "info", None)
        headers = info() if callable(info) else None
    if headers is None:
        return None
    value = headers.get(name)
    if value is None and hasattr(headers, "items"):
        for header_name, header_value in headers.items():
            if str(header_name).lower() == name.lower():
                value = header_value
                break
    return str(value) if value is not None else None


def _parse_content_type(value: str | None) -> tuple[str | None, str | None]:
    if value is None or not value.strip():
        return None, None
    media_type, *parameters = value.split(";")
    content_type = media_type.strip().lower()
    encoding: str | None = None
    for parameter in parameters:
        key, separator, parameter_value = parameter.partition("=")
        if separator and key.strip().lower() == "charset":
            encoding = parameter_value.strip().strip("\"'").lower() or None
    return content_type, encoding or "utf-8"


def _content_length_from_response(
    response: object,
    raw_sample: bytes,
    max_bytes: int,
) -> int | None:
    parsed = _parse_content_length(_header_value(response, "content-length"))
    if parsed is not None:
        return parsed
    if len(raw_sample) > max_bytes:
        return None
    return len(raw_sample)


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
    return len(raw_sample) > max_bytes


def _is_expected_status(source: SourceDefinition, status_code: int) -> bool:
    if source.expected_status_codes is None:
        return 200 <= status_code < 400
    return status_code in source.expected_status_codes


def _is_textual_content_type(content_type: str) -> bool:
    return content_type.startswith("text/") or content_type in _TEXTUAL_CONTENT_TYPES


def _is_binary_sample(raw_sample: bytes) -> bool:
    if b"\x00" in raw_sample:
        return True
    if not raw_sample:
        return False
    control_bytes = sum(
        1
        for byte in raw_sample
        if byte < 32 and byte not in {9, 10, 13}
    )
    return control_bytes / len(raw_sample) > 0.10


def _decode_text_sample(
    raw_sample: bytes,
    encoding: str | None,
) -> tuple[str, str | None]:
    effective_encoding = encoding or "utf-8"
    try:
        return raw_sample.decode(effective_encoding, errors="replace"), None
    except LookupError:
        return "", "invalid_encoding"


def _content_preview(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _preview_policy_for_error(error_code: str) -> str:
    if error_code == "unsupported_content_type":
        return "preview_omitted_unsupported_content_type"
    if error_code == "binary_content":
        return "preview_omitted_binary"
    if error_code in {"response_too_large", "html_too_large"}:
        return "preview_omitted_response_too_large"
    return "preview_omitted_error"


def _response_error_message(
    error_code: str,
    *,
    status_code: int,
    final_url: str,
    content_type: str | None,
) -> str:
    if error_code == "redirect_not_allowed":
        return f"Redirect not allowed. Final URL: {final_url}"
    if error_code == "unexpected_status":
        return f"Unexpected HTTP status {status_code}."
    if error_code == "empty_content":
        return "Response body is empty."
    if error_code == "missing_content_type":
        return "Response content-type is missing."
    if error_code == "unsupported_content_type":
        return f"Unsupported content-type: {content_type}"
    if error_code == "binary_content":
        return "Response appears to contain binary content."
    if error_code == "html_too_large":
        return "HTML response exceeds the configured maximum byte limit."
    if error_code == "response_too_large":
        return "Response exceeds the configured maximum byte limit."
    if error_code == "invalid_encoding":
        return "Response declares an unsupported text encoding."
    return error_code


def _legacy_error_for_code(error_code: str, status_code: int) -> str:
    if error_code == "unexpected_status":
        return f"unexpected_status:{status_code}"
    return error_code


def _sanitize_error_message(message: str, source: SourceDefinition) -> str:
    sanitized = " ".join(str(message).split())
    sanitized = sanitized.replace(source.url, "<source_url>")
    if len(sanitized) <= MAX_ERROR_MESSAGE_LENGTH:
        return sanitized
    return sanitized[: MAX_ERROR_MESSAGE_LENGTH - 3] + "..."


def _classify_exception(exc: BaseException) -> str:
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return "timeout"
    if isinstance(exc, URLError):
        return "url_error"
    if isinstance(exc, OSError):
        return "network_error"
    return "fetch_error"


def _effective_error_code(result: FetchedSourceContent) -> str | None:
    if result.error_code is not None:
        return result.error_code
    if result.error is None:
        return None
    if result.error.startswith("unexpected_status:"):
        return "unexpected_status"
    return result.error


def _status_from_ok(ok: bool) -> str:
    return "fetched" if ok else "failed"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
