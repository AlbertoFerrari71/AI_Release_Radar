# 0530) Scheduler Safety and Rollback

## A. Scopo

- [F] Lo step 0530 richiede protezioni e rollback prima di qualunque attivazione scheduler dry-report. Fonte: prompt `0510-0600` salvato nel Bridge.
- [F] Il task autorizzato e' solo dry-report e non puo' eseguire auto-azioni. Fonte: prompt `0510-0600` salvato nel Bridge.
- [F] Lo script schedulabile e' `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`. Fonte: commit `0520`.

## B. Identita' Task

- [F] Nome task: `AIReleaseRadar_DailyDryReport`. Fonte: prompt `0510-0600` e `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Descrizione prevista: `AI Release Radar daily dry-report simulation; no auto-action.` Fonte: prompt `0510-0600`.
- [F] Schedule prevista: daily alle 07:15, ora locale Europe/Rome del sistema Windows. Fonte: prompt `0510-0600`.
- [F] Output runtime autorizzato: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs`. Fonte: prompt `0510-0600`.
- [F] Log scheduler autorizzati: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\scheduler_logs`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.

## C. Comando Task

Comando previsto:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\alberto.ferrari\source\repos\AI_Release_Radar\scripts\scheduler\ai_release_radar_daily_dry_report.ps1"
```

- [F] Lo script esegue `python -m radar.cli daily-sim --output-root <Bridge runs root>`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Lo script scrive log datati nel Bridge. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Lo script non contiene comandi per email, notifiche esterne, LLM, `git commit`, `git push` o `setx`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.

## D. Verifica Stato Task

Verifica esistenza:

```powershell
Get-ScheduledTask -TaskName "AIReleaseRadar_DailyDryReport" -ErrorAction SilentlyContinue
```

Verifica ultimo esito:

```powershell
Get-ScheduledTaskInfo -TaskName "AIReleaseRadar_DailyDryReport"
```

- [INT] `LastTaskResult = 0` indica esecuzione processo completata senza errore di processo. Non equivale ad approvazione automatica di azioni.
- [INT] Gate `ACTION_REVIEW_REQUIRED` significa che il processo ha prodotto report, ma Alberto deve fare review umana prima di qualunque azione.

## E. Rollback

Disabilitare temporaneamente:

```powershell
Disable-ScheduledTask -TaskName "AIReleaseRadar_DailyDryReport"
```

Eliminare il task:

```powershell
Unregister-ScheduledTask -TaskName "AIReleaseRadar_DailyDryReport" -Confirm:$false
```

- [F] Il prompt autorizza rollback/disable documentato. Fonte: prompt `0510-0600`.
- [F] Non eseguire `Unregister-ScheduledTask` salvo rollback necessario o richiesta esplicita. Fonte: prompt `0510-0600`.

## F. Lettura Output

Percorsi da controllare dopo una run:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs\<run>\0180-Run_Summary.json
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs\<run>\0350-Daily_Sim_Gate.md
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs\<run>\0350-Daily_Sim_Summary.json
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs\<run>\runs_index.jsonl
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\scheduler_logs\scheduler_dry_report_<stamp>.log
```

- [F] Gli output runtime devono restare fuori repository. Fonte: prompt `0510-0600`.
- [F] I nomi runtime devono essere datati e non usare `LAST-*` o `latest-*`. Fonte: prompt `0510-0600`.

## G. Gestione Gate

### Gate FAIL

- [F] Se il gate fallisce, non procedere con azioni automatiche. Fonte: prompt `0510-0600`.
- [PROP] Disabilitare il task, leggere log e run summary, poi aprire uno step Codex di fix mirato.

### Gate ACTION_REVIEW_REQUIRED

- [F] `ACTION_REVIEW_REQUIRED` richiede review umana prima di qualunque azione. Fonte: `docs/architecture/0430_COVERAGE_WARNING_POLICY.md`.
- [PROP] Alberto deve leggere compact report, gate report e manual review queue prima di trasformare eventuali direct action in prompt Codex.

### Nessun Output

- [PROP] Controllare `Get-ScheduledTaskInfo`, poi i log in `scheduler_logs`.
- [PROP] Se non esiste log datato per l'orario atteso, disabilitare il task e aprire step Codex di diagnosi.

## H. Blocco Temporaneo

Blocco consigliato:

```powershell
Disable-ScheduledTask -TaskName "AIReleaseRadar_DailyDryReport"
```

- [INT] La disabilitazione e' preferibile alla cancellazione se serve sospendere il dry-report senza perdere la configurazione task.
- [F] Nessuna azione automatica esterna e' autorizzata da questo task. Fonte: prompt `0510-0600`.
