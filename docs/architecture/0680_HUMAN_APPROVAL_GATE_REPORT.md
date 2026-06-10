# 0680) Human Approval Gate Report

## A. Obiettivo

- [F] Il report HAG e' implementato in `radar/hag_report.py`. Fonte: `radar/hag_report.py`.
- [F] I test offline sono in `tests/test_hag_report.py`. Fonte: `tests/test_hag_report.py`.

## B. Contenuto

- [F] Il report indica cosa e' successo, cosa conta, cosa e' monitor-only, quali azioni sono bloccate, quali prompt sono suggeriti e cosa e' vietato fare automaticamente. Fonte: `radar/hag_report.py`.
- [F] Le decisioni esposte sono A/B/C/D. Fonte: `radar/hag_report.py`.
- [F] Il report dichiara `auto_actions_executed=false`, `emails_sent=false` e `llm_called=false`. Fonte: `radar/hag_report.py`.

## C. Stati

- [F] `FAIL_STOP` indica blocco su gate complessivo FAIL. Fonte: `radar/hag_report.py`.
- [F] `HOLD_FOR_HUMAN_APPROVAL` indica blocco coverage o manual review. Fonte: `radar/hag_report.py`.
- [F] `HUMAN_APPROVAL_REQUIRED` indica che serve decisione umana anche senza failure strutturale. Fonte: `radar/hag_report.py`.
- [F] `NO_ACTION_REQUIRED` indica che non emergono azioni da approvare. Fonte: `radar/hag_report.py`.
