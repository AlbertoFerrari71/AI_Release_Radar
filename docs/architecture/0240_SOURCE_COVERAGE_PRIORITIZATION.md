# 0240) Source Coverage Prioritization

## Scope

- [F] This document covers the 11 enabled sources listed in `config/sources/openai_sources.json`.
- [F] The 0200-0230 manual V1 baseline reported 11 checked sources, 1 parsed source, 10 items, and 60 project impacts in Alberto's 0240-0300 prompt.
- [F] The currently useful structured source is `github_api_openai_codex_releases`, according to Alberto's 0240-0300 prompt.
- [INT] V1.1 should improve source diagnostics and prioritization before adding any broad HTML parsing.

## Priority Legend

| Priority | Meaning | V1.1 posture |
|---|---|---|
| P0 | Already useful, structured, high priority | Keep parsed and use as the primary automated signal |
| P1 | Useful, but parser must be conservative | Improve diagnostics first; parse only if a stable format is available |
| P2 | Useful, but fragile or better for manual review | Mark clearly as manual review or fetched-but-unsupported |
| P3 | Low priority or high risk for current V1.1 | Keep monitored, but do not spend parser effort now |

## Source Matrix

| source_id | provider | source_type | current_fetch_status | current_parser_status | business/technical value | parsing risk | stability risk | recommended strategy | priority | reason |
|---|---|---|---|---|---|---|---|---|---|---|
| `github_api_openai_codex_releases` | github | github_api | [F] expected HTTP 200 from registry | [F] parsed by `radar.live_snapshot` for `github_api` | [F] Codex release signal used by V1 manual run | Low | Medium | Keep as primary structured source; keep max-bytes source override | P0 | Structured JSON is the only proven automated source in V1 |
| `github_openai_codex_releases` | github | github_releases | [F] expected HTTP 200 from registry | [F] no live parser in `radar.live_snapshot` | [INT] Useful human fallback for GitHub release context | High | Medium | Keep fetched-but-unsupported; link it in diagnostics as HTML fallback to the API source | P2 | HTML page duplicates API content and should not drive parsing |
| `openai_codex_changelog` | openai | official_changelog | [F] expected HTTP 200 from registry | [F] parsed only when fetched content is markdown or text | [INT] High value if a stable text/markdown form is available | Medium | High | Keep conservative text parser; otherwise classify fetched HTML as fetched-but-unsupported | P1 | Codex-specific source is valuable, but HTML parsing is out of scope |
| `openai_api_changelog` | openai | official_changelog | [F] expected HTTP 200 from registry | [F] no live parser in `radar.live_snapshot` | [INT] High value for API/platform and deprecation tracking | High | High | Keep unsupported but diagnosed; consider structured/feed fallback only if officially available later | P1 | API changes matter, but current page format is not proven stable |
| `openai_model_release_notes` | openai | official_release_notes | [F] expected HTTP 200 from registry; [F] manual review required in registry | [F] no live parser in `radar.live_snapshot` | [INT] Useful for model capability awareness | High | High | Keep manual_review_required and do not generate automated actions from unsupported fetches | P2 | Model notes are useful but broad for project actions |
| `openai_release_notes_hub` | openai | official_release_notes | [F] expected HTTP 200 from registry; [F] manual review required in registry | [F] no live parser in `radar.live_snapshot` | [INT] Useful navigation source, not a direct item source | High | High | Keep manual_review_required; use only as manual fallback hub | P3 | Hub pages are noisy and indirect |
| `openai_chatgpt_release_notes` | openai | official_release_notes | [F] expected HTTP 200 from registry; [F] manual review required in registry | [F] no live parser in `radar.live_snapshot` | [INT] Useful only when ChatGPT behavior affects Codex workflows | High | High | Keep manual_review_required; do not promote to automated parser in V1.1 | P2 | Valuable but too broad for deterministic project actions |
| `openai_api_deprecations` | openai | official_docs | [F] expected HTTP 200 from registry | [F] no live parser in `radar.live_snapshot` | [INT] High value for API/platform risk | High | Medium | Keep unsupported but diagnosed; revisit only with stable structured data | P1 | Deprecations can be high impact, but parser risk is high |
| `openai_codex_cli_reference` | openai | official_docs | [F] expected HTTP 200 from registry | [F] no live parser in `radar.live_snapshot` | [INT] High value for CLI compatibility checks | High | Medium | Keep fetched-but-unsupported; mark as manual review when fetch is denied or unsupported | P1 | CLI docs are direct, but reference pages need change-aware parsing |
| `openai_codex_agents_md` | openai | official_docs | [F] expected HTTP 200 from registry | [F] no live parser in `radar.live_snapshot` | [INT] High value for ASF and Codex_Skills governance | High | Medium | Keep fetched-but-unsupported; mark as manual review when fetch is denied or unsupported | P1 | AGENTS.md changes can affect repo workflow policy |
| `openai_codex_skills` | openai | official_docs | [F] expected HTTP 200 from registry | [F] no live parser in `radar.live_snapshot` | [INT] High value for Codex_Skills maintenance | High | Medium | Keep fetched-but-unsupported; mark as manual review when fetch is denied or unsupported | P1 | Skills docs are relevant, but free-form docs need conservative handling |

## V1.1 Decision

- [PROP] Keep `github_api_openai_codex_releases` as the only P0 parsed source.
- [PROP] Treat `github_openai_codex_releases` as a human-readable fallback to the P0 API source, not as a separate parser target.
- [PROP] Keep `openai_codex_changelog` as P1 only through the existing conservative text/markdown parser; do not parse arbitrary HTML.
- [PROP] Keep API changelog, API deprecations, Codex CLI reference, Codex AGENTS.md, and Codex Skills as P1/P2 fetched-but-unsupported or manual-review diagnostics until a stable structured format exists.
- [PROP] Keep release-note hub and broad ChatGPT/model notes as manual-review sources so they do not create false automated actions.
- [PROP] In V1.1 reports, show unsupported fetched sources separately from fetch failures and manual-review sources.

## Out Of Scope

- [F] No scheduler is introduced by this prioritization step.
- [F] No new dependency is required by this prioritization step.
- [F] No LLM call is required by this prioritization step.
- [INT] Parser work should be rejected when it depends on brittle HTML layout assumptions.
