# 1730) Source Policy Final

## Scopo

- [F] La source policy V1 finale classifica ogni fonte come parsed, diagnostic-only, manual review, replaced, unsupported documentata o esclusa. Fonte: `config/sources/openai_sources.json`, `radar/source_registry.py`.
- [F] Il target pragmatico V1 finale e' `parsed_count >= 3` senza parser HTML fragile. Fonte: `radar/source_coverage.py`.

## Fonti Parsate V1

- [F] `github_api_openai_codex_releases` usa GitHub Releases API JSON e parser `github_api_releases`. Fonte: `config/sources/openai_sources.json`, `radar/live_snapshot.py`.
- [F] `openai_api_deprecations` usa il twin Markdown ufficiale `https://developers.openai.com/api/docs/deprecations.md` e parser `api_deprecations_markdown`. Fonte: `config/sources/openai_sources.json`, `radar/parsers.py`.
- [F] `github_api_openai_python_releases` usa GitHub Releases API JSON e parser `github_api_releases`. Fonte: `config/sources/openai_sources.json`.
- [F] `github_api_openai_node_releases` usa GitHub Releases API JSON e parser `github_api_releases`. Fonte: `config/sources/openai_sources.json`.

## Fonti Diagnostic-Only

- [F] `openai_codex_cli_reference`, `openai_codex_agents_md` e `openai_codex_skills` restano documentazione ufficiale diagnostica, non feed release V1. Fonte: `config/sources/openai_sources.json`.
- [F] `openai_api_changelog` resta unsupported documentata per V1 perche' la discovery non ha trovato un markdown twin ufficiale stabile. Fonte: `1520-Source_Coverage_Discovery_Report.md` nel Bridge, `config/sources/openai_sources.json`.
- [F] `openai_codex_changelog` resta unsupported documentata per V1 perche' la pagina ufficiale e' HTML esteso e non viene parsata come parser produttivo. Fonte: `config/sources/openai_sources.json`, `radar/live_snapshot.py`.

## Manual Review

- [F] `openai_release_notes_hub`, `openai_chatgpt_release_notes` e `openai_model_release_notes` restano manual review 403/accesso fragile. Fonte: ultimo run Bridge `0180-Run_Summary.json`, `config/sources/openai_sources.json`.
- [F] V1 non usa login, cookie, token, browser automation o bypass 403. Fonte: `AGENTS.md`, `radar/source_fetcher.py`.

## Sostituzioni

- [F] `github_openai_codex_releases` HTML e' sostituita operativamente da `github_api_openai_codex_releases`. Fonte: `config/sources/openai_sources.json`.

## Criteri Nuovi Parser

- [F] Sono ammessi parser per GitHub API, JSON/RSS/Atom ufficiali e Markdown ufficiale stabile. Fonte: `radar/parsers.py`, `radar/live_snapshot.py`.
- [F] Non sono ammessi parser HTML/CSS fragili, browser/headless produttivi, autenticazione, token o item inventati. Fonte: `AGENTS.md`, `radar/source_coverage.py`.
- [F] Ogni parser nuovo richiede fixture offline e test. Fonte: `tests/test_parsers.py`, `tests/test_live_snapshot.py`.

## Backlog Manutentivo

- [PROP] Verificare periodicamente se `openai_api_changelog` ottiene un endpoint Markdown o feed ufficiale.
- [PROP] Rivalutare release notes 403 solo con alternativa machine-readable ufficiale, non con scraping.
- [PROP] Mantenere i GitHub API parser con fixture aggiornata quando cambia schema.
