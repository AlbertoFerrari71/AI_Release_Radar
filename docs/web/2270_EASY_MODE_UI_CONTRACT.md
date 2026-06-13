# 2270 Easy Mode UI Contract

## Scope

- [F] `GET /` renders Easy Mode and uses `radar_web/templates/easy_index.html`. Fonte: `radar_web/app.py`, `radar_web/templates/easy_index.html`.
- [F] `GET /easy` renders the same Easy Mode page as `/`. Fonte: `radar_web/app.py`.
- [F] `GET /easy-mode` redirects to `/easy` preserving the query string. Fonte: `radar_web/app.py`.
- [F] `GET /expert` renders the technical dashboard. Fonte: `radar_web/app.py`, `radar_web/templates/index.html`.
- [F] `GET /dashboard` redirects to `/expert` preserving the query string. Fonte: `radar_web/app.py`.
- [F] `GET /sources` redirects to the latest run detail `#sources` section when a run exists, or to `/expert#recent-runs` without runs. Fonte: `radar_web/app.py`.
- [F] Operator Acceptance lesson learned for Easy Mode is documented in `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`. Fonte: prompt 2390-2440.

## Default Mode

- [F] The default page `/` is Easy Mode. Fonte: `radar_web/app.py`.
- [F] Expert Mode remains reachable through `/expert`. Fonte: `radar_web/app.py`.
- [F] Easy and Expert navigation links are visible in Easy Mode, Expert Mode, Action Center, and run detail pages. Fonte: `radar_web/templates/easy_index.html`, `radar_web/templates/easy_run_detail.html`, `radar_web/templates/index.html`, `radar_web/templates/actions.html`, `radar_web/templates/run_detail.html`.
- [F] The current mode is visible as an `Easy Mode` or `Expert Mode` badge. Fonte: `radar_web/templates/easy_index.html`, `radar_web/templates/easy_run_detail.html`, `radar_web/templates/index.html`, `radar_web/templates/run_detail.html`.

## Language And Preferences

- [F] Supported UI languages are `it`, `en`, `fr`, `de`, and `es`. Fonte: `radar_web/i18n.py`.
- [F] UI language resolution order is URL `?lang=`, saved preference when not `auto`, browser `Accept-Language`, then Italian fallback. Fonte: `radar_web/ui_preferences.py`, `radar_web/app.py`.
- [F] UI preferences are stored at `Bridge/config/ui_preferences.ini`, resolved from `DashboardConfig.bridge_root`. Fonte: `radar_web/config.py`, `radar_web/ui_preferences.py`.
- [F] The default preference values are `language = auto`, `start_mode = easy`, `last_selected_language = it`, and `last_selected_mode = easy`. Fonte: `radar_web/ui_preferences.py`.
- [F] `GET /api/preferences/ui` reads preferences and performs no writes. Fonte: `radar_web/app.py`.
- [F] `POST /api/preferences/ui` accepts only `language`, `start_mode`, `last_selected_language`, and `last_selected_mode`. Fonte: `radar_web/ui_preferences.py`, `radar_web/app.py`.
- [F] `POST /api/preferences/ui` rejects preference paths inside the repository. Fonte: `radar_web/config.py`, `radar_web/ui_preferences.py`.
- [F] The preference endpoint does not mutate scheduler, runs, sources, Action Center decisions, HAG output, prompt files, Git, or external services. Fonte: `radar_web/app.py`, `radar_web/ui_preferences.py`.

## Main Pages And Controls

- [F] Main pages are Easy Mode, Easy run detail, Expert Mode, Expert run detail, Action Center, Sources, Runs/Reports, and read-only JSON APIs. Fonte: `radar_web/app.py`, `radar_web/templates/*.html`.
- [F] Visible navigation includes Easy Mode, Expert Mode, Action Center, Sources, and Runs/Reports. Fonte: `radar_web/templates/easy_index.html`, `radar_web/templates/index.html`, `radar_web/templates/actions.html`, `radar_web/templates/run_detail.html`.
- [F] Safe UI controls are language dropdown, start-mode dropdown, GET links, filter tabs, detail expanders, and read-only JSON links. Fonte: `radar_web/templates/*.html`, `radar_web/static/ui_preferences.js`.
- [F] Action Center decision buttons, prompt generation, and backlog export are manual-only controls and are excluded from automated safe-click crawling. Fonte: `radar_web/templates/actions.html`, `tests/test_radar_web_app.py`.

## Smoke Click Policy

- [F] The deterministic UI navigation audit may click internal GET links and dropdowns that save only UI preferences. Fonte: `tests/test_radar_web_app.py`, `radar_web/static/ui_preferences.js`.
- [F] The deterministic UI navigation audit must not click Action Center decisions, prompt generation, backlog export, scheduler triggers, run triggers, HAG approvals, or external side-effect links. Fonte: `tests/test_radar_web_app.py`, `radar_web/templates/actions.html`.
- [INT] If a new button has unclear side effects, it must be reported as manual review required before it is included in automated clicking. Fonte: `tests/test_radar_web_app.py`.

## Status Criteria

- [F] GREEN requires `/`, `/easy`, `/easy-mode`, `/expert`, `/actions`, `/sources`, Easy APIs, preference APIs, tests, diff checks, real operator port validation, UI navigation evidence, and local smoke to pass with preferences outside the repo. Fonte: prompt `2270-2380`, prompt 2390-2440, `tests/test_easy_mode.py`, `tests/test_radar_web_app.py`.
- [F] YELLOW applies when deterministic tests pass but visual Browser/HTML evidence is unavailable, real-port validation is incomplete, warnings are governed, or some ambiguous controls remain manual review only. Fonte: prompt `2270-2380`, prompt 2390-2440, `tests/test_radar_web_app.py`.
- [F] RED applies when Easy Mode is not reachable from `/`, `/easy`, or `/easy-mode`, `/expert` fails, tests fail, preferences write inside the repo, primary routes fail, or operational state is mutated by preference/UI audit. Fonte: prompt `2270-2380`, prompt 2390-2440, `tests/test_radar_web_app.py`.
