# 0310) Manual V1.1 Real Smoke Review Decisions

## Decisione Presa

- [F] Lo step 0310 ha analizzato il run Bridge `manual_test_0240_0300_20260610_160833`. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] Il run analizzato ha `source_count=11`, `parsed_count=1`, `unsupported_source_count=10`, `direct_action_count=10`, `monitor_only_action_count=50` e `scorecard_status=PASS`. Fonte: `0180-Run_Summary.json` del run Bridge analizzato.
- [PROP] Prossimo blocco raccomandato: `0320) Source Coverage V1.2 - aumentare fonti parsate / migliorare registry`.

## Perche' Non Scheduler Subito

- [F] Lo step 0310 non autorizza scheduler e richiede `NO AUTO-MERGE`. Fonte: prompt 0310 fornito da Alberto.
- [F] La V1.1 mantiene lo scheduler fuori scope. Fonte: `docs/architecture/0300_ACTIONABLE_RADAR_V1_1_CLOSURE_PACK.md`.
- [F] Il run reale V1.1 resta a `parsed_count=1` su `source_count=11`. Fonte: `0180-Run_Summary.json` del run Bridge analizzato.
- [INT] Uno scheduler sarebbe prematuro perche' automatizzerebbe un report leggibile ma ancora poco coperto lato fonti. Base: `parsed_count=1`, `unsupported_source_count=10`, scorecard PASS.

## Trade-Off Source Coverage, Action Quality, Scheduler

- [INT] Source coverage e' il blocco piu' urgente perche' aumenta la base informativa prima di ottimizzare ulteriormente priorita' e azioni. Base: unica fonte parsata `github_api_openai_codex_releases` nel run analizzato.
- [INT] Action quality resta importante ma dipende dalla qualita' del segnale in ingresso: se arrivano solo release GitHub Codex API, molte azioni continueranno a essere monitor-only o generiche. Base: `monitor_only_action_count=50` nel run analizzato.
- [INT] Scheduler readiness ha senso dopo una warning policy esplicita su coverage, unsupported sources e volume monitor-only. Base: scorecard PASS con `parsed_count=1`.
- [PROP] Trattare lo scheduler come blocco dedicato successivo, non come prosecuzione automatica della V1.1.

## Scorecard Critique

- [F] La documentazione 0280 definisce la scorecard come gate di qualita' report. Fonte: `docs/architecture/0280_REPORT_REVIEW_SCORECARD.md`.
- [F] Nel run analizzato `has_parsed_source_count` passa con `parsed_count=1`. Fonte: sezione `Report Review Scorecard` in `0180-Report_Full.md`.
- [INT] La scorecard PASS e' corretta come `report_readability_scorecard`, ma non deve essere interpretata come `source_coverage_scorecard`.
- [PROP] Nel prossimo hardening distinguere `report_readability_scorecard`, `source_coverage_warning` e `action_quality_warning`.

## Rischi Residui

- [F] Dieci fonti su undici non producono item parsati nel run analizzato. Fonte: `unsupported_source_count=10` in `0180-Run_Summary.json`.
- [F] Il run analizzato produce 50 monitor-only actions. Fonte: `monitor_only_action_count=50` in `0180-Run_Summary.json`.
- [INT] Le monitor-only actions riducono il rischio di azioni forti errate, ma restano rumorose se non aggregate o filtrate. Base: `monitor_only_action_count=50`.
- [INT] La dipendenza da una sola fonte parsata puo' generare falsa completezza percepita. Base: `scorecard_status=PASS` e `parsed_count=1`.

## Prossimo Step Consigliato

- [PROP] `0320) Source Coverage V1.2 - aumentare fonti parsate / migliorare registry`.
- [PROP] Scope minimo consigliato: mantenere no scheduler, no LLM e no nuove dipendenze; lavorare su registry/source diagnostics, seconda fonte strutturata se disponibile, fixture offline e warning coverage.
- [PROP] MERGE_RECOMMENDATION: YES dopo review manuale della draft PR e gate PASS.
- [F] NO AUTO-MERGE: confirmed. Fonte: prompt 0310 fornito da Alberto.
