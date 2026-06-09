# AI Release Radar Report — 0080-offline-report-fixture

## 1. Executive summary

- [F] Report status: CRITICAL.
- [F] Source `offline-0080-report-fixture` was provided by `openai_fixture`.
- [F] Diff contains 1 new, 1 changed, 1 removed and 2 unchanged item(s).
- [INT] Top relevance item is `0080_security_sandbox` with score 105.
- [PROP] Review 15 deterministic project action(s) before the next radar run.

## 2. Source and run metadata

- [F] run_id: `0080-offline-report-fixture`.
- [F] generated_at: `2026-06-09T19:30:00Z`.
- [F] source_id: `offline-0080-report-fixture`.
- [F] provider: `openai_fixture`.
- [F] note: Fixture covers one new, one changed, one removed and two unchanged items.
- [F] note: Report renderer must not fetch live data or call an LLM.

## 3. Diff summary

- [F] New items: 1.
- [F] Changed items: 1.
- [F] Removed items: 1.
- [F] Unchanged items: 2.

## 4. New items

- [F] `0080_security_sandbox` - Security sandbox permission issue
  - [F] category: security.
  - [F] severity: critical.
  - [F] score: 105.
  - [F] URL: https://example.invalid/0080/security-sandbox
  - [F] evidence: Offline fixture: critical security sandbox permission issue could expose credential handling.

## 5. Changed items

- [F] `0080_api_deprecation` - API deprecation notice
  - [F] category: deprecation.
  - [F] severity: high.
  - [F] score: 85.
  - [F] URL: https://example.invalid/0080/api-deprecation
  - [F] evidence: Offline fixture: Responses API endpoint deprecation and retirement path for platform clients.

## 6. Removed items

- [F] `0080_codex_cli_removed` - Removed Codex CLI terminal command
  - [F] category: codex_cli.
  - [F] severity: medium.
  - [F] score: 68.
  - [F] URL: https://example.invalid/0080/codex-cli-removed
  - [F] evidence: Offline fixture: removed Codex CLI terminal command previously used in local workflows.

## 7. Top relevance scores

1. [F] `0080_security_sandbox`: score 105; category security; severity critical.
   - [INT] score reasons: severity critical: 50; keywords 5: 20; confidence 0.95: 10; novelty new: 15; category security: 10; total: 105.
2. [F] `0080_api_deprecation`: score 85; category deprecation; severity high.
   - [INT] score reasons: severity high: 40; keywords 4: 16; confidence 0.90: 9; novelty changed: 10; category deprecation: 10; total: 85.
3. [F] `0080_codex_cli_removed`: score 68; category codex_cli; severity medium.
   - [INT] score reasons: severity medium: 25; keywords 3: 12; confidence 0.88: 9; novelty removed: 12; category codex_cli: 10; total: 68.
4. [F] `0080_image_vision_unchanged`: score 56; category image_vision; severity medium.
   - [INT] score reasons: severity medium: 25; keywords 4: 16; confidence 0.84: 8; novelty unchanged: 0; category image_vision: 7; total: 56.
5. [F] `0080_codex_skills_unchanged`: score 26; category codex_skills; severity info.
   - [INT] score reasons: severity info: 5; keywords 2: 8; confidence 0.78: 8; novelty unchanged: 0; category codex_skills: 5; total: 26.

## 8. Project impacts

- [F] AI Software Factory (`ai_software_factory`)
  - [F] item_id: `0080_api_deprecation`.
  - [F] impact_level: critical.
  - [INT] reasons: category deprecation relevant to project; deprecation relevant to API/platform project; deprecation score 85 >= 80; score 85; severity high.
  - [PROP] suggested_actions: review AGENTS.md; update workflow; update verification gate; create Codex step.
- [F] Mansionario_Vivo (`mansionario_vivo`)
  - [F] item_id: `0080_api_deprecation`.
  - [F] impact_level: critical.
  - [INT] reasons: category deprecation relevant to project; deprecation relevant to API/platform project; matched project keywords: api, deprecat; deprecation score 85 >= 80; score 85; severity high.
  - [PROP] suggested_actions: review FastAPI workflow; run regression tests; update deployment notes.
- [F] AI Software Factory (`ai_software_factory`)
  - [F] item_id: `0080_security_sandbox`.
  - [F] impact_level: critical.
  - [INT] reasons: category security relevant to project; matched project keywords: sandbox, security; critical severity on relevant project; score 105; severity critical.
  - [PROP] suggested_actions: review AGENTS.md; update workflow; update verification gate; create Codex step.
- [F] Family Photo Organizer (`family_photo_organizer`)
  - [F] item_id: `0080_security_sandbox`.
  - [F] impact_level: critical.
  - [INT] reasons: category security relevant to project; matched project keywords: security; critical severity on relevant project; score 105; severity critical.
  - [PROP] suggested_actions: review image workflow; run read-only safety test; update review checklist.
- [F] AI Software Factory (`ai_software_factory`)
  - [F] item_id: `0080_codex_cli_removed`.
  - [F] impact_level: medium.
  - [INT] reasons: category codex_cli relevant to project; matched project keywords: codex cli; medium severity on relevant project; score 68; severity medium.
  - [PROP] suggested_actions: review CLI workflow; update runner documentation.
- [F] Family Photo Organizer (`family_photo_organizer`)
  - [F] item_id: `0080_image_vision_unchanged`.
  - [F] impact_level: medium.
  - [INT] reasons: category image_vision relevant to project; matched project keywords: image, local file path, vision; medium severity on relevant project; score 56; severity medium.
  - [PROP] suggested_actions: review image workflow; run read-only safety test.
- [F] Codex_Skills (`codex_skills`)
  - [F] item_id: `0080_codex_skills_unchanged`.
  - [F] impact_level: low.
  - [INT] reasons: category codex_skills relevant to project; matched project keywords: skill, skills; relevant category with low score; score 26; severity info.
  - [PROP] suggested_actions: update skill; review skill trigger; update catalog.

## 9. Recommended actions

1. [PROP] AI Software Factory: review AGENTS.md for `0080_api_deprecation` (critical).
2. [PROP] AI Software Factory: update workflow for `0080_api_deprecation` (critical).
3. [PROP] AI Software Factory: update verification gate for `0080_api_deprecation` (critical).
4. [PROP] AI Software Factory: create Codex step for `0080_api_deprecation` (critical).
5. [PROP] Mansionario_Vivo: review FastAPI workflow for `0080_api_deprecation` (critical).
6. [PROP] Mansionario_Vivo: run regression tests for `0080_api_deprecation` (critical).
7. [PROP] Mansionario_Vivo: update deployment notes for `0080_api_deprecation` (critical).
8. [PROP] Family Photo Organizer: review image workflow for `0080_security_sandbox` (critical).
9. [PROP] Family Photo Organizer: run read-only safety test for `0080_security_sandbox` (critical).
10. [PROP] Family Photo Organizer: update review checklist for `0080_security_sandbox` (critical).
11. [PROP] AI Software Factory: review CLI workflow for `0080_codex_cli_removed` (medium).
12. [PROP] AI Software Factory: update runner documentation for `0080_codex_cli_removed` (medium).
13. [PROP] Codex_Skills: update skill for `0080_codex_skills_unchanged` (low).
14. [PROP] Codex_Skills: review skill trigger for `0080_codex_skills_unchanged` (low).
15. [PROP] Codex_Skills: update catalog for `0080_codex_skills_unchanged` (low).

## 10. Risks and caveats

- [F] offline fixture only.
- [F] no live fetch.
- [F] no LLM.
- [INT] report based on deterministic rules.

## 11. Next step recommendation

- [PROP] 0090) CLI Dry Run.
