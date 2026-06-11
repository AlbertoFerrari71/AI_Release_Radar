# 1100) Operator Loop Closure Pack

## A. Cosa E' Stato Aggiunto

- [F] Aggiunto modello Action Inbox supervisionato in `radar/action_inbox.py`. Fonte: `radar/action_inbox.py`.
- [F] Aggiunto adapter Action Center dashboard in `radar_web/action_center.py`. Fonte: `radar_web/action_center.py`.
- [F] Aggiunta pagina `/actions` e API `/api/actions`. Fonte: `radar_web/app.py`, `radar_web/templates/actions.html`.
- [F] Aggiunti endpoint decisione, prompt generation e backlog export. Fonte: `radar_web/app.py`.
- [F] Aggiunti test offline per modello Action Inbox e dashboard Action Center. Fonte: `tests/test_action_inbox.py`, `tests/test_radar_web_app.py`.

## B. Safety Model

- [F] Ogni azione ha `human_required=true`. Fonte: `radar/action_inbox.py`.
- [F] Ogni azione blocca `auto_action`, `external_repo_write`, `llm_call`, `email` e `scheduler_change`. Fonte: `radar/action_inbox.py`.
- [F] La prompt generation e' consentita solo dopo decisione umana `approved_for_prompt` o `review_requested`. Fonte: `radar/action_inbox.py`.
- [F] Nessun endpoint Action Center esegue prompt, invia email, chiama LLM o modifica scheduler. Fonte: `radar_web/action_center.py`.

## C. Decision Model

- [F] Le decisioni supportate sono `approve_prompt`, `defer`, `ignore`, `backlog` e `request_review`. Fonte: `radar/action_inbox.py`.
- [F] Il decision log e' append-only JSONL sotto `action_dispatch/decision_log.jsonl` nel Bridge. Fonte: `radar/action_inbox.py`.
- [F] Ogni record include timestamp, run id, action id, decision, reason, operator, source, `human_required` e `no_auto_action`. Fonte: `radar/action_inbox.py`.

## D. Prompt Pack Model

- [F] I prompt pack sono file Markdown `1000-Prompt_*.md` sotto `action_dispatch/<run_id>/`. Fonte: `radar/action_inbox.py`.
- [F] Il prompt pack contiene contesto, fonte radar, progetto target, rischio, obiettivo, vincoli, cosa non fare, test richiesti, output atteso, evidenze e ragioni. Fonte: `radar/action_inbox.py`.
- [F] La generazione prompt non copia negli appunti e non lancia Codex. Fonte: `radar_web/action_center.py`.

## E. Bridge Output Contract

- [F] Decision log: `action_dispatch/decision_log.jsonl`. Fonte: `radar/action_inbox.py`.
- [F] Prompt pack: `action_dispatch/<run_id>/1000-Prompt_*.md`. Fonte: `radar/action_inbox.py`.
- [F] Backlog export: `action_dispatch/<run_id>/1040-Action_Backlog.md` e `1040-Action_Backlog.json`. Fonte: `radar/action_inbox.py`.
- [F] Smoke output: `web_smoke/0960_1100_<timestamp>/`. Fonte: prompt operativo 0960-1100 fornito da Alberto il 2026-06-11.

## F. Priority, Trend E Noise

- [F] Ogni azione riceve `priority`, `priority_score` e `priority_reasons`. Fonte: `radar/action_inbox.py`.
- [F] Lo scoring usa score impatto, tipo azione, HAG status, risk level, ricorrenza, novita' e confidenza fonte. Fonte: `radar/action_inbox.py`.
- [F] Ogni azione riceve `trend_status` tra `new_today`, `recurring`, `already_backlogged`, `previously_ignored` e `prompt_already_generated`. Fonte: `radar/action_inbox.py`.
- [F] Le regole noise abbassano priorita' per ignored, backlog, monitor-only ricorrente e patch release ricorrente. Fonte: `radar/action_inbox.py`.

## G. Limiti Residui

- [F] L'Action Center usa i run Bridge disponibili e non crea nuove fonti dati. Fonte: `radar_web/action_center.py`.
- [F] Il decision log e' file-based e locale al Bridge. Fonte: `radar/action_inbox.py`.
- [F] Il modello non esegue prompt e non apre sessioni Codex. Fonte: `radar_web/action_center.py`.
- [INT] La qualita' delle azioni dipende ancora dalla qualita' di action triage, source coverage e prompt suggestions prodotti dai run giornalieri. Fonte: `radar/action_triage.py`, `radar_web/run_locator.py`.

## H. Prossimo Step Consigliato

- [PROP] `1110) Operator Loop First Real Morning Review`: Alberto usa `/actions` su un run reale mattutino, approva o mette in backlog una o due azioni, e valida se prompt pack e backlog sono abbastanza chiari per il lavoro quotidiano.
