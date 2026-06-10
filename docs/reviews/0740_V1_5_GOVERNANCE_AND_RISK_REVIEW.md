# 0740) V1.5 Governance and Risk Review

## A. Consentito Ora

- [F] Prompt suggestions sono consentiti come proposte `suggested_only`. Fonte: prompt `0610-0750`, `radar/prompt_suggestions.py`.
- [F] HAG e dashboard sono consentiti come output runtime nel Bridge. Fonte: prompt `0610-0750`, `radar/cli.py`.
- [F] Il task scheduler esistente resta dry-report only. Fonte: `docs/architecture/0600_SCHEDULER_DRY_REPORT_CLOSURE_PACK.md`.

## B. Vietato Ora

- [F] Cross-project PR automatiche restano vietate. Fonte: prompt `0610-0750`.
- [F] Auto-merge e push diretto su `main` restano vietati per questo step. Fonte: prompt `0610-0750`, `AGENTS.md`.
- [F] Email/notifiche automatiche e chiamate LLM automatiche restano vietate. Fonte: prompt `0610-0750`, `docs/decisions/0510_L3_SCHEDULER_DRY_REPORT_CONSENT.md`.
- [F] Nuovi scheduler o task Windows non sono stati autorizzati. Fonte: prompt `0610-0750`.

## C. Condizioni Per Future Auto-PR

- [PROP] Serve policy dedicata cross-project con allow-list repo, branch naming, HAG esplicito, test per repo target e stop su warning non classificati. Base: prompt `0610-0750`.
- [PROP] Serve separazione tra generazione prompt, approvazione umana, apertura branch target e PR draft target. Base: `radar/hag_report.py`.
- [PROP] Serve divieto di auto-merge cross-project finche' Alberto non autorizza nuova policy. Base: `AGENTS.md`.

## D. Decisione

- [INT] Decisione consigliata V1.5: prompt suggestions allowed; cross-project PR still HOLD; auto-merge forbidden. Base: prompt `0610-0750`, `AGENTS.md`.
