# 1290) Multilingual Dashboard Navigation Smoke

Fonte primaria: prompt `AI Release Radar - ASF Mega-Step 1260-1350` fornito da Alberto il 2026-06-11.

## Setup

- [F] Dashboard avviata con `python -m radar_web.app --host 127.0.0.1 --port 8787`. Fonte: smoke 1290 eseguito il 2026-06-11.
- [F] Server chiuso al termine; porta 8787 risultata libera. Fonte: smoke 1290 eseguito il 2026-06-11.
- [F] Nessun bind `0.0.0.0` usato. Fonte: comando smoke 1290.

## Output Bridge

- [F] Cartella smoke: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\web_smoke\1260_1350_20260611_095537`. Fonte: smoke 1290 eseguito il 2026-06-11.
- [F] HTML salvati per home EN/IT/FR/DE/ES. Fonte: file `1290-Home_*.html` nel Bridge smoke.
- [F] HTML salvati per Action Center EN/IT/FR/DE/ES. Fonte: file `1290-Actions_*.html` nel Bridge smoke.
- [F] Run detail testato e salvato per EN/IT/DE usando run `0320_0400_daily_sim_20260611_062420`. Fonte: file `1290-Run_EN.html`, `1290-Run_IT.html`, `1290-Run_DE.html` nel Bridge smoke.
- [F] API salvate: `1290-Api_Status_EN.json`, `1290-Api_Status_IT.json`, `1290-Api_Actions_DE.json`, `1290-Api_Scheduler.json`, `1290-Api_Runs_EN.json`, `1290-Health_*.json`. Fonte: Bridge smoke 1290.
- [F] Screenshot PNG non prodotti per errore runtime del browser in-app; HTML/API fallback usato. Fonte: `1290-Smoke_Manifest.json`.

## Esito Navigazione

- [F] Tutti gli URL smoke salvati hanno risposto HTTP 200. Fonte: `1290-Smoke_Manifest.json`.
- [F] `/api/status?lang=en` e `/api/status?lang=it` hanno risposto con payload JSON valido. Fonte: Bridge smoke 1290.
- [F] `/api/actions?lang=de` ha risposto con payload JSON valido. Fonte: Bridge smoke 1290.
- [F] `/api/scheduler` ha risposto con payload JSON valido. Fonte: Bridge smoke 1290.

## Esito

- [F] Esito 1290: PASS_WITH_NOTES per mancanza PNG, con fallback HTML/API accettato dal prompt. Fonte: prompt 1260-1350 e `1290-Smoke_Manifest.json`.
