# 2440) Decisions

Fonte primaria: prompt `2390-2440) AI Release Radar — Operator Acceptance Philosophy and UI Gate Lessons Learned` fornito da Alberto il 2026-06-13.

## Decisioni

- [F] Per modifiche UI-facing, AI Release Radar richiede un Operator Acceptance Gate oltre al Verification Gate. Fonte: prompt 2390-2440.
- [F] Per Easy Mode e dashboard, il gate finale deve validare la porta reale usata dall'operatore, `http://127.0.0.1:8787/`, salvo diversa configurazione documentata. Fonte: prompt 2390-2440; `docs/architecture/0760_WEB_DASHBOARD_ARCHITECTURE.md`.
- [F] Easy Mode e' requisito operativo e punto di ingresso, non decorazione estetica. Fonte: prompt 2390-2440; `docs/web/2270_EASY_MODE_UI_CONTRACT.md`.
- [F] Il UI Navigation Gate deve coprire home, Easy Mode, Expert Mode, Action Center, Source Matrix, run detail, tab, tendine, link GET interni, bottoni sicuri e preferenze UI. Fonte: prompt 2390-2440.
- [F] La safe-click policy consente solo click navigazionali/visuali e preferenze UI locali testate; vieta HAG approvals, decisioni operative, scheduler, trigger run reali, email, notifiche, azioni esterne e form mutativi non autorizzati. Fonte: prompt 2390-2440; `docs/web/2270_EASY_MODE_UI_CONTRACT.md`.
- [F] Il feedback operatore deve diventare test, smoke, UI contract, gate, lesson learned o backlog ASF generale. Fonte: prompt 2390-2440.

## Impatto

- [INT] Il vecchio concetto di GREEN tecnico resta necessario ma non sufficiente per chiudere modifiche che cambiano l'esperienza operatore. Base: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`; report 2270-2380; report 2385.
- [INT] Warning governati e documentati sono preferibili a PASS superficiali quando manca evidenza operatore o visuale. Base: prompt 2390-2440; report 2270-2380; report 2385.
- [F] Dal 2630-R, le future feature devono dichiarare anche il beneficio utente previsto tramite User Benefit Karma e User Benefit Gate. Fonte: `docs/values/2630_USER_BENEFIT_KARMA.md`, `docs/quality/2630_USER_BENEFIT_GATE.md`.

## Backlog

- [PROP] Promuovere questa lesson learned in AI Software Factory nello step `1290-1360) ASF — Verification Gate vs Acceptance Gate Philosophy and Standardization`. Fonte: prompt 2390-2440.
- [PROP] Aggiornare la presentazione V1 con Easy Mode, Operator Acceptance, UI Navigation Gate e bug utente trasformato in test. Fonte: `docs/quality/2440_PRESENTATION_UPDATE_NOTES.md`.
- [PROP] Valutare tag `v1.0.0` solo dopo run reali e Acceptance Gate esplicito. Fonte: prompt 2390-2440; `docs/release/1750_V1_0_TAG_PLAN.md`.
