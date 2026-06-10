# 0330) Second Structured Source Candidate

## A. Decisione

- [F] Il registry corrente contiene una fonte machine-readable esplicita: `github_api_openai_codex_releases`. Fonte: `config/sources/openai_sources.json`.
- [F] `radar/live_snapshot.py` parsa fonti `github_api` con `parse_github_releases_api_fixture`. Fonte: `radar/live_snapshot.py`.
- [F] `radar/live_snapshot.py` parsa `openai_codex_changelog` solo quando il contenuto fetchato e' `text/markdown` o `text/plain`. Fonte: `radar/live_snapshot.py`.
- [F] La review 0310 ha osservato una sola fonte parsata su 11 e ha identificato `github_api_openai_codex_releases` come fonte parsata. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [INT] Non c'e' una seconda fonte strutturata live gia' provata nel registry corrente senza assumere HTML fragile. Base: `config/sources/openai_sources.json`, `radar/live_snapshot.py`, `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [PROP] Per lo step 0330 si sceglie l'Opzione B: decisione documentata, senza nuovo parser live.

## B. Candidati Valutati

| candidate | segnale positivo | blocco | esito |
|---|---|---|---|
| `openai_codex_changelog` | [F] Esiste un parser conservativo markdown/text. Fonte: `radar/parsers.py`, `radar/live_snapshot.py`. | [F] Il parser live accetta solo `text/markdown` o `text/plain`. Fonte: `radar/live_snapshot.py`. | [INT] Candidato P1 da tenere, ma non da forzare su HTML. |
| `openai_api_changelog` | [F] Fonte ufficiale prioritaria nel registry. Fonte: `config/sources/openai_sources.json`. | [F] Nessun parser live dedicato in `radar/live_snapshot.py`. Fonte: `radar/live_snapshot.py`. | [INT] Non pronta senza endpoint strutturato o fixture stabile. |
| `openai_api_deprecations` | [F] Fonte ufficiale prioritaria nel registry. Fonte: `config/sources/openai_sources.json`. | [F] Nessun parser live dedicato in `radar/live_snapshot.py`. Fonte: `radar/live_snapshot.py`. | [INT] Importante, ma da lasciare unsupported finche' non c'e' formato stabile. |
| `github_openai_codex_releases` | [F] Fonte HTML GitHub collegata allo stesso dominio informativo della API. Fonte: `config/sources/openai_sources.json`. | [F] La matrice 0240 la tratta come fallback umano alla fonte API. Fonte: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`. | [INT] Non va duplicata come parser HTML. |

## C. Perche' Non Forzare Un Parser

- [F] La matrice 0240 raccomanda endpoint strutturato o formato stabile prima di aggiungere parser live. Fonte: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.
- [F] Lo step corrente vieta parser HTML aggressivi. Fonte: prompt `0320-0400` salvato in Bridge.
- [INT] Aggiungere un parser HTML ora aumenterebbe il rischio di falso verde, perche' la stabilita' del markup non e' dimostrata da test offline/live specifici. Base: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.
- [INT] La scelta prudente e' mantenere diagnostica esplicita e introdurre un gate coverage, invece di aumentare `parsed_count` con parser fragile. Base: review 0310 e requisiti 0360/0380.

## D. Criterio Per Promuovere Una Seconda Fonte In Futuro

Una seconda fonte puo' diventare parser V1.2 solo se soddisfa tutti i criteri:

1. [PROP] Formato strutturato o semi-strutturato stabile: JSON/API, feed ufficiale, markdown/text prevedibile o export documentato.
2. [PROP] Test offline con fixture realistica e casi errore.
3. [PROP] Fallback sicuro a `fetched_but_unsupported`, `manual_review_required` o `fetch_failed`.
4. [PROP] Nessuna nuova dipendenza.
5. [PROP] Nessun parser HTML live basato su classi CSS, layout o selettori fragili.
6. [PROP] Nessun cambio a scheduler, task Windows o LLM automatici.

## E. Output Dello Step

- [F] Nessun nuovo parser live viene aggiunto dallo step 0330. Fonte: questo documento.
- [F] Nessuna nuova dipendenza viene aggiunta dallo step 0330. Fonte: questo documento.
- [PROP] Il prossimo incremento tecnico deve essere un gate che renda visibile la coverage bassa anche quando la scorecard report resta `PASS`.
