# 0850) Web Dashboard Runbook

## A. Avvio

Da repository:

```powershell
Set-Location "C:\Users\alberto.ferrari\source\repos\AI_Release_Radar"
python -m radar_web.app --host 127.0.0.1 --port 8787
```

- [F] Il comando avvia la dashboard locale FastAPI. Fonte: `radar_web/app.py`.
- [F] Host e porta default sono `127.0.0.1` e `8787`. Fonte: `radar_web/config.py`.

## B. URL

```text
http://127.0.0.1:8787
```

- [F] La home mostra ultimo run, gate, coverage, azioni, HAG, scheduler e run recenti. Fonte: `radar_web/templates/index.html`.
- [F] Il dettaglio run e' `http://127.0.0.1:8787/runs/<run_id>`. Fonte: `radar_web/app.py`, `radar_web/templates/run_detail.html`.

## C. Cosa Mostra

- [F] Ultimo run Bridge. Fonte: `radar_web/run_locator.py`.
- [F] `0180-Report_Compact.md`. Fonte: `radar_web/bridge_reader.py`.
- [F] Automation gate e daily quality gate. Fonte: `radar_web/bridge_reader.py`.
- [F] Human Approval Gate report. Fonte: `radar_web/bridge_reader.py`.
- [F] Prompt suggestions `suggested_only`. Fonte: `radar_web/run_locator.py`, `radar_web/templates/run_detail.html`.
- [F] Scheduler status read-only. Fonte: `radar_web/scheduler_status.py`.

## D. Trigger Manuale Daily-Sim

- [F] Il bottone `Run daily-sim now` chiama `POST /api/daily-sim/run`. Fonte: `radar_web/templates/index.html`, `radar_web/app.py`.
- [F] Il backend esegue solo `python -m radar.cli daily-sim --output-root "<Bridge runs root>"`. Fonte: `radar_web/manual_trigger.py`.
- [F] Il Bridge runs root default e':

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs
```

Fonte: `radar_web/config.py`.

## E. Cosa Non Fa

- [F] Non fa merge su `main`. Fonte: `AGENTS.md`.
- [F] Non crea nuovi scheduler o task Windows. Fonte: `radar_web/scheduler_status.py`, `radar_web/manual_trigger.py`.
- [F] Non modifica lo scheduler esistente. Fonte: `radar_web/scheduler_status.py`.
- [F] Non invia email o notifiche automatiche. Fonte: `radar_web/manual_trigger.py`.
- [F] Non chiama LLM automaticamente. Fonte: `radar_web/manual_trigger.py`.
- [F] Non esegue prompt suggestions. Fonte: `radar_web/templates/run_detail.html`, `radar/prompt_suggestions.py`.
- [F] Non scrive output runtime nel repository. Fonte: `radar_web/config.py`, `radar_web/manual_trigger.py`.

## F. Stop

Nel terminale che esegue la dashboard:

```powershell
Ctrl+C
```

- [F] Il server locale e' avviato dal processo `python -m radar_web.app`. Fonte: `radar_web/app.py`.

## G. Troubleshooting

- [F] Se `/api/scheduler` restituisce `NO_DATA`, controllare che Windows Task Scheduler e il task `AIReleaseRadar_DailyDryReport` siano disponibili. Fonte: `radar_web/scheduler_status.py`.
- [F] Se la home mostra `runs_root_missing`, verificare che il Bridge root esista. Fonte: `radar_web/app.py`, `radar_web/config.py`.
- [F] Se il trigger manuale restituisce `ALREADY_RUNNING`, attendere la fine del run in corso. Fonte: `radar_web/manual_trigger.py`.
- [F] Se il trigger manuale restituisce `REFUSED`, controllare che l'output root non sia dentro repo e non contenga `LAST-*` o `latest-*`. Fonte: `radar_web/config.py`, `radar_web/manual_trigger.py`.

## H. Prossimo Step

- [PROP] `0860) First Local Dashboard Operator Smoke`: avvio locale, verifica ultimo run Bridge, verifica card scheduler e prova del trigger manuale solo con consenso esplicito di Alberto.
