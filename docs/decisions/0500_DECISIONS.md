# 0500) Decisions

## A. Decisioni

- [INT] Strategia PR scelta per il super-step: PR batch unica con commit separati per step. Base: prompt `0410-0500` e intreccio tecnico fra registry, gate, queue e daily-sim.
- [INT] Source coverage 0410: non aggiungere una seconda fonte live parsata senza formato stabile. Base: `docs/architecture/0410_SOURCE_COVERAGE_V1_2_IMPLEMENTATION.md`.
- [F] Registry 0420: aggiungere metadata quality/readiness opzionali ma valorizzati nel registry operativo. Fonte: `docs/architecture/0420_REGISTRY_QUALITY_HARDENING.md`.
- [F] Coverage policy 0430: esporre `scheduler_readiness_recommendation` e impedire falso PASS con coverage bassa. Fonte: `docs/architecture/0430_COVERAGE_WARNING_POLICY.md`.
- [F] Manual review 0440: produrre queue deterministica nel gate e nel daily-sim summary. Fonte: `docs/architecture/0440_MANUAL_REVIEW_QUEUE.md`.
- [F] Daily sim 0450: aggiungere regressioni offline per gate, warning, queue e no scheduler flags. Fonte: `docs/architecture/0450_DAILY_SIM_REGRESSION_PACK.md`.
- [INT] Scheduler readiness: `GO_WITH_WARNINGS` solo per dry/report futuro; `HOLD` per scheduler operativo pieno. Base: `docs/reviews/0490_FINAL_SCHEDULER_READINESS_REVIEW.md`.

## B. Vincoli Confermati

- [F] Nessun merge su `main` e nessun push diretto su `main`. Fonte: `AGENTS.md`.
- [F] Nessun scheduler reale o task Windows in questo step. Fonte: prompt `0410-0500`, `AGENTS.md`.
- [F] Nessuna nuova dipendenza. Fonte: `pyproject.toml`.
- [F] Nessun output runtime versionato nel repo. Fonte: `AGENTS.md`.
- [F] Nessun file `LAST-*` o `latest-*` nel repo. Fonte: `AGENTS.md`.
- [F] No auto-merge per questo step L1/L2. Fonte: prompt `0410-0500`, `AGENTS.md`.

## C. Rischi Residui

- [INT] Coverage parser reale resta bassa. Base: `docs/architecture/0410_SOURCE_COVERAGE_V1_2_IMPLEMENTATION.md`.
- [INT] Fonti manual review e HTML unsupported possono restare rumorose. Base: `config/sources/openai_sources.json`, `radar/manual_review_queue.py`.
- [INT] Direct actions richiedono lettura umana. Base: `radar/automation_gate.py`.

## D. Prossimo Step Consigliato

- [PROP] `0510) Scheduler Dry-Report L3 Approval` se Alberto vuole provare un task dry/report disabilitabile.
- [PROP] In alternativa, proseguire con una fonte P1 machine-readable/stabile prima di qualunque scheduler.
