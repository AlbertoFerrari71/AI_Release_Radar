# 0540) Windows Task Creation - Dry Report Only

## A. Scopo

- [F] Lo step 0540 autorizza la creazione del primo Windows Scheduled Task reale solo per dry-report. Fonte: prompt `0510-0600` salvato nel Bridge.
- [F] Il task non e' scheduler operativo pieno e non puo' eseguire auto-azioni. Fonte: prompt `0510-0600`.
- [F] Rollback e safety pack sono documentati in `docs/architecture/0530_SCHEDULER_SAFETY_AND_ROLLBACK.md`. Fonte: file versionato.

## B. Condizioni Prima della Creazione

- [F] Test completi prima della creazione: `236 passed, 2 skipped`. Fonte: esecuzione `python -m pytest` del 2026-06-10.
- [F] `git --no-pager diff --check` prima della creazione: PASS. Fonte: esecuzione locale del 2026-06-10.
- [F] Working tree prima della creazione: pulito. Fonte: `git --no-pager status --short` del 2026-06-10.
- [F] Smoke test manuale dello script 0520: exit code 0. Fonte: esecuzione manuale `powershell.exe -NoProfile -ExecutionPolicy Bypass -File ...ai_release_radar_daily_dry_report.ps1` del 2026-06-10.
- [F] Smoke test manuale ha scritto output in Bridge. Fonte: run `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs\0320_0400_daily_sim_20260610_165531`.
- [F] Il task non esisteva prima della creazione. Fonte: `Get-ScheduledTask -TaskName "AIReleaseRadar_DailyDryReport" -ErrorAction SilentlyContinue` del 2026-06-10.

## C. Task Creato

- [F] Nome task: `AIReleaseRadar_DailyDryReport`. Fonte: `Get-ScheduledTask` del 2026-06-10.
- [F] Stato dopo creazione: `Ready`. Fonte: `Get-ScheduledTask` del 2026-06-10.
- [F] Action executable: `C:\windows\System32\WindowsPowerShell\v1.0\powershell.exe`. Fonte: `Get-ScheduledTask` del 2026-06-10.
- [F] Action arguments: `-NoProfile -ExecutionPolicy Bypass -File "C:\Users\alberto.ferrari\source\repos\AI_Release_Radar\scripts\scheduler\ai_release_radar_daily_dry_report.ps1"`. Fonte: `Get-ScheduledTask` del 2026-06-10.
- [F] Trigger: daily. Fonte: `New-ScheduledTaskTrigger -Daily -At 07:15` e `Get-ScheduledTask` del 2026-06-10.
- [F] Next run time iniziale: `2026-06-11 07:15:00` ora locale Windows. Fonte: `Get-ScheduledTaskInfo` del 2026-06-10.
- [F] Multiple instances policy: `IgnoreNew`. Fonte: comando `New-ScheduledTaskSettingsSet -MultipleInstances IgnoreNew`.
- [F] Execution time limit: 120 minuti. Fonte: comando `New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes 120)`.

## D. PowerShell Scelto

- [F] Il task usa Windows PowerShell (`powershell.exe`) invece di `pwsh`. Fonte: `Get-Command powershell.exe` e task action creata.
- [INT] Windows PowerShell e' la scelta piu' robusta per questo host perche' e' disponibile nel sistema senza assumere installazione di PowerShell 7.

## E. Scope Confermato

- [F] Output runtime: Bridge, non repository. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Log scheduler: Bridge, non repository. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Nessuna email, notifica esterna, chiamata LLM, commit o push Git. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Nessun file `LAST-*` o `latest-*` previsto. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.

## F. Rollback

Disabilitare:

```powershell
Disable-ScheduledTask -TaskName "AIReleaseRadar_DailyDryReport"
```

Eliminare:

```powershell
Unregister-ScheduledTask -TaskName "AIReleaseRadar_DailyDryReport" -Confirm:$false
```

- [F] I comandi rollback sono documentati nello step 0530. Fonte: `docs/architecture/0530_SCHEDULER_SAFETY_AND_ROLLBACK.md`.
