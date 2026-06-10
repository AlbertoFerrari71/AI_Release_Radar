# 0450) Daily Sim Regression Pack

## A. Obiettivo

- [F] `daily-sim` e' implementato in `radar/cli.py`. Fonte: `radar/cli.py`.
- [F] `daily-sim` deve restare simulazione controllata e non creare scheduler o task Windows. Fonte: `radar/cli.py`, `AGENTS.md`.
- [F] Il super-step 0410-0500 richiede regressioni offline per output fuori repo, gate report, summary, ACTION_REVIEW_REQUIRED, coverage warning e manual review queue. Fonte: prompt `0410-0500` salvato nel Bridge.

## B. Regressioni Coperte

- [F] `daily-sim` crea una directory datata sotto `--output-root`. Fonte: `tests/test_cli.py`.
- [F] `daily-sim` rifiuta un output root dentro repository. Fonte: `tests/test_cli.py`.
- [F] `daily-sim` produce `0350-Daily_Sim_Summary.json`. Fonte: `tests/test_cli.py`.
- [F] `daily-sim` produce `0350-Daily_Sim_Gate.json` e `0350-Daily_Sim_Gate.md`. Fonte: `tests/test_cli.py`.
- [F] `daily-sim` propaga `ACTION_REVIEW_REQUIRED` quando il gate lo produce. Fonte: `tests/test_cli.py`.
- [F] `daily-sim` include coverage warnings nel gate JSON. Fonte: `tests/test_cli.py`.
- [F] `daily-sim` include `manual_review_queue` e `manual_review_queue_count`. Fonte: `tests/test_cli.py`.
- [F] `daily-sim` serializza `scheduler_readiness_recommendation`. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] I test verificano `scheduler_activated=False`, `windows_task_created=False` e `llm_called=False`. Fonte: `tests/test_cli.py`.

## C. Strategia Test

- [F] I test usano mock/fake runner offline e non richiedono live fetch. Fonte: `tests/test_cli.py`.
- [F] Il fake real-run scrive output minimi validi fuori repo per consentire al gate di validare report, summary e `runs_index.jsonl`. Fonte: `tests/test_cli.py`.
- [F] Nessun output runtime dei test viene scritto nel repository. Fonte: `tests/test_cli.py`.

## D. Esito

- [F] Daily sim regression pack completato con test offline. Fonte: `tests/test_cli.py`.
- [PROP] Usare questi test come gate obbligatorio prima di qualunque futura modifica a `daily-sim`, `automation_gate.py` o scheduler design.
