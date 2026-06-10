# 0650) Action Triage Engine

## A. Obiettivo

- [F] Il triage deterministico e' implementato in `radar/action_triage.py`. Fonte: `radar/action_triage.py`.
- [F] I test offline sono in `tests/test_action_triage.py`. Fonte: `tests/test_action_triage.py`.

## B. Classi

- [F] Le classi supportate sono `ignore`, `monitor`, `manual_review`, `codex_prompt_candidate`, `blocked_by_coverage` e `blocked_by_manual_review`. Fonte: `radar/action_triage.py`.
- [F] Il triage usa conteggi direct/monitor/manual, source coverage, project profile opzionale, category, severity/score e gate status quando disponibili. Fonte: `radar/action_triage.py`.
- [F] Il triage non esegue azioni e produce solo JSON serializzabile. Fonte: `radar/action_triage.py`.

## C. Regola Operativa

- [F] Direct actions con coverage bassa diventano `blocked_by_coverage`. Fonte: `radar/action_triage.py`, `tests/test_action_triage.py`.
- [F] Manual review queue produce entries `manual_review`. Fonte: `radar/action_triage.py`.
- [F] Direct action con coverage e gate puliti puo' diventare `codex_prompt_candidate`, sempre come proposta. Fonte: `radar/action_triage.py`, `tests/test_action_triage.py`.
