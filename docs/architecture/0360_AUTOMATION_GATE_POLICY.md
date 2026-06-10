# 0360) Automation Gate Policy

## A. Scopo

- [F] `real-run` produce report, summary e `runs_index.jsonl` fuori repository. Fonte: `radar/real_run.py`.
- [F] La review 0310 ha concluso che `report_scorecard_status=PASS` non equivale a scheduler readiness quando `parsed_count=1` su 11. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] Lo step 0340 definisce il contratto minimo di run automatico/simulato. Fonte: `docs/architecture/0340_AUTOMATION_RUN_CONTRACT.md`.
- [INT] Il gate deve proteggere contro il falso verde: output leggibile ma coverage insufficiente, index corrotto o output nel posto sbagliato. Base: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.

## B. Implementazione

- [F] La policy deterministica e' implementata in `radar/automation_gate.py`. Fonte: `radar/automation_gate.py`.
- [F] `daily-sim` valuta il gate dopo `real-run` e scrive `0350-Daily_Sim_Gate.json` e `0350-Daily_Sim_Gate.md` nella directory runtime fuori repo. Fonte: `radar/cli.py`.
- [F] Il gate usa `validate_run_index` per verificare `runs_index.jsonl` senza riscriverlo. Fonte: `radar/automation_gate.py`, `radar/run_index.py`.
- [F] Il gate non crea scheduler, task Windows, notifiche o chiamate LLM. Fonte: `radar/automation_gate.py`, `radar/cli.py`.

## C. Stati

| stato | significato | esito operativo |
|---|---|---|
| `FAIL` | [F] Condizione strutturale non rispettata: output mancante, summary mancante, index corrotto, output dentro repo, `source_count=0`, `parsed_count=0` o item zero senza status esplicativo. Fonte: `radar/automation_gate.py`. | [PROP] Fermare scheduler e correggere prima di proseguire. |
| `PASS_WITH_WARNINGS` | [F] Run completo ma con warning: coverage bassa, manual review, unsupported alto, scorecard non PASS o volume monitor-only alto. Fonte: `radar/automation_gate.py`. | [PROP] Consentire solo simulazione controllata e review umana. |
| `ACTION_REVIEW_REQUIRED` | [F] Run completo con una o piu' `direct_action`. Fonte: `radar/automation_gate.py`. | [PROP] Richiedere review manuale prima di aprire azioni operative. |
| `PASS` | [F] Nessun failure, nessun warning e nessuna direct action. Fonte: `radar/automation_gate.py`. | [PROP] Idoneo a una review di readiness, non ad attivare scheduler senza prompt dedicato. |

## D. Regole FAIL

- [F] `FAIL` se `0180-Run_Summary.json` manca o non contiene `result`. Fonte: `radar/automation_gate.py`.
- [F] `FAIL` se `0180-Report_Full.md`, `0180-Report_Compact.md`, `0180-Run_Index_Entry.json` o `runs_index.jsonl` mancano. Fonte: `radar/automation_gate.py`.
- [F] `FAIL` se `runs_index.jsonl` e' corrotto secondo `validate_run_index`. Fonte: `radar/automation_gate.py`, `radar/run_index.py`.
- [F] `FAIL` se `output_dir` e' dentro il repository. Fonte: `radar/automation_gate.py`.
- [F] `FAIL` se `source_count=0` o `parsed_count=0`. Fonte: `radar/automation_gate.py`.
- [F] `FAIL` se `item_count=0` e lo status non e' `NO_CHANGE` o `NO_PARSED_ITEMS`. Fonte: `radar/automation_gate.py`.

## E. Regole Warning

- [F] `WARN` se `parsed_count/source_count` e' sotto 0.50. Fonte: `radar/automation_gate.py`.
- [F] `WARN` se `manual_review_required_count>0`. Fonte: `radar/automation_gate.py`.
- [F] `WARN` se `unsupported_source_count/source_count>=0.50`. Fonte: `radar/automation_gate.py`.
- [F] `WARN` se `report_scorecard_status` e' diverso da `PASS`. Fonte: `radar/automation_gate.py`.
- [F] `WARN` se il volume `monitor_only` e' almeno il 75% delle azioni. Fonte: `radar/automation_gate.py`.
- [F] `WARN` se `failed_count>0`. Fonte: `radar/automation_gate.py`.

## F. Regola Direct Action

- [F] Se `direct_action_count>0` e non ci sono failure, lo stato e' `ACTION_REVIEW_REQUIRED`. Fonte: `radar/automation_gate.py`.
- [INT] Questo stato e' piu' prudente di `PASS_WITH_WARNINGS` perche' segnala che il report propone almeno un'azione diretta. Base: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [PROP] Nessuna direct action deve essere eseguita automaticamente da questo progetto.

## G. Implicazione Per Scheduler

- [INT] Con `parsed_count=1/11`, il gate deve produrre almeno warning coverage, anche quando la scorecard report e' `PASS`. Base: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [PROP] Scheduler reale resta fuori scope finche' un prompt L3 dedicato non lo autorizza e finche' il gate non e' stato osservato su run ripetuti senza failure.
