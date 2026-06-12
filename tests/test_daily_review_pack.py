import json
import tempfile
import unittest
from pathlib import Path

from radar.daily_review_pack import build_daily_review_pack, write_daily_review_pack


class DailyReviewPackTests(unittest.TestCase):
    def test_daily_review_pack_is_bridge_only_manual_and_deterministic(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = self.create_run(root / "runs" / "0320_0400_daily_sim_20260612_051505")
            scheduler_log = self.create_scheduler_log(root / "scheduler.log")
            output_dir = root / "daily_review_packs" / run_dir.name

            result = write_daily_review_pack(
                run_dir,
                output_dir,
                scheduler_log_path=scheduler_log,
            )
            pack = json.loads(Path(result["json_path"]).read_text(encoding="utf-8"))
            markdown = Path(result["markdown_path"]).read_text(encoding="utf-8")

            self.assertEqual(result["run_id"], run_dir.name)
            self.assertEqual(pack["readiness"], "READY_FOR_SUPERVISED_HUMAN_REVIEW_WITH_WARNINGS")
            self.assertTrue(pack["safety_summary"]["no_auto_action"])
            self.assertTrue(pack["safety_summary"]["no_email"])
            self.assertTrue(pack["safety_summary"]["no_runtime_llm"])
            self.assertFalse(pack["prompt_suggestions_summary"]["suggestions"][0]["executed"])
            self.assertTrue(pack["prompt_suggestions_summary"]["suggestions"][0]["manual_only"])
            self.assertEqual(pack["source_coverage_summary"]["manual_review_required_count"], 1)
            self.assertEqual(len(pack["manual_review_sources"]), 1)
            self.assertEqual(pack["unsupported_sources_explained"], [])
            self.assertIn("maintenance_backlog_pointers", pack)
            self.assertIn("Source Coverage Final Matrix", markdown)
            self.assertIn("Manual Review Queue", markdown)
            self.assertIn("prompts_executed: false", markdown)
            self.assertEqual(
                {path.name for path in output_dir.iterdir()},
                {"1390-Daily_Review_Pack.json", "1390-Daily_Review_Pack.md"},
            )

    def test_daily_review_pack_rejects_repo_and_latest_output_paths(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = self.create_run(root / "run")

            with self.assertRaisesRegex(ValueError, "outside repository"):
                write_daily_review_pack(run_dir, Path.cwd() / "tmp_daily_review_pack")

            with self.assertRaisesRegex(ValueError, "LAST-\\* or latest-\\*"):
                write_daily_review_pack(run_dir, root / "latest-review-pack")

    def test_build_daily_review_pack_does_not_write_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            run_dir = self.create_run(root / "run")
            before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))

            pack = build_daily_review_pack(run_dir)

            after = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
            self.assertEqual(pack["run_id"], "run")
            self.assertEqual(after, before)

    def create_run(self, run_dir: Path) -> Path:
        run_dir.mkdir(parents=True)
        diagnostics = [
            {
                "source_id": "github_api_openai_codex_releases",
                "provider": "github",
                "coverage_priority": "P0",
                "diagnostic_status": "parsed",
                "fetch_status": "fetched",
                "parser_status": "parsed",
                "http_status_code": 200,
                "item_count": 10,
                "manual_review_required": False,
                "scheduler_readiness": "ready",
                "recommended_follow_up": "use_parsed_items",
            },
            {
                "source_id": "openai_release_notes_hub",
                "provider": "openai",
                "coverage_priority": "P2",
                "diagnostic_status": "manual_review_required",
                "fetch_status": "rejected",
                "parser_status": "fetch_failed",
                "http_status_code": 403,
                "item_count": 0,
                "manual_review_required": True,
                "scheduler_readiness": "hold",
                "recommended_follow_up": "manual_review_source",
            },
        ]
        result = {
            "run_id": "0180-20260612-051505Z",
            "status": "CHANGES_FOUND",
            "source_count": 2,
            "parsed_count": 1,
            "failed_count": 1,
            "unsupported_source_count": 0,
            "manual_review_required_count": 1,
            "direct_action_count": 2,
            "monitor_only_action_count": 3,
            "no_action_count": 0,
            "item_count": 10,
            "source_diagnostics": diagnostics,
        }
        (run_dir / "0180-Run_Summary.json").write_text(
            json.dumps({"schema_version": 1, "result": result}),
            encoding="utf-8",
        )
        (run_dir / "0350-Daily_Sim_Summary.json").write_text(
            json.dumps(
                {
                    "status": "CHANGES_FOUND",
                    "automation_gate_status": "ACTION_REVIEW_REQUIRED",
                    "recommendation": "Manual review required before acting; no auto-action.",
                    "hag_status": "HOLD_FOR_HUMAN_APPROVAL",
                    "manual_review_queue_count": 1,
                    "scheduler_readiness_recommendation": "HOLD",
                    "auto_action_executed": False,
                    "email_sent": False,
                    "llm_called": False,
                    "scheduler_activated": False,
                    "real_run": result,
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "0630-Daily_Quality_Gate_V2.json").write_text(
            json.dumps(
                {
                    "overall_daily_review_status": "ACTION_REVIEW_REQUIRED",
                    "source_coverage_status": "WARN",
                    "warnings": ["low_source_coverage:1/2"],
                }
            ),
            encoding="utf-8",
        )
        (run_dir / "0650-Action_Triage.json").write_text(
            json.dumps({"status": "HOLD", "counts": {"blocked_by_coverage": 1, "manual_review": 1}}),
            encoding="utf-8",
        )
        (run_dir / "0660-Codex_Prompt_Suggestions.json").write_text(
            json.dumps(
                {
                    "status": "suggested_only",
                    "suggestions_count": 1,
                    "suggestions": [
                        {
                            "suggested_step_number": "PS-001",
                            "title": "Review one prompt",
                            "target_project": "AI Release Radar",
                            "risk_class": "L1",
                            "reason": "operator review",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return run_dir

    def create_scheduler_log(self, path: Path) -> Path:
        path.write_text(
            "\n".join(
                [
                    "2026-06-12T05:15:02 command_exit_code=0",
                    "2026-06-12T05:15:02 daily_sim_exit_code=0",
                    "2026-06-12T05:15:02 script_exit_code=0",
                    "2026-06-12T05:15:02 no_auto_action=confirmed",
                    "2026-06-12T05:15:02 no_email=confirmed",
                    "2026-06-12T05:15:02 no_external_notification=confirmed",
                    "2026-06-12T05:15:02 no_llm=confirmed",
                    "2026-06-12T05:15:02 no_git_commit_push=confirmed",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        return path


if __name__ == "__main__":
    unittest.main()
