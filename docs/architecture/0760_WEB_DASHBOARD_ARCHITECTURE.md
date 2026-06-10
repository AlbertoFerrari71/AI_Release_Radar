# 0760) Web Dashboard Architecture

## A. Obiettivo

- [F] La dashboard locale serve a leggere rapidamente l'ultimo run Bridge e i suoi output giornalieri supervisionati. Fonte: prompt `0760-0850` fornito da Alberto il 2026-06-10.
- [F] La dashboard deve esporre ultimo run, gate, scheduler, azioni, Human Approval Gate e prompt suggestions. Fonte: prompt `0760-0850`.
- [F] La dashboard non sostituisce la review umana. Fonte: `AGENTS.md`, `docs/architecture/0750_SUPERVISED_DAILY_INTELLIGENCE_CLOSURE_PACK.md`.

## B. Modalita Locale

- [F] Il backend locale usa host default `127.0.0.1` e porta default `8787`. Fonte: prompt `0760-0850`.
- [F] L'URL operativo previsto e' `http://127.0.0.1:8787`. Fonte: prompt `0760-0850`.
- [F] La prima versione non introduce autenticazione perche' resta locale su PC. Fonte: prompt `0760-0850`.

## C. Read-Only Di Default

- [F] La dashboard legge output runtime dal Bridge senza modificarli. Fonte: prompt `0760-0850`.
- [F] La dashboard non scrive output runtime nel repository. Fonte: `AGENTS.md`, prompt `0760-0850`.
- [F] La dashboard non usa file `LAST-*` o `latest-*`. Fonte: `AGENTS.md`, prompt `0760-0850`.

## D. Unica Azione Ammessa

- [F] L'unica azione ammessa e' il trigger manuale controllato di `daily-sim`. Fonte: prompt `0760-0850`.
- [F] Il comando ammesso e' `python -m radar.cli daily-sim --output-root "<Bridge runs root>"`. Fonte: prompt `0760-0850`, `radar/cli.py`.
- [F] L'output del trigger manuale deve restare nel Bridge runs root, fuori repository. Fonte: prompt `0760-0850`, `radar/cli.py`.
- [F] Il trigger manuale deve avere lock e timeout per evitare doppie esecuzioni o run appesi. Fonte: prompt `0760-0850`.

## E. Cosa Non Fa

- [F] Non crea nuovi scheduler o task Windows. Fonte: prompt `0760-0850`.
- [F] Non modifica lo scheduler esistente salvo lettura dello stato. Fonte: prompt `0760-0850`.
- [F] Non esegue auto-azioni. Fonte: `AGENTS.md`, `docs/reviews/0740_V1_5_GOVERNANCE_AND_RISK_REVIEW.md`.
- [F] Non invia email o notifiche automatiche. Fonte: `AGENTS.md`, prompt `0760-0850`.
- [F] Non chiama LLM automaticamente. Fonte: `AGENTS.md`, prompt `0760-0850`.
- [F] Non modifica altri repository. Fonte: `AGENTS.md`, prompt `0760-0850`.
- [F] Non esegue prompt suggestions; le mostra come `suggested_only`. Fonte: `radar/prompt_suggestions.py`.

## F. Fonti Dati Bridge

- [F] La dashboard legge i run da `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] I log scheduler sono in `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\scheduler_logs`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] I run giornalieri usano directory `0320_0400_daily_sim_<stamp>`. Fonte: `radar/cli.py`, `docs/architecture/0580_SCHEDULER_RUN_INDEX_AND_RETENTION.md`.
- [F] Output letti dalla dashboard:
  - `0180-Report_Compact.md`;
  - `0180-Run_Summary.json`;
  - `0350-Daily_Sim_Gate.md`;
  - `0350-Daily_Sim_Gate.json`;
  - `0350-Daily_Sim_Summary.json`;
  - `0630-Daily_Quality_Gate_V2.md`;
  - `0630-Daily_Quality_Gate_V2.json`;
  - `0650-Action_Triage.json`;
  - `0660-Codex_Prompt_Suggestions.json`;
  - `0660-Codex_Prompt_Suggestions.md`;
  - `0680-Human_Approval_Gate_Report.md`;
  - `0710-Daily_Operator_Dashboard.md`;
  - `0730-Supervised_Action_Loop_Dry_Run.md`;
  - `runs_index.jsonl`.
  Fonte: `radar/cli.py`, prompt `0760-0850`.

## G. Endpoint Backend Previsti

- [F] `GET /` rende la dashboard HTML. Fonte: prompt `0760-0850`.
- [F] `GET /health` rende health locale. Fonte: prompt `0760-0850`.
- [F] `GET /api/status` rende stato sintetico dashboard. Fonte: prompt `0760-0850`.
- [F] `GET /api/runs` lista i run recenti. Fonte: prompt `0760-0850`.
- [F] `GET /api/runs/{run_id}` rende dettaglio JSON di un run. Fonte: prompt `0760-0850`.
- [F] `GET /api/runs/{run_id}/compact` rende il compact report. Fonte: prompt `0760-0850`.
- [F] `GET /api/runs/{run_id}/gate` rende gate automation e daily quality. Fonte: prompt `0760-0850`.
- [F] `GET /api/runs/{run_id}/hag` rende HAG report e prompt suggestions. Fonte: prompt `0760-0850`.
- [F] `GET /api/runs/{run_id}/dashboard` rende dashboard operatore e supervised dry-run. Fonte: prompt `0760-0850`.
- [F] `GET /api/scheduler` legge lo stato del task Windows senza modificarlo. Fonte: prompt `0760-0850`.
- [F] `POST /api/daily-sim/run` avvia solo il trigger manuale controllato. Fonte: prompt `0760-0850`.
- [F] `GET /runs/{run_id}` rende il dettaglio HTML. Fonte: prompt `0760-0850`.

## H. UI Prevista

- [F] La UI e' HTML/CSS/Jinja2 semplice. Fonte: prompt `0760-0850`.
- [F] La home mostra ultimo run, status, automation gate, daily quality gate, scheduler readiness, source coverage, actions summary, manual review queue, prompt suggestions e scheduler status. Fonte: prompt `0760-0850`.
- [F] La pagina dettaglio mostra report compact, gate markdown, HAG report, operator dashboard, source diagnostics, direct actions, monitor-only summary, manual review queue e prompt suggestions. Fonte: prompt `0760-0850`.
- [F] I link ai file locali sono mostrati come path testuali, senza apertura automatica. Fonte: prompt `0760-0850`.

## I. Rischi E Mitigazioni

- [F] Rischio: doppio click sul trigger manuale. Mitigazione: lock in memoria lato backend. Fonte: prompt `0760-0850`.
- [F] Rischio: run appeso. Mitigazione: timeout subprocess. Fonte: prompt `0760-0850`.
- [F] Rischio: output dentro repo. Mitigazione: validazione Bridge runs root fuori repository prima del subprocess. Fonte: `radar/cli.py`, prompt `0760-0850`.
- [F] Rischio: confusione tra suggerimento e azione. Mitigazione: UI e report indicano `suggested_only` e `no auto-action`. Fonte: `radar/prompt_suggestions.py`, prompt `0760-0850`.
- [F] Rischio: scheduler non disponibile o ambiente non Windows. Mitigazione: card `NO_DATA` senza fallimento dashboard. Fonte: prompt `0760-0850`.
- [F] Rischio: file Bridge mancanti. Mitigazione: warning espliciti e stato `NO_DATA` dove applicabile. Fonte: prompt `0760-0850`.
