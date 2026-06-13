# AI Release Radar

Sistema giornaliero supervisionato per monitorare novità OpenAI, Codex, GPT e futuri strumenti AI, trasformandole in raccomandazioni operative per i progetti software di Alberto.

## Principio operativo

Il radar osserva, confronta, classifica e propone.

Non aggiorna automaticamente repository, skill, script, modelli, scheduler o configurazioni.

## V1 finale locale supervisionata

- [F] La V1 finale e' un prodotto operatore locale supervisionato: scheduler dry-report, Bridge run/log, dashboard locale, Daily Review Pack, Action Center, Human Approval Gate e decisione manuale di Alberto. Fonte: `docs/runbooks/1720_V1_FINAL_OPERATOR_RUNBOOK.md`.
- [F] La V1 finale non invia email, non chiama LLM/API automaticamente a runtime, non esegue auto-action, non modifica scheduler e non agisce su altri repository. Fonte: `AGENTS.md`, `radar/daily_review_pack.py`, `radar_web/manual_trigger.py`.
- [F] La source coverage finale usa parser robusti per GitHub API e Markdown ufficiale deprecations, lasciando le altre fonti diagnosticate, manual-review o unsupported documentate. Fonte: `docs/source_policy/1730_SOURCE_POLICY_FINAL.md`, `config/sources/openai_sources.json`, `radar/source_coverage.py`.
- [F] Il tag `v1.0.0` e' solo pianificato e non creato da questo prodotto. Fonte: `docs/release/1750_V1_0_TAG_PLAN.md`.

## Operator Acceptance

- [F] Easy Mode e' il punto di ingresso operativo della web app locale; Expert Mode resta il cockpit tecnico. Fonte: `docs/web/2270_EASY_MODE_UI_CONTRACT.md`, `radar_web/app.py`.
- [F] Per modifiche UI-facing, AI Release Radar distingue Verification Gate e Acceptance Gate: il primo verifica test/smoke/API/diff/safety, il secondo verifica accesso reale, primo utilizzo e navigazione dell'operatore. Fonte: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`.
- [F] Principio guida: `PASS tecnico ≠ PASS operatore`. Fonte: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`.

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

## Local web dashboard

- [F] La dashboard locale si avvia con `python -m radar_web.app --host 127.0.0.1 --port 8787`. Fonte: `radar_web/app.py`, `docs/runbooks/0850_WEB_DASHBOARD_RUNBOOK.md`.
- [F] La dashboard legge i run Bridge da `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs`. Fonte: `radar_web/config.py`.
- [F] La home mostra ultimo run, gate, source coverage, data completeness, HAG, prompt suggestions, scheduler status e run recenti. Fonte: `radar_web/templates/index.html`, `radar_web/app.py`.
- [F] La pagina dettaglio mostra report compact, gate, HAG, dashboard operatore, diagnostics, direct actions, blocked actions, monitor-only, manual review queue, prompt suggestions e path locali come testo. Fonte: `radar_web/templates/run_detail.html`.
- [F] L'Action Center `/actions` mostra Action Inbox, filtri, routing progetto, priorita', rischio, decision status, safety status, trend, noise e controlli umani. Fonte: `radar_web/templates/actions.html`, `radar_web/app.py`.
- [F] Le decisioni Action Center vengono scritte nel Bridge sotto `action_dispatch/decision_log.jsonl`. Fonte: `radar_web/action_center.py`, `radar/action_inbox.py`.
- [F] I prompt pack vengono generati solo come Markdown nel Bridge dopo decisione umana esplicita. Fonte: `radar/action_inbox.py`, `radar_web/action_center.py`.
- [F] Il bottone manuale esegue solo `python -m radar.cli daily-sim --output-root "<Bridge runs root>"`, con lock, timeout e JSON safety esplicito. Fonte: `radar_web/manual_trigger.py`.
- [F] La scheduler card interpreta `Ready` + `LastTaskResult=0` come `OK`. Fonte: `radar_web/scheduler_status.py`.
- [F] Il runbook troubleshooting V1 e' `docs/runbooks/0940_WEB_DASHBOARD_TROUBLESHOOTING.md`. Fonte: `docs/runbooks/0940_WEB_DASHBOARD_TROUBLESHOOTING.md`.
- [F] Il runbook operator loop e' `docs/runbooks/1090_DAILY_RADAR_OPERATOR_LOOP_RUNBOOK.md`. Fonte: `docs/runbooks/1090_DAILY_RADAR_OPERATOR_LOOP_RUNBOOK.md`.
- [F] Il closure pack operator-ready V1 e' `docs/architecture/0950_DASHBOARD_V1_OPERATOR_READY_CLOSURE_PACK.md`. Fonte: `docs/architecture/0950_DASHBOARD_V1_OPERATOR_READY_CLOSURE_PACK.md`.
- [F] Nessuna email, nessun LLM, nessuna auto-azione, nessun nuovo scheduler e nessun altro repository vengono toccati dalla dashboard. Fonte: `radar_web/manual_trigger.py`, `radar_web/scheduler_status.py`.

## V1 operator release candidate

- [F] La V1 operator release candidate resta un radar supervisionato: prepara decisioni, ma non le esegue. Fonte: `radar/daily_review_pack.py`, `radar/v1_readiness.py`, `radar_web/action_center.py`.
- [F] Il Daily Review Pack si genera con `python -m radar.cli daily-review-pack --run-dir <run-dir> --output-dir <Bridge-daily-review-pack-dir> --scheduler-log <scheduler-log>`. Fonte: `radar/cli.py`, `radar/daily_review_pack.py`.
- [F] Il V1 readiness gate si genera con `python -m radar.cli v1-readiness-gate --run-dir <run-dir> --output-dir <Bridge-codex-command-dir> --dashboard-smoke-status PASS --action-center-smoke-status PASS --action-center-run-scope-status PASS`. Fonte: `radar/cli.py`, `radar/v1_readiness.py`.
- [F] L'Action Center distingue decisioni del run corrente da decisioni storiche e segnala quando il run ha HAG/prompt suggestions nel run output ma non una cartella `action_dispatch` dedicata. Fonte: `radar_web/action_center.py`, `radar/action_inbox.py`.
- [F] La pagina dettaglio run e l'API source-matrix espongono la matrice diagnostica fonti con fetch, parser, HTTP, item, manual review e follow-up. Fonte: `radar/source_coverage.py`, `radar_web/run_locator.py`, `radar_web/app.py`.
- [F] I prompt suggestions restano manual-only, associati al run e non eseguiti. Fonte: `radar/daily_review_pack.py`, `radar/action_inbox.py`.
- [F] Il runbook V1 RC e' `docs/runbooks/1460_V1_OPERATOR_RC_RUNBOOK.md`. Fonte: `docs/runbooks/1460_V1_OPERATOR_RC_RUNBOOK.md`.

## Documentazione V1 finale

- [F] Runbook operatore finale: `docs/runbooks/1720_V1_FINAL_OPERATOR_RUNBOOK.md`. Fonte: file indicato.
- [F] Source policy finale: `docs/source_policy/1730_SOURCE_POLICY_FINAL.md`. Fonte: file indicato.
- [F] Troubleshooting e manutenzione: `docs/troubleshooting/1740_TROUBLESHOOTING_AND_MAINTENANCE.md`. Fonte: file indicato.
- [F] Piano tag V1.0, non eseguito: `docs/release/1750_V1_0_TAG_PLAN.md`. Fonte: file indicato.

## Multilingual dashboard and news translation

- [F] La UI dashboard supporta `?lang=en|it|fr|de|es` con cataloghi JSON versionati in `radar_web/locales/`. Fonte: `radar_web/i18n.py`, `radar_web/locales/*.json`.
- [F] I template home, run detail e Action Center usano helper `t()` e preservano `lang` nei link interni. Fonte: `radar_web/app.py`, `radar_web/templates/index.html`, `radar_web/templates/run_detail.html`, `radar_web/templates/actions.html`.
- [F] I formati locali per data/ora, status e boolean sono gestiti in modo deterministico senza nuove dipendenze. Fonte: `radar_web/i18n.py`, `pyproject.toml`.
- [F] Le traduzioni delle news dinamiche sono Bridge-only sotto `translations/<run_id>/` e non sono salvate nel repo. Fonte: `radar/news_translation.py`, `docs/architecture/1190_DYNAMIC_NEWS_TRANSLATION_CONTRACT.md`.
- [F] Il prompt pack traduzioni viene generato nel Bridge con profilo default `balanced` e non esegue LLM. Fonte: `radar/translation_prompt_pack.py`.
- [F] Il runbook multilingua e' `docs/runbooks/1250_MULTILINGUAL_RUNBOOK.md`. Fonte: `docs/runbooks/1250_MULTILINGUAL_RUNBOOK.md`.
- [F] La review finale 1260-1350 ha verificato cataloghi, fallback, Action Center, smoke HTML/API e cache sample Bridge per EN/IT/FR/DE/ES. Fonte: `docs/architecture/1350_MULTILINGUAL_FINAL_REVIEW_CLOSURE_PACK.md`.
- [F] La scorecard finale multilingua e' `docs/reviews/1340_MULTILINGUAL_FINAL_QA_SCORECARD.md`. Fonte: `docs/reviews/1340_MULTILINGUAL_FINAL_QA_SCORECARD.md`.

## Comandi principali

```powershell
python -m radar.cli --help
python -m radar.cli real-run --help
python -m radar.cli real-run --profile manual --output-dir "<directory-fuori-repo>"
python -m radar.cli daily-sim --output-root "<Bridge-runs-fuori-repo>"
python -m radar.cli daily-review-pack --run-dir "<Bridge-run-dir>" --output-dir "<Bridge-daily-review-pack-dir>" --scheduler-log "<Bridge-scheduler-log>"
python -m radar.cli v1-readiness-gate --run-dir "<Bridge-run-dir>" --output-dir "<Bridge-codex-command-dir>" --scheduler-log "<Bridge-scheduler-log>" --dashboard-smoke-status PASS --action-center-smoke-status PASS --action-center-run-scope-status PASS
python -m radar_web.app --host 127.0.0.1 --port 8787
Invoke-RestMethod -Uri "http://127.0.0.1:8787/api/actions" -Method Get
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\alberto.ferrari\source\repos\AI_Release_Radar\scripts\scheduler\ai_release_radar_daily_dry_report.ps1"
```

- [F] La V1 manuale `real-run` non crea scheduler. Fonte: `radar/cli.py`, `AGENTS.md`.
- [F] Dal 0600 esiste un task Windows dry-report controllato, non operativo pieno. Fonte: `docs/architecture/0600_SCHEDULER_DRY_REPORT_CLOSURE_PACK.md`.
