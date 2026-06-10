# 0230) V1 Manual Run Closure Pack

## Stato V1 Manuale

- [F] La CLI espone `real-run` per generare snapshot live read-only e report manuali. Fonte: `radar/cli.py`, `radar/real_run.py`.
- [F] `real-run --profile manual` e' disponibile come profilo operativo semplice. Fonte: `radar/cli.py`.
- [F] `--output-dir` resta esplicito per il profilo manuale. Fonte: `radar/cli.py`.
- [F] Gli output runtime vengono rifiutati se puntano dentro il repository. Fonte: `radar/real_run.py`, `radar/live_snapshot.py`.
- [F] Gli output runtime vengono rifiutati se la directory finale usa `LAST-*` o `latest-*`. Fonte: `radar/real_run.py`, `radar/live_snapshot.py`.

## Componenti Coinvolti

- [F] `radar/cli.py` risolve argomenti CLI, profilo manuale e summary console. Fonte: `radar/cli.py`.
- [F] `radar/real_run.py` orchestra live snapshot, diff, classificazione, scoring, impatti e report. Fonte: `radar/real_run.py`.
- [F] `radar/live_snapshot.py` fetch/parsa fonti abilitate e scrive snapshot fuori repo. Fonte: `radar/live_snapshot.py`.
- [F] `radar/run_index.py` gestisce append e validazione di `runs_index.jsonl`. Fonte: `radar/run_index.py`.
- [F] `radar/models.py` definisce `RunIndexEntry` con campi per report, snapshot, conteggi e timestamp. Fonte: `radar/models.py`.

## Report Readability

- [F] Il full report reale mostra titolo/versione, provider, `source_id`, URL, data pubblicazione, categoria, severita', confidence e score degli item osservati. Fonte: `radar/real_run.py`.
- [F] Il compact report reale mostra top item leggibili e top action con titolo/URL quando disponibili. Fonte: `radar/real_run.py`.
- [F] Il fallback per item senza titolo e' `Untitled item from <source_id>`. Fonte: `radar/real_run.py`, `tests/test_real_run.py`.
- [F] Le azioni principali del compact report non mostrano solo `item_id` quando titolo o URL sono disponibili. Fonte: `tests/test_real_run.py`.

## Profilo Manuale

- [F] Il profilo manuale imposta registry default solo se `--source-registry` e' omesso. Fonte: `radar/cli.py`.
- [F] Il profilo manuale imposta timeout 30 secondi, max 11 fonti e max bytes 2000000 quando quei parametri sono omessi. Fonte: `radar/cli.py`.
- [F] Il comando esistente con `--source-registry` esplicito resta compatibile. Fonte: `radar/cli.py`, `tests/test_cli.py`.

## Storico Run

- [F] `runs_index.jsonl` resta append-only. Fonte: `radar/run_index.py`.
- [F] Ogni `RunIndexEntry` puo' contenere `source_count`, `parsed_count`, `item_count`, `failed_count`, `skipped_count` e `timestamp`. Fonte: `radar/models.py`.
- [F] `real-run` valorizza report full, report compact, snapshot dir, conteggi e timestamp nell'indice. Fonte: `radar/real_run.py`.
- [F] `live-snapshot` valorizza conteggi source/parser/item e timestamp nell'indice anche senza report. Fonte: `radar/live_snapshot.py`.
- [F] `validate_run_index` legge un indice e restituisce problemi per riga senza riscriverlo. Fonte: `radar/run_index.py`.

## Output Attesi

- [F] Full report: `0180-Report_Full.md`. Fonte: `radar/real_run.py`.
- [F] Compact report: `0180-Report_Compact.md`. Fonte: `radar/real_run.py`.
- [F] Run summary: `0180-Run_Summary.json`. Fonte: `radar/real_run.py`.
- [F] Run index entry: `0180-Run_Index_Entry.json`. Fonte: `radar/real_run.py`.
- [F] Runs index: `runs_index.jsonl`. Fonte: `radar/real_run.py`, `radar/run_index.py`.

## Stati E Diagnostica

- [F] `NO_PARSED_ITEMS` evita il falso verde quando ci sono fonti ma zero parsed source. Fonte: `radar/real_run.py`.
- [F] `source_diagnostics` include provider, source type, fetch status, HTTP status, parser status, item count ed errore. Fonte: `radar/live_snapshot.py`, `radar/real_run.py`.
- [F] `partial` e' prodotto dal live snapshot se ci sono errori o fetch failure. Fonte: `radar/live_snapshot.py`.

## Limiti Residui

- [F] Le fonti HTML non supportate restano `parser_skipped_unsupported_source`. Fonte: `radar/live_snapshot.py`.
- [F] Una fonte puo' fallire per HTTP 403 o status inatteso. Fonte: prompt 0200-0230 fornito da Alberto.
- [F] Il progetto non ha scheduler attivo. Fonte: `AGENTS.md`, `radar/cli.py`.
- [F] Il report produce proposte, non modifiche automatiche su altri repository. Fonte: `radar/project_impact.py`, `radar/real_run.py`.

## Readiness Per Step Successivi

- [INT] La V1 manuale e' sufficiente per run supervisionati perche' command, output, report e indice sono documentati e testati. Fonte: `radar/cli.py`, `radar/real_run.py`, `radar/run_index.py`, `tests/`.
- [PROP] Prima di L3 scheduler servono criteri espliciti su frequenza, path Bridge, retention, alerting, fallimenti parziali e revisione umana.
- [PROP] Il prossimo incremento dovrebbe privilegiare parser coverage o qualita' source registry, non automazione scheduler.
