# 0630) Daily Report Quality Gate v2

## A. Obiettivo

- [F] Lo step 0630 richiede tre dimensioni separate: `report_readability`, `source_coverage` e `actionability`. Fonte: prompt `0610-0750`.
- [F] Il modulo implementato e' `radar/daily_quality_gate.py`. Fonte: `radar/daily_quality_gate.py`.
- [F] I test offline sono in `tests/test_daily_quality_gate.py`. Fonte: `tests/test_daily_quality_gate.py`.

## B. Campi

- [F] `report_readability_status` deriva dallo status della scorecard report. Fonte: `radar/daily_quality_gate.py`, `radar/report_scorecard.py`.
- [F] `source_coverage_status` usa `source_count`, `parsed_count`, `parsed_ratio`, source warning e failure. Fonte: `radar/daily_quality_gate.py`, `radar/automation_gate.py`.
- [F] `actionability_status` usa gate status, direct actions, manual review queue e warning. Fonte: `radar/daily_quality_gate.py`, `radar/automation_gate.py`.
- [F] `overall_daily_review_status` usa priorita' deterministica: `FAIL` > `ACTION_REVIEW_REQUIRED` > `HOLD` > `WARN` > `PASS`. Fonte: `radar/daily_quality_gate.py`.
- [F] Il gate produce warning espliciti. Fonte: `radar/daily_quality_gate.py`.

## C. Regola Anti Falso Verde

- [F] Il risultato complessivo non puo' essere `PASS` se una dimensione e' `HOLD`, `ACTION_REVIEW_REQUIRED` o `FAIL`. Fonte: `radar/daily_quality_gate.py`, `tests/test_daily_quality_gate.py`.
- [F] La compatibilita' con la scorecard attuale e' mantenuta: `report_scorecard_status=PASS` alimenta solo `report_readability_status`, non la readiness complessiva. Fonte: `radar/daily_quality_gate.py`, `radar/report_scorecard.py`.

## D. Esempio Baseline

```text
report_readability_status = PASS
source_coverage_status = WARN
actionability_status = ACTION_REVIEW_REQUIRED
overall_daily_review_status = ACTION_REVIEW_REQUIRED
```

- [F] Questo caso e' coperto da test offline. Fonte: `tests/test_daily_quality_gate.py`.
