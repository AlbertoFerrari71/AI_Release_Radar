# Operator Acceptance Lesson Learned — PASS tecnico ≠ PASS operatore

Fonte primaria: prompt `2390-2440) AI Release Radar — Operator Acceptance Philosophy and UI Gate Lessons Learned` fornito da Alberto il 2026-06-13.

## 1. Titolo

- [F] Questa lesson learned formalizza il principio: `PASS tecnico ≠ PASS operatore`. Fonte: prompt 2390-2440.

## 2. Contesto

- [F] La PR #36 ha introdotto la UX Easy Mode iniziale. Fonte: `git --no-pager log --oneline --decorate -5`, merge commit `7af61f3`.
- [F] Dopo la PR #36, lo step 2270-2380 ha prodotto un esito YELLOW perche' `127.0.0.1:8787` era occupato da un uvicorn stale che serviva route rotte: `/` 500, `/easy` 404, `/easy-mode` 404, `/expert` 404. Fonte: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\codex_command\2270-2380-Report_Codex.md`, sezioni B e T.
- [F] Lo step 2270-2380 ha aggiunto `/easy`, `/easy-mode`, preferenze UI locali e audit di navigazione sicura. Fonte: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\codex_command\2270-2380-Report_Codex.md`, sezioni E, L e S.
- [F] La PR #37 ha corretto Easy Mode access e UI preferences. Fonte: `git --no-pager log --oneline --decorate -5`, commit `7e5a34e`.
- [F] Lo step 2385 ha chiuso GREEN con smoke reale 18/18 su `http://127.0.0.1:8787`, `python -m pytest` PASS con 314 passed e 2 skipped, e merge della PR #37 su `main`. Fonte: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\codex_command\2385-Report_Codex.md`, sezioni A, D, F e G.
- [F] Il merge commit finale della PR #37 e' `b375f81a6ae047c3bce78fad6947942d83a8dafa`. Fonte: `git rev-parse HEAD`, `git rev-parse origin/main`, report 2385 sezione H.

## 3. Cosa E' Successo

- [F] I gate codice/test/smoke fallback dello step 2270-2380 erano PASS, ma lo stato finale e' rimasto YELLOW perche' la porta realmente usata dall'operatore serviva una versione stale. Fonte: report 2270-2380, sezione B.
- [INT] Il problema non era solo una route mancante: era una mancata garanzia di accesso operativo sul punto di ingresso reale dell'utente. Base: report 2270-2380 sezioni B, D e U; report 2385 sezioni B, C e D.
- [F] La correzione e' stata validata avviando e controllando la versione PR e poi `main` post-merge sulla porta reale `127.0.0.1:8787`. Fonte: report 2385 sezioni C e D.

## 4. Perche' Il GREEN Tecnico Non Bastava

- [INT] Test unitari, smoke fallback, diff check, PR e merge verificano che il software sia tecnicamente coerente; non dimostrano da soli che Alberto riesca ad aprire la web app, riconoscere Easy Mode e navigare il flusso operativo previsto. Base: report 2270-2380 sezioni B, U e V; report 2385 sezioni B, D e F.
- [INT] Un sistema puo' essere pronto per il repository e non ancora pronto per l'operatore se l'accesso reale, la prima schermata o la navigazione principale restano ambigui o non validati. Base: prompt 2390-2440 e report 2270-2380.

## 5. Verification Gate Vs Acceptance Gate

- [F] Verification Gate, per questo progetto, controlla test, smoke tecnico, API, diff, safety, branch, PR e merge quando autorizzato. Fonte: prompt 2390-2440; `AGENTS.md`.
- [F] Acceptance Gate, per questo progetto, controlla che una persona riesca davvero a usare il prodotto: accesso reale, primo utilizzo, navigazione, comprensibilita' e coerenza con il flusso progettato. Fonte: prompt 2390-2440.
- [INT] Il Verification Gate risponde alla domanda "il software funziona secondo i controlli tecnici?"; l'Acceptance Gate risponde alla domanda "l'operatore riesce a ottenere valore dal prodotto nel contesto reale?". Base: prompt 2390-2440 e sequenza PR #36/#37 documentata nei report 2270-2380 e 2385.

## 6. Regola Fondativa

- [F] Regola adottata: Un bug trovato dall'utente e' un test che non avevamo ancora scritto. Fonte: prompt 2390-2440.
- [F] Il feedback operativo deve essere trasformato in test, smoke, UI contract, gate, safe-click policy, lesson learned o backlog ASF generale. Fonte: prompt 2390-2440.

## 7. Impatto Su AI Release Radar

- [F] `GET /` rende Easy Mode e `GET /easy` rende la stessa pagina. Fonte: `docs/web/2270_EASY_MODE_UI_CONTRACT.md`, `radar_web/app.py`.
- [F] Expert Mode resta raggiungibile da `/expert`. Fonte: `docs/web/2270_EASY_MODE_UI_CONTRACT.md`, `radar_web/app.py`.
- [F] L'Action Center `/actions` mostra Action Inbox, filtri, routing progetto, priorita', rischio, decision status, safety status, trend, noise e controlli umani. Fonte: `README.md`, `radar_web/templates/actions.html`, `radar_web/app.py`.
- [INT] Easy Mode e' requisito operativo validato: e' il punto di ingresso che deve permettere all'operatore di capire in pochi secondi giorno/run, novita' importanti, dove leggere dettagli e quando passare a Expert Mode. Base: prompt 2390-2440; `docs/web/2270_EASY_MODE_UI_CONTRACT.md`; report 2385 sezione D.
- [F] La porta operativa prevista della dashboard e' `http://127.0.0.1:8787`. Fonte: `docs/architecture/0760_WEB_DASHBOARD_ARCHITECTURE.md`, `radar_web/app.py`.

## 8. UI Navigation Gate

- [F] Per web app e dashboard, il gate deve navigare davvero home, Easy Mode, Expert Mode, Action Center, Source Matrix, run detail, tab, tendine, link GET interni, bottoni sicuri e preferenze UI. Fonte: prompt 2390-2440.
- [F] Le pagine principali del contratto Easy Mode sono Easy Mode, Easy run detail, Expert Mode, Expert run detail, Action Center, Sources, Runs/Reports e API JSON read-only. Fonte: `docs/web/2270_EASY_MODE_UI_CONTRACT.md`.
- [F] Lo smoke reale dello step 2385 ha validato su `127.0.0.1:8787`: `/`, `/easy`, `/easy-mode?lang=fr`, `/expert`, `/actions`, `/sources?lang=en`, API Easy e preferenze UI. Fonte: report 2385 sezioni D ed E.
- [INT] Il UI Navigation Gate deve essere trattato come parte dell'Acceptance Gate per modifiche UI-facing, non come evidenza opzionale. Base: prompt 2390-2440; report 2270-2380; report 2385.

## 9. Safe-Click Policy

- [F] Il crawler puo' cliccare link GET interni, tab, tendine lingua, filtri visuali, pulsanti di dettaglio, toggle visuali non operativi e POST strettamente limitati alle preferenze UI locali se previsti e testati. Fonte: prompt 2390-2440; `docs/web/2270_EASY_MODE_UI_CONTRACT.md`.
- [F] Il crawler non deve cliccare approvazioni HAG, decisioni operative, comandi scheduler, trigger run reali, azioni esterne, email, notifiche o form mutativi non esplicitamente autorizzati. Fonte: prompt 2390-2440; `docs/web/2270_EASY_MODE_UI_CONTRACT.md`.
- [F] I decision buttons Action Center, prompt generation e backlog export sono manual-only ed esclusi dal crawling safe-click automatizzato. Fonte: `docs/web/2270_EASY_MODE_UI_CONTRACT.md`, `radar_web/templates/actions.html`, `tests/test_radar_web_app.py`.

## 10. Criteri GREEN/YELLOW/RED Futuri

- [F] GREEN per modifiche UI-facing richiede test, smoke, accesso reale, navigazione, porta operatore e safety PASS. Fonte: prompt 2390-2440.
- [F] YELLOW si applica quando il software funziona ma manca review visuale, manca evidenza Browser/HTML equivalente, o restano warning governati e documentati. Fonte: prompt 2390-2440; report 2385 sezione A.
- [F] RED si applica quando accesso principale o route principali sono rotte, compare una safety regression, oppure il crawler/flow introduce mutazioni non autorizzate. Fonte: prompt 2390-2440; `docs/web/2270_EASY_MODE_UI_CONTRACT.md`.
- [INT] Un warning dichiarato, spiegato e trasformato in backlog e' preferibile a un PASS superficiale. Base: prompt 2390-2440; report 2270-2380 stato YELLOW; report 2385 warning classificato su GitHub checks assenti.

## 11. Valori Operativi

- [F] I valori operativi adottati per questa lesson learned sono trasparenza, supervisione, umilta', evidenza, responsabilita', miglioramento continuo e fiducia dell'utente. Fonte: prompt 2390-2440.
- [INT] Per AI Release Radar, sicurezza prima dell'autonomia e fiducia dell'operatore prima della velocita' sono criteri di metodo, non preferenze estetiche. Base: prompt 2390-2440; `AGENTS.md`; `docs/architecture/0760_WEB_DASHBOARD_ARCHITECTURE.md`.

## 12. Impatto Futuro Su ASF

- [F] La lesson learned deve essere promossa in AI Software Factory come standard generale nello step proposto `1290-1360) ASF — Verification Gate vs Acceptance Gate Philosophy and Standardization`. Fonte: prompt 2390-2440.
- [F] Gli elementi da promuovere sono Acceptance Gate, UI Navigation Gate, Browser/Playwright/Edge headless audit, safe-click policy e operator acceptance report. Fonte: prompt 2390-2440.
- [INT] Il valore generale per ASF e' trasformare feedback operatore e falsi GREEN in gate riusabili, invece di trattarli come incidenti isolati di un singolo prodotto. Base: prompt 2390-2440 e sequenza report 2270-2380/2385.

## 13. Frasi Guida

- [F] PASS tecnico ≠ PASS operatore. Fonte: prompt 2390-2440.
- [F] Verification Gate verifica che il software funzioni. Fonte: prompt 2390-2440.
- [F] Acceptance Gate verifica che una persona riesca davvero a usarlo. Fonte: prompt 2390-2440.
- [F] Un bug trovato dall'utente e' un test che non avevamo ancora scritto. Fonte: prompt 2390-2440.
- [F] La qualita' finale non e' solo assenza di errori: e' fiducia operativa. Fonte: prompt 2390-2440.
