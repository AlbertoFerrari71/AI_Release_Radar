import json
import os
import unittest

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


if __name__ == "__main__":
    unittest.main()
