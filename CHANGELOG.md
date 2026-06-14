# Changelog

## 2630-R) User Benefit Karma Doctrine and Gate

- [F] Aggiunta doctrine `User Benefit Karma` con principio `Prima il beneficio, poi l’algoritmo`. Fonte: `docs/values/2630_USER_BENEFIT_KARMA.md`.
- [F] Aggiunto `User Benefit Gate` per valutare fatica, rischio, tempo, confusione, decisione reale, chiarezza, lavoro inutile evitato ed evidenza operatore. Fonte: `docs/quality/2630_USER_BENEFIT_GATE.md`.
- [F] Aggiornati README e AGENTS con regola per dichiarare il beneficio utente nei futuri step non banali. Fonte: `README.md`, `AGENTS.md`.

## 2460-2600) Daily Intelligence Brief

- [F] Aggiunto generatore deterministic/template-based `daily-brief` per Human Brief, AI Model Packet e Project Impact Map con output Bridge-only. Fonte: `radar/daily_intelligence.py`, `radar/cli.py`.
- [F] Aggiunta mappa configurabile `config/project_impact_map.json` per AI Software Factory, Codex Skills, AI Release Radar, ASF Blueprint Studio, Family Photo Organizer e Conti Chiari AI. Fonte: `config/project_impact_map.json`.
- [F] Aggiunti endpoint GET/read-only Easy Mode per brief e model packet. Fonte: `radar_web/app.py`.
- [F] Aggiornata Easy Mode con sezione `Oggi in 30 secondi` e contesto manual-only in Action Center. Fonte: `radar_web/templates/easy_index.html`, `radar_web/templates/actions.html`.
- [F] Applicato polish P3 2620: pulsanti Daily Brief impilati su mobile stretto e sigla HAG esplicita nei titoli localizzati. Fonte: `radar_web/static/style.css`, `radar_web/locales/*.json`.
- [F] Aggiunto Skill Invocation Ledger v0 come schema/validatore stabile con output effettivi nel Bridge. Fonte: `docs/process/2460_SKILL_INVOCATION_LEDGER.md`, `radar/skill_ledger.py`.
- [F] Nessuna chiamata LLM runtime, nessuna auto-azione, nessuna email/notifica, nessuna scheduler mutation e nessun output runtime versionato introdotti. Fonte: `radar/daily_intelligence.py`, `radar_web/app.py`, `AGENTS.md`.

## 2390-2440) Operator Acceptance Philosophy and UI Gate Lessons Learned

- [F] Aggiunta lesson learned Operator Acceptance con principio `PASS tecnico ≠ PASS operatore`. Fonte: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`.
- [F] Documentata la differenza tra Verification Gate e Acceptance Gate per modifiche UI-facing. Fonte: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`, `docs/decisions/2440_DECISIONS.md`.
- [F] Formalizzato UI Navigation Gate per home, Easy Mode, Expert Mode, Action Center, Source Matrix, run detail, tab, tendine, link GET interni, bottoni sicuri e preferenze UI. Fonte: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`, `docs/web/2270_EASY_MODE_UI_CONTRACT.md`.
- [F] Formalizzata safe-click policy con divieto di click automatici su HAG approvals, decisioni operative, scheduler, trigger run reali, email, notifiche e azioni esterne. Fonte: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`, `docs/web/2270_EASY_MODE_UI_CONTRACT.md`.
- [F] Collegata la correzione Easy Mode/accesso della PR #37 e la validazione reale 18/18 su `127.0.0.1:8787`. Fonte: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`, report Bridge `2385-Report_Codex.md`.
- [F] Nessuna modifica funzionale al prodotto: aggiornamento documentale, decision record, handoff ASF e note presentazione. Fonte: diff 2390-2440.

## 1520-2000) V1 Final Operator Product

- [F] Aggiunta classificazione finale V1 delle fonti con `final_v1_status`, motivazione e categoria backlog manutentivo. Fonte: `config/sources/openai_sources.json`, `radar/source_registry.py`.
- [F] Promossa `openai_api_deprecations` al twin Markdown ufficiale con parser deterministico `api_deprecations_markdown` e fixture offline. Fonte: `radar/parsers.py`, `examples/fixtures/1520_api_deprecations_fixture.md`, `tests/test_parsers.py`.
- [F] Aggiunte fonti machine-readable GitHub API per OpenAI Python e Node SDK releases. Fonte: `config/sources/openai_sources.json`.
- [F] Aggiunto gate finale source coverage con target `parsed_count >= 3`, completezza classificazione, spiegazioni manual/unsupported e controllo parser fragile. Fonte: `radar/source_coverage.py`, `tests/test_source_coverage.py`.
- [F] Aggiunto gate finale V1 readiness 1810 con classificazioni `AI_RADAR_V1_FINAL_READY`, `AI_RADAR_V1_FINAL_READY_WITH_WARNINGS`, `MICRO_FIX_REQUIRED_BEFORE_FINAL`, `BLOCKED`. Fonte: `radar/v1_readiness.py`, `tests/test_v1_readiness.py`.
- [F] Rafforzati Daily Review Pack e dashboard con source matrix finale, manual review queue, unsupported explained e testi no-auto-action/no-email/no-LLM/manual-approval. Fonte: `radar/daily_review_pack.py`, `radar_web/templates/index.html`, `radar_web/locales/*.json`.
- [F] Aggiunta documentazione finale: runbook operatore, source policy, troubleshooting/manutenzione e piano tag `v1.0.0` non eseguito. Fonte: `docs/runbooks/1720_V1_FINAL_OPERATOR_RUNBOOK.md`, `docs/source_policy/1730_SOURCE_POLICY_FINAL.md`, `docs/troubleshooting/1740_TROUBLESHOOTING_AND_MAINTENANCE.md`, `docs/release/1750_V1_0_TAG_PLAN.md`.
- [F] Nessuna modifica scheduler, nessuna email/notifica automatica, nessuna chiamata LLM runtime, nessuna auto-azione e nessun tag/release introdotti. Fonte: `AGENTS.md`, diff 1520-2000.

## 1380-1500) V1 Operator-Ready Release Candidate

- [F] Aggiunta generazione Bridge-only del Daily Review Pack con executive summary, safety summary, source coverage, action/HAG/prompt summary e checklist operatore. Fonte: `radar/daily_review_pack.py`, `tests/test_daily_review_pack.py`.
- [F] Aggiunta matrice diagnostica source coverage riusabile da pack, run detail e API read-only. Fonte: `radar/source_coverage.py`, `radar_web/run_locator.py`, `radar_web/app.py`, `tests/test_source_coverage.py`.
- [F] Rafforzato Action Center per distinguere run corrente, decisioni storiche, assenza di cartella run-scoped `action_dispatch`, HAG corrente e prompt suggestions manual-only. Fonte: `radar/action_inbox.py`, `radar_web/action_center.py`, `radar_web/templates/actions.html`, `tests/test_action_inbox.py`, `tests/test_radar_web_app.py`.
- [F] Aggiunto V1 Operator Readiness Gate con classificazioni `V1_OPERATOR_READY`, `V1_OPERATOR_READY_WITH_WARNINGS`, `MICRO_FIX_REQUIRED_BEFORE_V1`, `BLOCKED`. Fonte: `radar/v1_readiness.py`, `tests/test_v1_readiness.py`.
- [F] Estesa CLI con `daily-review-pack` e `v1-readiness-gate`, entrambe con output directory esplicita fuori repo. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] Aggiornata UI multilingua EN/IT/FR/DE/ES per nuovi badge, HAG corrente, safety strip e matrice fonti. Fonte: `radar_web/locales/*.json`, `tests/test_i18n.py`.
- [F] Aggiunto runbook V1 RC supervisionato. Fonte: `docs/runbooks/1460_V1_OPERATOR_RC_RUNBOOK.md`.
- [F] Nessuna modifica scheduler, nessuna email/notifica automatica, nessuna chiamata LLM runtime, nessuna auto-azione e nessun output runtime versionato introdotti. Fonte: `AGENTS.md`, `radar/daily_review_pack.py`, `radar/v1_readiness.py`.

## 1260-1350) Multilingual UI and Translation QA Final Review

- [F] Aggiunta review preflight multilingua, catalog consistency, linguistic QA, navigation smoke, Action Center UX, fallback QA e scorecard finale. Fonte: `docs/reviews/1260_MULTILINGUAL_PREFLIGHT_BASELINE_REVIEW.md`, `docs/reviews/1340_MULTILINGUAL_FINAL_QA_SCORECARD.md`.
- [F] Rafforzati i test cataloghi con controllo duplicati, valori vuoti, placeholder vietati e placeholder mismatch. Fonte: `tests/test_i18n.py`.
- [F] Rafforzato il fallback cache traduzioni con test su cache corrotta senza crash. Fonte: `tests/test_news_translation.py`.
- [F] Applicate micro-correzioni linguistiche FR/DE/ES e micro-polish CSS per testi lunghi. Fonte: `radar_web/locales/fr.json`, `radar_web/locales/de.json`, `radar_web/locales/es.json`, `radar_web/static/style.css`.
- [F] Prodotti smoke HTML/API e cache sample/prompt pack nel Bridge, non versionati nel repo. Fonte: `docs/architecture/1350_MULTILINGUAL_FINAL_REVIEW_CLOSURE_PACK.md`.
- [F] Nessuna nuova dipendenza, nessuna modifica scheduler, nessuna email/notifica automatica, nessun LLM runtime, nessuna auto-azione e nessun altro repository introdotti. Fonte: `pyproject.toml`, diff 1260-1350, `AGENTS.md`.

## 1110-1250) Multilingual Dashboard and News Translation Pipeline

- [F] Aggiunta architettura i18n deterministica per UI dashboard con cataloghi JSON EN/IT/FR/DE/ES. Fonte: `docs/architecture/1110_I18N_ARCHITECTURE_REVIEW.md`, `radar_web/i18n.py`, `radar_web/locales/*.json`.
- [F] Estratte le principali stringhe UI di home, run detail e Action Center tramite helper `t()`. Fonte: `radar_web/templates/index.html`, `radar_web/templates/run_detail.html`, `radar_web/templates/actions.html`.
- [F] Aggiunto selettore lingua e preservazione `?lang=` nei link interni. Fonte: `radar_web/app.py`, `radar_web/templates/*.html`, `radar_web/static/style.css`.
- [F] Aggiunti helper deterministici per date/time, status e bool localizzati. Fonte: `radar_web/i18n.py`, `tests/test_i18n.py`.
- [F] Aggiunto glossario terminologico EN/IT/FR/DE/ES. Fonte: `docs/i18n/1180_TRANSLATION_GLOSSARY.md`.
- [F] Aggiunto contratto/cache Bridge-only per traduzioni news dinamiche, con preservation QA per link, versioni, comandi e path. Fonte: `docs/architecture/1190_DYNAMIC_NEWS_TRANSLATION_CONTRACT.md`, `radar/news_translation.py`, `tests/test_news_translation.py`.
- [F] Aggiunto generatore prompt pack traduzione Bridge-only con profili `cheap`, `balanced`, `quality` e `llm_executed=false`. Fonte: `radar/translation_prompt_pack.py`, `tests/test_translation_prompt_pack.py`.
- [F] L'Action Center legge cache traduzioni esistenti e mostra fallback originale con badge se la traduzione manca, senza generare traduzioni runtime. Fonte: `radar_web/app.py`, `radar_web/templates/actions.html`.
- [F] Aggiunti closure pack, decision record e runbook multilingua. Fonte: `docs/architecture/1250_MULTILINGUAL_CLOSURE_PACK.md`, `docs/decisions/1250_DECISIONS.md`, `docs/runbooks/1250_MULTILINGUAL_RUNBOOK.md`.
- [F] Nessuna nuova dipendenza, nessun nuovo scheduler, nessuna email/notifica automatica, nessuna chiamata LLM runtime, nessuna auto-azione, nessun altro repository e nessun output runtime versionato introdotti. Fonte: `pyproject.toml`, `radar/news_translation.py`, `radar/translation_prompt_pack.py`, `AGENTS.md`.

## 0960-1100) Daily Radar Operator Loop and Action Dispatch Readiness

- [F] Aggiunta review morning-use 0960 della dashboard V1. Fonte: `docs/reviews/0960_DASHBOARD_MORNING_USE_REVIEW.md`.
- [F] Aggiunto modello Action Inbox con scoring, routing, safety gate, trend e noise suppression. Fonte: `radar/action_inbox.py`, `tests/test_action_inbox.py`.
- [F] Aggiunto Action Center web `/actions` con filtri, card azione, decision buttons, prompt generation e backlog export. Fonte: `radar_web/app.py`, `radar_web/action_center.py`, `radar_web/templates/actions.html`, `radar_web/static/style.css`.
- [F] Aggiunto decision log append-only Bridge e prompt/backlog export Bridge-only. Fonte: `radar/action_inbox.py`, `radar_web/action_center.py`.
- [F] Aggiunto routing esplicito per `AI Release Radar` nei project profiles. Fonte: `config/projects/project_profiles.json`, `radar/project_profiles.py`.
- [F] Aggiunti runbook operator loop, closure pack e decisioni 1100. Fonte: `docs/runbooks/1090_DAILY_RADAR_OPERATOR_LOOP_RUNBOOK.md`, `docs/architecture/1100_OPERATOR_LOOP_CLOSURE_PACK.md`, `docs/decisions/1100_DECISIONS.md`.
- [F] Nessuna nuova dipendenza, nessun nuovo scheduler, nessuna email/notifica automatica, nessuna chiamata LLM automatica, nessuna auto-azione, nessun altro repository e nessun output runtime versionato introdotti. Fonte: `pyproject.toml`, `radar/action_inbox.py`, `radar_web/action_center.py`, `AGENTS.md`.

## 0860-0950) Local Web Dashboard Operator-Ready V1

- [F] Aggiunto smoke operator offline per home, health, status, runs, scheduler, dettaglio run e API detail. Fonte: `tests/test_radar_web_app.py`.
- [F] Migliorata la UI home con griglia piu' ampia, badge leggibili, wrapping controllato, date human-readable e booleani Yes/No. Fonte: `radar_web/templates/index.html`, `radar_web/static/style.css`, `radar_web/app.py`.
- [F] Migliorata la pagina dettaglio con sezioni collassabili, alert per warning/HOLD/blocked actions, path lunghi leggibili e prompt suggestions evidenti. Fonte: `radar_web/templates/run_detail.html`, `radar_web/static/style.css`.
- [F] Rafforzato il trigger manuale `daily-sim` con JSON safety esplicito, lock, timeout, automation gate, HAG status e conferme no scheduler/email/LLM/auto-action/other repo. Fonte: `radar_web/manual_trigger.py`, `tests/test_radar_web_app.py`.
- [F] Aggiunto data completeness gate per Bridge/runs root, runs_index e artifact mancanti. Fonte: `radar_web/app.py`, `radar_web/run_locator.py`, `radar_web/models.py`, `tests/test_radar_web_run_locator.py`.
- [F] Migliorata la scheduler card con interpretation `OK` per `Ready` + `LastTaskResult=0`. Fonte: `radar_web/scheduler_status.py`, `tests/test_radar_web_scheduler_status.py`.
- [F] Resi piu' evidenti HAG e prompt suggestions `SUGGESTED ONLY - not executed`. Fonte: `radar_web/templates/index.html`, `radar_web/templates/run_detail.html`, `radar_web/run_locator.py`.
- [F] Aggiunti runbook screenshot pack, troubleshooting e closure pack operator-ready V1. Fonte: `docs/runbooks/0930_OPERATOR_SCREENSHOT_PACK.md`, `docs/runbooks/0940_WEB_DASHBOARD_TROUBLESHOOTING.md`, `docs/architecture/0950_DASHBOARD_V1_OPERATOR_READY_CLOSURE_PACK.md`, `docs/decisions/0950_DECISIONS.md`.
- [F] Nessuna nuova dipendenza, nessun nuovo scheduler, nessuna email/notifica automatica, nessuna chiamata LLM automatica, nessuna auto-azione, nessun altro repository e nessun output runtime versionato introdotti. Fonte: `pyproject.toml`, `radar_web/`, `AGENTS.md`.

## 0760-0850) Local Web Dashboard

- [F] Aggiunta architettura dashboard locale e closure pack 0850. Fonte: `docs/architecture/0760_WEB_DASHBOARD_ARCHITECTURE.md`, `docs/architecture/0850_WEB_DASHBOARD_CLOSURE_PACK.md`.
- [F] Aggiunto package `radar_web` con Bridge run locator, backend FastAPI, scheduler card read-only e trigger manuale `daily-sim`. Fonte: `radar_web/`.
- [F] Aggiunte UI home e dettaglio run con template Jinja2 e CSS semplice. Fonte: `radar_web/templates/index.html`, `radar_web/templates/run_detail.html`, `radar_web/static/style.css`.
- [F] Aggiunto endpoint controllato `POST /api/daily-sim/run` con output root Bridge, lock e timeout. Fonte: `radar_web/manual_trigger.py`, `radar_web/app.py`.
- [F] Aggiunti test offline per locator, app, scheduler fallback e trigger manuale. Fonte: `tests/test_radar_web_run_locator.py`, `tests/test_radar_web_app.py`, `tests/test_radar_web_scheduler_status.py`.
- [F] Nessun nuovo scheduler, nessuna email/notifica automatica, nessuna chiamata LLM automatica, nessuna auto-azione, nessun altro repository e nessuna nuova dipendenza introdotti. Fonte: `radar_web/`, `pyproject.toml`.

## 0610-0750) Supervised Daily Intelligence Loop

- [F] Aggiunti protocollo di review del primo run schedulato e contratto `Radar fatto` per recupero Bridge. Fonte: `docs/architecture/0610_FIRST_SCHEDULED_RUN_REVIEW_PROTOCOL.md`, `docs/architecture/0620_RADAR_DONE_BRIDGE_RETRIEVAL_CONTRACT.md`.
- [F] Aggiunto daily quality gate v2 con dimensioni readability, source coverage e actionability. Fonte: `radar/daily_quality_gate.py`, `tests/test_daily_quality_gate.py`.
- [F] Aggiunti action triage, prompt suggestions `suggested_only`, profili progetto, HAG report e dashboard operatore. Fonte: `radar/action_triage.py`, `radar/prompt_suggestions.py`, `radar/project_profiles.py`, `radar/hag_report.py`, `radar/operator_dashboard.py`.
- [F] Esteso `daily-sim` con output runtime Bridge per quality gate v2, triage, prompt suggestions, HAG, dashboard e supervised loop dry run. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] Esteso confronto multi-day per item ripetuti, stale actions e warning fonte persistenti. Fonte: `radar/run_comparison.py`, `tests/test_run_comparison.py`.
- [F] Documentati failure recovery, noise reduction, governance V1.5 e closure pack. Fonte: `docs/architecture/0700_NOISE_REDUCTION_AND_DEDUPLICATION.md`, `docs/architecture/0720_FAILURE_RECOVERY_DRILL.md`, `docs/reviews/0740_V1_5_GOVERNANCE_AND_RISK_REVIEW.md`, `docs/architecture/0750_SUPERVISED_DAILY_INTELLIGENCE_CLOSURE_PACK.md`.
- [F] Nessuna auto-azione, nessuna email/notifica automatica, nessuna chiamata LLM automatica, nessun nuovo scheduler e nessuna modifica ad altri repository introdotta. Fonte: `radar/cli.py`, `docs/reviews/0740_V1_5_GOVERNANCE_AND_RISK_REVIEW.md`.

## 0510-0600) Scheduler Dry-Report Controlled Activation

- [F] Registrato consenso L3 esplicito per scheduler dry-report controllato. Fonte: `docs/decisions/0510_L3_SCHEDULER_DRY_REPORT_CONSENT.md`.
- [F] Lo scope autorizzato resta limitato a output Bridge, nessuna auto-azione, nessuna email/notifica automatica, nessuna chiamata LLM automatica, nessun deploy e nessuna modifica ad altri repository. Fonte: `docs/decisions/0510_L3_SCHEDULER_DRY_REPORT_CONSENT.md`.
- [F] Aggiunto command pack PowerShell schedulabile con log e lock nel Bridge. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`, `docs/architecture/0520_SCHEDULER_COMMAND_PACK.md`.
- [F] Creato task Windows `AIReleaseRadar_DailyDryReport`, daily alle 07:15, dry-report only. Fonte: `docs/architecture/0540_WINDOWS_TASK_CREATION.md`.
- [F] Verificato primo trigger manuale con output Bridge, gate report e `LastTaskResult=0`. Fonte: `docs/architecture/0550_FIRST_SCHEDULED_TASK_TRIGGER.md`, `docs/architecture/0560_SCHEDULED_RUN_OUTPUT_VERIFICATION.md`.
- [F] Documentati rollback, lock handling, retention senza cancellazione automatica e review flow operatore. Fonte: `docs/architecture/0530_SCHEDULER_SAFETY_AND_ROLLBACK.md`, `docs/architecture/0570_SCHEDULER_FAILURE_HANDLING_AND_LOCKING.md`, `docs/architecture/0580_SCHEDULER_RUN_INDEX_AND_RETENTION.md`, `docs/runbooks/0590_OPERATOR_REVIEW_FLOW.md`.
- [F] Lo scheduler operativo pieno resta non autorizzato. Fonte: `docs/decisions/0510_L3_SCHEDULER_DRY_REPORT_CONSENT.md`, `docs/reviews/0490_FINAL_SCHEDULER_READINESS_REVIEW.md`.

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
