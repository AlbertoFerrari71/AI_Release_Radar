import json
import tempfile
import unittest
from pathlib import Path

from radar.json_utils import read_json, write_json
from radar.live_snapshot import RUNS_INDEX_FILENAME, run_live_snapshot
from radar.models import SourceSnapshot
from radar.source_fetcher import FetchedSourceContent


REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "examples" / "fixtures"


class LiveSnapshotTests(unittest.TestCase):
    def test_run_live_snapshot_writes_outputs_outside_repo_with_fake_fetcher(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            registry_path = temp_root / "sources.json"
            output_dir = temp_root / "0170_manual"
            write_json(registry_path, self.registry())

            result = run_live_snapshot(
                source_registry=str(registry_path),
                output_dir=str(output_dir),
                timeout_seconds=1.0,
                max_sources=None,
                max_bytes=65536,
                run_id="0170-test-run",
                fetched_at="2026-06-10T10:00:00Z",
                fetcher=self.fake_fetcher,
            )

            self.assertEqual(result.status, "success")
            self.assertEqual(result.source_count, 2)
            self.assertEqual(result.snapshot_count, 2)
            self.assertEqual(result.parsed_count, 2)
            self.assertEqual(result.skipped_count, 0)
            self.assertEqual(result.failed_count, 0)
            self.assertTrue(Path(result.run_summary_path).is_file())
            self.assertTrue(Path(result.run_index_entry_path).is_file())
            self.assertTrue((output_dir / RUNS_INDEX_FILENAME).is_file())
            self.assertEqual(len((output_dir / RUNS_INDEX_FILENAME).read_text().splitlines()), 1)

            snapshots = [
                SourceSnapshot.from_dict(read_json(path))
                for path in result.snapshot_paths
            ]
            self.assertEqual({snapshot.fetch_status for snapshot in snapshots}, {"fetch_ok_parsed"})
            self.assertTrue(all(snapshot.items for snapshot in snapshots))

    def test_run_live_snapshot_rejects_output_inside_repo(self):
        with tempfile.TemporaryDirectory() as tmp:
            registry_path = Path(tmp) / "sources.json"
            write_json(registry_path, self.registry())
            with self.assertRaisesRegex(ValueError, "outside repository"):
                run_live_snapshot(
                    source_registry=str(registry_path),
                    output_dir=str(REPO_ROOT / "tmp_live_snapshot_output"),
                    fetcher=self.fake_fetcher,
                )

    def test_run_live_snapshot_does_not_create_last_or_latest_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            registry_path = temp_root / "sources.json"
            output_dir = temp_root / "0170_manual"
            write_json(registry_path, self.registry())

            run_live_snapshot(
                source_registry=str(registry_path),
                output_dir=str(output_dir),
                run_id="0170-test-run",
                fetched_at="2026-06-10T10:00:00Z",
                fetcher=self.fake_fetcher,
            )

            forbidden = [
                path.name
                for path in output_dir.rglob("*")
                if path.name.startswith("LAST-") or path.name.startswith("latest-")
            ]
            self.assertEqual(forbidden, [])

    def test_run_live_snapshot_skips_unsupported_source_without_failing(self):
        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            registry_data = self.registry()
            registry_data["sources"].append(self.source("openai_codex_skills", "official_docs"))
            registry_path = temp_root / "sources.json"
            output_dir = temp_root / "0170_manual"
            write_json(registry_path, registry_data)

            result = run_live_snapshot(
                source_registry=str(registry_path),
                output_dir=str(output_dir),
                run_id="0170-test-run",
                fetched_at="2026-06-10T10:00:00Z",
                fetcher=self.fake_fetcher,
            )

            self.assertEqual(result.status, "success")
            self.assertEqual(result.source_count, 3)
            self.assertEqual(result.parsed_count, 2)
            self.assertEqual(result.skipped_count, 1)

    def fake_fetcher(self, sources, timeout_seconds=None, max_sources=None, max_bytes=65536):
        results = []
        github_body = (FIXTURES_DIR / "0150_github_releases_api_fixture.json").read_text(
            encoding="utf-8"
        )
        changelog_body = (FIXTURES_DIR / "0160_codex_changelog_fixture.md").read_text(
            encoding="utf-8"
        )
        for source in sources:
            if source.source_type == "github_api":
                body = github_body
                content_type = "application/json"
            elif source.source_id == "openai_codex_changelog":
                body = changelog_body
                content_type = "text/markdown"
            else:
                body = "Unsupported source fixture body."
                content_type = "text/plain"
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
                    fetched_at="2026-06-10T10:00:00Z",
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
            "notes": "Offline live-snapshot test source.",
            "expected_status_codes": [200],
            "allow_redirects": True,
            "timeout_seconds": 1.0,
            "live_check_enabled": True,
            "manual_review_required": False,
        }


if __name__ == "__main__":
    unittest.main()
