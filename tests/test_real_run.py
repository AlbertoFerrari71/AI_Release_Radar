import tempfile
import unittest
from pathlib import Path

from radar.json_utils import read_json, write_json
from radar.real_run import run_real_radar_report
from radar.source_fetcher import FetchedSourceContent


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "examples" / "fixtures"
PROJECT_MAP_PATH = FIXTURES_DIR / "0070_project_map.json"


class RealRunTests(unittest.TestCase):
    def test_real_run_writes_manual_report_outputs_outside_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            registry_path = temp_root / "sources.json"
            output_dir = temp_root / "0180_first_real_manual_run"
            write_json(registry_path, self.registry())

            result = run_real_radar_report(
                source_registry=str(registry_path),
                output_dir=str(output_dir),
                project_map=str(PROJECT_MAP_PATH),
                run_id="0180-test-run",
                generated_at="2026-06-10T11:00:00Z",
                fetcher=self.fake_fetcher,
            )

            self.assertIn(result.status, {"CHANGES_FOUND", "ACTION_RECOMMENDED"})
            self.assertEqual(result.source_count, 2)
            self.assertGreater(result.item_count, 0)
            self.assertEqual(result.new_count, result.item_count)
            self.assertTrue(Path(result.report_full).is_file())
            self.assertTrue(Path(result.report_compact).is_file())
            self.assertTrue(Path(result.run_summary).is_file())
            self.assertTrue(Path(result.run_index_entry).is_file())
            self.assertTrue(Path(result.runs_index).is_file())
            full_report = Path(result.report_full).read_text(encoding="utf-8")
            self.assertIn("baseline / first observation", full_report)
            self.assertNotIn("offline fixture only", full_report)
            summary = read_json(result.run_summary)
            self.assertEqual(summary["result"]["run_id"], "0180-test-run")

    def test_real_run_rejects_output_inside_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "sources.json"
            write_json(registry_path, self.registry())
            with self.assertRaisesRegex(ValueError, "outside repository"):
                run_real_radar_report(
                    source_registry=str(registry_path),
                    output_dir=str(REPO_ROOT / "tmp_real_run_output"),
                    project_map=str(PROJECT_MAP_PATH),
                    fetcher=self.fake_fetcher,
                )

    def test_real_run_does_not_create_last_or_latest_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            registry_path = temp_root / "sources.json"
            output_dir = temp_root / "0180_first_real_manual_run"
            write_json(registry_path, self.registry())

            run_real_radar_report(
                source_registry=str(registry_path),
                output_dir=str(output_dir),
                project_map=str(PROJECT_MAP_PATH),
                run_id="0180-test-run",
                generated_at="2026-06-10T11:00:00Z",
                fetcher=self.fake_fetcher,
            )

            forbidden = [
                path.name
                for path in output_dir.rglob("*")
                if path.name.startswith("LAST-") or path.name.startswith("latest-")
            ]
            self.assertEqual(forbidden, [])

    def test_real_run_compares_with_previous_snapshot_dir_when_available(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            registry_path = temp_root / "sources.json"
            first_dir = temp_root / "first"
            second_dir = temp_root / "second"
            write_json(registry_path, self.registry())

            run_real_radar_report(
                source_registry=str(registry_path),
                output_dir=str(first_dir),
                project_map=str(PROJECT_MAP_PATH),
                run_id="0180-first",
                generated_at="2026-06-10T11:00:00Z",
                fetcher=self.fake_fetcher,
            )
            second = run_real_radar_report(
                source_registry=str(registry_path),
                output_dir=str(second_dir),
                project_map=str(PROJECT_MAP_PATH),
                previous_snapshot_dir=str(first_dir),
                run_id="0180-second",
                generated_at="2026-06-10T12:00:00Z",
                fetcher=self.fake_fetcher,
            )

            self.assertEqual(second.new_count, 0)
            self.assertEqual(second.changed_count, 0)
            self.assertEqual(second.removed_count, 0)
            self.assertEqual(second.unchanged_count, second.item_count)

    def fake_fetcher(self, sources, timeout_seconds=None, max_sources=None, max_bytes=65536):
        github_body = (FIXTURES_DIR / "0150_github_releases_api_fixture.json").read_text(
            encoding="utf-8"
        )
        changelog_body = (FIXTURES_DIR / "0160_codex_changelog_fixture.md").read_text(
            encoding="utf-8"
        )
        results = []
        for source in sources:
            if source.source_type == "github_api":
                body = github_body
                content_type = "application/json"
            else:
                body = changelog_body
                content_type = "text/markdown"
            results.append(
                FetchedSourceContent(
                    source_id=source.source_id,
                    url=source.url,
                    ok=True,
                    status_code=200,
                    http_status_code=200,
                    final_url=source.url,
                    content_type=content_type,
                    encoding="utf-8",
                    content_length=len(body.encode("utf-8")),
                    fetched_at="2026-06-10T11:00:00Z",
                    content_preview_or_path_policy="inline_preview_only",
                    body_sample=body,
                    truncated=False,
                    error_code=None,
                    error_message_sanitized=None,
                    error=None,
                    status="fetched",
                )
            )
        return results

    def registry(self):
        return {
            "schema_version": 1,
            "provider": "openai",
            "sources": [
                self.source("openai_codex_changelog", "official_changelog"),
                self.source("github_api_openai_codex_releases", "github_api", provider="github"),
            ],
        }

    def source(self, source_id: str, source_type: str, provider: str = "openai"):
        return {
            "source_id": source_id,
            "provider": provider,
            "name": source_id.replace("_", " ").title(),
            "url": f"https://example.invalid/{source_id}",
            "source_type": source_type,
            "priority": 1 if provider == "openai" else 2,
            "reliability": "primary" if provider == "openai" else "secondary",
            "machine_readable": source_type == "github_api",
            "category_hints": ["codex_cli"],
            "verification_status": "verified_url_format",
            "notes": "Offline real-run test source.",
            "expected_status_codes": [200],
            "allow_redirects": True,
            "timeout_seconds": 1.0,
            "live_check_enabled": True,
            "manual_review_required": False,
        }


if __name__ == "__main__":
    unittest.main()
