# 0340) Automation Run Contract

## A. Scopo

- [F] La V1 manuale usa `real-run --profile manual` e scrive output runtime fuori repository. Fonte: `docs/runbooks/0230_V1_MANUAL_RUN_RUNBOOK.md`, `radar/real_run.py`.
- [F] Il repository vieta output runtime versionati e file `LAST-*` o `latest-*`. Fonte: `AGENTS.md`.
- [INT] Un run daily simulato deve essere auditabile come un run manuale, ma deve aggiungere una valutazione di automation readiness separata dalla scorecard report. Base: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.

## B. Output Obbligatori Fuori Repo

Ogni run simulato o automatico deve produrre, nella directory runtime fuori repository:

- [F] `0180-Run_Summary.json`. Fonte: `radar/real_run.py`.
- [F] `0180-Report_Compact.md`. Fonte: `radar/real_run.py`.
- [F] `0180-Report_Full.md`. Fonte: `radar/real_run.py`.
- [F] `0180-Run_Index_Entry.json`. Fonte: `radar/real_run.py`.
- [F] `runs_index.jsonl`. Fonte: `radar/real_run.py`, `radar/run_index.py`.
- [PROP] `0350-Daily_Sim_Summary.json`, se il run e' avviato dal simulatore daily.
- [PROP] `0350-Daily_Sim_Gate.md` e `0350-Daily_Sim_Gate.json`, se il run e' valutato dall'automation gate.

## C. Campi Minimi Nel Summary

`0180-Run_Summary.json` deve permettere di leggere almeno:

| campo | fonte attesa | obbligo |
|---|---|---|
| `run_id` | [F] `result.run_id` in `radar/real_run.py` | obbligatorio |
| `timestamp` | [F] `0180-Run_Index_Entry.json` / `runs_index.jsonl` in `radar/real_run.py` | obbligatorio |
| `status` | [F] `result.status` in `radar/real_run.py` | obbligatorio |
| `source_count` | [F] `result.source_count` in `radar/real_run.py` | obbligatorio |
| `parsed_count` | [F] `result.parsed_count` in `radar/real_run.py` | obbligatorio |
| `item_count` | [F] `result.item_count` in `radar/real_run.py` | obbligatorio |
| `failed_count` | [F] `result.failed_count` in `radar/real_run.py` | obbligatorio |
| `skipped_count` | [F] `result.skipped_count` in `radar/real_run.py` | obbligatorio |
| `unsupported_source_count` | [F] `result.unsupported_source_count` in `radar/real_run.py` | obbligatorio |
| `manual_review_required_count` | [PROP] derivato da `source_diagnostics` o serializzato nel `result` | obbligatorio per gate |
| `direct_action_count` | [F] `result.direct_action_count` in `radar/real_run.py` | obbligatorio |
| `monitor_only_action_count` | [F] `result.monitor_only_action_count` in `radar/real_run.py` | obbligatorio |
| `no_action_count` | [F] `result.no_action_count` in `radar/real_run.py` | obbligatorio |
| `report_scorecard_status` | [F] `result.report_scorecard_status` in `radar/real_run.py` | obbligatorio |
| `source_diagnostics` | [F] `source_diagnostics` in `radar/real_run.py` | obbligatorio |
| `output paths` | [F] `result.report_full`, `result.report_compact`, `result.run_summary`, `result.run_index_entry`, `result.runs_index` | obbligatorio |
| `next_step` | [F] `REAL_RUN_NEXT_STEP_RECOMMENDATION` in `radar/real_run.py` | obbligatorio per report; [PROP] serializzare anche in daily summary |

## D. Stati Minimi Del Gate

- [PROP] `FAIL`: output mancante, summary non leggibile, `source_count=0`, `parsed_count=0`, output dentro repo, index corrotto o report obbligatorio mancante.
- [PROP] `PASS_WITH_WARNINGS`: run completo ma coverage bassa, fonti manual review presenti, molte fonti unsupported o scorecard report diversa da `PASS`.
- [PROP] `ACTION_REVIEW_REQUIRED`: run completo con una o piu' `direct_action`.
- [PROP] `PASS`: run completo, coverage sopra soglia, report scorecard `PASS`, nessuna fonte manual review e nessun warning di automazione.

## E. Divieti

- [F] Output runtime nel repository vietato. Fonte: `AGENTS.md`, `radar/real_run.py`.
- [F] `LAST-*` e `latest-*` vietati. Fonte: `AGENTS.md`, `radar/run_index.py`, `radar/real_run.py`.
- [F] Scheduler non approvato vietato. Fonte: `AGENTS.md`.
- [F] Push diretto su `main` vietato. Fonte: `AGENTS.md`.
- [F] Chiamate LLM automatiche non presenti nella V1 manuale. Fonte: `docs/runbooks/0230_V1_MANUAL_RUN_RUNBOOK.md`.
- [PROP] Silent `PASS` vietato: ogni `PASS` deve provare file output, index valido, coverage e scorecard.

## F. Contratto Daily Simulation

- [PROP] `daily-sim` deve generare una directory datata sotto output root fuori repository.
- [PROP] `daily-sim` deve chiamare la logica `real-run --profile manual` o equivalente interno con gli stessi default sicuri.
- [PROP] `daily-sim` non deve creare scheduler, task Windows, notifiche automatiche o chiamate LLM.
- [PROP] `daily-sim` deve stampare almeno status, `source_count`, `parsed_count`, `item_count`, action counts, coverage warning, automation gate status, recommendation e output path.
