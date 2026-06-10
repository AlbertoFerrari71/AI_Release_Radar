# 0560) Scheduled Run Output Verification

## A. Scopo

- [F] Lo step 0560 richiede verifica dell'output prodotto dal task schedulato. Fonte: prompt `0510-0600` salvato nel Bridge.
- [F] Il report operativo di verifica e' stato scritto nel Bridge: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\codex_command\0560-Scheduled_Run_Verification.md`. Fonte: esecuzione locale del 2026-06-10.

## B. Run Verificato

- [F] Run Bridge verificata: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs\0320_0400_daily_sim_20260610_170102`. Fonte: Bridge.
- [F] Log scheduler verificato: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\scheduler_logs\scheduler_dry_report_20260610_170102.log`. Fonte: Bridge.
- [F] Il task ha chiuso con `LastTaskResult=0`. Fonte: `Get-ScheduledTaskInfo` del 2026-06-10.

## C. File Obbligatori

- [F] `0180-Run_Summary.json` presente. Fonte: run Bridge `0320_0400_daily_sim_20260610_170102`.
- [F] `0350-Daily_Sim_Gate.md` presente. Fonte: run Bridge `0320_0400_daily_sim_20260610_170102`.
- [F] `0350-Daily_Sim_Summary.json` presente. Fonte: run Bridge `0320_0400_daily_sim_20260610_170102`.
- [F] `runs_index.jsonl` presente. Fonte: run Bridge `0320_0400_daily_sim_20260610_170102`.
- [F] Log scheduler datato presente. Fonte: `scheduler_dry_report_20260610_170102.log`.

## D. Metriche Verificate

- [F] Status: `CHANGES_FOUND`. Fonte: `0350-Daily_Sim_Summary.json`.
- [F] Source count: `11`. Fonte: `0350-Daily_Sim_Summary.json`.
- [F] Parsed count: `1`. Fonte: `0350-Daily_Sim_Summary.json`.
- [F] Item count: `10`. Fonte: `0350-Daily_Sim_Summary.json`.
- [F] Automation gate status: `ACTION_REVIEW_REQUIRED`. Fonte: `0350-Daily_Sim_Summary.json`.
- [F] Scheduler readiness: `HOLD`. Fonte: `0350-Daily_Sim_Summary.json`.
- [F] Manual review queue count: `11`. Fonte: `0350-Daily_Sim_Summary.json`.

## E. Guardrail Verificati

- [F] Output path fuori repository: `true`. Fonte: report Bridge `0560-Scheduled_Run_Verification.md`.
- [F] No auto-action: `true`. Fonte: log scheduler `scheduler_dry_report_20260610_170102.log`.
- [F] No LLM: `true`. Fonte: `0350-Daily_Sim_Summary.json` e log scheduler.
- [F] No email: `true`. Fonte: log scheduler `scheduler_dry_report_20260610_170102.log`.

## F. Esito

- [F] Verification status: `PASS`. Fonte: report Bridge `0560-Scheduled_Run_Verification.md`.
- [INT] Il task e' valido solo come dry-report: `ACTION_REVIEW_REQUIRED` e `HOLD` mantengono il gate umano obbligatorio.
