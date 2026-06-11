# 1260) Multilingual Preflight and Baseline Review

Fonte primaria: prompt `AI Release Radar - ASF Mega-Step 1260-1350` fornito da Alberto il 2026-06-11.

## Stato Main

- [F] `main` era allineato a `origin/main` prima del branch di step. Fonte: comando `git checkout main`, `git pull`, `git --no-pager status` eseguiti il 2026-06-11.
- [F] PR #31 era gia' mergiata su `main` tramite commit `f0a4ded Merge pull request #31 from AlbertoFerrari71/step-1110-1250-multilingual-dashboard-news-translation`. Fonte: comando `git --no-pager log --oneline --max-count=190` eseguito il 2026-06-11.
- [F] Working tree iniziale pulito su `main`. Fonte: comando `git --no-pager status` eseguito il 2026-06-11.
- [F] Nessuna PR aperta residua rilevata. Fonte: comando `gh pr list --state open` eseguito il 2026-06-11.

## Test Iniziali

- [F] `python -m pytest` iniziale: 287 passed, 2 skipped. Fonte: output pytest del preflight 1260 eseguito il 2026-06-11.
- [F] `git --no-pager diff --check` iniziale: PASS senza output. Fonte: comando preflight 1260 eseguito il 2026-06-11.
- [F] `python -m radar.cli --help`, `python -m radar.cli daily-sim --help` e `python -m radar_web.app --help` erano eseguibili. Fonte: comandi preflight 1260 eseguiti il 2026-06-11.

## Scheduler

- [F] Task Windows `AIReleaseRadar_DailyDryReport` presente e in stato `Ready`. Fonte: `Get-ScheduledTask -TaskName "AIReleaseRadar_DailyDryReport"` eseguito il 2026-06-11.
- [F] `LastTaskResult = 0`, `LastRunTime = 11/06/2026 08:24:17`, `NextRunTime = 12/06/2026 07:15:00`. Fonte: `Get-ScheduledTaskInfo -TaskName "AIReleaseRadar_DailyDryReport"` eseguito il 2026-06-11.
- [F] Nessuna modifica scheduler e' stata autorizzata o necessaria in questo step. Fonte: prompt 1260-1350 e `AGENTS.md`.

## Cataloghi

- [F] Cataloghi presenti: `radar_web/locales/en.json`, `it.json`, `fr.json`, `de.json`, `es.json`. Fonte: `Test-Path` e listing `radar_web/locales` eseguiti il 2026-06-11.
- [F] Lingue supportate: EN, IT, FR, DE, ES. Fonte: `radar_web/i18n.py`.
- [F] DE e' tedesco per istruzione esplicita di Alberto. Fonte: prompt 1260-1350.

## Dashboard Coinvolta

- [F] Pagine coinvolte: `/`, `/actions`, `/health`, `/api/status`, `/api/runs`, `/api/scheduler` e `/runs/<run_id>` quando disponibile. Fonte: prompt 1260-1350 e route in `radar_web/app.py`.
- [F] Run usato per smoke e translation sample: `0320_0400_daily_sim_20260611_062420`. Fonte: Bridge `runs/0320_0400_daily_sim_20260611_062420`.

## Rischi Principali

- [INT] Rischio principale UI: testi FR/DE piu' lunghi che possono rompere badge, bottoni o card. Fonte: review cataloghi e CSS 1260-1350.
- [INT] Rischio principale dati: cache traduzione mancante o corrotta deve degradare a originale EN senza crash. Fonte: `radar/news_translation.py`.
- [INT] Rischio operativo: nessun output runtime deve finire nel repo. Fonte: `AGENTS.md`.

## Blocker

- [F] Blocker: cataloghi con chiavi mancanti, pagina non renderizzata in una lingua, Action Center rotto in una lingua, fallback i18n non funzionante, cache news che causa crash, LLM automatico runtime, modifica scheduler o auto-azione. Fonte: prompt 1260-1350.

## Micro-Fix Ammessi

- [F] Micro-fix ammessi: cataloghi lingua, helper i18n, CSS/template, test, traduzioni UI palesemente sbagliate e wrap layout sicuro. Fonte: prompt 1260-1350.
- [PROP] Limitare i fix a correzioni linguistiche puntuali, test QA cataloghi/cache e CSS di wrapping, senza nuove dipendenze.
