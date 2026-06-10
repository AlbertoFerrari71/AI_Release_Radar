# 0300) Actionable Radar V1.1 Decisions

## Strategia Step

- [F] Gli step 0240-0300 sono stati eseguiti come batch PR con commit separati. Fonte: prompt 0240-0300 fornito da Alberto.
- [INT] Una PR batch e' stata scelta perche' source diagnostics, impact quality, action quality, scorecard, comparison e closure descrivono un unico incremento V1.1.
- [F] Nessuno step autorizza auto-merge. Fonte: prompt 0240-0300 fornito da Alberto.

## Source Coverage

- [F] La matrice fonti V1.1 e' `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.
- [F] La fonte P0 automatizzata resta `github_api_openai_codex_releases`. Fonte: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.
- [F] Non viene introdotto parsing HTML fragile. Fonte: `radar/live_snapshot.py`.

## Fallback Diagnostics

- [F] `source_diagnostics` include `diagnostic_status`, `manual_review_required`, `error_code` e `recommended_follow_up`. Fonte: `radar/live_snapshot.py`.
- [F] 401/403 sono classificati come `manual_review_required` per la diagnostica. Fonte: `radar/live_snapshot.py`, `tests/test_live_snapshot.py`.
- [INT] Questa scelta evita che una fonte fragile generi falso allarme parser o rumore operativo.

## Project Impact E Action Quality

- [F] `ProjectImpact` distingue `action_type` da `impact_level`. Fonte: `radar/project_impact.py`.
- [F] I tipi azione sono `direct_action`, `monitor_only` e `no_action`. Fonte: `radar/project_impact.py`.
- [F] Le azioni includono titolo, motivo di rilevanza e prossimo passo. Fonte: `radar/project_impact.py`, `tests/test_project_impact.py`.
- [INT] I progetti restano visibili, ma un segnale Codex/API generico non apre automaticamente lavoro tecnico su tutti.

## Scorecard E Comparison

- [F] La scorecard e' implementata in `radar/report_scorecard.py`.
- [F] Il confronto offline e' implementato in `radar/run_comparison.py`.
- [F] `real-run` serializza scorecard, conteggi action type e unsupported source count nel run summary. Fonte: `radar/real_run.py`.
- [INT] Questi campi consentono confronto V1/V1.1 senza parsing Markdown.

## Rischio

- [F] La fase resta L1/L2 prudenziale perche' modifica logica offline e comportamento `real-run`, senza scheduler. Fonte: prompt 0240-0300 fornito da Alberto.
- [F] Nessuna nuova dipendenza esterna e' stata aggiunta. Fonte: `pyproject.toml`.
- [F] Nessun file high-risk `AGENTS.md`, `.githooks/*`, `.github/*` o scheduler e' stato modificato. Fonte: diff dello step 0240-0300.
- [F] Nessun output runtime/live viene versionato nel repository. Fonte: `radar/real_run.py`, `radar/live_snapshot.py`.

## Merge Recommendation

- [PROP] MERGE_RECOMMENDATION: YES dopo review manuale della draft PR e gate PASS.
- [F] NO AUTO-MERGE: confirmed. Fonte: prompt 0240-0300 fornito da Alberto.

## Prossimo Step

- [PROP] 0310) Manual V1.1 Review On Real Smoke Output, con output fuori repository e confronto V1/V1.1 prima di decidere parser coverage o scheduler readiness.
