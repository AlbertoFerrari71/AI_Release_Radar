# 0430) Coverage Warning Policy

## A. Obiettivo

- [F] Il gate automation e' implementato in `radar/automation_gate.py`. Fonte: `radar/automation_gate.py`.
- [F] La scorecard report puo' essere `PASS` anche con `parsed_count=1` su 11. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] Lo step 0410-0500 richiede che bassa coverage non possa essere interpretata come PASS pieno. Fonte: prompt `0410-0500` salvato nel Bridge.
- [INT] La policy deve distinguere qualita' del report, copertura fonti e readiness scheduler. Base: `docs/architecture/0360_AUTOMATION_GATE_POLICY.md`, `docs/reviews/0390_DAILY_RUN_READINESS_REVIEW.md`.

## B. Regole Implementate

- [F] `parsed_count=0` genera failure `parsed_count_zero`. Fonte: `radar/automation_gate.py`, `tests/test_automation_gate.py`.
- [F] `source_count=0` genera failure `source_count_zero`. Fonte: `radar/automation_gate.py`.
- [F] `parsed_count/source_count < 0.50` genera warning `low_source_coverage`. Fonte: `radar/automation_gate.py`.
- [F] `manual_review_required_count > 0` genera warning. Fonte: `radar/automation_gate.py`.
- [F] `unsupported_source_count/source_count >= 0.50` genera warning. Fonte: `radar/automation_gate.py`.
- [F] `report_scorecard_status != PASS` genera warning. Fonte: `radar/automation_gate.py`.
- [F] `direct_action_count > 0` produce `ACTION_REVIEW_REQUIRED` se non ci sono failure. Fonte: `radar/automation_gate.py`.

## C. Scheduler Readiness Recommendation

- [F] Il gate espone `scheduler_readiness_recommendation` con valori `GO`, `GO_WITH_WARNINGS`, `HOLD`, `STOP`. Fonte: `radar/automation_gate.py`.
- [F] Failure strutturali producono `STOP`. Fonte: `radar/automation_gate.py`, `tests/test_automation_gate.py`.
- [F] Coverage sotto 0.25, direct action, manual review o unsupported alto producono `HOLD`. Fonte: `radar/automation_gate.py`, `tests/test_automation_gate.py`.
- [F] Warning non bloccanti producono `GO_WITH_WARNINGS`. Fonte: `radar/automation_gate.py`.
- [F] Gate pulito senza warning produce `GO`. Fonte: `radar/automation_gate.py`, `tests/test_automation_gate.py`.
- [INT] `GO` nel campo readiness non attiva scheduler: lo scheduler reale resta vietato senza step L3 autorizzato. Base: `AGENTS.md`.

## D. Casi Offline Coperti

- [F] `parsed_count=0` e' coperto da test. Fonte: `tests/test_automation_gate.py`.
- [F] `parsed_count=1/11` con scorecard `PASS` produce warning coverage e non e' `PASS` pieno. Fonte: `tests/test_automation_gate.py`.
- [F] Coverage pulita sopra soglia puo' produrre gate `PASS`. Fonte: `tests/test_automation_gate.py`.
- [F] Manual review richiesta produce warning. Fonte: `tests/test_automation_gate.py`.
- [F] Manual review alta produce warning. Fonte: `tests/test_automation_gate.py`.

## E. Esito

- [F] La policy impedisce falso verde con coverage bassa. Fonte: `radar/automation_gate.py`, `tests/test_automation_gate.py`.
- [PROP] Usare `scheduler_readiness_recommendation` insieme alla manual review queue prima di qualunque step scheduler.
