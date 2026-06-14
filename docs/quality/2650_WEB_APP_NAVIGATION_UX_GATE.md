# 2650 Web App Navigation UX Gate

## Scopo

- [F] Questo gate nasce dal bug in cui il CTA umano "Leggi riepilogo umano" apriva l'endpoint macchina `/api/easy/latest/brief?lang=it` e mostrava JSON grezzo. Fonte: prompt `2650) AI Release Radar - Human Brief Pages, Global Home Navigation and Web App Navigation UX Gate`.
- [F] Il gate applica la User Benefit Karma Doctrine: prima il beneficio, poi l'algoritmo. Fonte: `docs/values/2630_USER_BENEFIT_KARMA.md`.
- [F] Il gate integra il User Benefit Gate riusabile. Fonte: `docs/quality/2630_USER_BENEFIT_GATE.md`.
- [F] Il gate estende la lezione Operator Acceptance sulle verifiche reali della web app. Fonte: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`.

Un pulsante umano non deve portare a una pagina macchina.

## Regole

1. [F] Un CTA umano rivolto all'operatore deve puntare a una pagina HTML leggibile. Fonte: prompt 2650.
2. [F] Un link verso `/api/*` puo' esistere nella UI solo se e' etichettato come JSON tecnico, dati tecnici o endpoint macchina equivalente. Fonte: prompt 2650.
3. [F] Le API `/api/*` devono restare read-only quando il contratto le definisce GET/read-only. Fonte: `docs/web/2460_DAILY_INTELLIGENCE_BRIEF_CONTRACT.md`.
4. [F] Ogni pagina HTML secondaria navigabile deve avere un link visibile in alto a sinistra verso Home/Easy Mode. Fonte: prompt 2650.
5. [F] Action Center, HAG e prompt suggeriti restano manual-only. Fonte: `docs/web/2270_EASY_MODE_UI_CONTRACT.md`.

## Pagine Umane E API Macchina

- [F] Pagina umana: restituisce HTML, include navigazione Home, espone contenuto leggibile e separa eventuali dati tecnici in sezioni o link etichettati. Fonte: prompt 2650.
- [F] API macchina: restituisce JSON per integrazioni o debug tecnico, non e' la destinazione primaria di CTA come "Leggi", "Apri" o "Visualizza". Fonte: prompt 2650.
- [INT] Se una pagina serve sia operatore sia debug, la destinazione primaria resta HTML e il JSON diventa link secondario etichettato.

## Checklist Per Nuove Pagine

1. [F] Dichiarare User Benefit: fatica ridotta, rischio ridotto, tempo risparmiato, confusione eliminata, decisione migliorata o lavoro inutile evitato. Fonte: `docs/quality/2630_USER_BENEFIT_GATE.md`.
2. [F] Verificare che i CTA primari non puntino a `/api/*`. Fonte: prompt 2650.
3. [F] Verificare che ogni pagina secondaria abbia `Home` o `Easy Mode` in alto a sinistra. Fonte: prompt 2650.
4. [F] Verificare che link tecnici siano etichettati come JSON tecnico o dati tecnici. Fonte: prompt 2650.
5. [F] Verificare che HAG e manual-only siano visibili quando la pagina mostra azioni o suggerimenti. Fonte: `docs/web/2270_EASY_MODE_UI_CONTRACT.md`.
6. [F] Eseguire smoke reale su `127.0.0.1:8787` quando la modifica riguarda la web app. Fonte: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`.

## Esempi

- [F] Buono: `Leggi riepilogo umano` -> `/easy/latest/brief?lang=it`. Fonte: prompt 2650.
- [F] Buono: `JSON tecnico` -> `/api/easy/latest/brief?lang=it`. Fonte: prompt 2650.
- [F] Cattivo: `Leggi riepilogo umano` -> `/api/easy/latest/brief?lang=it`. Fonte: bug osservato nel prompt 2650.
- [F] Cattivo: pagina secondaria senza link Home/Easy Mode. Fonte: prompt 2650.

## Test Minimi

- [F] Verificare HTML per route umane e JSON per API. Fonte: prompt 2650.
- [F] Verificare assenza di CTA primari verso `/api/easy/latest/brief` e `/api/easy/latest/model-packet`. Fonte: prompt 2650.
- [F] Verificare Home link su Easy Mode, Expert Mode, Action Center, run detail, Human Brief e AI Model Packet. Fonte: prompt 2650.
- [F] Verificare POST 405 sulle route GET/read-only. Fonte: prompt 2650.
