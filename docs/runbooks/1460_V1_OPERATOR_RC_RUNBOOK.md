# 1460) V1 Operator RC Runbook

## Scopo

- [F] AI Release Radar V1 operator RC e' un radar locale supervisionato. Fonte: `README.md`, `radar/v1_readiness.py`.
- [F] Il sistema legge run e log dal Bridge, mostra dashboard locale, prepara Action Center, Daily Review Pack e readiness gate. Fonte: `radar_web/app.py`, `radar/daily_review_pack.py`, `radar/v1_readiness.py`.
- [F] Il sistema non invia email, non chiama LLM runtime, non esegue auto-azioni e non modifica scheduler. Fonte: `radar/daily_review_pack.py`, `radar_web/action_center.py`, `AGENTS.md`.

## Routine mattutina

1. Avviare la dashboard locale se non e' gia' attiva:

```powershell
python -m radar_web.app --host 127.0.0.1 --port 8787
```

2. Aprire `http://127.0.0.1:8787/?lang=it`.
3. Verificare ultimo run, scheduler card, HAG, gate, source coverage e prompt suggestions.
4. Aprire `/actions?lang=it` e controllare che il run corrente sia visibile.
5. Se l'Action Center segnala decisioni storiche, trattarle come evidenza e non come approvazione del run corrente.
6. Aprire il dettaglio run e leggere la matrice sorgenti prima di decidere un follow-up tecnico.

## Daily Review Pack

- [F] Il pack deve essere scritto nel Bridge, non nel repository. Fonte: `radar/daily_review_pack.py`.
- [F] Comando:

```powershell
python -m radar.cli daily-review-pack --run-dir "<Bridge-run-dir>" --output-dir "<Bridge-daily_review_packs>\<run_id>" --scheduler-log "<Bridge-scheduler-log>"
```

- [F] Output attesi: `1390-Daily_Review_Pack.md` e `1390-Daily_Review_Pack.json`. Fonte: `radar/daily_review_pack.py`.
- [INT] Usare il Markdown per review umana e il JSON per controlli o smoke futuri.

## HAG e HOLD

- [F] `HOLD_FOR_HUMAN_APPROVAL` significa che il radar ha deliberatamente fermato l'azione automatica. Fonte: `radar/hag_report.py`, `radar/daily_review_pack.py`.
- [F] HOLD non e' un errore generico: richiede che Alberto approvi manualmente un passo successivo separato. Fonte: `radar/v1_readiness.py`.
- [F] Nessun prompt suggestion e' approvato solo perche' compare nel run output. Fonte: `radar/action_inbox.py`, `radar_web/action_center.py`.

## Action Center

- [F] `/actions` mostra azioni potenziali, monitor-only, manual review, prompt suggestions e decisioni registrate. Fonte: `radar_web/templates/actions.html`, `radar/action_inbox.py`.
- [F] Le decisioni sono scoperte per run corrente; decisioni storiche con stesso action key non approvano il run corrente. Fonte: `radar/action_inbox.py`, `tests/test_action_inbox.py`.
- [F] I GET della dashboard e delle API read-only non scrivono in `action_dispatch`. Fonte: `tests/test_radar_web_app.py`.
- [F] I prompt pack sono generati solo dopo una decisione POST esplicita e restano Markdown nel Bridge. Fonte: `radar/action_inbox.py`, `radar_web/action_center.py`.

## Source Coverage

- [F] La matrice sorgenti distingue parsed, unsupported, failed e manual review. Fonte: `radar/source_coverage.py`.
- [F] Un HTTP 403 con manual review non e' un parser failure generico: e' una fonte da verificare manualmente o sostituire con alternativa machine-readable. Fonte: `radar/source_coverage.py`.
- [PROP] Se la copertura resta bassa, il prossimo ciclo tecnico deve migliorare fonti strutturate o alternative machine-readable prima di aumentare automazione.

## Scheduler Evidence

- [F] Lo scheduler dry-report e' evidenza operativa, non autorizzazione ad auto-azioni. Fonte: `docs/decisions/0510_L3_SCHEDULER_DRY_REPORT_CONSENT.md`.
- [F] LastTaskResult `0`, stderr vuoto e script exit code `0` indicano run tecnico riuscito. Fonte: `radar/daily_review_pack.py`.
- [F] Un lock stale storico deve essere letto come evidenza da revisionare, non cancellato automaticamente. Fonte: `docs/architecture/0570_SCHEDULER_FAILURE_HANDLING_AND_LOCKING.md`.
- [PROP] Retention futura consigliata: mantenere run, scheduler log e daily review pack indicizzati per data; introdurre pulizia solo con step dedicato e review manuale.

## V1 Readiness Gate

- [F] Comando:

```powershell
python -m radar.cli v1-readiness-gate --run-dir "<Bridge-run-dir>" --output-dir "<Bridge-codex_command-dir>" --scheduler-log "<Bridge-scheduler-log>" --dashboard-smoke-status PASS --action-center-smoke-status PASS --action-center-run-scope-status PASS
```

- [F] Output attesi: `1450-V1_Operator_Readiness_Gate.md` e `1450-V1_Operator_Readiness_Gate.json`. Fonte: `radar/v1_readiness.py`.
- [F] `V1_OPERATOR_READY_WITH_WARNINGS` e' accettabile quando flusso, UI, HAG e pack sono usabili ma restano warning di source coverage o fonti manual review. Fonte: `radar/v1_readiness.py`.
- [F] `BLOCKED` va usato se dashboard non parte, run/log non sono leggibili, safety non e' esclusa o Action Center non e' utilizzabile. Fonte: `radar/v1_readiness.py`.

## Cosa non fare

- [F] Non eseguire prompt suggestions automaticamente. Fonte: `radar/prompt_suggestions.py`, `radar/action_inbox.py`.
- [F] Non inviare email o notifiche automatiche. Fonte: `AGENTS.md`.
- [F] Non chiamare LLM/API runtime da questo flusso. Fonte: `AGENTS.md`, `radar/daily_review_pack.py`.
- [F] Non modificare scheduler, trigger, orari o policy Windows Task. Fonte: `AGENTS.md`.
- [F] Non creare file `LAST-*` o `latest-*`. Fonte: `AGENTS.md`.

## Prossimo ciclo consigliato

- [PROP] Dopo RC review e publish flow, lavorare sul ciclo source coverage: ridurre fonti unsupported, chiarire 403/manual review e preferire endpoint machine-readable.
