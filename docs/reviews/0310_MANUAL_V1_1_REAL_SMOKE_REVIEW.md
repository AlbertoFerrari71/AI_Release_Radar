# 0310) Manual V1.1 Real Smoke Review

## A. Run Analizzato

- [F] Run principale analizzato: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs\manual_test_0240_0300_20260610_160833`. Fonte: `0180-Run_Summary.json` nel run Bridge.
- [F] Report compact analizzato: `0180-Report_Compact.md` nello stesso run Bridge. Fonte: file Bridge `0180-Report_Compact.md`.
- [F] Report full analizzato: `0180-Report_Full.md` nello stesso run Bridge. Fonte: file Bridge `0180-Report_Full.md`.
- [F] Run storico indicato dal prompt e usato come riferimento secondario: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs\0240_0300_manual_smoke_20260610_130910`. Fonte: prompt 0310 fornito da Alberto e `0180-Run_Summary.json` nel run Bridge.
- [F] Nessun nuovo smoke live e' stato eseguito nello step 0310. Fonte: esecuzione step 0310.

## B. Sintesi Esito

- [F] Il run principale ha `report_status=CHANGES_FOUND`, `live_snapshot_status=success`, `source_count=11`, `parsed_count=1`, `skipped_count=10`, `failed_count=0`, `item_count=10`, `project_impact_count=60`, `direct_action_count=10`, `monitor_only_action_count=50`, `no_action_count=0`, `unsupported_source_count=10` e `scorecard_status=PASS`. Fonte: `0180-Run_Summary.json` del run Bridge principale.
- [F] I diagnostic status del run principale sono `parsed=1`, `fetched_but_unsupported=7` e `manual_review_required=3`. Fonte: `0180-Run_Summary.json` del run Bridge principale.
- [INT] La V1.1 e' leggibile per review manuale perche' mostra titoli, link, action type, source diagnostics e scorecard. Base: `0180-Report_Compact.md`, `0180-Report_Full.md`, `0180-Run_Summary.json`.
- [INT] La V1.1 non e' ancora una base sufficiente per scheduler come prossimo blocco principale perche' il run reale resta dipendente da una sola fonte parsata su undici. Base: `parsed_count=1`, `source_count=11` e `unsupported_source_count=10` in `0180-Run_Summary.json`.

## C. Qualita Report Compact

- [F] Il compact report mostra status, scorecard, sources checked, parsed sources, items found, top items e top actions. Fonte: `0180-Report_Compact.md`.
- [F] I top items mostrano titoli leggibili e link GitHub release invece di soli item id. Fonte: sezione `Top Items` in `0180-Report_Compact.md`.
- [F] Le top actions distinguono `direct_action` e `monitor_only` e includono un next step testuale. Fonte: sezione `Top Actions` in `0180-Report_Compact.md`.
- [INT] Il compact report e' adatto a una prima lettura di Alberto per capire se aprire il full report. Base: presenza di status, conteggi, top items e top actions in `0180-Report_Compact.md`.
- [INT] Il compact report resta parziale come strumento decisionale perche' evidenzia `parsed sources: 1` ma non rende immediato il peso operativo di `unsupported_source_count=10`. Base: `0180-Report_Compact.md` e `0180-Run_Summary.json`.

## D. Qualita Report Full

- [F] Il full report include executive summary, run notes, sources controlled, source parser diagnostics, observed items, project impacts, risks, report review scorecard e recommended next Codex step. Fonte: intestazioni in `0180-Report_Full.md`.
- [F] La sezione source parser diagnostics elenca gli stati per tutte le 11 fonti. Fonte: `0180-Report_Full.md` e `0180-Run_Summary.json`.
- [F] La sezione project impacts contiene 60 impatti generati dai 10 item osservati. Fonte: `project_impact_count=60` in `0180-Run_Summary.json`.
- [INT] Il full report e' auditabile e molto piu' informativo della V1 manuale, ma e' ripetitivo perche' ogni release Codex produce molte righe monitor-only. Base: `project_impact_count=60`, `monitor_only_action_count=50` e sezione `Project Impacts` in `0180-Report_Full.md`.

## E. Qualita Direct Actions

- [F] Il run principale produce 10 direct actions. Fonte: `direct_action_count=10` in `0180-Run_Summary.json`.
- [F] Le direct actions viste nel report sono legate ad AI Software Factory e propongono compatibility review solo se cambiano CLI, sandbox, approvals, AGENTS.md o output format. Fonte: sezione `Top Actions` in `0180-Report_Compact.md` e sezione `Project Impacts` in `0180-Report_Full.md`.
- [INT] Le direct actions sono utili come postura prudente: non aprono lavoro automatico, ma indirizzano la review dove Codex/API puo' davvero incidere. Base: testo delle direct actions in `0180-Report_Full.md`.
- [INT] Le direct actions restano ancora migliorabili perche' l'azione breve `review AGENTS.md` e' ripetuta anche quando il titolo release non dimostra un cambio AGENTS.md specifico. Base: testo delle direct actions in `0180-Report_Compact.md` e `0180-Report_Full.md`.

## F. Qualita Monitor-Only Actions

- [F] Il run principale produce 50 monitor-only actions e 0 no-action. Fonte: `monitor_only_action_count=50` e `no_action_count=0` in `0180-Run_Summary.json`.
- [F] Le monitor-only actions dicono di mantenere il progetto visibile e di non aprire implementazione senza un segnale diretto. Fonte: sezione `Top Actions` in `0180-Report_Compact.md` e sezione `Project Impacts` in `0180-Report_Full.md`.
- [INT] Le monitor-only actions sono un miglioramento rispetto ad azioni tecniche forti e generiche su progetti non direttamente coinvolti. Base: distinzione `monitor_only` nel report V1.1.
- [INT] Il volume 50 monitor-only su 60 impatti e' ancora rumoroso per uso quotidiano non supervisionato. Base: `monitor_only_action_count=50` e `project_impact_count=60` in `0180-Run_Summary.json`.
- [PROP] Nel prossimo blocco di qualita' azioni, valutare soglie o raggruppamenti per mostrare monitor-only aggregate invece di ripetere la stessa postura per ogni release/progetto.

## G. Qualita Source Diagnostics

- [F] Il run principale ha 11 diagnostics: 1 `parsed`, 7 `fetched_but_unsupported`, 3 `manual_review_required`. Fonte: `source_diagnostics` in `0180-Run_Summary.json`.
- [F] Il run principale ha `failed_count=0`. Fonte: `live_snapshot.failed_count` in `0180-Run_Summary.json`.
- [F] La fonte parsata e' `github_api_openai_codex_releases`. Fonte: `source_diagnostics` in `0180-Run_Summary.json`.
- [F] Le fonti `openai_release_notes_hub`, `openai_chatgpt_release_notes` e `openai_model_release_notes` sono `manual_review_required`. Fonte: `source_diagnostics` in `0180-Run_Summary.json`.
- [INT] Il limite principale del run non e' il fetch live, ma la copertura parser: le fonti sono raggiunte o diagnosticate, ma non generano item strutturati. Base: `failed_count=0`, `parsed=1`, `fetched_but_unsupported=7`, `manual_review_required=3`.

## H. Qualita Scorecard

- [F] La scorecard del run principale e' `PASS`. Fonte: `report_scorecard.status` in `0180-Run_Summary.json` e sezione `Report Review Scorecard` in `0180-Report_Full.md`.
- [F] La scorecard passa `has_parsed_source_count` con messaggio `parsed_count=1`. Fonte: sezione `Report Review Scorecard` in `0180-Report_Full.md`.
- [F] La documentazione 0280 definisce la scorecard come gate di qualita' report, non come sostituto della review umana. Fonte: `docs/architecture/0280_REPORT_REVIEW_SCORECARD.md`.
- [INT] Il PASS e' credibile se letto come `report_readability_scorecard=PASS`: il report e' leggibile, tracciabile e non basato su soli item id. Base: scorecard PASS e check `has_readable_titles`, `has_source_links`, `has_no_item_id_only_top_actions`.
- [INT] Il PASS e' troppo permissivo se letto come readiness complessiva del radar, perche' non penalizza `parsed_count=1` su `source_count=11`. Base: `has_parsed_source_count: PASS - parsed_count=1` in `0180-Report_Full.md`.
- [PROP] Separare semanticamente tre segnali: `report_readability_scorecard=PASS`, `source_coverage_warning=WARN` e `action_quality_warning=WARN`.

## I. Rumore Residuo

- [F] Il run principale genera 60 project impacts da 10 item, con 10 direct actions e 50 monitor-only actions. Fonte: `0180-Run_Summary.json`.
- [F] Il compact report mostra solo una selezione delle top actions. Fonte: `0180-Report_Compact.md`.
- [INT] Il rumore residuo e' accettabile per review manuale perche' le azioni forti sono limitate, ma e' ancora alto per scheduler, notifiche o consumo quotidiano non supervisionato. Base: `monitor_only_action_count=50` e `unsupported_source_count=10`.
- [PROP] Prima di automatizzare, introdurre almeno una regola di compressione o soglia per monitor-only ripetuti e una warning policy sulla source coverage.

## J. Copertura Fonti

- [F] Il run principale controlla 11 fonti e ne parsa 1. Fonte: `source_count=11` e `parsed_count=1` in `0180-Run_Summary.json`.
- [F] Il run principale ha `unsupported_source_count=10`. Fonte: `result.unsupported_source_count` in `0180-Run_Summary.json`.
- [F] La matrice V1.1 identifica `github_api_openai_codex_releases` come fonte P0 strutturata e lascia molte fonti OpenAI come P1/P2 diagnosticate o manual review. Fonte: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.
- [INT] La copertura fonti non e' sufficiente per procedere verso scheduler come prossimo blocco principale. Base: `parsed_count=1`, `source_count=11`, `unsupported_source_count=10`.

## K. Rischi Prima Dello Scheduler

- [F] La V1.1 non introduce scheduler. Fonte: `docs/architecture/0300_ACTIONABLE_RADAR_V1_1_CLOSURE_PACK.md`.
- [F] Lo scheduler e' fuori scope dello step 0310. Fonte: prompt 0310 fornito da Alberto.
- [INT] Uno scheduler giornaliero rischierebbe di ripetere un PASS di leggibilita' anche quando la copertura fonti resta bassa. Base: scorecard PASS con `parsed_count=1`.
- [INT] Uno scheduler prima della source coverage potrebbe rendere sistematico un bias verso release GitHub Codex API, lasciando fuori segnali OpenAI ufficiali non parsati. Base: unica fonte parsata `github_api_openai_codex_releases`.
- [PROP] Prima dello scheduler servono almeno: soglia/warning source coverage, policy per manual-review sources, decisione su retention Bridge e criterio umano per partial/success.

## L. Decisione Raccomandata Per Prossimo Blocco

- [PROP] Raccomandazione: `0320) Source Coverage V1.2 - aumentare fonti parsate / migliorare registry`.
- [INT] Questa raccomandazione e' preferibile allo scheduler perche' il run reale conferma `parsed_count=1` su `source_count=11`. Base: `0180-Run_Summary.json`.
- [INT] Questa raccomandazione e' preferibile a un blocco solo action quality perche' molte azioni restano genericamente Codex/API proprio perche' il contenuto utile arriva da una sola fonte strutturata. Base: `github_api_openai_codex_releases` come unica fonte parsata e `monitor_only_action_count=50`.
- [PROP] Ambito consigliato per 0320: migliorare source registry quality, cercare una seconda fonte strutturata o un parser conservativo con fixture offline, e introdurre warning di coverage senza introdurre scheduler.
