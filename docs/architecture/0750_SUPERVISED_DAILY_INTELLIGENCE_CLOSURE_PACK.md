# 0750) Supervised Daily Intelligence Closure Pack

## A. Cosa Fa V1.5

- [F] V1.5 trasforma il radar in ciclo supervisionato: run schedulato, report, review, triage, prompt suggestions e Human Approval Gate. Fonte: prompt `0610-0750`, `radar/cli.py`.
- [F] `daily-sim` produce quality gate v2, action triage, prompt suggestion pack, HAG, dashboard e supervised-loop dry run nella directory Bridge. Fonte: `radar/cli.py`.
- [F] Il retrieval `Radar fatto` e' documentato in `docs/architecture/0620_RADAR_DONE_BRIDGE_RETRIEVAL_CONTRACT.md`. Fonte: `docs/architecture/0620_RADAR_DONE_BRIDGE_RETRIEVAL_CONTRACT.md`.

## B. Cosa Non Fa

- [F] Non esegue prompt suggestions. Fonte: `radar/prompt_suggestions.py`, `radar/supervised_loop.py`.
- [F] Non modifica altri repository. Fonte: `radar/cli.py`, prompt `0610-0750`.
- [F] Non invia email o notifiche. Fonte: `radar/cli.py`, prompt `0610-0750`.
- [F] Non chiama LLM automaticamente. Fonte: `radar/cli.py`, prompt `0610-0750`.
- [F] Non crea nuovi scheduler o task Windows. Fonte: prompt `0610-0750`.

## C. Come Leggere Dashboard

- [F] Aprire `0710-Daily_Operator_Dashboard.md` nel run Bridge. Fonte: `radar/cli.py`.
- [F] Leggere gate, coverage, direct actions, prompt suggestions e HAG status. Fonte: `radar/operator_dashboard.py`.
- [F] Se HAG e' `HOLD_FOR_HUMAN_APPROVAL`, scegliere una decisione A/B/C/D dal report HAG. Fonte: `radar/hag_report.py`.

## D. Come Usare Prompt Suggestions

- [F] Aprire `0660-Codex_Prompt_Suggestions.md`. Fonte: `radar/cli.py`.
- [F] Trattare ogni suggestion come proposta, non come comando da eseguire automaticamente. Fonte: `radar/prompt_suggestions.py`.
- [F] Per procedere serve approvazione esplicita di Alberto e uno step separato. Fonte: prompt `0610-0750`.

## E. Readiness V2

- [INT] V1.5 e' pronta per supervised daily intelligence, non per V2 semi-autonomous. Base: `docs/reviews/0740_V1_5_GOVERNANCE_AND_RISK_REVIEW.md`.
- [PROP] Prossimo step consigliato: `0760) First Real Scheduled Run V1.5 Review`, dopo il prossimo run schedulato reale. Base: prompt `0610-0750`.
