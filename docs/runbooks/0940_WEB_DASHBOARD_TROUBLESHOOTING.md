# 0940) Web Dashboard Troubleshooting

## A. Avvio Dashboard

Da repository:

```powershell
Set-Location "C:\Users\alberto.ferrari\source\repos\AI_Release_Radar"
python -m radar_web.app --host 127.0.0.1 --port 8787
```

- [F] Il comando avvia la dashboard locale FastAPI. Fonte: `radar_web/app.py`.
- [F] La dashboard deve restare su `127.0.0.1`; non e' prevista esposizione pubblica. Fonte: `radar_web/config.py`, prompt `0860-0950`.

## B. URL Locale

```text
http://127.0.0.1:8787
```

- [F] `GET /` mostra la home operatore. Fonte: `radar_web/app.py`, `radar_web/templates/index.html`.
- [F] `GET /health` espone lo stato minimo del servizio locale. Fonte: `radar_web/app.py`.
- [F] `GET /api/status`, `GET /api/runs` e `GET /api/scheduler` espongono dati JSON read-only. Fonte: `radar_web/app.py`.

## C. Come Fermarla

Nel terminale dove gira il server:

```text
Ctrl+C
```

- [F] Il processo e' avviato da `python -m radar_web.app`. Fonte: `radar_web/app.py`.

## D. Come Leggere La Home

- [F] `latest run` apre il dettaglio del run Bridge piu' recente. Fonte: `radar_web/templates/index.html`, `radar_web/run_locator.py`.
- [F] `status`, `automation gate`, `daily quality gate`, `source coverage` e `data completeness` sono badge sintetici. Fonte: `radar_web/templates/index.html`, `radar_web/app.py`.
- [F] `Data Completeness Warnings` mostra file o radici mancanti senza far crashare la UI. Fonte: `radar_web/app.py`, `radar_web/run_locator.py`, `radar_web/bridge_reader.py`.
- [F] La card HAG mostra HAG status, blocked actions, prompt suggestions, `SUGGESTED ONLY - not executed` e no auto-action. Fonte: `radar_web/templates/index.html`.
- [F] La card scheduler mostra task name, state, last run time, last task result, next run time, missed runs e interpretation. Fonte: `radar_web/templates/index.html`, `radar_web/scheduler_status.py`.

## E. Come Leggere Il Dettaglio Run

- [F] URL dettaglio: `http://127.0.0.1:8787/runs/<run_id>`. Fonte: `radar_web/app.py`.
- [F] La pagina dettaglio mostra run id, Bridge path, report compact, gate markdown, HAG report, operator dashboard, source diagnostics summary, direct actions, monitor-only summary, manual review queue e prompt suggestions. Fonte: `radar_web/templates/run_detail.html`.
- [F] I path locali sono mostrati come testo e non aperti automaticamente. Fonte: `radar_web/templates/run_detail.html`.
- [F] Warning, HOLD e blocked actions sono evidenziati nella sezione `operator attention`. Fonte: `radar_web/templates/run_detail.html`.

## F. Uso Del Bottone Daily-Sim

- [F] Il bottone `Run daily-sim now` invoca `POST /api/daily-sim/run`. Fonte: `radar_web/templates/index.html`, `radar_web/app.py`.
- [F] Il backend esegue solo `python -m radar.cli daily-sim --output-root "<Bridge runs root>"`. Fonte: `radar_web/manual_trigger.py`.
- [F] Il trigger usa lock anti doppio click e timeout. Fonte: `radar_web/manual_trigger.py`.
- [F] Il JSON del trigger dichiara manual only, writes to Bridge, no auto-action, scheduler not triggered, email not sent e LLM not called. Fonte: `radar_web/manual_trigger.py`.

## G. Se Non Ci Sono Run

- [F] La home mostra `NO_DATA` invece di fallire. Fonte: `radar_web/app.py`, `radar_web/templates/index.html`.
- [F] Controllare che il Bridge root esista e che i run siano sotto `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs`. Fonte: `radar_web/config.py`.
- [PROP] Se serve un nuovo run, usare il bottone manuale oppure CLI `python -m radar.cli daily-sim --output-root "<Bridge-runs-fuori-repo>"` solo in modo consapevole.

## H. Se Scheduler Card E' NO_DATA

- [F] Su sistemi non Windows, la card restituisce `NO_DATA`. Fonte: `radar_web/scheduler_status.py`.
- [F] Se il task `AIReleaseRadar_DailyDryReport` non esiste o PowerShell non risponde, la card restituisce `NO_DATA` con warning. Fonte: `radar_web/scheduler_status.py`.
- [F] `LastTaskResult = 0` e state `Ready` producono interpretation `OK`. Fonte: `radar_web/scheduler_status.py`.

## I. Se Il Trigger Fallisce

- [F] `ALREADY_RUNNING` significa lock attivo per un run gia' in corso. Fonte: `radar_web/manual_trigger.py`.
- [F] `REFUSED` indica output root non valido, per esempio dentro repository o con componenti vietati. Fonte: `radar_web/config.py`, `radar_web/manual_trigger.py`.
- [F] `TIMEOUT` indica superamento del timeout configurato. Fonte: `radar_web/manual_trigger.py`.
- [F] `FAIL` indica errore del processo CLI `daily-sim`; leggere `return_code`, `stdout`, `stderr` e `warnings` nel JSON. Fonte: `radar_web/manual_trigger.py`.

## J. Se Bridge Non E' Accessibile

- [F] `bridge_root_missing` o `runs_root_missing` compaiono nei warning di completezza dati. Fonte: `radar_web/app.py`, `radar_web/run_locator.py`.
- [F] La dashboard non crea il Bridge root automaticamente. Fonte: `radar_web/app.py`, `radar_web/config.py`.
- [PROP] Verificare che Dropbox sia sincronizzato e che il path Bridge locale sia montato prima di rilanciare la dashboard.

## K. Cosa Non Fa La Dashboard

- [F] Non fa merge su `main`. Fonte: `AGENTS.md`.
- [F] Non crea nuovi scheduler e non modifica il task esistente. Fonte: `radar_web/scheduler_status.py`.
- [F] Non invia email o notifiche automatiche. Fonte: `radar_web/manual_trigger.py`.
- [F] Non chiama LLM automaticamente. Fonte: `radar_web/manual_trigger.py`.
- [F] Non esegue prompt suggestions; restano `suggested_only`. Fonte: `radar_web/templates/index.html`, `radar_web/templates/run_detail.html`.
- [F] Non modifica altri repository. Fonte: `radar_web/manual_trigger.py`, `AGENTS.md`.
- [F] Non salva output runtime nel repository. Fonte: `radar_web/config.py`, `AGENTS.md`.
