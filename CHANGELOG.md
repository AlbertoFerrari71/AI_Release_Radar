# Changelog

## 0410-0500) Source Coverage V1.2 and Scheduler Readiness Final Gate

- [F] Confermata la scelta di non aggiungere una seconda fonte live parsata senza formato stabile, evitando parser HTML fragile. Fonte: `docs/architecture/0410_SOURCE_COVERAGE_V1_2_IMPLEMENTATION.md`.
- [F] Rafforzato il source registry con metadata quality/readiness e validazione loader. Fonte: `config/sources/openai_sources.json`, `radar/source_registry.py`, `tests/test_source_registry.py`.
- [F] Esteso l'automation gate con `scheduler_readiness_recommendation` e manual review queue. Fonte: `radar/automation_gate.py`, `radar/manual_review_queue.py`, `tests/test_automation_gate.py`.
- [F] Esteso `daily-sim` con manual review queue, scheduler readiness summary e regressioni offline. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] Aggiunti checklist scheduler readiness, scheduler dry-run design, operator runbook, final review e closure pack V1.2. Fonte: `docs/architecture/0460_SCHEDULER_READINESS_CHECKLIST.md`, `docs/architecture/0470_SCHEDULER_DRY_RUN_DESIGN.md`, `docs/runbooks/0480_OPERATOR_RUNBOOK.md`, `docs/reviews/0490_FINAL_SCHEDULER_READINESS_REVIEW.md`, `docs/architecture/0500_SOURCE_COVERAGE_AND_SCHEDULER_READINESS_CLOSURE_PACK.md`.
- [F] Nessuno scheduler reale, task Windows, LLM automatico, nuova dipendenza, `LAST-*` o `latest-*` introdotto. Fonte: `AGENTS.md`, `radar/cli.py`, `pyproject.toml`.
- [PROP] Prossimo blocco consigliato: `0510) Scheduler Dry-Report L3 Approval` solo con prompt L3 esplicito.

## 0320-0400) Automation Readiness and Daily Run Simulation

- [F] Aggiunta pianificazione Source Coverage V1.2 e decisione documentata sulla seconda fonte strutturata senza parser HTML fragile. Fonte: `docs/architecture/0320_SOURCE_COVERAGE_V1_2_PLANNING.md`, `docs/architecture/0330_SECOND_STRUCTURED_SOURCE_CANDIDATE.md`.
- [F] Aggiunto automation run contract e Bridge retrieval contract. Fonte: `docs/architecture/0340_AUTOMATION_RUN_CONTRACT.md`, `docs/architecture/0370_BRIDGE_RETRIEVAL_CONTRACT.md`.
- [F] Aggiunto comando `daily-sim` per simulazione controllata senza scheduler. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] Aggiunto automation gate deterministico con failure injection offline. Fonte: `radar/automation_gate.py`, `tests/test_automation_gate.py`.
- [F] Aggiunta readiness review 0390 e closure pack 0400. Fonte: `docs/reviews/0390_DAILY_RUN_READINESS_REVIEW.md`, `docs/architecture/0400_AUTOMATION_READINESS_CLOSURE_PACK.md`, `docs/decisions/0400_DECISIONS.md`.
- [F] Nessuno scheduler, task Windows, LLM automatico, nuova dipendenza, `LAST-*` o `latest-*` introdotto. Fonte: `radar/cli.py`, `pyproject.toml`, `AGENTS.md`.
- [PROP] Prossimo blocco consigliato: `0410) Source Coverage V1.2 Implementation`. Fonte: `docs/decisions/0400_DECISIONS.md`.

## 0310) Manual V1.1 Real Smoke Review

- [F] Aggiunta review del run reale V1.1 prodotto fuori repository. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] Documentata critica alla scorecard: PASS valido come qualita' report, non come readiness complessiva con `parsed_count=1` su 11 fonti. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`, `docs/decisions/0310_DECISIONS.md`.
- [F] Confermata la raccomandazione di non procedere subito allo scheduler. Fonte: `docs/decisions/0310_DECISIONS.md`.
- [PROP] Prossimo blocco consigliato: `0320) Source Coverage V1.2 - aumentare fonti parsate / migliorare registry`. Fonte: `docs/decisions/0310_DECISIONS.md`.

## 0240-0300) Actionable Radar V1.1

- [F] Aggiunta matrice di priorita' fonti e decisione V1.1 su fonti P0/P1/P2/P3. Fonte: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.
- [F] Rafforzate source diagnostics con `diagnostic_status`, `manual_review_required`, `error_code` e follow-up deterministico. Fonte: `radar/live_snapshot.py`, `tests/test_live_snapshot.py`.
- [F] Migliorata qualita' project impact con `action_type` separato da `impact_level`. Fonte: `radar/project_impact.py`, `tests/test_project_impact.py`.
- [F] Migliorate le azioni consigliate con titolo, motivo di rilevanza e prossimo passo. Fonte: `radar/project_impact.py`.
- [F] Aggiunta report scorecard offline e integrazione nel real-run. Fonte: `radar/report_scorecard.py`, `radar/real_run.py`, `tests/test_report_scorecard.py`.
- [F] Aggiunto confronto offline V1/V1.1 per run summary. Fonte: `radar/run_comparison.py`, `tests/test_run_comparison.py`.
- [F] Aggiunti closure pack e decisioni V1.1. Fonte: `docs/architecture/0300_ACTIONABLE_RADAR_V1_1_CLOSURE_PACK.md`, `docs/decisions/0300_DECISIONS.md`.
- [F] Nessuno scheduler, nessuna nuova dipendenza, nessun LLM automatico e nessun `LAST-*` o `latest-*` introdotto. Fonte: `radar/real_run.py`, `pyproject.toml`, `tests/`.

## 0200-0230) V1 Manual Run Stabilization

- [F] Migliorata leggibilita' dei report reali full e compact con titolo/versione, source label, provider, URL, data, categoria, severita', score e motivi di impatto. Fonte: `radar/real_run.py`, `tests/test_real_run.py`.
- [F] Aggiunto profilo CLI `real-run --profile manual` mantenendo `--output-dir` esplicito. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] Rafforzato `runs_index.jsonl` con conteggi source/parser/item/fail/skip, timestamp e validazione offline. Fonte: `radar/models.py`, `radar/run_index.py`, `tests/test_run_index.py`.
- [F] `real-run` e `live-snapshot` valorizzano i nuovi campi di indice. Fonte: `radar/real_run.py`, `radar/live_snapshot.py`.
- [F] Aggiunto runbook V1 manuale, closure pack e decisioni 0230. Fonte: `docs/runbooks/0230_V1_MANUAL_RUN_RUNBOOK.md`, `docs/architecture/0230_V1_MANUAL_RUN_CLOSURE_PACK.md`, `docs/decisions/0230_DECISIONS.md`.
- [F] Nessuno scheduler, nessuna nuova dipendenza, nessun `LAST-*` o `latest-*` introdotto. Fonte: `radar/cli.py`, `pyproject.toml`, `tests/test_cli.py`.
- [F] Auto-merge non consentito per fase L1/L2 prudenziale. Fonte: `AGENTS.md`, prompt 0200-0230 fornito da Alberto.

## 0190) First Real Output Review and Parser Coverage Hardening

- [F] Aggiunto stato `NO_PARSED_ITEMS` per real-run con fonti presenti ma zero fonti parsate. Fonte: `radar/real_run.py`.
- [F] Aggiunta diagnostica source/parser nei risultati live snapshot e real-run. Fonte: `radar/live_snapshot.py`, `radar/real_run.py`.
- [F] Aggiunto `max_bytes` opzionale per fonte nel registry e nel fetcher. Fonte: `radar/source_registry.py`, `radar/source_fetcher.py`.
- [F] Collegata in modo piu' robusto la fonte `github_api_openai_codex_releases` al parser GitHub Releases API tramite limite per-fonte. Fonte: `config/sources/openai_sources.json`, `radar/live_snapshot.py`.
- [F] Aggiunti test offline per routing GitHub API, zero parsed items, diagnostica e limite per-fonte. Fonte: `tests/test_live_snapshot.py`, `tests/test_real_run.py`, `tests/test_source_fetcher.py`, `tests/test_source_registry.py`.
- [F] Aggiunta documentazione tecnica e decisione 0190. Fonte: `docs/architecture/0190_FIRST_REAL_OUTPUT_PARSER_COVERAGE_HARDENING.md`, `docs/decisions/0190_DECISIONS.md`.
- [F] Auto-merge non consentito per step L2. Fonte: `AGENTS.md`, prompt 0190.

## 0130) Source Fetcher Skeleton Without Parsing

- [F] Aggiunto source fetcher skeleton. Fonte: `radar/source_fetcher.py`.
- [F] Aggiunto `FetchedSourceContent`. Fonte: `radar/source_fetcher.py`.
- [F] Aggiunto comando CLI `fetch-sources`. Fonte: `radar/cli.py`.
- [F] Aggiunti test offline/mock. Fonte: `tests/test_source_fetcher.py`.
- [F] Aggiunto live smoke fuori repo come flusso CLI esplicito. Fonte: `radar/cli.py`, prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.
- [F] Nessun parsing live introdotto. Fonte: `radar/source_fetcher.py`, `tests/test_source_fetcher.py`.
- [F] Nessuno snapshot live introdotto. Fonte: `radar/source_fetcher.py`, `radar/cli.py`.
- [F] Auto-merge non consentito per step L2. Fonte: `AGENTS.md`, prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.

## 0120) Controlled Live URL Check Review and Source Registry Hardening

- [F] Rafforzato source registry. Fonte: `radar/source_registry.py`, `config/sources/openai_sources.json`.
- [F] Rafforzata verifica URL live/read-only. Fonte: `radar/url_verifier.py`.
- [F] Aggiunti casi redirect/timeout/unreachable. Fonte: `examples/fixtures/0120_url_verification_cases.json`, `tests/test_url_verifier.py`.
- [F] Aggiunta review dei risultati live. Fonte: `radar/live_url_check.py`.
- [F] Eseguito live smoke controllato fuori repo. Fonte: output comando `python -m radar.cli check-urls`.
- [F] Nessun parsing live introdotto. Fonte: `radar/url_verifier.py`, `radar/live_url_check.py`.
- [F] Nessuno snapshot live introdotto. Fonte: `radar/url_verifier.py`, `radar/live_url_check.py`, `radar/cli.py`.
- [F] Auto-merge non consentito per step L2. Fonte: `AGENTS.md`, prompt `0120-A) AI Release Radar - Controlled Live URL Check Review and Source Registry Hardening`.

## 0110) First Controlled Live URL Check

- [F] Aggiunto live URL checker controllato. Fonte: `radar/live_url_check.py`.
- [F] Aggiunto summary risultati URL. Fonte: `radar/live_url_check.py`.
- [F] Aggiunto test offline con mock. Fonte: `tests/test_live_url_check.py`.
- [F] Aggiunta CLI `check-urls`. Fonte: `radar/cli.py`.
- [F] Aggiunto live test opt-in. Fonte: `tests/test_live_url_check.py`.
- [F] Nessun parsing live introdotto. Fonte: `radar/live_url_check.py`.
- [F] Nessuno snapshot live introdotto. Fonte: `radar/live_url_check.py`, `radar/cli.py`.
- [F] Auto-merge non consentito per step L2. Fonte: `AGENTS.md`, prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.

## 0100) OpenAI Source Registry and URL Verification

- [F] Aggiunto registry fonti OpenAI/Codex. Fonte: `config/sources/openai_sources.json`.
- [F] Aggiunto modello `SourceDefinition`. Fonte: `radar/source_registry.py`.
- [F] Aggiunto URL verifier read-only. Fonte: `radar/url_verifier.py`.
- [F] Aggiunti test offline. Fonte: `tests/test_source_registry.py`, `tests/test_url_verifier.py`.
- [F] Aggiunte fixture registry e URL verification. Fonte: `examples/fixtures/0100_openai_sources_valid.json`, `examples/fixtures/0100_openai_sources_invalid.json`, `examples/fixtures/0100_url_verification_expected.json`.
- [F] Nessun parsing live introdotto. Fonte: `radar/url_verifier.py`.
- [F] Nessuno scheduler introdotto. Fonte: `radar/source_registry.py`, `radar/url_verifier.py`.
- [F] Auto-merge non consentito per step L2. Fonte: `AGENTS.md`, prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.

## 0090) CLI Dry Run

- [F] Aggiunta CLI `python -m radar.cli dry-run`. Fonte: `radar/cli.py`.
- [F] Aggiunto output full/compact/summary. Fonte: `radar/cli.py`.
- [F] Aggiunti test CLI. Fonte: `tests/test_cli.py`.
- [F] Aggiunte fixture expected CLI. Fonte: `examples/fixtures/0090_cli_expected_summary.txt`, `examples/fixtures/0090_cli_expected_full.md`, `examples/fixtures/0090_cli_expected_compact.md`.
- [F] Nessun fetch live introdotto. Fonte: `radar/cli.py`.
- [F] Auto-merge trial L1 documentato. Fonte: `docs/decisions/0090_DECISIONS.md`.

## 0080) Report Engine

- [F] Aggiunto report engine Markdown. Fonte: `radar/report_engine.py`.
- [F] Aggiunto report full. Fonte: `radar/report_engine.py`, `examples/fixtures/0080_report_expected_full.md`.
- [F] Aggiunto report compact. Fonte: `radar/report_engine.py`, `examples/fixtures/0080_report_expected_compact.md`.
- [F] Aggiunto status report. Fonte: `radar/report_engine.py`.
- [F] Aggiunti golden test. Fonte: `tests/test_report_engine.py`, `examples/fixtures/0080_report_expected_full.md`, `examples/fixtures/0080_report_expected_compact.md`.
- [F] Nessun fetch live introdotto. Fonte: `radar/report_engine.py`.
- [F] Auto-merge trial L1 documentato. Fonte: `docs/decisions/0080_DECISIONS.md`.

## 0070) Project Impact Mapping

- [F] Aggiunto mapping impatto progetti. Fonte: `radar/project_impact.py`.
- [F] Aggiunto `ProjectImpact`. Fonte: `radar/project_impact.py`.
- [F] Aggiunta project map offline. Fonte: `examples/fixtures/0070_project_map.json`.
- [F] Aggiunte fixture impatti. Fonte: `examples/fixtures/0070_impact_*.json`.
- [F] Aggiunti test offline. Fonte: `tests/test_project_impact.py`.
- [F] Nessun fetch live introdotto. Fonte: `radar/project_impact.py`.
- [F] Auto-merge trial L1 documentato. Fonte: `docs/decisions/0070_DECISIONS.md`.

## 0065) ASF Auto-Merge Policy Clarification

- [F] Chiarita policy auto-merge ASF. Fonte: `AGENTS.md`.
- [F] Definite classi rischio L0-L4. Fonte: `AGENTS.md`.
- [F] Definiti file high-risk. Fonte: `AGENTS.md`.
- [F] Chiarito che modifiche a `AGENTS.md` non sono auto-mergeable. Fonte: `AGENTS.md`.
- [F] Documentata lesson learned dallo step 0060. Fonte: `docs/decisions/0065_DECISIONS.md`.

## 0060) Classification and Relevance Scoring

- [F] Aggiunta classificazione deterministica keyword-based. Fonte: `radar/classification.py`.
- [F] Aggiunto scoring di rilevanza con componenti auditabili. Fonte: `radar/scoring.py`.
- [F] Aggiunte fixture scoring artificiali offline. Fonte: `examples/fixtures/0060_scoring_*.json`.
- [F] Aggiunti test offline per classificazione e scoring. Fonte: `tests/test_classification.py`, `tests/test_scoring.py`.
- [F] Nessun fetch live introdotto. Fonte: `radar/classification.py`, `radar/scoring.py`.
- [F] Primo trial auto-review/auto-merge low-risk documentato. Fonte: `docs/decisions/0060_DECISIONS.md`.

## 0050) Snapshot and Diff Engine

- [F] Aggiunto workflow offline snapshot/diff. Fonte: `radar/offline_workflow.py`.
- [F] Aggiunte fixture previous/current. Fonte: `examples/fixtures/0050_*`.
- [F] Aggiunti snapshot e diff attesi. Fonte: `examples/snapshots/0050_*`.
- [F] Rafforzato il workflow diff con test su `page_hash`, ordine input, previous assente e duplicati. Fonte: `tests/test_offline_workflow.py`.
- [F] Aggiunti test end-to-end offline. Fonte: `tests/test_offline_workflow.py`.
- [F] Nessun fetch live introdotto. Fonte: prompt 0050-A e `radar/offline_workflow.py`.

## 0040) Offline Fixture Parser

- [F] Aggiunti parser fixture offline JSON/HTML/text. Fonte: `radar/parsers.py`.
- [F] Aggiunto snapshot builder da item gia' parsati. Fonte: `radar/snapshot_builder.py`.
- [F] Aggiunte fixture artificiali per changelog Codex, release GitHub e API deprecations. Fonte: `examples/fixtures/0040_*`.
- [F] Aggiunti snapshot fixture attesi. Fonte: `examples/snapshots/0040_*`.
- [F] Aggiunti test offline per parser e snapshot builder. Fonte: `tests/test_parsers.py` e `tests/test_snapshot_builder.py`.
- [F] Nessun fetch live introdotto. Fonte: prompt 0040-A e `radar/parsers.py`.

## 0030) Core Item Model and Snapshot Format

- [F] Aggiunti modelli core `Item`, `SourceSnapshot`, `DiffResult`, `RunIndexEntry`.
- [F] Aggiunte utility deterministiche per JSON, hash contenuto, `item_id` stabile, diff snapshot e run index JSONL append-only.
- [F] Aggiunte fixture offline 0030, test unitari offline e documentazione tecnica schema/decisioni.

## 0010) AI Release Radar Repository Foundation

- Creazione repository dedicato.
- Impostazione struttura iniziale.
- Regola deterministica: nessun file LAST-* o latest-*.
