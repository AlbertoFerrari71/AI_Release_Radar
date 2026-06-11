# 0570) Scheduler Failure Handling and Locking

## A. Scopo

- [F] Lo step 0570 richiede strategia per doppie esecuzioni, errori controllati, timeout, log nel Bridge ed exit code coerenti. Fonte: prompt `0510-0600` salvato nel Bridge.
- [F] La strategia e' implementata nello script `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`. Fonte: file versionato.

## B. Runtime Lock

- [F] Lock path: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\scheduler_locks\AIReleaseRadar_DailyDryReport.lock.json`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Il lock contiene `task_name`, `run_id`, `started_at_utc`, `repo_root`, `runs_root`, `log_path`, `stdout_path` e `stderr_path`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Soglia stale lock: 150 minuti. Fonte: `$StaleLockMinutes = 150` nello script.
- [F] Se il lock esiste ed e' entro soglia stale, lo script registra `ACTIVE_LOCK_DETECTED` ed esce con exit code `2`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Se il lock e' oltre soglia stale, lo script registra `STALE_LOCK_DETECTED`, archivia contenuto/path con nome datato e procede. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Per lock legacy senza `run_id`, lo script puo' registrare `STALE_LOCK_DETECTED reason=legacy_lock_without_owner` se il task non e' `Running` e non trova altri processi dello script scheduler. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Se il lock non e' JSON valido o non ha `started_at_utc` valido, lo script registra `CORRUPT_LOCK_DETECTED`, archivia contenuto/path con nome datato e procede. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] A fine esecuzione normale o errore gestito, il blocco `finally` rimuove solo il lock con `run_id` della run corrente. Fonte: `Test-CurrentRunOwnsLock` nello script.

## C. Log Failure Handling

- [F] I log scheduler sono scritti nel Bridge in `scheduler_logs`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] I nomi log sono datati e non usano `LAST-*` o `latest-*`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Lo script cattura stdout e stderr del comando in file separati datati e mantiene anche un command output combinato. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Il log include cwd iniziale, cwd dopo `Set-Location`, versione PowerShell, python path, python version, path lock/output, stato lock, command start/end, exit code comando, durata, rimozione lock e exit code script. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] La scrittura log usa append con retry/backoff su `System.IO.IOException`. Fonte: `Write-LogLine` nello script.
- [INT] Il retry/backoff evita che un lock transitorio del file log da sync o antivirus faccia fallire la run senza motivo operativo.

## D. Exit Code

- [F] Exit code `0`: `daily-sim` completato senza errore processo. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Exit code `1`: errore script o errore propagato da `daily-sim`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Exit code `2`: lock attivo entro soglia stale o lock creato in parallelo da un'altra run. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [INT] Exit code `0` non equivale ad approvazione automatica: il gate resta l'autorita' su `ACTION_REVIEW_REQUIRED`, `FAIL` o warning.

## E. Timeout Task

- [F] Il task creato nello step 0540 usa execution time limit di 120 minuti. Fonte: `docs/architecture/0540_WINDOWS_TASK_CREATION.md`.
- [F] La policy task usa `MultipleInstances IgnoreNew`. Fonte: `docs/architecture/0540_WINDOWS_TASK_CREATION.md`.
- [INT] Il task scheduler e il runtime lock coprono due livelli: Windows evita nuove istanze parallele mentre una e' Running, lo script evita collisioni anche se il task viene lanciato manualmente fuori scheduler.

## F. Test Offline Lock

- [F] Test lock sintetico eseguito il 2026-06-10. Fonte: esecuzione locale controllata.
- [F] Lock sintetico creato nel Bridge con `started_at_utc` corrente. Fonte: esecuzione locale controllata.
- [F] Script eseguito con lock attivo. Fonte: esecuzione locale controllata.
- [F] Exit code atteso: `2`. Exit code ottenuto: `2`. Fonte: log Bridge `scheduler_dry_report_20260610_170422.log`.
- [F] Il log contiene `error=lock_present` ed `exit_code=2`. Fonte: log Bridge `scheduler_dry_report_20260610_170422.log`.
- [F] Il lock sintetico e' stato rimosso dopo il test per non bloccare il task reale. Fonte: esecuzione locale controllata.

## G. Limiti

- [F] Nessun cleanup distruttivo degli output run e' implementato nello script. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Nessuna notifica email o esterna e' implementata. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Nessuna chiamata LLM e' implementata. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
