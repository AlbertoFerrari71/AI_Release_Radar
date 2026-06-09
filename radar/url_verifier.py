"""Read-only URL format and live verification helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from radar.source_registry import SourceDefinition


_MAX_BODY_READ_BYTES = 1024
_USER_AGENT = "AI-Release-Radar-0100/1.0"


@dataclass(frozen=True, kw_only=True)
class UrlVerificationResult:
    """Outcome of one read-only URL verification attempt."""

    source_id: str
    url: str
    ok: bool
    status_code: int | None
    final_url: str | None
    error: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "url": self.url,
            "ok": self.ok,
            "status_code": self.status_code,
            "final_url": self.final_url,
            "error": self.error,
        }


def verify_url_format(url: str) -> bool:
    """Return True when url is a syntactically usable https URL."""
    if not isinstance(url, str) or not url.strip():
        return False
    parsed = urlparse(url)
    return parsed.scheme == "https" and bool(parsed.netloc)


def verify_url_live(
    source: SourceDefinition,
    timeout_seconds: float = 10.0,
) -> UrlVerificationResult:
    """Verify one source URL without saving or parsing page content.

    HEAD is attempted first because it avoids reading a response body. When a
    server rejects HEAD with 403 or 405, the verifier falls back to GET and
    reads at most a small fixed prefix before closing the response.
    """
    if not verify_url_format(source.url):
        return UrlVerificationResult(
            source_id=source.source_id,
            url=source.url,
            ok=False,
            status_code=None,
            final_url=None,
            error="invalid_url_format",
        )
    if (
        not isinstance(timeout_seconds, (int, float))
        or isinstance(timeout_seconds, bool)
        or timeout_seconds <= 0
    ):
        return UrlVerificationResult(
            source_id=source.source_id,
            url=source.url,
            ok=False,
            status_code=None,
            final_url=None,
            error="invalid_timeout",
        )

    try:
        return _request_url(source, "HEAD", float(timeout_seconds), read_body=False)
    except HTTPError as exc:
        if exc.code in {403, 405}:
            return _verify_url_live_with_get(source, float(timeout_seconds))
        return _result_from_http_error(source, exc)
    except (TimeoutError, URLError, OSError) as exc:
        return _result_from_error(source, exc)


def _verify_url_live_with_get(
    source: SourceDefinition,
    timeout_seconds: float,
) -> UrlVerificationResult:
    try:
        return _request_url(source, "GET", timeout_seconds, read_body=True)
    except HTTPError as exc:
        return _result_from_http_error(source, exc)
    except (TimeoutError, URLError, OSError) as exc:
        return _result_from_error(source, exc)


def _request_url(
    source: SourceDefinition,
    method: str,
    timeout_seconds: float,
    *,
    read_body: bool,
) -> UrlVerificationResult:
    request = Request(
        source.url,
        method=method,
        headers={"User-Agent": _USER_AGENT},
    )
    with urlopen(request, timeout=timeout_seconds) as response:
        if read_body:
            response.read(_MAX_BODY_READ_BYTES)
        status_code = int(response.getcode())
        final_url = response.geturl()
    return UrlVerificationResult(
        source_id=source.source_id,
        url=source.url,
        ok=200 <= status_code < 400,
        status_code=status_code,
        final_url=final_url,
        error=None if 200 <= status_code < 400 else f"http_status:{status_code}",
    )


def _result_from_http_error(source: SourceDefinition, exc: HTTPError) -> UrlVerificationResult:
    status_code = int(exc.code)
    return UrlVerificationResult(
        source_id=source.source_id,
        url=source.url,
        ok=False,
        status_code=status_code,
        final_url=exc.geturl(),
        error=f"http_error:{status_code}",
    )


def _result_from_error(source: SourceDefinition, exc: BaseException) -> UrlVerificationResult:
    return UrlVerificationResult(
        source_id=source.source_id,
        url=source.url,
        ok=False,
        status_code=None,
        final_url=None,
        error=f"{exc.__class__.__name__}: {exc}",
    )
