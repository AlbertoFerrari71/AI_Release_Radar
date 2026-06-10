# 0500) Source Coverage V1.2 and Scheduler Readiness Closure Pack

## A. Cosa E' Stato Migliorato

- [F] Source Coverage V1.2 ha confermato di non forzare una seconda fonte senza formato stabile. Fonte: `docs/architecture/0410_SOURCE_COVERAGE_V1_2_IMPLEMENTATION.md`.
- [F] Il registry ora espone metadata quality/readiness per ogni fonte. Fonte: `config/sources/openai_sources.json`, `docs/architecture/0420_REGISTRY_QUALITY_HARDENING.md`.
- [F] L'automation gate espone `scheduler_readiness_recommendation`. Fonte: `radar/automation_gate.py`, `docs/architecture/0430_COVERAGE_WARNING_POLICY.md`.
- [F] Il gate e `daily-sim` includono manual review queue. Fonte: `radar/manual_review_queue.py`, `radar/automation_gate.py`, `radar/cli.py`, `docs/architecture/0440_MANUAL_REVIEW_QUEUE.md`.
- [F] `daily-sim` ha regressioni offline per gate, summary, ACTION_REVIEW_REQUIRED, coverage warning e queue. Fonte: `tests/test_cli.py`, `docs/architecture/0450_DAILY_SIM_REGRESSION_PACK.md`.
- [F] Checklist, dry-run design, operator runbook e final readiness review sono stati prodotti. Fonte: `docs/architecture/0460_SCHEDULER_READINESS_CHECKLIST.md`, `docs/architecture/0470_SCHEDULER_DRY_RUN_DESIGN.md`, `docs/runbooks/0480_OPERATOR_RUNBOOK.md`, `docs/reviews/0490_FINAL_SCHEDULER_READINESS_REVIEW.md`.

## B. Cosa Resta Incompleto

- [F] Non e' stata aggiunta una seconda fonte live parsata. Fonte: `docs/architecture/0410_SOURCE_COVERAGE_V1_2_IMPLEMENTATION.md`.
- [F] Lo scheduler reale non e' stato introdotto. Fonte: `docs/architecture/0470_SCHEDULER_DRY_RUN_DESIGN.md`, `AGENTS.md`.
- [F] Non sono state introdotte notifiche automatiche o chiamate LLM. Fonte: `radar/cli.py`, `AGENTS.md`.
- [INT] La principale incompletezza resta la coverage parser reale: la strategia corretta e' evitare un falso verde invece di aumentare `parsed_count` con HTML fragile. Base: `docs/architecture/0410_SOURCE_COVERAGE_V1_2_IMPLEMENTATION.md`.

## C. Coverage Status

- [F] Baseline corrente: `parsed_count=1/11`, con `github_api_openai_codex_releases` come fonte strutturata parsata. Fonte: `docs/architecture/0410_SOURCE_COVERAGE_V1_2_IMPLEMENTATION.md`.
- [F] `github_api_openai_codex_releases` e' `P0`, `scheduler_readiness=ready`. Fonte: `config/sources/openai_sources.json`.
- [F] Le fonti HTML/manual review restano `hold` o `warn` nel registry. Fonte: `config/sources/openai_sources.json`.
- [INT] Coverage sufficiente per report supervisionato, non per scheduler operativo pieno. Base: `docs/architecture/0460_SCHEDULER_READINESS_CHECKLIST.md`.

## D. Automation Gate Status

- [F] Il gate fallisce su zero parsed, output mancante/corrotto, output dentro repo e index invalido. Fonte: `radar/automation_gate.py`.
- [F] Il gate produce warning su coverage bassa, manual review, unsupported alto, scorecard non PASS e monitor-only alto. Fonte: `radar/automation_gate.py`.
- [F] Il gate produce `ACTION_REVIEW_REQUIRED` quando esistono direct actions. Fonte: `radar/automation_gate.py`.
- [F] Il gate espone `scheduler_readiness_recommendation`. Fonte: `radar/automation_gate.py`.

## E. Manual Review Queue

- [F] La queue contiene righe `source` e `action` con reason, severity, follow-up e flag `blocking_for_scheduler`. Fonte: `radar/manual_review_queue.py`.
- [F] La queue viene serializzata nel gate JSON/Markdown e nel daily-sim summary. Fonte: `radar/automation_gate.py`, `radar/cli.py`.
- [INT] La queue e' una lista di review, non una lista di azioni automatiche. Base: `docs/architecture/0440_MANUAL_REVIEW_QUEUE.md`.

## F. Scheduler Readiness Decision

- [INT] Decisione per scheduler dry/report futuro: `GO_WITH_WARNINGS`. Base: `docs/reviews/0490_FINAL_SCHEDULER_READINESS_REVIEW.md`.
- [INT] Decisione per scheduler operativo pieno: `HOLD`. Base: `docs/reviews/0490_FINAL_SCHEDULER_READINESS_REVIEW.md`.
- [F] Nessun scheduler reale, task Windows, notifica automatica o chiamata LLM viene introdotta dal closure pack. Fonte: `AGENTS.md`, `radar/cli.py`.

## G. Perche' Lo Scheduler Reale Resta Vietato Qui

- [F] Lo step 0410-0500 vieta scheduler reale. Fonte: prompt `0410-0500` salvato nel Bridge.
- [F] `AGENTS.md` vieta scheduler senza istruzione esplicita. Fonte: `AGENTS.md`.
- [INT] Con coverage bassa e queue manuale, lo scheduler reale deve essere uno step L3 separato con piano di disable/restore. Base: `docs/architecture/0470_SCHEDULER_DRY_RUN_DESIGN.md`.

## H. Prossimo Step Consigliato

- [PROP] Se Alberto vuole procedere verso automazione: `0510) Scheduler Dry-Report L3 Approval`, limitato a dry/report, senza email, senza auto-action e con disable plan.
- [PROP] Se Alberto preferisce ridurre warning: continuare con source coverage e cercare una seconda fonte machine-readable o Markdown stabile, senza parser HTML fragile.
