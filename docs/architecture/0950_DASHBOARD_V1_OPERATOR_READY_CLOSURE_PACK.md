# 0950) Dashboard V1 Operator-Ready Closure Pack

## A. Cosa Fa La Dashboard

- [F] La dashboard locale si avvia con `python -m radar_web.app --host 127.0.0.1 --port 8787`. Fonte: `radar_web/app.py`.
- [F] La home mostra latest run, status, automation gate, daily quality gate, scheduler readiness, source coverage, data completeness, actions, HAG, prompt suggestions, scheduler e recent runs. Fonte: `radar_web/templates/index.html`.
- [F] Il dettaglio run mostra run id, Bridge path, report compact, gate markdown, HAG report, operator dashboard, source diagnostics summary, direct actions, blocked actions, monitor-only summary, manual review queue, prompt suggestions e path locali. Fonte: `radar_web/templates/run_detail.html`.
- [F] La dashboard espone endpoint JSON read-only per status, runs, scheduler, run detail, compact report, gate, HAG e operator dashboard. Fonte: `radar_web/app.py`.
- [F] La dashboard puo' lanciare manualmente `daily-sim` solo tramite `POST /api/daily-sim/run`. Fonte: `radar_web/app.py`, `radar_web/manual_trigger.py`.

## B. Cosa Non Fa

- [F] Non fa push diretto su `main`, merge, deploy, tag o release. Fonte: `AGENTS.md`.
- [F] Non crea nuovi scheduler e non modifica il task Windows esistente. Fonte: `radar_web/scheduler_status.py`.
- [F] Non invia email o notifiche automatiche. Fonte: `radar_web/manual_trigger.py`.
- [F] Non chiama LLM automaticamente. Fonte: `radar_web/manual_trigger.py`.
- [F] Non esegue prompt suggestions; sono marcati `SUGGESTED ONLY - not executed`. Fonte: `radar_web/templates/index.html`, `radar_web/templates/run_detail.html`.
- [F] Non modifica altri repository. Fonte: `radar_web/manual_trigger.py`, `AGENTS.md`.
- [F] Non salva output runtime nel repository. Fonte: `radar_web/config.py`, `AGENTS.md`.

## C. UX Operator-Ready

- [F] I badge hanno wrapping controllato e min-width piu' leggibile. Fonte: `radar_web/static/style.css`.
- [F] La griglia dashboard usa max-width piu' generoso e layout responsive. Fonte: `radar_web/static/style.css`.
- [F] Le date ISO dello scheduler sono formattate come `dd/mm/yyyy HH:MM`. Fonte: `radar_web/app.py`, `radar_web/templates/index.html`.
- [F] I booleani rilevanti sono mostrati come `Yes`/`No`. Fonte: `radar_web/app.py`, `radar_web/templates/index.html`, `radar_web/templates/run_detail.html`.
- [F] La pagina dettaglio usa sezioni collassabili e alert per warning, HOLD e blocked actions. Fonte: `radar_web/templates/run_detail.html`, `radar_web/static/style.css`.

## D. Data Completeness

- [F] La dashboard segnala `bridge_root_missing`, `runs_root_missing`, warning `runs_index` e artifact run mancanti senza crashare. Fonte: `radar_web/app.py`, `radar_web/run_locator.py`, `radar_web/bridge_reader.py`.
- [F] `data_completeness_status` e `data_completeness_warnings` sono esposti in `/api/status`. Fonte: `radar_web/models.py`, `radar_web/app.py`.
- [F] Fixture incomplete sono coperte da test offline. Fonte: `tests/test_radar_web_app.py`, `tests/test_radar_web_run_locator.py`.

## E. Scheduler Card

- [F] La scheduler card mostra task name, state, last run time, last task result, next run time, missed runs e interpretation. Fonte: `radar_web/templates/index.html`.
- [F] `Ready` con `LastTaskResult = 0` produce interpretation `OK`. Fonte: `radar_web/scheduler_status.py`, `tests/test_radar_web_scheduler_status.py`.
- [F] Su non-Windows, task assente o errore PowerShell, lo scheduler restituisce `NO_DATA` senza bloccare la dashboard. Fonte: `radar_web/scheduler_status.py`.

## F. Manual Trigger

- [F] Il trigger manuale usa solo `python -m radar.cli daily-sim --output-root "<Bridge runs root>"`. Fonte: `radar_web/manual_trigger.py`.
- [F] Il trigger valida output root fuori repo e path senza componenti vietati. Fonte: `radar_web/config.py`, `radar_web/manual_trigger.py`.
- [F] Il trigger usa lock anti doppio click e timeout. Fonte: `radar_web/manual_trigger.py`.
- [F] Il JSON del trigger include manual only, writes to Bridge, automation gate, HAG status, dashboard updated e conferme no scheduler/email/LLM/auto-action/other repo. Fonte: `radar_web/manual_trigger.py`.

## G. Come E' Stata Testata

- [F] Test mirati aggiunti/aggiornati per smoke endpoint, UI formatting, run detail UX, data completeness, scheduler interpretation, HAG/prompt suggestions e trigger manuale. Fonte: `tests/test_radar_web_app.py`, `tests/test_radar_web_run_locator.py`, `tests/test_radar_web_scheduler_status.py`.
- [F] Smoke backend locale eseguito su `127.0.0.1:8787` con `GET /`, `/health`, `/api/status`, `/api/runs`, `/api/scheduler`, `/runs/{run_id}` e le API detail. Fonte: Bridge smoke `0860-Smoke_Report.md`.
- [F] Screenshot prodotti con Edge headless gia' installato. Fonte: Bridge smoke `0860-Smoke_Report.md`.
- [F] Manual trigger testato via `POST /api/daily-sim/run`, endpoint usato dal bottone UI. Fonte: Bridge smoke `0890-Manual_Trigger_Response.json`.

## H. Screenshot Bridge Prodotti

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\web_smoke\0860_0950_20260610_214256
```

- [F] La cartella contiene screenshot home, dettaglio run e post-trigger. Fonte: Bridge smoke folder `0860_0950_20260610_214256`.
- [F] La cartella contiene HTML/API e `0860-Smoke_Report.md`. Fonte: Bridge smoke folder `0860_0950_20260610_214256`.

## I. Limiti Residui

- [F] Browser in-app non disponibile nello smoke per errore sandbox del runtime node_repl; e' stato usato fallback Edge headless e richieste HTTP locali. Fonte: Bridge smoke `0860-Smoke_Report.md`.
- [F] Click fisico del bottone non e' stato eseguito con automazione browser; e' stato testato l'endpoint backend invocato dal bottone. Fonte: Bridge smoke `0860-Smoke_Report.md`.
- [F] Il lock del trigger e' in memoria del processo web e non coordina piu' processi dashboard paralleli. Fonte: `radar_web/manual_trigger.py`.
- [F] La dashboard resta locale e senza autenticazione; non va esposta su rete pubblica. Fonte: `radar_web/app.py`, `radar_web/config.py`.

## J. Prossimo Step Consigliato

- [PROP] `0960) Dashboard V1 Manual Review and Morning-Use Feedback`: Alberto usa la dashboard in una sessione mattutina reale, annota frizioni residue e decide se procedere con piccoli polish V1.1 o con un gate di review del run schedulato.
