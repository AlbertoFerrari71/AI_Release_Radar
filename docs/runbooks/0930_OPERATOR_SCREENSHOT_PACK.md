# 0930) Operator Screenshot Pack

## A. Scopo

- [F] Il pacchetto screenshot serve a documentare una review operatore della dashboard locale senza salvare output runtime nel repository. Fonte: prompt `0860-0950`, `AGENTS.md`.
- [F] Gli artifact devono essere salvati nel Bridge, non nel repository. Fonte: prompt `0860-0950`, `AGENTS.md`.
- [F] Non devono essere usati file `LAST-*` o `latest-*`. Fonte: `AGENTS.md`.

## B. Percorso Bridge

Pattern autorizzato:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\web_smoke\0860_0950_<timestamp>
```

- [F] Il path e' fuori repository. Fonte: prompt `0860-0950`.
- [F] Il timestamp rende l'output deterministico e non sovrascritto. Fonte: prompt `0860-0950`.

## C. Artifact Attesi

```text
0860-Home_Before.png
0870-Home_After.png
0880-Run_Detail.png
0890-After_Manual_Trigger.png
0860-Home.html
0880-Run_Detail.html
0860-Api_Status.json
0860-Api_Scheduler.json
0860-Smoke_Report.md
```

- [F] Se screenshot browser non sono disponibili, HTML/API devono essere salvati e il limite deve essere dichiarato nel report. Fonte: prompt `0860-0950`.

## D. Vincoli

- [F] La dashboard deve restare su `127.0.0.1:8787`; non usare `0.0.0.0` o tunnel pubblici. Fonte: prompt `0860-0950`, `radar_web/config.py`.
- [F] Lo smoke puo' cliccare `Run daily-sim now`, ma il trigger deve restare manuale e controllato. Fonte: prompt `0860-0950`, `radar_web/manual_trigger.py`.
- [F] Il server web locale deve essere fermato al termine dello smoke. Fonte: prompt `0860-0950`.

## E. Checklist Operatore

1. Avviare `python -m radar_web.app --host 127.0.0.1 --port 8787`.
2. Aprire `http://127.0.0.1:8787`.
3. Salvare home HTML/API e screenshot home.
4. Aprire un run recente e salvare detail HTML/screenshot.
5. Tornare alla home e testare il trigger manuale solo nello scope dello step.
6. Salvare report smoke nel Bridge.
7. Fermare il server locale.
