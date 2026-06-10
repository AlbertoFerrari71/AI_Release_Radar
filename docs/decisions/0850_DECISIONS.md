# 0850) Decisions

## A. Dashboard Locale

- [F] La dashboard V1 e' locale su `127.0.0.1:8787`. Fonte: prompt `0760-0850`, `radar_web/config.py`.
- [F] Non viene introdotta autenticazione nella prima versione locale. Fonte: prompt `0760-0850`.
- [INT] La mancanza di autenticazione e' accettabile solo per uso locale sul PC di Alberto; non e' una decisione valida per esposizione remota. Base: prompt `0760-0850`.

## B. Frontend Semplice

- [F] La UI usa HTML/CSS/Jinja2 senza framework pesanti. Fonte: prompt `0760-0850`, `radar_web/templates/index.html`, `radar_web/static/style.css`.
- [F] I path locali sono mostrati come testo e non aperti automaticamente. Fonte: prompt `0760-0850`, `radar_web/templates/run_detail.html`.

## C. Bridge Read-Only

- [F] La dashboard legge Bridge run directory e file esistenti senza modificarli. Fonte: `radar_web/bridge_reader.py`, `radar_web/run_locator.py`.
- [F] File mancanti producono warning, non fallimento della dashboard. Fonte: `radar_web/bridge_reader.py`.
- [F] Path con componenti `LAST-*` o `latest-*` vengono rifiutati o ignorati. Fonte: `radar_web/bridge_reader.py`, `radar_web/run_locator.py`, `radar_web/config.py`.

## D. Trigger Manuale Daily-Sim

- [F] L'unica azione ammessa dalla dashboard e' `POST /api/daily-sim/run`. Fonte: `radar_web/app.py`.
- [F] Il comando eseguito e' solo `python -m radar.cli daily-sim --output-root "<Bridge runs root>"`. Fonte: `radar_web/manual_trigger.py`.
- [F] Il trigger usa lock e timeout. Fonte: `radar_web/manual_trigger.py`.
- [F] Il trigger non crea scheduler, non invia email, non chiama LLM, non esegue auto-azioni e non modifica altri repository. Fonte: `radar_web/manual_trigger.py`.

## E. Scheduler

- [F] Lo scheduler esistente viene letto soltanto con `Get-ScheduledTask` e `Get-ScheduledTaskInfo`. Fonte: `radar_web/scheduler_status.py`.
- [F] Nessun nuovo task Windows viene creato. Fonte: `radar_web/scheduler_status.py`, `radar_web/app.py`.

## F. Merge

- [F] Lo step e' prudenzialmente L1/L2 e il prompt impone `NO AUTO-MERGE`. Fonte: prompt `0760-0850`.
- [PROP] MERGE_RECOMMENDATION: manual review required; non fare auto-merge.
