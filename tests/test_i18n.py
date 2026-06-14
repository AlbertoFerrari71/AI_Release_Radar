import json
import re
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from radar_web import i18n
from radar_web.app import create_app
from radar_web.config import DashboardConfig


SCHEDULER_NO_DATA = {
    "status": "NO_DATA",
    "task_name": "AIReleaseRadar_DailyDryReport",
    "read_only": True,
    "interpretation": "NO_DATA",
    "warnings": [],
}


class I18nTests(unittest.TestCase):
    def create_bridge(self, root: Path) -> Path:
        bridge = root / "bridge"
        run_dir = bridge / "runs" / "0320_0400_daily_sim_20260610_090000"
        run_dir.mkdir(parents=True)
        (run_dir / "0180-Report_Compact.md").write_text("# Compact\n", encoding="utf-8")
        (run_dir / "0350-Daily_Sim_Summary.json").write_text(
            json.dumps(
                {
                    "status": "PASS",
                    "automation_gate_status": "PASS",
                    "daily_quality_gate_v2": {
                        "overall_daily_review_status": "PASS",
                        "source_coverage_status": "PASS",
                    },
                    "real_run": {
                        "status": "PASS",
                        "source_count": 2,
                        "parsed_count": 1,
                        "direct_action_count": 1,
                        "monitor_only_action_count": 0,
                    },
                    "action_triage": {
                        "status": "ACTION_REVIEW_REQUIRED",
                        "counts": {"codex_prompt_candidate": 1},
                        "entries": [
                            {
                                "triage_class": "codex_prompt_candidate",
                                "title": "Review multilingual dashboard",
                                "target_project": "AI Release Radar",
                                "project_key": "ai_release_radar",
                                "reason": "dashboard needs localization",
                                "risk_class": "L1/L2",
                                "item_category": "codex_cli",
                                "score": 82,
                                "item_id": "multilingual-dashboard",
                            }
                        ],
                    },
                    "prompt_suggestions": {
                        "status": "suggested_only",
                        "suggestions_count": 1,
                        "suggestions": [
                            {
                                "suggested_step_number": "PS-001",
                                "title": "Review translations",
                                "status": "suggested_only",
                                "target_project": "AI Release Radar",
                                "risk_class": "L1/L2",
                            }
                        ],
                    },
                    "prompt_suggestions_count": 1,
                    "manual_review_queue_count": 0,
                    "hag_status": "NO_ACTION_REQUIRED",
                }
            ),
            encoding="utf-8",
        )
        return bridge

    def test_all_supported_locales_load_with_same_keys(self):
        en_keys = i18n.catalog_keys("en")
        self.assertGreater(len(en_keys), 20)
        for locale in i18n.SUPPORTED_LOCALES:
            with self.subTest(locale=locale):
                self.assertEqual(i18n.missing_keys(locale), set())
                self.assertEqual(i18n.catalog_keys(locale), en_keys)

    def test_catalogs_have_no_duplicate_empty_or_placeholder_values(self):
        catalog_root = Path.cwd() / "radar_web" / "locales"
        placeholder_re = re.compile(r"\{[^{}]+\}")
        forbidden_re = re.compile(r"\b(TODO|TBD|FIXME|PLACEHOLDER)\b", re.IGNORECASE)

        en_data = json.loads((catalog_root / "en.json").read_text(encoding="utf-8"))
        for locale in i18n.SUPPORTED_LOCALES:
            with self.subTest(locale=locale):
                duplicates = []

                def object_pairs_hook(items):
                    seen = set()
                    for key, _value in items:
                        if key in seen:
                            duplicates.append(key)
                        seen.add(key)
                    return dict(items)

                data = json.loads(
                    (catalog_root / f"{locale}.json").read_text(encoding="utf-8"),
                    object_pairs_hook=object_pairs_hook,
                )
                empty_keys = [key for key, value in data.items() if not str(value).strip()]
                placeholder_keys = [
                    key for key, value in data.items() if forbidden_re.search(str(value))
                ]
                placeholder_mismatches = [
                    key
                    for key in sorted(set(en_data).intersection(data))
                    if sorted(placeholder_re.findall(en_data[key]))
                    != sorted(placeholder_re.findall(data[key]))
                ]

                self.assertEqual(duplicates, [])
                self.assertEqual(empty_keys, [])
                self.assertEqual(placeholder_keys, [])
                self.assertEqual(placeholder_mismatches, [])

    def test_locale_and_key_fallbacks(self):
        self.assertEqual(i18n.normalize_locale("it-IT"), "it")
        self.assertEqual(i18n.normalize_locale("pt-BR"), "en")
        self.assertEqual(i18n.translate("nav.dashboard", "pt-BR"), "Dashboard")
        self.assertEqual(i18n.translate("missing.everywhere", "it"), "[missing:missing.everywhere]")

        original_cache = dict(i18n._CATALOG_CACHE)
        try:
            i18n._CATALOG_CACHE["it"] = {}
            self.assertEqual(i18n.translate("nav.dashboard", "it"), "Dashboard")
        finally:
            i18n._CATALOG_CACHE.clear()
            i18n._CATALOG_CACHE.update(original_cache)

    def test_placeholder_datetime_status_and_bool_formatting(self):
        self.assertEqual(
            i18n.translate("detail.title", "en", run_id="run-1"),
            "AI Release Radar - run-1",
        )
        value = "2026-06-11T07:15:00.0000000+02:00"
        self.assertEqual(i18n.format_datetime_for_locale(value, "en"), "2026-06-11 07:15")
        self.assertEqual(i18n.format_datetime_for_locale(value, "it"), "11/06/2026 07:15")
        self.assertEqual(i18n.format_datetime_for_locale(value, "fr"), "11/06/2026 07:15")
        self.assertEqual(i18n.format_datetime_for_locale(value, "de"), "11.06.2026 07:15")
        self.assertEqual(i18n.format_datetime_for_locale(value, "es"), "11/06/2026 07:15")
        self.assertEqual(
            i18n.format_status_for_locale("PASS_WITH_WARNINGS", "it"),
            "Superato con avvisi",
        )
        self.assertEqual(i18n.format_bool_for_locale(True, "it"), "Sì")
        self.assertEqual(i18n.format_bool_for_locale(False, "fr"), "Non")

    def test_strict_localized_catalogs_avoid_known_english_ui_terms(self):
        catalog_root = Path.cwd() / "radar_web" / "locales"
        forbidden_re = re.compile(
            r"\b("
            r"API|Backlog|Dashboard|Scheduler|Gate|Prompt|Review|Daily-Sim|daily-sim|"
            r"run id|NO_DATA|RUNNING|Pass|Hold|Monitor|Bridge|Action Inbox|Action Center|"
            r"backlog|auto-action|auto-azione|Auto-Aktion|auto-acción"
            r")\b"
        )

        for locale in ("it", "fr", "de", "es"):
            with self.subTest(locale=locale):
                data = json.loads((catalog_root / f"{locale}.json").read_text(encoding="utf-8"))
                offenders = {
                    key: value
                    for key, value in data.items()
                    if forbidden_re.search(str(value))
                }
                self.assertEqual(offenders, {})

    def test_main_templates_render_for_all_locales(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            bridge = self.create_bridge(Path(tmpdir))
            run_id = next((bridge / "runs").iterdir()).name
            config = DashboardConfig(repo_root=Path.cwd(), bridge_root=bridge)
            with patch("radar_web.app.read_scheduler_status", return_value=SCHEDULER_NO_DATA):
                client = TestClient(create_app(config))
                for locale in i18n.SUPPORTED_LOCALES:
                    with self.subTest(locale=locale):
                        self.assertEqual(client.get(f"/?lang={locale}").status_code, 200)
                        self.assertEqual(client.get(f"/actions?lang={locale}").status_code, 200)
                        self.assertEqual(client.get(f"/easy/latest/brief?lang={locale}").status_code, 200)
                        self.assertEqual(
                            client.get(f"/easy/latest/model-packet?lang={locale}").status_code,
                            200,
                        )
                        self.assertEqual(client.get(f"/runs/{run_id}?lang={locale}").status_code, 200)

    def test_no_forbidden_last_or_latest_files(self):
        forbidden = [
            path
            for path in Path.cwd().rglob("*")
            if path.is_file() and (path.name.startswith("LAST-") or path.name.startswith("latest-"))
        ]
        self.assertEqual(forbidden, [])


if __name__ == "__main__":
    unittest.main()
