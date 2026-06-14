# User Benefit Gate

Fonte primaria: prompt `2630-R) AI Release Radar — User Benefit Karma Doctrine and User Benefit Gate Retry After 2620 Publish` fornito da Alberto il 2026-06-14.

## Scopo

- [F] Il User Benefit Gate verifica che una feature migliori il valore operativo per l'utente, non solo la correttezza tecnica. Fonte: prompt 2630-R.
- [F] Un gate tecnico PASS non implica automaticamente User Benefit PASS. Fonte: prompt 2630 originale e prompt 2630-R.
- [INT] Questo gate completa Verification Gate e Acceptance Gate: verifica perche' la feature merita di esistere per l'operatore. Base: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`.

## Frase fondativa

Prima il beneficio, poi l’algoritmo.
Ogni feature deve ridurre fatica, rischio, tempo o confusione per l’utente.
La tecnologia è valida solo se migliora una decisione reale, rende più chiaro cosa fare o evita lavoro inutile.

## Checklist obbligatoria

Per ogni feature non banale, compilare queste domande:

- Quale fatica riduce per l’utente?
- Quale rischio riduce?
- Quale tempo fa risparmiare?
- Quale confusione elimina?
- Quale decisione reale migliora?
- Cosa rende più chiaro?
- Quale lavoro inutile evita?
- Come l’utente vede concretamente il beneficio in UI, report, CLI o workflow?
- Come distinguiamo beneficio reale da tecnologia fine a sé stessa?
- Quale evidenza dimostra il beneficio?

## Stati ammessi

- `USER_BENEFIT_PASS`: beneficio chiaro, osservabile e supportato da evidenza operatore o artifact verificabili.
- `USER_BENEFIT_PASS_WITH_NOTES`: beneficio reale ma con note di polish, comunicazione o misurazione.
- `USER_BENEFIT_WEAK`: beneficio plausibile ma non ancora dimostrato, oppure troppo indiretto per chiudere come pieno PASS.
- `USER_BENEFIT_FAIL`: beneficio assente, non spiegato, o tecnologia fine a se' stessa.

## Regole di valutazione

- [F] Ogni futuro step dovrebbe dichiarare il beneficio utente previsto. Fonte: prompt 2630-R.
- [INT] Il beneficio deve essere visibile dove l'utente lavora: UI, report, CLI, Bridge artifact o workflow operativo. Base: prompt 2630-R.
- [INT] Un aumento di accuratezza interna non basta se non rende piu' chiaro cosa fare. Base: frase fondativa 2630-R.
- [INT] Un output piu' ricco puo' essere un peggioramento se aumenta rumore, tempo di lettura o ambiguita'. Base: prompt 2630-R.
- [INT] Se l'evidenza e' solo tecnica, lo stato massimo consigliato e' `USER_BENEFIT_WEAK` finche' non esiste evidenza operatore. Base: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`.

## Evidenza minima

Almeno una evidenza deve essere indicata:

- [PROP] screenshot o real-port validation per modifiche UI-facing;
- [PROP] esempio di report/Bridge artifact per modifiche reportistiche;
- [PROP] output CLI verificato per comandi operativi;
- [PROP] confronto prima/dopo su tempo, fatica o confusione ridotta;
- [PROP] test o smoke che dimostra il comportamento utile senza introdurre auto-action.

## Stop policy

- [F] Se la feature introduce auto-action, runtime LLM, email/notifica, scheduler mutation o bypass HAG/403 non autorizzati, il gate deve fallire o fermarsi per safety. Fonte: `AGENTS.md`.
- [INT] Se il beneficio non e' dichiarato, non trattare lo step come completo: assegnare `USER_BENEFIT_WEAK` o `USER_BENEFIT_FAIL` secondo evidenza. Base: prompt 2630-R.
- [INT] Se il beneficio e' reale ma resta polish operatore, usare `USER_BENEFIT_PASS_WITH_NOTES` e trasformare le note in follow-up. Base: report 2610 e prompt 2630-R.

## Template di sezione per prompt o PR

```markdown
## User Benefit

- Fatica ridotta:
- Rischio ridotto:
- Tempo risparmiato:
- Confusione eliminata:
- Decisione migliorata:
- Lavoro inutile evitato:
- Evidenza operatore:
- Stato User Benefit:
```

## Collegamenti

- Doctrine: `docs/values/2630_USER_BENEFIT_KARMA.md`
- Operator Acceptance: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`
- Easy Mode contract: `docs/web/2270_EASY_MODE_UI_CONTRACT.md`
- Daily Intelligence Brief contract: `docs/web/2460_DAILY_INTELLIGENCE_BRIEF_CONTRACT.md`
