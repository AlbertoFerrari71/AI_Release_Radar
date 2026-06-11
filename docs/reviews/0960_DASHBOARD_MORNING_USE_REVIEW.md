# 0960) Dashboard Morning-Use Review

## A. Cosa Funziona

- [F] La dashboard locale si avvia con `python -m radar_web.app --host 127.0.0.1 --port 8787`. Fonte: `radar_web/app.py`.
- [F] La home mostra latest run, gate, source coverage, data completeness, HAG, prompt suggestions, scheduler status e run recenti. Fonte: `radar_web/templates/index.html`.
- [F] Il dettaglio run mostra report compact, gate markdown, HAG report, dashboard operatore, source diagnostics, direct actions, blocked actions, monitor-only, manual review queue e prompt suggestions. Fonte: `radar_web/templates/run_detail.html`.
- [F] Il trigger manuale esegue solo `python -m radar.cli daily-sim --output-root "<Bridge runs root>"`. Fonte: `radar_web/manual_trigger.py`.
- [F] Le prompt suggestions sono marcate `SUGGESTED ONLY - not executed`. Fonte: `radar_web/templates/index.html`, `radar_web/templates/run_detail.html`.

## B. Cosa E' Leggibile

- [F] I badge status usano classi CSS dedicate per PASS, WARN, HOLD, FAIL, review e NO_DATA. Fonte: `radar_web/app.py`, `radar_web/static/style.css`.
- [F] La home usa metriche e tabelle con path lunghi wrappati. Fonte: `radar_web/templates/index.html`, `radar_web/static/style.css`.
- [F] La pagina dettaglio usa sezioni collassabili per report lunghi e path locali. Fonte: `radar_web/templates/run_detail.html`.
- [INT] La dashboard e' leggibile per una review mattutina perche' separa gate, scheduler, HAG, prompt suggestions e run detail in aree distinte. Fonte: struttura di `radar_web/templates/index.html` e `radar_web/templates/run_detail.html`.

## C. Cosa E' Ancora Passivo

- [F] Prima dello step 0960-1100 la dashboard mostra direct actions e prompt suggestions ma non espone una inbox decisionale dedicata. Fonte: `radar_web/templates/index.html`, `radar_web/templates/run_detail.html`.
- [F] Prima dello step 0960-1100 non esistono endpoint `/actions` o `/api/actions`. Fonte: `radar_web/app.py`.
- [F] Prima dello step 0960-1100 non esiste un decision log append-only per le scelte dell'operatore. Fonte: assenza di moduli Action Center in `radar_web/` prima dello step.
- [INT] La dashboard V1 e' un report viewer operativo, non ancora un loop decisionale, perche' non collega una decisione umana a prompt pack e backlog Bridge. Fonte: `docs/architecture/0950_DASHBOARD_V1_OPERATOR_READY_CLOSURE_PACK.md`.

## D. Decisioni Umane Mancanti

- [F] Le decisioni richieste dal mega-step sono `approve_prompt`, `defer`, `ignore`, `backlog` e `request_review`. Fonte: prompt operativo 0960-1100 fornito da Alberto il 2026-06-11.
- [F] Le regole repo vietano auto-azioni, email automatiche, chiamate LLM automatiche, scheduler change e modifiche ad altri repository. Fonte: `AGENTS.md`.
- [INT] Le decisioni mancanti sono: approvare la generazione di un prompt, rimandare, ignorare, mettere in backlog e chiedere review supervisionata. Fonte: prompt operativo 0960-1100 e policy `AGENTS.md`.

## E. Dati Gia' Disponibili Per Action Inbox

- [F] `radar_web/run_locator.py` espone `direct_actions`, `blocked_actions`, `monitor_only_summary`, `manual_review_queue`, `prompt_suggestions`, HAG status e file Bridge del run. Fonte: `radar_web/run_locator.py`.
- [F] `radar/action_triage.py` produce entries con triage class, title, target project, project key, reason, risk class, category, severity e score. Fonte: `radar/action_triage.py`.
- [F] `radar/project_profiles.py` carica profili progetto con threshold, categorie dirette/monitor/ignored e permesso di prompt generation. Fonte: `radar/project_profiles.py`.
- [F] `radar/run_comparison.py` contiene gia' logica offline per item ripetuti, stale actions e warning persistenti. Fonte: `radar/run_comparison.py`.
- [INT] Questi dati bastano per costruire una Action Inbox senza fetch live e senza nuove dipendenze. Fonte: moduli citati sopra.

## F. Perche' Serve Action Center

- [F] Il prompt operativo 0960-1100 richiede che Alberto decida cosa fare con le novita' senza esecuzione automatica. Fonte: prompt operativo 0960-1100 fornito da Alberto il 2026-06-11.
- [F] `AGENTS.md` vieta auto-azioni, push diretto su `main`, merge non autorizzati, scheduler change e output runtime nel repo. Fonte: `AGENTS.md`.
- [INT] L'Action Center serve a trasformare evidenze gia' visibili in candidate action supervisionate, decision log append-only, prompt pack e backlog Bridge. Fonte: requisiti 0970-1050 del prompt operativo.
- [PROP] Il flusso consigliato e': aprire `/actions`, filtrare le azioni, scegliere una decisione, generare prompt pack solo se approvato, esportare backlog e usare il prompt in una sessione Codex separata supervisionata.
