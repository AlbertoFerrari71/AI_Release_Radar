# 0230) V1 Manual Run Decisions

## Strategia Step

- [F] Gli step 0200, 0210, 0220 e 0230 sono stati trattati come una stabilizzazione V1 manuale unica con commit separati. Fonte: prompt 0200-0230 fornito da Alberto.
- [INT] Una PR batch e' preferibile perche' report readability, profilo manuale, indice run e runbook descrivono un unico flusso operativo V1. Fonte: prompt 0200-0230 fornito da Alberto.
- [F] Non e' consentito auto-merge per questa fase. Fonte: prompt 0200-0230 fornito da Alberto, `AGENTS.md`.

## Report Readability

- [F] Il report reale compatto ora mostra top item con titolo, source label, provider, data, categoria, severita', score e URL. Fonte: `radar/real_run.py`.
- [F] Le top action del report compatto usano titolo/URL quando disponibili. Fonte: `radar/real_run.py`, `tests/test_real_run.py`.
- [F] Il full report reale mostra anche `item_id`, provider, `source_id`, published date, score e impact reason. Fonte: `radar/real_run.py`.
- [F] Il fallback per item senza titolo e' `Untitled item from <source_id>`. Fonte: `radar/real_run.py`, `tests/test_real_run.py`.

## Profilo Manuale

- [F] `--profile manual` e' stato aggiunto a `real-run`. Fonte: `radar/cli.py`.
- [F] `--output-dir` resta richiesto anche con `--profile manual`. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] Senza `--profile manual`, `--source-registry` resta richiesto. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] Il profilo manuale non attiva scheduler e non introduce dipendenze. Fonte: `radar/cli.py`, `pyproject.toml`.

## Runs Index

- [F] `RunIndexEntry` ora supporta conteggi source/parser/item/fail/skip e timestamp. Fonte: `radar/models.py`.
- [F] `real-run` e `live-snapshot` valorizzano i nuovi campi dell'indice. Fonte: `radar/real_run.py`, `radar/live_snapshot.py`.
- [F] `validate_run_index` valida righe JSONL senza riscrivere l'indice. Fonte: `radar/run_index.py`.
- [F] Non e' stato creato alcun latest pointer. Fonte: `radar/run_index.py`, `tests/test_run_index.py`.

## Runbook E Chiusura V1

- [F] Il runbook V1 manuale e' `docs/runbooks/0230_V1_MANUAL_RUN_RUNBOOK.md`. Fonte: `docs/runbooks/0230_V1_MANUAL_RUN_RUNBOOK.md`.
- [F] Il closure pack architetturale e' `docs/architecture/0230_V1_MANUAL_RUN_CLOSURE_PACK.md`. Fonte: `docs/architecture/0230_V1_MANUAL_RUN_CLOSURE_PACK.md`.
- [F] Il runbook documenta `CHANGES_FOUND`, `NO_CHANGE`, `NO_PARSED_ITEMS`, `partial`, 403 e parser unsupported. Fonte: `docs/runbooks/0230_V1_MANUAL_RUN_RUNBOOK.md`.

## Rischio

- [F] La fase resta L1/L2 prudenziale perche' tocca logica offline/test e comportamento CLI `real-run`, ma non attiva scheduler. Fonte: prompt 0200-0230 fornito da Alberto, `radar/cli.py`.
- [F] Nessuna nuova dipendenza esterna e' stata aggiunta. Fonte: `pyproject.toml`.
- [F] Nessun file high-risk `AGENTS.md`, `.githooks/*`, `.github/*` o scheduler e' stato modificato. Fonte: `git diff --name-only` dello step 0200-0230.
- [PROP] MERGE_RECOMMENDATION: YES dopo review manuale della draft PR e gate PASS; NO AUTO-MERGE.

## Prossimo Step Consigliato

- [PROP] 0240) Parser/source coverage prioritization for manual V1, con focus su fonti OpenAI HTML non supportate o alternative strutturate.
