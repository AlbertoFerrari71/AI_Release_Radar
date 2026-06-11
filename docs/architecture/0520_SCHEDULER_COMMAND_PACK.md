# 0520) Scheduler Command Pack

## A. Scopo

- [F] Lo step 0520 richiede uno script PowerShell schedulabile per eseguire `daily-sim`. Fonte: prompt `0510-0600` salvato nel Bridge.
- [F] Lo script versionato e' `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`. Fonte: file versionato.
- [F] Il comando operativo eseguito dallo script e' `python -m radar.cli daily-sim --output-root <Bridge runs root>`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.

## B. Runtime Path

- [F] Repository root: `C:\Users\alberto.ferrari\source\repos\AI_Release_Radar`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Runs root: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Scheduler logs root: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\scheduler_logs`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Scheduler lock root: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\scheduler_locks`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Log, command output, stdout e stderr hanno nomi datati, non `LAST-*` o `latest-*`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.

## C. Guardrail Script

- [F] Lo script imposta `Set-StrictMode -Version Latest`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Lo script imposta `$ErrorActionPreference = "Stop"`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Lo script verifica che `runs_root` non sia dentro il repository. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Lo script verifica che root e file runtime scheduler non contengano path part `LAST-*` o `latest-*`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Lo script scrive log operativo nel Bridge. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Lo script usa un runtime lock in Bridge per ridurre il rischio di doppia esecuzione. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.

## D. Divieti Confermati

- [F] Lo script non contiene comandi `git commit`, `git push`, email, notifiche esterne o chiamate LLM. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Lo script non modifica altri repository. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Lo script non usa `setx`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Lo script non crea file `LAST-*` o `latest-*`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.

## E. Exit Code

- [F] Exit code 0 passa quando `daily-sim` non produce gate `FAIL`. Fonte: `radar/cli.py`, `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Exit code 1 segnala errore script o gate `FAIL` propagato da `daily-sim`. Fonte: `radar/cli.py`, `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Exit code 2 segnala lock attivo entro soglia stale o lock creato in parallelo da un'altra run. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [INT] `ACTION_REVIEW_REQUIRED` non e' errore processo, ma richiede review umana. Base: `radar/cli.py`, `docs/architecture/0430_COVERAGE_WARNING_POLICY.md`.

## F. Smoke Test Manuale

Comando manuale da eseguire prima della creazione task:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\alberto.ferrari\source\repos\AI_Release_Radar\scripts\scheduler\ai_release_radar_daily_dry_report.ps1"
```

- [F] Il test deve produrre output in Bridge e log datato in `scheduler_logs`. Fonte: prompt `0510-0600` salvato nel Bridge.
- [F] Il test non deve produrre output runtime nel repository. Fonte: `AGENTS.md`, `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.

## G. Esito

- [F] Command pack creato come script versionato e documentato. Fonte: questo documento e script versionato.
- [PROP] Usare questo script come unica action del Windows Scheduled Task `AIReleaseRadar_DailyDryReport`.
