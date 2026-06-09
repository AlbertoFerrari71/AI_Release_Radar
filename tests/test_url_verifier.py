import json
import os
import unittest
from urllib.error import HTTPError, URLError
from unittest.mock import patch

from radar.source_registry import SourceDefinition
from radar.url_verifier import (
    UrlVerificationResult,
    verify_url_format,
    verify_url_live,
)


class UrlVerifierTests(unittest.TestCase):
    def test_verify_url_format_accepts_https_url(self):
        self.assertTrue(verify_url_format("https://developers.openai.com/codex/changelog"))

    def test_verify_url_format_rejects_http_url(self):
        self.assertFalse(verify_url_format("http://developers.openai.com/codex/changelog"))

    def test_verify_url_format_rejects_invalid_url(self):
        self.assertFalse(verify_url_format("not-a-url"))

    def test_url_verification_result_is_json_serializable(self):
        result = UrlVerificationResult(
            source_id="offline_source",
            url="https://example.invalid/source",
            ok=False,
            status_code=None,
            final_url=None,
            error="simulated_unreachable",
        )
        encoded = json.dumps(result.to_dict(), sort_keys=True)
        self.assertIn("simulated_unreachable", encoded)

    def test_live_check_enabled_false_returns_disabled_without_network(self):
        source = self.source(live_check_enabled=False)
        with patch("radar.url_verifier.urlopen") as mocked_urlopen:
            result = verify_url_live(source)
        mocked_urlopen.assert_not_called()
        self.assertFalse(result.ok)
        self.assertTrue(result.disabled)
        self.assertEqual(result.error, "live_check_disabled")

    def test_redirect_is_classified(self):
        source = self.source()
        response = FakeResponse(
            status_code=200,
            final_url="https://developers.openai.com/codex/changelog",
        )
        with patch("radar.url_verifier.urlopen", return_value=response):
            result = verify_url_live(source)
        self.assertTrue(result.ok)
        self.assertTrue(result.redirected)
        self.assertFalse(result.unexpected_status)

    def test_redirect_not_allowed_is_unexpected(self):
        source = self.source(allow_redirects=False)
        response = FakeResponse(
            status_code=200,
            final_url="https://developers.openai.com/codex/changelog",
        )
        with patch("radar.url_verifier.urlopen", return_value=response):
            result = verify_url_live(source)
        self.assertFalse(result.ok)
        self.assertTrue(result.redirected)
        self.assertTrue(result.unexpected_status)
        self.assertEqual(result.error, "redirect_not_allowed")

    def test_timeout_is_classified(self):
        source = self.source()
        with patch("radar.url_verifier.urlopen", side_effect=TimeoutError("simulated timeout")):
            result = verify_url_live(source)
        self.assertFalse(result.ok)
        self.assertTrue(result.timeout)
        self.assertFalse(result.unreachable)

    def test_unreachable_is_classified(self):
        source = self.source()
        with patch("radar.url_verifier.urlopen", side_effect=URLError("simulated unreachable")):
            result = verify_url_live(source)
        self.assertFalse(result.ok)
        self.assertTrue(result.unreachable)
        self.assertFalse(result.timeout)

    def test_unexpected_status_is_classified(self):
        source = self.source(expected_status_codes=[200])
        error = HTTPError(source.url, 500, "server error", hdrs=None, fp=None)
        with patch("radar.url_verifier.urlopen", side_effect=error):
            result = verify_url_live(source)
        self.assertFalse(result.ok)
        self.assertTrue(result.unexpected_status)
        self.assertEqual(result.status_code, 500)

    def test_expected_http_error_status_can_be_ok(self):
        source = self.source(expected_status_codes=[404])
        error = HTTPError(source.url, 404, "not found", hdrs=None, fp=None)
        with patch("radar.url_verifier.urlopen", side_effect=error):
            result = verify_url_live(source)
        self.assertTrue(result.ok)
        self.assertFalse(result.unexpected_status)

    @unittest.skipUnless(
        os.environ.get("AI_RELEASE_RADAR_RUN_LIVE_TESTS") == "1",
        "live URL tests require AI_RELEASE_RADAR_RUN_LIVE_TESTS=1",
    )
    def test_live_verify_url_is_opt_in(self):
        source = SourceDefinition(
            source_id="openai_codex_changelog",
            provider="openai",
            name="OpenAI Codex Changelog",
            url="https://developers.openai.com/codex/changelog",
            source_type="official_changelog",
            priority=1,
            reliability="primary",
            machine_readable=False,
            category_hints=["codex_cli"],
            verification_status="verified_url_format",
            notes="Live opt-in test source.",
        )
        result = verify_url_live(source, timeout_seconds=10.0)
        self.assertEqual(result.source_id, source.source_id)
        self.assertIsInstance(result.ok, bool)

    def source(self, **overrides):
        data = {
            "source_id": "openai_codex_changelog",
            "provider": "openai",
            "name": "OpenAI Codex Changelog",
            "url": "https://developers.openai.com/codex",
            "source_type": "official_changelog",
            "priority": 1,
            "reliability": "primary",
            "machine_readable": False,
            "category_hints": ["codex_cli"],
            "verification_status": "verified_url_format",
            "notes": "Offline test source.",
        }
        data.update(overrides)
        return SourceDefinition(**data)


class FakeResponse:
    def __init__(self, status_code: int, final_url: str):
        self.status_code = status_code
        self.final_url = final_url

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self, size: int):
        return b""

    def getcode(self):
        return self.status_code

    def geturl(self):
        return self.final_url


if __name__ == "__main__":
    unittest.main()
