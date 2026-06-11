# 1100) Decisions

## A. Action Center Supervision

- [F] L'Action Center e' supervisionato e non autorizza auto-azioni. Fonte: `radar/action_inbox.py`, `radar_web/action_center.py`.
- [F] Tutte le decisioni hanno `human_required=true` e `no_auto_action=true`. Fonte: `radar/action_inbox.py`.
- [INT] La dashboard passa da report viewer a operator loop perche' collega Action Inbox, decision log, prompt pack e backlog export. Fonte: `radar_web/app.py`, `radar_web/templates/actions.html`.

## B. Bridge-Only Runtime Outputs

- [F] Decision log, prompt pack e backlog export sono scritti sotto `action_dispatch` nel Bridge. Fonte: `radar_web/action_center.py`.
- [F] Nessun output runtime dell'Action Center viene scritto nel repository. Fonte: `radar_web/action_center.py`.
- [F] I file `LAST-*` e `latest-*` restano vietati. Fonte: `AGENTS.md`, `radar_web/config.py`.

## C. Prompt Generation Gate

- [F] La prompt generation viene rifiutata finche' non esiste decisione umana compatibile. Fonte: `radar/action_inbox.py`, `tests/test_action_inbox.py`.
- [F] Il prompt pack e' Markdown suggerito e non viene eseguito. Fonte: `radar/action_inbox.py`, `tests/test_radar_web_app.py`.

## D. No Auto-Merge

- [F] Lo step 0960-1100 e' classificato L1/L2 e richiede NO AUTO-MERGE. Fonte: prompt operativo 0960-1100 fornito da Alberto il 2026-06-11.
- [F] La PR finale deve restare draft. Fonte: prompt operativo 0960-1100 fornito da Alberto il 2026-06-11.

## E. Prossimo Step

- [PROP] Procedere con `1110) Operator Loop First Real Morning Review` dopo review manuale della PR draft 0960-1100.
