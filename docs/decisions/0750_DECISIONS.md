# 0750) Decisions

## A. Decisioni

- [F] La strategia scelta per lo step 0610-0750 e' PR batch unica con commit separati per step. Fonte: prompt `0610-0750`, report finale Codex dello step.
- [F] La PR resta draft e non viene eseguito merge su `main`. Fonte: prompt `0610-0750`, `AGENTS.md`.
- [F] V1.5 abilita prompt suggestions `suggested_only`, HAG report e dashboard Bridge. Fonte: `radar/cli.py`, `radar/prompt_suggestions.py`, `radar/hag_report.py`, `radar/operator_dashboard.py`.
- [F] Cross-project PR, auto-azioni, email/notifiche automatiche e LLM automatici restano vietati. Fonte: prompt `0610-0750`.
- [INT] V2 semi-autonomous resta `HOLD` finche' Alberto non approva una policy dedicata. Base: `docs/reviews/0740_V1_5_GOVERNANCE_AND_RISK_REVIEW.md`.

## B. Prossimo Step

- [PROP] `0760) First Real Scheduled Run V1.5 Review`: recuperare il primo run schedulato prodotto dopo questa PR e validare dashboard, HAG e prompt suggestions. Base: `docs/architecture/0750_SUPERVISED_DAILY_INTELLIGENCE_CLOSURE_PACK.md`.
