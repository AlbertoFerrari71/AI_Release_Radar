# 0710) Daily Operator Dashboard Markdown

## A. Output

- [F] `daily-sim` produce `0710-Daily_Operator_Dashboard.md` nella directory run Bridge. Fonte: `radar/cli.py`.
- [F] Il renderer e' `radar/operator_dashboard.py`. Fonte: `radar/operator_dashboard.py`.
- [F] I test offline sono in `tests/test_operator_dashboard.py` e `tests/test_cli.py`. Fonte: `tests/test_operator_dashboard.py`, `tests/test_cli.py`.

## B. Campi

- [F] Il dashboard include run status, gate, scheduler status, source coverage, new meaningful items, direct actions, monitor-only summary, prompt suggestions, manual review queue, HAG e next step. Fonte: `radar/operator_dashboard.py`.
- [F] Il dashboard dichiara `no_auto_action: confirmed`. Fonte: `radar/operator_dashboard.py`.

## C. Runtime

- [F] Il dashboard e' output runtime e non va versionato nel repository. Fonte: `AGENTS.md`, prompt `0610-0750`.
