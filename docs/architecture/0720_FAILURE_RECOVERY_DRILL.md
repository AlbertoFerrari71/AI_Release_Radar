# 0720) Failure Recovery Drill

## A. Scopo

- [F] Lo step 0720 richiede scenari di fallimento e recupero. Fonte: prompt `0610-0750`.
- [F] L'automation gate ha gia' failure path per summary/report/index mancanti, output in repo, zero parsed e metriche invalide. Fonte: `radar/automation_gate.py`, `tests/test_automation_gate.py`.

## B. Scenari

| Scenario | Esito atteso | Fonte |
|---|---|---|
| task non partito | controllare `Get-ScheduledTaskInfo` e log Bridge | `docs/runbooks/0590_OPERATOR_REVIEW_FLOW.md` |
| run output mancante | gate `FAIL` o report assente | `radar/automation_gate.py` |
| gate `FAIL` | stop, fix-only step | `docs/runbooks/0590_OPERATOR_REVIEW_FLOW.md` |
| summary corrotto | gate `FAIL` con `run_summary_invalid` | `radar/automation_gate.py` |
| no parsed sources | gate `FAIL` con `parsed_count_zero` | `radar/automation_gate.py` |
| manual review queue troppo alta | HAG `HOLD_FOR_HUMAN_APPROVAL` | `radar/hag_report.py` |
| Bridge non accessibile | chiedere file/output ad Alberto | `docs/architecture/0620_RADAR_DONE_BRIDGE_RETRIEVAL_CONTRACT.md` |
| scheduler log assente | diagnosi task/action path e permessi | `docs/runbooks/0590_OPERATOR_REVIEW_FLOW.md` |

## C. Regola

- [F] Nessuno scenario autorizza auto-azioni o modifiche ad altri repository. Fonte: prompt `0610-0750`, `docs/decisions/0510_L3_SCHEDULER_DRY_REPORT_CONSENT.md`.
