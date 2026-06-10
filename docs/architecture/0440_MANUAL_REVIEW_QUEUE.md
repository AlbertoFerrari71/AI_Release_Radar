# 0440) Manual Review Queue

## A. Obiettivo

- [F] Il super-step 0410-0500 richiede una coda deterministica per fonti o azioni che richiedono review manuale. Fonte: prompt `0410-0500` salvato nel Bridge.
- [F] I `source_diagnostics` sono prodotti da `radar/live_snapshot.py` e inclusi nel run summary reale. Fonte: `radar/live_snapshot.py`, `radar/real_run.py`.
- [F] L'automation gate legge il run summary e produce output JSON/Markdown fuori repository quando usato da `daily-sim`. Fonte: `radar/automation_gate.py`, `radar/cli.py`.

## B. Implementazione

- [F] La queue e' costruita da `radar/manual_review_queue.py`. Fonte: `radar/manual_review_queue.py`.
- [F] Il gate include `manual_review_queue` e `manual_review_queue_count` nel risultato serializzato. Fonte: `radar/automation_gate.py`.
- [F] Il Markdown del gate contiene una sezione `Manual Review Queue`. Fonte: `radar/automation_gate.py`.
- [F] `daily-sim` include `manual_review_queue`, `manual_review_queue_count` e `scheduler_readiness_recommendation` nel summary JSON. Fonte: `radar/cli.py`.
- [F] La queue e' testata offline. Fonte: `tests/test_manual_review_queue.py`, `tests/test_automation_gate.py`.

## C. Schema Riga Queue

Ogni riga contiene:

- [F] `type`: `source` o `action`. Fonte: `radar/manual_review_queue.py`.
- [F] `source_id`: source id o `0180_real_radar_run` per righe aggregate. Fonte: `radar/manual_review_queue.py`.
- [F] `reason`: motivo deterministico, per esempio `manual_review_required`, `fetched_but_unsupported`, `direct_actions_present`. Fonte: `radar/manual_review_queue.py`.
- [F] `severity`: `medium`, `high` o `critical`. Fonte: `radar/manual_review_queue.py`.
- [F] `recommended_follow_up`: follow-up deterministico. Fonte: `radar/manual_review_queue.py`.
- [F] `blocking_for_scheduler`: boolean. Fonte: `radar/manual_review_queue.py`.

## D. Regole

- [F] Fonti `manual_review_required`, `fetched_but_unsupported`, `fetch_failed`, `parser_failed`, `fetched_but_truncated` e `fetched_but_empty` entrano in queue. Fonte: `radar/manual_review_queue.py`.
- [F] `direct_action_count > 0` aggiunge una riga `action` con `reason=direct_actions_present`. Fonte: `radar/manual_review_queue.py`.
- [F] `parsed_count=0` aggiunge una riga critica `parsed_count_zero`. Fonte: `radar/manual_review_queue.py`.
- [F] Fonti P0/P1 o status manual/failure hanno severita' alta. Fonte: `radar/manual_review_queue.py`.
- [F] La queue e' ordinata deterministicamente. Fonte: `radar/manual_review_queue.py`.

## E. Limiti

- [F] La queue non esegue azioni automatiche. Fonte: `radar/manual_review_queue.py`, `radar/automation_gate.py`.
- [F] La queue non crea scheduler, task Windows, notifiche o chiamate LLM. Fonte: `radar/manual_review_queue.py`, `radar/cli.py`.
- [INT] Una queue non vuota e' compatibile con daily-sim controllato, ma blocca scheduler operativo pieno finche' Alberto non revisiona le righe rilevanti. Base: `docs/architecture/0430_COVERAGE_WARNING_POLICY.md`.

## F. Esito

- [F] Manual review queue disponibile in gate JSON/Markdown e daily-sim summary. Fonte: `radar/automation_gate.py`, `radar/cli.py`.
- [PROP] Usare la queue come lista di lavoro manuale prima di qualunque step scheduler L3.
