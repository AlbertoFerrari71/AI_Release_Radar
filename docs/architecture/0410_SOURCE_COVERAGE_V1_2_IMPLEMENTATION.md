# 0410) Source Coverage V1.2 Implementation

## A. Decisione

- [F] Il registry operativo contiene 11 fonti abilitate. Fonte: `config/sources/openai_sources.json`.
- [F] Il blocco 0320 ha documentato `parsed_count=1` su `source_count=11` come limite principale di coverage. Fonte: `docs/architecture/0320_SOURCE_COVERAGE_V1_2_PLANNING.md`.
- [F] Lo step 0330 ha valutato una seconda fonte strutturata e ha scelto di non aggiungere un parser live HTML fragile. Fonte: `docs/architecture/0330_SECOND_STRUCTURED_SOURCE_CANDIDATE.md`.
- [F] `radar/live_snapshot.py` parsa `github_api` e parsa `openai_codex_changelog` solo quando il contenuto fetchato e' `text/markdown` o `text/plain`. Fonte: `radar/live_snapshot.py`.
- [INT] Nel perimetro 0410 non esiste una seconda fonte live sicura da promuovere senza assumere stabilita' HTML non dimostrata. Base: `config/sources/openai_sources.json`, `radar/live_snapshot.py`, `docs/architecture/0330_SECOND_STRUCTURED_SOURCE_CANDIDATE.md`.
- [PROP] Applicare l'Opzione B: mantenere `parsed_count=1` come baseline atteso, rafforzare metadata registry, warning coverage, manual review queue e readiness scheduler.

## B. Candidate Rivalutate

| candidate | stato corrente | esito 0410 |
|---|---|---|
| `openai_codex_changelog` | [F] Parser conservativo disponibile solo per Markdown/plain text. Fonte: `radar/live_snapshot.py`. | [INT] Tenere come P1/future candidate; non forzare parsing HTML live. |
| `openai_api_changelog` | [F] Fonte ufficiale nel registry, senza parser live dedicato. Fonte: `config/sources/openai_sources.json`, `radar/live_snapshot.py`. | [INT] Non pronta senza endpoint strutturato o fixture stabile. |
| `openai_model_release_notes` | [F] Fonte candidate/manual review nel registry. Fonte: `config/sources/openai_sources.json`. | [INT] Non pronta per parsing automatico; resta manual review. |
| `openai_api_deprecations` | [F] Fonte ufficiale nel registry, senza parser live dedicato. Fonte: `config/sources/openai_sources.json`, `radar/live_snapshot.py`. | [INT] Candidato importante ma non promuovibile senza formato stabile. |
| `github_openai_codex_releases` | [F] Fonte HTML GitHub collegata alla fonte API gia' parsata. Fonte: `config/sources/openai_sources.json`. | [INT] Non duplicare con parser HTML; usare la API GitHub come fonte strutturata. |

## C. Perche' Non Aggiungere Codice Parser

- [F] Lo step 0410-0500 vieta parser HTML fragile e nuove dipendenze. Fonte: prompt `0410-0500` salvato nel Bridge.
- [F] La fonte strutturata utile esistente e' `github_api_openai_codex_releases`. Fonte: `docs/architecture/0330_SECOND_STRUCTURED_SOURCE_CANDIDATE.md`.
- [INT] Un secondo parser basato su HTML live aumenterebbe il rischio di falso verde: il conteggio parsed salirebbe, ma senza garanzia di stabilita' semantica. Base: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`, `docs/architecture/0330_SECOND_STRUCTURED_SOURCE_CANDIDATE.md`.
- [INT] La decisione piu' sicura e' rendere esplicita la bassa coverage e impedire che `scorecard_status=PASS` venga letto come scheduler readiness. Base: `docs/reviews/0390_DAILY_RUN_READINESS_REVIEW.md`.

## D. Output 0410

- [F] Nessun nuovo parser live viene aggiunto dallo step 0410. Fonte: questo documento.
- [F] Nessuna nuova dipendenza viene aggiunta dallo step 0410. Fonte: questo documento.
- [PROP] Prossimo incremento tecnico interno al super-step: metadata registry espliciti, warning policy e manual review queue.
