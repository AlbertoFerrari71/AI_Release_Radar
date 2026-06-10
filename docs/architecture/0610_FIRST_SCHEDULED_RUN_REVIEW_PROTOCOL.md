# 0610) First Scheduled Run Review Protocol

## A. Scopo

- [F] Questo protocollo definisce la review del primo run schedulato reale dopo le 07:15. Fonte: prompt `0610-0750` fornito da Alberto il 2026-06-10.
- [F] Il task scheduler esistente si chiama `AIReleaseRadar_DailyDryReport` ed e' dry-report only. Fonte: `docs/architecture/0600_SCHEDULER_DRY_REPORT_CLOSURE_PACK.md`.
- [F] Il task scrive output runtime e log nel Bridge, non nel repository. Fonte: `docs/architecture/0600_SCHEDULER_DRY_REPORT_CLOSURE_PACK.md`, `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.

## B. Dove Cercare Il Run

- [F] Root run Bridge: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs`. Fonte: `docs/architecture/0600_SCHEDULER_DRY_REPORT_CLOSURE_PACK.md`.
- [F] Root log scheduler: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\scheduler_logs`. Fonte: `docs/architecture/0600_SCHEDULER_DRY_REPORT_CLOSURE_PACK.md`.
- [F] Le directory run `daily-sim` sono datate e iniziano con `0320_0400_daily_sim_`. Fonte: `radar/cli.py`.

## C. Uso Di `runs_index.jsonl`

1. [F] Aprire il `runs_index.jsonl` nella directory run candidata. Fonte: `radar/run_index.py`, `radar/real_run.py`.
2. [F] Leggere l'ultima riga valida append-only. Fonte: `radar/run_index.py`.
3. [F] Confrontare `run_id`, `status`, `source_count`, `parsed_count`, `item_count`, `failed_count`, `skipped_count`, `report_full`, `report_compact` e `snapshot_dir` con i file presenti. Fonte: `radar/models.py`, `radar/run_index.py`.
4. [F] Se `runs_index.jsonl` e' invalido, il gate deve fallire. Fonte: `radar/automation_gate.py`.

## D. File Obbligatori

- [F] `0180-Report_Compact.md`. Fonte: `radar/real_run.py`.
- [F] `0180-Report_Full.md`. Fonte: `radar/real_run.py`.
- [F] `0180-Run_Summary.json`. Fonte: `radar/real_run.py`.
- [F] `0350-Daily_Sim_Gate.md`. Fonte: `radar/cli.py`, `radar/automation_gate.py`.
- [F] `0350-Daily_Sim_Gate.json`. Fonte: `radar/cli.py`.
- [F] `0350-Daily_Sim_Summary.json`. Fonte: `radar/cli.py`.
- [F] `runs_index.jsonl`. Fonte: `radar/real_run.py`.
- [F] Dal 0710 il run produce anche `0710-Daily_Operator_Dashboard.md`. Fonte: `radar/cli.py`.

## E. Scheduler Info

- [F] Verificare `LastTaskResult`, `LastRunTime`, `NextRunTime` con `Get-ScheduledTaskInfo -TaskName "AIReleaseRadar_DailyDryReport"`. Fonte: prompt `0610-0750`.
- [F] `LastTaskResult=0` indica che lo script schedulato e' terminato con exit code 0, non che il radar autorizzi azioni automatiche. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`, `radar/automation_gate.py`.

## F. Classificazione Gate

- [F] `PASS`: nessun failure, warning o direct action nel gate. Fonte: `radar/automation_gate.py`.
- [F] `PASS_WITH_WARNINGS`: run completo con warning. Fonte: `radar/automation_gate.py`.
- [F] `ACTION_REVIEW_REQUIRED`: direct actions presenti; serve review manuale prima di qualunque azione. Fonte: `radar/automation_gate.py`.
- [F] `FAIL`: blocco strutturale, output mancante/corrotto, index invalido o metriche impossibili. Fonte: `radar/automation_gate.py`.

## G. Lettura Report

- [F] Nel compact report leggere status, scorecard, source count, parsed count, top items e top actions. Fonte: `radar/real_run.py`.
- [F] Nel full report leggere source diagnostics, observed items, project impacts, risks e report review scorecard. Fonte: `radar/real_run.py`.
- [INT] Il compact report serve per orientarsi; il full report serve per audit e spiegazione delle decisioni. Base: `radar/real_run.py`.

## H. Failure Path

- [F] Se il run manca, controllare scheduler log e `Get-ScheduledTaskInfo`. Fonte: `docs/runbooks/0590_OPERATOR_REVIEW_FLOW.md`.
- [F] Se il task non e' partito, controllare `NextRunTime`, `NumberOfMissedRuns`, action path e permessi. Fonte: `docs/runbooks/0590_OPERATOR_REVIEW_FLOW.md`.
- [F] Se `gate=ACTION_REVIEW_REQUIRED`, non eseguire azioni; leggere manual review queue, triage e HAG. Fonte: `radar/automation_gate.py`, `radar/action_triage.py`, `radar/hag_report.py`.
- [F] Se `gate=FAIL`, non usare il report per pianificare azioni; aprire fix mirato. Fonte: `docs/runbooks/0590_OPERATOR_REVIEW_FLOW.md`, `radar/automation_gate.py`.
