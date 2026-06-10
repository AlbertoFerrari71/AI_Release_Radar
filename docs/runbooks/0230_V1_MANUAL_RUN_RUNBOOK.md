# 0230) V1 Manual Run Runbook

## Scopo

- [F] AI Release Radar osserva fonti OpenAI/Codex, costruisce snapshot, confronta gli item e produce report Markdown con impatti progetto. Fonte: `radar/live_snapshot.py`, `radar/real_run.py`, `radar/report_engine.py`.
- [F] La V1 manuale si esegue a mano tramite CLI e non attiva scheduler. Fonte: `radar/cli.py`, `radar/real_run.py`.
- [F] La V1 manuale scrive output runtime fuori repository. Fonte: `radar/real_run.py`.
- [F] Il repository vieta file `LAST-*` e `latest-*`. Fonte: `AGENTS.md`, `radar/real_run.py`, `radar/live_snapshot.py`.

## Cosa Fa Oggi

- [F] `real-run` esegue live snapshot read-only, combina gli snapshot, calcola diff, classificazione, score, impatti progetto e report. Fonte: `radar/real_run.py`.
- [F] `real-run --profile manual` usa il registry sorgenti di default se `--source-registry` non e' specificato. Fonte: `radar/cli.py`.
- [F] Il profilo manuale mantiene `--output-dir` obbligatorio. Fonte: `radar/cli.py`.
- [F] Il profilo manuale imposta 11 fonti massime, timeout 30 secondi e `max_bytes` 2000000 quando quei parametri sono omessi. Fonte: `radar/cli.py`.
- [F] Il run scrive full report, compact report, run summary, run index entry e `runs_index.jsonl`. Fonte: `radar/real_run.py`.
- [F] Il run summary include scorecard, conteggi `direct_action`, `monitor_only`, `no_action` e conteggio fonti unsupported. Fonte: `radar/real_run.py`.

## Cosa Non Fa Ancora

- [F] Non attiva Windows Task Scheduler o altri scheduler. Fonte: `radar/cli.py`, `AGENTS.md`.
- [F] Non esegue modifiche automatiche sui progetti impattati. Fonte: `radar/project_impact.py`, `radar/real_run.py`.
- [F] Non chiama LLM automaticamente. Fonte: `radar/real_run.py`.
- [F] Non crea puntatori `LAST-*` o `latest-*`. Fonte: `radar/real_run.py`, `radar/run_index.py`.
- [F] Non garantisce parsing utile per tutte le fonti HTML ufficiali. Fonte: `radar/live_snapshot.py`, `docs/architecture/0190_FIRST_REAL_OUTPUT_PARSER_COVERAGE_HARDENING.md`.

## Comando Consigliato

Eseguire da PowerShell nel repository:

```powershell
Set-Location "C:\Users\alberto.ferrari\source\repos\AI_Release_Radar"
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$out = "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs\0230_manual_run_$stamp"
python -m radar.cli real-run --profile manual --output-dir $out
```

- [F] `--output-dir` deve puntare fuori repository. Fonte: `radar/real_run.py`.
- [F] Il percorso Bridge sopra e' fuori repository. Fonte: prompt 0200-0230 fornito da Alberto.
- [F] Il nome directory e' numerato/datato e non usa `LAST-*` o `latest-*`. Fonte: prompt 0200-0230 fornito da Alberto, `AGENTS.md`.

## Dove Sono Gli Output

- [F] Il full report e' `0180-Report_Full.md` nella directory output. Fonte: `radar/real_run.py`.
- [F] Il compact report e' `0180-Report_Compact.md` nella directory output. Fonte: `radar/real_run.py`.
- [F] Il run summary e' `0180-Run_Summary.json` nella directory output. Fonte: `radar/real_run.py`.
- [F] La singola riga indice del run e' `0180-Run_Index_Entry.json`. Fonte: `radar/real_run.py`.
- [F] Lo storico append-only e' `runs_index.jsonl`. Fonte: `radar/real_run.py`, `radar/run_index.py`.

## Come Leggere Il Compact Report

- [F] Il compact report mostra status, conteggi source, conteggi item, top item e top action. Fonte: `radar/real_run.py`.
- [F] Il compact report mostra lo stato scorecard. Fonte: `radar/real_run.py`.
- [F] Le azioni top usano titolo e URL quando disponibili, non solo `item_id`. Fonte: `radar/real_run.py`, `tests/test_real_run.py`.
- [INT] Usare il compact report per decidere se aprire il full report e quali progetti controllare per primi. Fonte: `radar/real_run.py`.

## Come Leggere Il Full Report

- [F] Il full report include executive summary, note run, source diagnostics, item osservati, impatti progetto, rischi e prossimo step. Fonte: `radar/real_run.py`.
- [F] Ogni item osservato mostra titolo/versione, provider, `source_id`, URL, data pubblicazione, categoria, severita' e score quando disponibili. Fonte: `radar/real_run.py`, `tests/test_real_run.py`.
- [F] La diagnostica source mostra `diagnostic_status`, `manual_review_required`, `fetch_status`, HTTP status, `parser_status`, `error_code`, item count e follow-up. Fonte: `radar/live_snapshot.py`, `radar/real_run.py`.
- [F] Il full report include `Report Review Scorecard`. Fonte: `radar/real_run.py`, `radar/report_scorecard.py`.

## Come Leggere Gli Action Type

- [F] `direct_action` indica un segnale diretto per il progetto. Fonte: `radar/project_impact.py`.
- [F] `monitor_only` mantiene il progetto visibile ma non apre lavoro implementativo senza segnale diretto. Fonte: `radar/project_impact.py`.
- [F] `no_action` indica che non va aperto un task di progetto. Fonte: `radar/project_impact.py`.
- [INT] Per una release Codex generica, progetti non-Codex possono restare monitor-only invece di ricevere azioni tecniche forti. Fonte: `radar/project_impact.py`, `tests/test_project_impact.py`.

## Interpretazione Status

- [F] `CHANGES_FOUND` indica item nuovi, cambiati o rimossi senza condizione piu' severa. Fonte: `radar/report_engine.py`, `radar/real_run.py`.
- [F] `NO_CHANGE` indica assenza di item nuovi, cambiati o rimossi quando esiste base parsata confrontabile. Fonte: `radar/report_engine.py`.
- [F] `NO_PARSED_ITEMS` indica fonti presenti ma zero fonti parsate. Fonte: `radar/real_run.py`.
- [F] `partial` e' uno status del live snapshot quando una o piu' fonti falliscono. Fonte: `radar/live_snapshot.py`.
- [INT] Un real-run con live snapshot `partial` puo' comunque produrre report utile se almeno una fonte e' parsata. Fonte: `radar/live_snapshot.py`, `radar/real_run.py`.

## Fonti 403

- [F] Una fonte che restituisce HTTP 403 viene trattata come fetch non riuscito o unexpected status nel percorso live. Fonte: `radar/source_fetcher.py`, `radar/live_snapshot.py`.
- [F] La diagnostica V1.1 marca 401/403 come `manual_review_required`. Fonte: `radar/live_snapshot.py`, `tests/test_live_snapshot.py`.
- [INT] Se una fonte 403 non blocca tutte le fonti, leggere `source_diagnostics` e non interpretare automaticamente il run come falso verde. Fonte: `radar/live_snapshot.py`, `radar/real_run.py`.
- [PROP] Per fonti 403 ripetute, valutare registry note, source alternativa strutturata o esclusione temporanea in uno step dedicato.

## Parser Unsupported

- [F] Le fonti non supportate sono marcate `parser_skipped_unsupported_source`. Fonte: `radar/live_snapshot.py`.
- [F] La diagnostica V1.1 espone `fetched_but_unsupported` per fonti fetchate ma non parsate. Fonte: `radar/live_snapshot.py`.
- [F] Molte fonti OpenAI HTML restano fetchate ma non parsate. Fonte: `docs/architecture/0190_FIRST_REAL_OUTPUT_PARSER_COVERAGE_HARDENING.md`.
- [PROP] Prima di introdurre un parser HTML live, preferire una fonte machine-readable o un parser conservativo con fixture offline.

## Scorecard E Confronto

- [F] La scorecard valuta titoli, link fonte, parsed source count, source diagnostics, azioni progetto, top actions, noise control e next step. Fonte: `radar/report_scorecard.py`.
- [F] Il confronto offline V1/V1.1 e' disponibile in `radar/run_comparison.py`. Fonte: `radar/run_comparison.py`.
- [INT] Usare il confronto per verificare se V1.1 riduce azioni dirette generiche e rende esplicite le azioni monitor-only.
- [INT] Dopo la review 0310, leggere `PASS` come qualita' report e verificare separatamente copertura fonti e rumore azioni prima di pianificare scheduler. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.

## Checklist Prima Dello Scheduler

- [F] Nessuno scheduler e' attivo nella V1 manuale. Fonte: `radar/cli.py`, `AGENTS.md`.
- [PROP] Prima dello scheduler verificare: output Bridge stabile, `runs_index.jsonl` valido, zero falsi verdi, gestione 403 documentata, parser coverage sufficiente, test full PASS, runbook aggiornato.
- [PROP] Lo scheduler deve restare fuori scope finche' un prompt dedicato non autorizza L3.

## Criteri Dopo V1.1

- [F] 0310 ha rivisto un real-run V1.1 fuori repo e ha documentato la review in `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [PROP] Con `parsed_count=1` su 11 fonti nel run analizzato, privilegiare parser/source coverage prima dello scheduler. Fonte: `docs/decisions/0310_DECISIONS.md`.
- [PROP] Se il confronto e' buono, preparare un readiness gate scheduler dedicato senza attivarlo nello stesso step.

## Limiti Noti

- [F] Una sola fonte strutturata reale e' attualmente parsata in modo utile: `github_api_openai_codex_releases`. Fonte: prompt 0200-0230 fornito da Alberto, `radar/live_snapshot.py`.
- [F] Molte fonti OpenAI HTML sono fetchate ma non parsate. Fonte: `docs/architecture/0190_FIRST_REAL_OUTPUT_PARSER_COVERAGE_HARDENING.md`.
- [F] Alcune fonti possono restituire 403 o status inattesi. Fonte: prompt 0200-0230 fornito da Alberto.
- [F] Il report suggerisce azioni ma non le esegue. Fonte: `radar/project_impact.py`, `radar/real_run.py`.
- [F] Non ci sono chiamate LLM automatiche. Fonte: `radar/real_run.py`.
- [F] Non c'e' scheduler attivo. Fonte: `radar/cli.py`, `AGENTS.md`.
