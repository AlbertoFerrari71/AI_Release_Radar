# 0460) Scheduler Readiness Checklist

## A. Scopo

- [F] Il repository vieta scheduler reali senza istruzione esplicita. Fonte: `AGENTS.md`.
- [F] `daily-sim` esegue simulazione controllata senza creare scheduler, task Windows o chiamate LLM. Fonte: `radar/cli.py`.
- [F] Lo step 0410-0500 richiede una checklist tecnica prima di qualunque scheduler reale. Fonte: prompt `0410-0500` salvato nel Bridge.
- [INT] Questa checklist valuta readiness, non autorizza l'attivazione dello scheduler. Base: `AGENTS.md`.

## B. Legenda

- [F] `PASS`: requisito soddisfatto nel perimetro attuale. Fonte: questa checklist.
- [F] `WARN`: requisito parzialmente soddisfatto, richiede review o follow-up. Fonte: questa checklist.
- [F] `FAIL`: requisito non soddisfatto e bloccante. Fonte: questa checklist.
- [F] `N/A`: non applicabile allo step corrente. Fonte: questa checklist.

## C. Checklist

| area | esito | evidenza | interpretazione |
|---|---|---|---|
| Source coverage | WARN | [F] Baseline V1.2 resta `parsed_count=1/11`. Fonte: `docs/architecture/0410_SOURCE_COVERAGE_V1_2_IMPLEMENTATION.md`. | [INT] Sufficiente per daily-sim supervisionato, non per scheduler pieno. |
| Automation gate | PASS | [F] Gate deterministico con status `PASS`, `PASS_WITH_WARNINGS`, `ACTION_REVIEW_REQUIRED`, `FAIL`. Fonte: `radar/automation_gate.py`, `tests/test_automation_gate.py`. | [INT] Blocca falsi verdi noti. |
| Manual review queue | PASS | [F] Queue disponibile in gate e daily-sim summary. Fonte: `radar/manual_review_queue.py`, `radar/automation_gate.py`, `radar/cli.py`. | [INT] Rende visibile il lavoro umano prima dello scheduler. |
| Bridge output path | PASS | [F] `daily-sim` richiede `--output-root` fuori repo. Fonte: `radar/cli.py`, `tests/test_cli.py`. | [INT] Output runtime separato dal codice. |
| runs_index integrity | PASS | [F] Gate valida `runs_index.jsonl`. Fonte: `radar/automation_gate.py`, `radar/run_index.py`. | [INT] Protegge lo storico run da corruzione silenziosa. |
| Failure handling | PASS | [F] Failure injection coprono summary/report mancanti, index corrotto, output nel repo, zero parsed e altri casi. Fonte: `tests/test_automation_gate.py`. | [INT] Base sufficiente per simulazione controllata. |
| Operator review | WARN | [F] Direct action produce `ACTION_REVIEW_REQUIRED`. Fonte: `radar/automation_gate.py`. | [INT] Serve lettura umana sistematica prima di qualunque azione. |
| Security/no secrets | PASS | [F] Nessuna API key e nessun secret sono richiesti dal flusso. Fonte: `radar/cli.py`, `AGENTS.md`. | [INT] Il flusso resta local/read-only verso fonti. |
| No output in repo | PASS | [F] `real-run`, `live-snapshot` e `daily-sim` rifiutano output dentro repo. Fonte: `radar/real_run.py`, `radar/live_snapshot.py`, `radar/cli.py`. | [INT] Riduce rischio di versionare runtime output. |
| No auto-action | PASS | [F] Il codice produce report e azioni consigliate ma non le esegue. Fonte: `radar/real_run.py`, `radar/project_impact.py`. | [INT] Compatible con review umana. |
| Windows environment | WARN | [F] Nessun task Windows e' creato da questo step. Fonte: `radar/cli.py`, `AGENTS.md`. | [INT] Prima dello scheduler reale serve uno step L3 su ambiente Windows. |
| Restore/disable plan | WARN | [F] Il dry-run design 0470 documenta un piano futuro di disabilitazione. Fonte: `docs/architecture/0470_SCHEDULER_DRY_RUN_DESIGN.md`. | [INT] Deve essere validato nello step L3, non qui. |
| Human approval gate | PASS | [F] Scheduler reale e merge su main restano vietati senza policy/prompt dedicato. Fonte: `AGENTS.md`. | [INT] Il gate umano resta attivo. |

## D. Decisione Checklist

- [INT] Scheduler readiness per dry/report futuro: `GO_WITH_WARNINGS`. Base: daily-sim, gate e queue sono disponibili, ma coverage resta bassa.
- [INT] Scheduler readiness per scheduler operativo pieno: `HOLD`. Base: `parsed_count=1/11`, manual review queue e direct actions richiedono review.
- [F] Lo scheduler reale non viene attivato nello step 0460. Fonte: questo documento.

## E. Prossimo Passo

- [PROP] Usare la checklist come prerequisito per un futuro step L3 esplicitamente autorizzato, limitato a scheduler dry/report e con piano di disable/restore verificato.
