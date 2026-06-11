# 0950) Decisions

## A. Dashboard Operator-Ready Locale

- [F] La dashboard V1 operator-ready resta locale su `127.0.0.1:8787`. Fonte: `radar_web/config.py`, prompt `0860-0950`.
- [F] Non viene introdotta autenticazione o esposizione remota. Fonte: `radar_web/app.py`, prompt `0860-0950`.
- [INT] La mancanza di autenticazione resta accettabile solo per uso locale sul PC di Alberto. Base: `docs/decisions/0850_DECISIONS.md`, prompt `0860-0950`.

## B. UI Semplice

- [F] Il polish usa HTML/CSS/Jinja2 esistenti e non introduce framework pesanti. Fonte: `radar_web/templates/index.html`, `radar_web/templates/run_detail.html`, `radar_web/static/style.css`, `pyproject.toml`.
- [F] Date scheduler e booleani sono formattati lato Jinja filter. Fonte: `radar_web/app.py`.
- [F] Warning, HOLD e blocked actions sono evidenziati nella detail page. Fonte: `radar_web/templates/run_detail.html`.

## C. Data Completeness Gate

- [F] La dashboard espone `data_completeness_status` e `data_completeness_warnings` in `/api/status`. Fonte: `radar_web/models.py`, `radar_web/app.py`.
- [F] Bridge root, runs root, runs_index e artifact run mancanti producono warning, non crash. Fonte: `radar_web/app.py`, `radar_web/run_locator.py`, `radar_web/bridge_reader.py`.
- [F] I casi incompleti sono coperti da test offline. Fonte: `tests/test_radar_web_app.py`, `tests/test_radar_web_run_locator.py`.

## D. Manual Trigger

- [F] Il trigger manuale resta l'unica azione UI. Fonte: `radar_web/templates/index.html`, `radar_web/app.py`.
- [F] Il comando resta solo `python -m radar.cli daily-sim --output-root "<Bridge runs root>"`. Fonte: `radar_web/manual_trigger.py`.
- [F] Il JSON del trigger conferma no scheduler, no email, no LLM, no auto-action e no other repo. Fonte: `radar_web/manual_trigger.py`.
- [INT] Lo step resta L1/L2 perche' il trigger manuale puo' avviare il flusso daily-sim controllato e richiede review manuale. Base: prompt `0860-0950`, `radar_web/manual_trigger.py`.

## E. Smoke UI

- [F] Browser in-app non disponibile nello smoke per errore sandbox node_repl. Fonte: Bridge smoke `0860-Smoke_Report.md`.
- [F] Screenshot prodotti con Edge headless gia' installato, senza installare dipendenze. Fonte: Bridge smoke `0860-Smoke_Report.md`.
- [F] Il trigger manuale e' stato testato via endpoint locale `POST /api/daily-sim/run`, non con click fisico browser automatizzato. Fonte: Bridge smoke `0860-Smoke_Report.md`.
- [INT] Il fallback e' accettabile per lo step perche' copre HTML/API locali, screenshot visuali e la stessa azione backend invocata dal bottone. Base: prompt `0860-0950`, Bridge smoke `0860-Smoke_Report.md`.

## F. Merge

- [F] Lo step e' classificato L1/L2 e il prompt impone `NO AUTO-MERGE`. Fonte: prompt `0860-0950`.
- [F] La PR deve restare draft. Fonte: prompt `0860-0950`.
- [PROP] MERGE_RECOMMENDATION: `YES` dopo review manuale di Alberto della PR draft e degli screenshot Bridge; non fare auto-merge.
