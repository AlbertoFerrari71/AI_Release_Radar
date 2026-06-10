# AI Release Radar

Sistema giornaliero supervisionato per monitorare novità OpenAI, Codex, GPT e futuri strumenti AI, trasformandole in raccomandazioni operative per i progetti software di Alberto.

## Principio operativo

Il radar osserva, confronta, classifica e propone.

Non aggiorna automaticamente repository, skill, script, modelli, scheduler o configurazioni.

## V1 manuale

- [F] La V1 manuale si esegue con `python -m radar.cli real-run --profile manual --output-dir <directory-fuori-repo>`. Fonte: `radar/cli.py`.
- [F] `--output-dir` resta esplicito e deve puntare fuori repository. Fonte: `radar/cli.py`, `radar/real_run.py`.
- [F] Gli output runtime non devono usare file o directory `LAST-*` o `latest-*`. Fonte: `AGENTS.md`, `radar/real_run.py`.
- [F] Il run produce full report, compact report, run summary e `runs_index.jsonl`. Fonte: `radar/real_run.py`.
- [F] Il runbook operativo V1 e' `docs/runbooks/0230_V1_MANUAL_RUN_RUNBOOK.md`. Fonte: `docs/runbooks/0230_V1_MANUAL_RUN_RUNBOOK.md`.

## V1.1 actionable radar

- [F] La V1.1 aggiunge source diagnostics piu' esplicite per `parsed`, `fetched_but_unsupported`, `manual_review_required` e `fetch_failed`. Fonte: `radar/live_snapshot.py`.
- [F] Gli impatti progetto distinguono `direct_action`, `monitor_only` e `no_action`. Fonte: `radar/project_impact.py`.
- [F] Le azioni consigliate includono titolo, motivo di rilevanza e prossimo passo deterministico. Fonte: `radar/project_impact.py`.
- [F] Il report reale include una scorecard e il run summary serializza i conteggi action type. Fonte: `radar/real_run.py`, `radar/report_scorecard.py`.
- [F] Il closure pack V1.1 e' `docs/architecture/0300_ACTIONABLE_RADAR_V1_1_CLOSURE_PACK.md`. Fonte: `docs/architecture/0300_ACTIONABLE_RADAR_V1_1_CLOSURE_PACK.md`.
- [INT] Dopo la review 0310, la scorecard PASS va letta come qualita' report, non come readiness scheduler o copertura fonti sufficiente. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [PROP] Il prossimo blocco consigliato e' source coverage V1.2 prima dello scheduler. Fonte: `docs/decisions/0310_DECISIONS.md`.

## Automation readiness simulation

- [F] `daily-sim` esegue una simulazione daily controllata senza creare scheduler. Fonte: `radar/cli.py`.
- [F] `daily-sim` genera una directory datata fuori repository e valuta `automation_gate_status`. Fonte: `radar/cli.py`, `radar/automation_gate.py`.
- [F] Il closure pack 0400 conclude `HOLD` per scheduler reale e consente solo simulazione controllata con review umana. Fonte: `docs/architecture/0400_AUTOMATION_READINESS_CLOSURE_PACK.md`, `docs/reviews/0390_DAILY_RUN_READINESS_REVIEW.md`.
- [PROP] Il prossimo blocco consigliato e' `0410) Source Coverage V1.2 Implementation`. Fonte: `docs/decisions/0400_DECISIONS.md`.

## V1.2 source coverage and scheduler readiness

- [F] La V1.2 conferma di non forzare una seconda fonte live parsata senza formato stabile. Fonte: `docs/architecture/0410_SOURCE_COVERAGE_V1_2_IMPLEMENTATION.md`.
- [F] Il registry include metadata quality/readiness per parser strategy, coverage priority, failure mode, follow-up e scheduler readiness. Fonte: `config/sources/openai_sources.json`, `docs/architecture/0420_REGISTRY_QUALITY_HARDENING.md`.
- [F] L'automation gate espone `scheduler_readiness_recommendation` e manual review queue. Fonte: `radar/automation_gate.py`, `radar/manual_review_queue.py`.
- [F] `daily-sim` serializza manual review queue e scheduler readiness nel summary. Fonte: `radar/cli.py`.
- [F] Il runbook operatore V1.2 e' `docs/runbooks/0480_OPERATOR_RUNBOOK.md`. Fonte: `docs/runbooks/0480_OPERATOR_RUNBOOK.md`.
- [INT] Readiness finale: `GO_WITH_WARNINGS` per futuro scheduler dry/report supervisionato, `HOLD` per scheduler operativo pieno. Fonte: `docs/reviews/0490_FINAL_SCHEDULER_READINESS_REVIEW.md`.
- [PROP] Prossimo blocco consigliato: `0510) Scheduler Dry-Report L3 Approval` solo se Alberto autorizza esplicitamente uno step L3.

## Scheduler dry-report L3

- [F] Il consenso L3 per scheduler dry-report e' registrato in `docs/decisions/0510_L3_SCHEDULER_DRY_REPORT_CONSENT.md`. Fonte: `docs/decisions/0510_L3_SCHEDULER_DRY_REPORT_CONSENT.md`.
- [F] Il consenso autorizza solo scheduler dry-report con output Bridge e human review gate. Fonte: `docs/decisions/0510_L3_SCHEDULER_DRY_REPORT_CONSENT.md`.
- [F] Il consenso non autorizza auto-azioni, email/notifiche automatiche, chiamate LLM automatiche, deploy o modifiche ad altri repository. Fonte: `docs/decisions/0510_L3_SCHEDULER_DRY_REPORT_CONSENT.md`.
- [F] Il task `AIReleaseRadar_DailyDryReport` e' stato creato con schedule daily 07:15 e action Windows PowerShell verso `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`. Fonte: `docs/architecture/0540_WINDOWS_TASK_CREATION.md`.
- [F] Il primo trigger manuale riuscito ha prodotto output Bridge e gate report. Fonte: `docs/architecture/0550_FIRST_SCHEDULED_TASK_TRIGGER.md`, `docs/architecture/0560_SCHEDULED_RUN_OUTPUT_VERIFICATION.md`.
- [INT] Lo scheduler dry-report non cambia la decisione `HOLD` per scheduler operativo pieno. Fonte: `docs/reviews/0490_FINAL_SCHEDULER_READINESS_REVIEW.md`.

## V1.5 supervised daily intelligence

- [F] V1.5 aggiunge quality gate v2, action triage, prompt suggestions, Human Approval Gate report e dashboard giornaliera al run `daily-sim`. Fonte: `radar/cli.py`.
- [F] Il contratto `Radar fatto` e' documentato in `docs/architecture/0620_RADAR_DONE_BRIDGE_RETRIEVAL_CONTRACT.md`. Fonte: `docs/architecture/0620_RADAR_DONE_BRIDGE_RETRIEVAL_CONTRACT.md`.
- [F] I prompt suggestions restano `suggested_only` e non vengono eseguiti automaticamente. Fonte: `radar/prompt_suggestions.py`, `radar/supervised_loop.py`.
- [F] Cross-project PR, email/notifiche automatiche, chiamate LLM automatiche e auto-azioni restano vietate. Fonte: `docs/reviews/0740_V1_5_GOVERNANCE_AND_RISK_REVIEW.md`.
- [PROP] Prossimo passo consigliato: `0760) First Real Scheduled Run V1.5 Review`. Fonte: `docs/architecture/0750_SUPERVISED_DAILY_INTELLIGENCE_CLOSURE_PACK.md`.

## Comandi principali

```powershell
python -m radar.cli --help
python -m radar.cli real-run --help
python -m radar.cli real-run --profile manual --output-dir "<directory-fuori-repo>"
python -m radar.cli daily-sim --output-root "<Bridge-runs-fuori-repo>"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\alberto.ferrari\source\repos\AI_Release_Radar\scripts\scheduler\ai_release_radar_daily_dry_report.ps1"
```

- [F] La V1 manuale `real-run` non crea scheduler. Fonte: `radar/cli.py`, `AGENTS.md`.
- [F] Dal 0600 esiste un task Windows dry-report controllato, non operativo pieno. Fonte: `docs/architecture/0600_SCHEDULER_DRY_REPORT_CLOSURE_PACK.md`.
