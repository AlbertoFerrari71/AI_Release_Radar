# User Benefit Karma — Prima il beneficio, poi l’algoritmo

Fonte primaria: prompt `2630-R) AI Release Radar — User Benefit Karma Doctrine and User Benefit Gate Retry After 2620 Publish` fornito da Alberto il 2026-06-14.

## Frase fondativa

Prima il beneficio, poi l’algoritmo.
Ogni feature deve ridurre fatica, rischio, tempo o confusione per l’utente.
La tecnologia è valida solo se migliora una decisione reale, rende più chiaro cosa fare o evita lavoro inutile.

## Regola di prodotto

- [F] User Benefit Karma e' una regola di qualita' e progettazione, non solo una frase di README. Fonte: prompt 2630-R.
- [F] Ogni futuro step non banale dovrebbe dichiarare il beneficio utente previsto. Fonte: prompt 2630-R.
- [INT] La tecnologia e' mezzo, non fine: un algoritmo e' utile solo quando rende piu' chiaro, meno rischioso o meno faticoso il lavoro dell'operatore. Base: frase fondativa 2630-R.
- [INT] Una feature buona produce un beneficio percepibile in UI, report, CLI o workflow. Base: prompt 2630-R.
- [INT] Aumentare complessita' senza valore operativo e' debito prodotto. Base: prompt 2630-R.
- [INT] I test tecnici non bastano se l'utente non capisce meglio, decide meglio o lavora con meno fatica. Base: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`.

## Collegamento ai principi esistenti

- [F] `PASS tecnico ≠ PASS operatore` e' gia' formalizzato in `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`. Fonte: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`.
- [F] Verification Gate e Acceptance Gate sono distinti per modifiche UI-facing. Fonte: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`, `docs/decisions/2440_DECISIONS.md`.
- [F] Easy Mode e' requisito operativo e punto di ingresso, non decorazione estetica. Fonte: `docs/decisions/2440_DECISIONS.md`.
- [F] HAG e Action Center restano supervisionati: il radar osserva e propone, l'umano decide. Fonte: `AGENTS.md`, `docs/web/2460_DAILY_INTELLIGENCE_BRIEF_CONTRACT.md`.
- [F] Daily Intelligence Brief e' un esempio concreto: mostra `Oggi in 30 secondi` per ridurre tempo di lettura e confusione operativa. Fonte: `docs/web/2460_DAILY_INTELLIGENCE_BRIEF_CONTRACT.md`.

## Esempi pratici

- [F] Buona feature: riduce il tempo di lettura del Daily Brief. Fonte: prompt 2630-R.
- [F] Buona feature: chiarisce cosa ignorare. Fonte: prompt 2630-R.
- [F] Buona feature: evita azioni automatiche rischiose. Fonte: prompt 2630-R.
- [F] Cattiva feature: aggiunge algoritmo complesso senza vantaggio leggibile. Fonte: prompt 2630-R.
- [F] Cattiva feature: aumenta fonti ma aumenta rumore. Fonte: prompt 2630-R.
- [F] Cattiva feature: passa i test ma confonde l'operatore. Fonte: prompt 2630-R.

## Regola operativa per futuri step

Per ogni feature non banale, lo step dovrebbe dichiarare:

- [PROP] fatica utente ridotta;
- [PROP] rischio ridotto;
- [PROP] tempo risparmiato;
- [PROP] confusione eliminata;
- [PROP] decisione reale migliorata;
- [PROP] lavoro inutile evitato;
- [PROP] evidenza operatore che dimostra il beneficio.

Il gate riusabile e' definito in `docs/quality/2630_USER_BENEFIT_GATE.md`.
