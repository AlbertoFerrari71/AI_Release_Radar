"""Read-only URL format and live verification helpers."""

from __future__ import annotations

from dataclasses import dataclass
import socket
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
    redirected: bool = False
    unreachable: bool = False
    timeout: bool = False
    unexpected_status: bool = False
    invalid_url: bool = False
    disabled: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "url": self.url,
            "ok": self.ok,
            "status_code": self.status_code,
            "final_url": self.final_url,
            "error": self.error,
            "redirected": self.redirected,
            "unreachable": self.unreachable,
            "timeout": self.timeout,
            "unexpected_status": self.unexpected_status,
            "invalid_url": self.invalid_url,
            "disabled": self.disabled,
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
    if not source.live_check_enabled:
        return UrlVerificationResult(
            source_id=source.source_id,
            url=source.url,
            ok=False,
            status_code=None,
            final_url=None,
            error="live_check_disabled",
            disabled=True,
        )
    if not verify_url_format(source.url):
        return UrlVerificationResult(
            source_id=source.source_id,
            url=source.url,
            ok=False,
            status_code=None,
            final_url=None,
            error="invalid_url_format",
            invalid_url=True,
        )
    effective_timeout = (
        source.timeout_seconds if source.timeout_seconds is not None else timeout_seconds
    )
    if (
        not isinstance(effective_timeout, (int, float))
        or isinstance(effective_timeout, bool)
        or effective_timeout <= 0
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
        return _request_url(source, "HEAD", float(effective_timeout), read_body=False)
    except HTTPError as exc:
        if exc.code in {403, 405}:
            return _verify_url_live_with_get(source, float(effective_timeout))
        return _result_from_http_error(source, exc)
    except (TimeoutError, URLError, OSError, socket.timeout) as exc:
        return _result_from_error(source, exc)


def _verify_url_live_with_get(
    source: SourceDefinition,
    timeout_seconds: float,
) -> UrlVerificationResult:
    try:
        return _request_url(source, "GET", timeout_seconds, read_body=True)
    except HTTPError as exc:
        return _result_from_http_error(source, exc)
    except (TimeoutError, URLError, OSError, socket.timeout) as exc:
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
    redirected = final_url != source.url
    unexpected_status = not _is_expected_status(source, status_code)
    redirect_not_allowed = redirected and not source.allow_redirects
    ok = not unexpected_status and not redirect_not_allowed
    return UrlVerificationResult(
        source_id=source.source_id,
        url=source.url,
        ok=ok,
        status_code=status_code,
        final_url=final_url,
        error=_build_success_error(status_code, unexpected_status, redirect_not_allowed),
        redirected=redirected,
        unexpected_status=unexpected_status or redirect_not_allowed,
    )


def _result_from_http_error(source: SourceDefinition, exc: HTTPError) -> UrlVerificationResult:
    status_code = int(exc.code)
    final_url = exc.geturl()
    redirected = final_url != source.url
    unexpected_status = not _is_expected_status(source, status_code)
    redirect_not_allowed = redirected and not source.allow_redirects
    ok = not unexpected_status and not redirect_not_allowed
    return UrlVerificationResult(
        source_id=source.source_id,
        url=source.url,
        ok=ok,
        status_code=status_code,
        final_url=final_url,
        error=None if ok else f"http_error:{status_code}",
        redirected=redirected,
        unexpected_status=unexpected_status or redirect_not_allowed,
    )


def _result_from_error(source: SourceDefinition, exc: BaseException) -> UrlVerificationResult:
    timeout = _is_timeout_error(exc)
    return UrlVerificationResult(
        source_id=source.source_id,
        url=source.url,
        ok=False,
        status_code=None,
        final_url=None,
        error=f"{exc.__class__.__name__}: {exc}",
        timeout=timeout,
        unreachable=not timeout,
    )


def _is_expected_status(source: SourceDefinition, status_code: int) -> bool:
    if source.expected_status_codes is None:
        return 200 <= status_code < 400
    return status_code in source.expected_status_codes


def _build_success_error(
    status_code: int,
    unexpected_status: bool,
    redirect_not_allowed: bool,
) -> str | None:
    if redirect_not_allowed:
        return "redirect_not_allowed"
    if unexpected_status:
        return f"unexpected_status:{status_code}"
    return None


def _is_timeout_error(exc: BaseException) -> bool:
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return True
    if isinstance(exc, URLError):
        reason = getattr(exc, "reason", None)
        return isinstance(reason, (TimeoutError, socket.timeout))
    return False
