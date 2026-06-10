# 0190) First Real Output Review and Parser Coverage Hardening Decisions

## Decisioni Tecniche

- [F] Il real-run non deve restituire `NO_CHANGE` quando `source_count > 0` e `parsed_count == 0`. Fonte: prompt 0190, `radar/real_run.py`.
- [F] E' stato introdotto lo stato `NO_PARSED_ITEMS` per il real-run live/manuale. Fonte: `radar/real_run.py`, `radar/report_engine.py`.
- [F] La diagnostica source/parser e' inclusa nel risultato live snapshot e nel summary/report del real-run. Fonte: `radar/live_snapshot.py`, `radar/real_run.py`.
- [F] Il registry supporta `max_bytes` opzionale per singola fonte. Fonte: `radar/source_registry.py`.
- [F] Il fetcher usa `source.max_bytes` quando presente. Fonte: `radar/source_fetcher.py`.

## GitHub API Releases

- [F] `github_api_openai_codex_releases` ha `source_type = "github_api"`. Fonte: `config/sources/openai_sources.json`.
- [F] Il workflow live snapshot invoca `parse_github_releases_api_fixture` quando `source_type == "github_api"`. Fonte: `radar/live_snapshot.py`.
- [F] `github_api_openai_codex_releases` ora dichiara `max_bytes = 5242880`. Fonte: `config/sources/openai_sources.json`.
- [INT] Questa scelta mantiene la fonte GitHub API come target primario perche' e' piu' strutturata della pagina HTML GitHub releases. Fonte: prompt 0190, `radar/parsers.py`.

## Fonti Non Supportate

- [F] `github_openai_codex_releases` resta non parsata perche' e' una pagina HTML, non la risposta JSON GitHub Releases API. Fonte: `config/sources/openai_sources.json`, `radar/live_snapshot.py`.
- [F] Le fonti OpenAI docs/release notes HTML restano `parser_skipped_unsupported_source`. Fonte: `radar/live_snapshot.py`.
- [INT] Non e' stato introdotto un parser HTML fragile per fonti ufficiali live. Fonte: prompt 0190, `radar/live_snapshot.py`.

## Test Offline

- [F] Sono stati aggiunti test per routing GitHub API e diagnostica source/parser. Fonte: `tests/test_live_snapshot.py`.
- [F] Sono stati aggiunti test per `NO_PARSED_ITEMS`. Fonte: `tests/test_real_run.py`.
- [F] Sono stati aggiunti test per `max_bytes` per-fonte nel registry e nel fetcher. Fonte: `tests/test_source_registry.py`, `tests/test_source_fetcher.py`.

## No Auto-Merge

- [F] Lo step 0190 e' L2. Fonte: prompt 0190.
- [F] Gli step L2 non consentono auto-merge. Fonte: `AGENTS.md`, prompt 0190.
- [F] Nessuno scheduler e nessuna dipendenza esterna sono introdotti nello step. Fonte: `radar/`, `pyproject.toml` non modificato.

## Prossimo Step Consigliato

- [PROP] 0200) Eseguire un real-run controllato dopo merge manuale della PR 0190 e valutare una copertura parser conservativa per una fonte OpenAI ufficiale ancora non supportata.
