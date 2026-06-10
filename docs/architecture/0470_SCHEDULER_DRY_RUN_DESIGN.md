# 0470) Scheduler Dry-Run Design

## A. Scopo

- [F] Lo step 0410-0500 richiede design scheduler senza attivazione reale. Fonte: prompt `0410-0500` salvato nel Bridge.
- [F] Il repository vieta scheduler/task Windows senza istruzione esplicita. Fonte: `AGENTS.md`.
- [F] `daily-sim` e' il comando corrente per simulazione controllata senza scheduler. Fonte: `radar/cli.py`.
- [INT] Questo documento e' un design futuro per uno step L3 dedicato, non una procedura da eseguire ora. Base: `AGENTS.md`.

## B. Task Windows Futuro

- [PROP] Nome task futuro: `AI Release Radar Daily Sim Dry Report`.
- [PROP] Tipo task futuro: Windows Task Scheduler, utente Alberto, esecuzione giornaliera in una finestra oraria da approvare.
- [PROP] Working directory futura: `C:\Users\alberto.ferrari\source\repos\AI_Release_Radar`.
- [PROP] Il task futuro dovra' chiamare solo `daily-sim`; non dovra' eseguire azioni sui progetti, inviare email o chiamare LLM.
- [F] Nessun task viene creato nello step 0470. Fonte: questo documento.

## C. Comando Futuro Proposto

Solo documentale, da non eseguire come scheduler in questo step:

```powershell
Set-Location "C:\Users\alberto.ferrari\source\repos\AI_Release_Radar"
python -m radar.cli daily-sim --output-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs"
```

- [F] `daily-sim --output-root` richiede output root fuori repository. Fonte: `radar/cli.py`.
- [F] `daily-sim` non crea scheduler, task Windows o chiamate LLM. Fonte: `radar/cli.py`.

## D. Output E Logging

- [PROP] Output runtime futuro: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs\0320_0400_daily_sim_YYYYMMDD_HHMMSS`.
- [F] La directory runtime e' datata e non usa `LAST-*` o `latest-*`. Fonte: `radar/cli.py`, `AGENTS.md`.
- [PROP] Log task futuro: usare il log nativo di Windows Task Scheduler piu' i file `0350-Daily_Sim_Gate.md`, `0350-Daily_Sim_Gate.json` e `0350-Daily_Sim_Summary.json`.
- [PROP] Non aggiungere email automatica nel primo step scheduler; rendere visibile l'esito tramite Bridge e controllo manuale.

## E. Doppie Esecuzioni

- [PROP] Il task futuro deve impostare `Do not start a new instance` se una precedente esecuzione e' ancora attiva.
- [PROP] Un eventuale lock file futuro deve stare fuori repository, nella root Bridge runtime, e deve essere datato o contenere PID/timestamp.
- [PROP] Se il lock risulta stale, la procedura di recupero deve essere manuale e documentata nel runbook dello step L3.

## F. Exit Code

- [F] La CLI `daily-sim` ritorna exit code 1 solo se `automation_gate_status` e' `FAIL`. Fonte: `radar/cli.py`.
- [F] `ACTION_REVIEW_REQUIRED` e `PASS_WITH_WARNINGS` non sono errori processo. Fonte: `radar/cli.py`.
- [PROP] Il task futuro deve registrare come failed solo exit code non zero, ma l'operatore deve leggere comunque `automation_gate_status` e `scheduler_readiness_recommendation`.
- [PROP] Se `automation_gate_status=ACTION_REVIEW_REQUIRED`, nessuna azione automatica deve partire; Alberto deve leggere la manual review queue.

## G. Disable/Restore Plan

- [PROP] Lo step L3 futuro deve documentare prima dell'attivazione:
  - comando o UI path per disabilitare il task;
  - come verificare che il task sia disabilitato;
  - come eliminare il task se serve rollback;
  - come fare una run manuale sostitutiva con `daily-sim`.
- [F] Nessun comando di disable/enable viene eseguito nello step 0470. Fonte: questo documento.

## H. Criteri Di Non Attivazione

- [F] Coverage bassa produce warning e puo' portare `scheduler_readiness_recommendation=HOLD`. Fonte: `radar/automation_gate.py`.
- [F] Manual review queue non vuota indica lavoro umano da leggere. Fonte: `radar/manual_review_queue.py`.
- [INT] Se `parsed_count` resta 1/11, lo scheduler futuro deve essere limitato a dry/report supervisionato, non operativo pieno. Base: `docs/architecture/0460_SCHEDULER_READINESS_CHECKLIST.md`.

## I. Esito

- [F] Design scheduler dry-run prodotto senza attivazione. Fonte: questo documento.
- [PROP] Prossimo step scheduler, se autorizzato, deve essere L3 e deve fermarsi a task dry/report disabilitabile, con review manuale obbligatoria.
