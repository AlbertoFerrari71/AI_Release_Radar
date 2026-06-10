# 0190) First Real Output Parser Coverage Hardening

## Problema Rilevato

- [F] Il primo run reale manuale ha prodotto `Status: NO_CHANGE` con `parsed_count = 0`, `item_count = 0`, `skipped_count = 9` e `failed_count = 2`. Fonte: prompt 0190 fornito da Alberto.
- [F] La fonte `github_api_openai_codex_releases` ha restituito `response_too_large` nel run reale manuale con `--max-bytes 2000000`. Fonte: prompt 0190 fornito da Alberto.
- [F] La fonte `github_openai_codex_releases` e altre fonti HTML/docs erano fetchate ma non parsate per `parser_skipped_unsupported_source`. Fonte: prompt 0190 fornito da Alberto.
- [INT] `NO_CHANGE` era fuorviante in quel caso perche' indicava assenza di variazioni, mentre la pipeline non aveva ottenuto nessun item parsato su cui calcolare variazioni. Fonte: `radar/real_run.py`, prompt 0190.

## Correzioni Implementate

- [F] `SourceDefinition` ora supporta il campo opzionale `max_bytes`. Fonte: `radar/source_registry.py`.
- [F] `fetch_sources_content` usa `source.max_bytes` quando presente e mantiene il parametro globale `max_bytes` come fallback. Fonte: `radar/source_fetcher.py`.
- [F] `github_api_openai_codex_releases` dichiara `max_bytes = 5242880` nel registry stabile. Fonte: `config/sources/openai_sources.json`.
- [F] Il workflow live snapshot esporta `source_diagnostics` nel risultato serializzabile. Fonte: `radar/live_snapshot.py`.
- [F] Il workflow real-run include `source_diagnostics` nel summary JSON e nei report Markdown. Fonte: `radar/real_run.py`.
- [F] Il real-run usa `NO_PARSED_ITEMS` quando `source_count > 0` e `parsed_count == 0`. Fonte: `radar/real_run.py`.

## Copertura Parser Prima

- [F] Il parser GitHub Releases API esisteva gia' come parser offline deterministico. Fonte: `radar/parsers.py`.
- [F] Il live workflow invocava il parser per `source_type == "github_api"` solo se il fetch produceva contenuto JSON entro il limite. Fonte: `radar/live_snapshot.py`.
- [F] Il parser Codex changelog era invocato solo per `openai_codex_changelog` con `content_type` `text/markdown` o `text/plain`. Fonte: `radar/live_snapshot.py`.

## Copertura Parser Dopo

- [F] La fonte reale strutturata `github_api_openai_codex_releases` ha un limite per-fonte adeguato al parser GitHub API. Fonte: `config/sources/openai_sources.json`, `radar/source_fetcher.py`.
- [F] I test offline verificano che una fonte `github_api` fetchata come JSON venga parsata e produca item. Fonte: `tests/test_live_snapshot.py`.
- [F] I test offline verificano che un run senza fonti parsate produca `NO_PARSED_ITEMS` e non `NO_CHANGE`. Fonte: `tests/test_real_run.py`.

## Fonti Ancora Non Supportate

- [F] `github_openai_codex_releases` resta una pagina HTML GitHub e non usa il parser GitHub API. Fonte: `config/sources/openai_sources.json`, `radar/live_snapshot.py`.
- [F] Le fonti `official_docs` e `official_release_notes` restano non supportate dal parser live. Fonte: `radar/live_snapshot.py`.
- [F] `openai_codex_changelog` resta parsabile solo quando il contenuto fetchato e' markdown o testo semplice, non HTML reale. Fonte: `radar/live_snapshot.py`, `radar/parsers.py`.
- [INT] Le fonti HTML ufficiali richiedono un parser conservativo dedicato o una fonte machine-readable alternativa prima di essere affidabili nel radar reale. Fonte: prompt 0190, `radar/live_snapshot.py`.

## Rischi Residui

- [F] Lo step resta L2 perche' riguarda integrazione live/read-only e registry reale. Fonte: prompt 0190.
- [F] I test restano offline e deterministici. Fonte: `tests/test_live_snapshot.py`, `tests/test_real_run.py`, `tests/test_source_fetcher.py`, `tests/test_source_registry.py`.
- [INT] Il limite per-fonte di 5 MiB riduce il rischio `response_too_large` per GitHub API, ma non garantisce successo se GitHub cambia payload, status, rate limit o content-type. Fonte: `config/sources/openai_sources.json`, `radar/source_fetcher.py`.

## Prossimo Step Consigliato

- [PROP] 0200) Execute a controlled real-run review after merging 0190, then decide whether to add a conservative parser for one official OpenAI HTML source or switch that source to a structured feed/API when available.
