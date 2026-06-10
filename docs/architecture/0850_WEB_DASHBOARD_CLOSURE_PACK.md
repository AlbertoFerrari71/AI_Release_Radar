# 0850) Web Dashboard Closure Pack

## A. Cosa Aggiunge

- [F] Aggiunto package `radar_web` per dashboard locale FastAPI. Fonte: `radar_web/app.py`.
- [F] Aggiunti lettori Bridge read-only per run `0320_0400_daily_sim_*`, summary, gate, HAG, dashboard operatore e prompt suggestions. Fonte: `radar_web/bridge_reader.py`, `radar_web/run_locator.py`.
- [F] Aggiunta UI HTML/CSS/Jinja2 semplice per home e dettaglio run. Fonte: `radar_web/templates/index.html`, `radar_web/templates/run_detail.html`, `radar_web/static/style.css`.
- [F] Aggiunta card scheduler read-only via PowerShell su Windows con fallback `NO_DATA`. Fonte: `radar_web/scheduler_status.py`.
- [F] Aggiunto trigger manuale controllato per `daily-sim`. Fonte: `radar_web/manual_trigger.py`, `radar_web/app.py`.
- [F] Aggiunti test offline per locator, app, scheduler fallback e trigger manuale. Fonte: `tests/test_radar_web_run_locator.py`, `tests/test_radar_web_app.py`, `tests/test_radar_web_scheduler_status.py`.

## B. Backend

- [F] Il backend espone `GET /`, `GET /health`, `GET /api/status`, `GET /api/runs`, `GET /api/runs/{run_id}`, `GET /api/runs/{run_id}/compact`, `GET /api/runs/{run_id}/gate`, `GET /api/runs/{run_id}/hag`, `GET /api/runs/{run_id}/dashboard`, `GET /api/scheduler`, `GET /runs/{run_id}` e `POST /api/daily-sim/run`. Fonte: `radar_web/app.py`.
- [F] Host e porta default sono `127.0.0.1:8787`. Fonte: `radar_web/config.py`, `radar_web/app.py`.
- [F] Il Bridge root default e' `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar`. Fonte: `radar_web/config.py`, `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.

## C. Frontend

- [F] La home mostra ultimo run, status, automation gate, daily quality gate, scheduler readiness, source coverage, actions summary, manual review queue, prompt suggestions, HAG e scheduler status. Fonte: `radar_web/templates/index.html`.
- [F] La pagina dettaglio mostra report compact, gate markdown, HAG report, operator dashboard, source diagnostics summary, direct actions, blocked actions, monitor-only summary, manual review queue, prompt suggestions e path locali come testo. Fonte: `radar_web/templates/run_detail.html`.

## D. Trigger Manuale

- [F] Il trigger manuale usa solo `python -m radar.cli daily-sim --output-root "<Bridge runs root>"`. Fonte: `radar_web/manual_trigger.py`.
- [F] Il trigger valida che l'output root non sia dentro il repository e non contenga path part `LAST-*` o `latest-*`. Fonte: `radar_web/config.py`, `radar_web/manual_trigger.py`.
- [F] Il trigger usa lock in memoria e timeout. Fonte: `radar_web/manual_trigger.py`.
- [F] Il trigger non chiama scheduler, email, LLM, auto-azioni o altri repository. Fonte: `radar_web/manual_trigger.py`.

## E. Scheduler Card

- [F] La lettura scheduler usa `Get-ScheduledTask` e `Get-ScheduledTaskInfo` solo in lettura. Fonte: `radar_web/scheduler_status.py`.
- [F] Se non e' Windows, PowerShell manca, il task manca o il comando fallisce, la dashboard restituisce `NO_DATA` senza bloccare la UI. Fonte: `radar_web/scheduler_status.py`.

## F. Limiti Residui

- [F] La dashboard V1 e' locale e senza autenticazione. Fonte: prompt `0760-0850`, `radar_web/app.py`.
- [F] Il lock del trigger manuale e' in memoria del processo web; non coordina processi dashboard multipli. Fonte: `radar_web/manual_trigger.py`.
- [F] Il trigger manuale puo' eseguire il fetch live previsto da `daily-sim`; resta L2 e richiede review manuale della PR. Fonte: prompt `0760-0850`, `radar/cli.py`.

## G. Readiness

- [INT] La milestone `0850) AI Release Radar Local Web Dashboard` e' pronta per review manuale via draft PR se test e diff-check finali passano. Base: file e test citati in questo closure pack.
- [PROP] Prossimo step consigliato: `0860) First Local Dashboard Operator Smoke`, con avvio locale, lettura ultimo Bridge run e trigger manuale controllato solo se Alberto lo autorizza.
