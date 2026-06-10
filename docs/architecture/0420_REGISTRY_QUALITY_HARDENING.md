# 0420) Registry Quality Hardening

## A. Obiettivo

- [F] Il registry operativo e' `config/sources/openai_sources.json`. Fonte: `radar/cli.py`, `config/sources/openai_sources.json`.
- [F] Il loader del registry e' `radar/source_registry.py`. Fonte: `radar/source_registry.py`.
- [F] Il super-step 0410-0500 richiede metadata espliciti per strategia parser, priorita' coverage, failure mode, follow-up e scheduler readiness. Fonte: prompt `0410-0500` salvato nel Bridge.
- [INT] Rendere espliciti questi campi nel registry riduce ambiguita' operativa senza introdurre nuovo fetch live, nuove dipendenze o parser fragile. Base: `docs/architecture/0410_SOURCE_COVERAGE_V1_2_IMPLEMENTATION.md`.

## B. Campi Aggiunti

| campo | valori ammessi | uso operativo |
|---|---|---|
| `parser_strategy` | `github_api_releases`, `codex_changelog_markdown`, `unsupported_diagnostic`, `manual_review_only`, `future_candidate` | [F] Descrive come la fonte viene o non viene parsata. Fonte: `radar/source_registry.py`. |
| `coverage_priority` | `P0`, `P1`, `P2`, `P3` | [F] Ordina la priorita' di coverage. Fonte: `radar/source_registry.py`. |
| `expected_failure_mode` | `none`, `api_rate_or_response_change`, `content_type_not_supported`, `html_unsupported`, `manual_review_403_or_fragile` | [F] Esplicita il failure mode atteso. Fonte: `radar/source_registry.py`. |
| `recommended_follow_up` | `use_parsed_items_after_gate`, `evaluate_structured_endpoint`, `keep_diagnostic_no_parser`, `manual_review_source`, `prefer_machine_readable_alternative` | [F] Esplicita il follow-up registry-level. Fonte: `radar/source_registry.py`. |
| `machine_readable_preferred` | boolean | [F] Indica se una versione machine-readable sarebbe preferibile. Fonte: `radar/source_registry.py`. |
| `scheduler_readiness` | `ready`, `warn`, `hold` | [F] Espone se la fonte puo' contribuire alla readiness scheduler. Fonte: `radar/source_registry.py`. |

## C. Compatibilita'

- [F] I nuovi campi sono opzionali nel loader e hanno default deterministici. Fonte: `radar/source_registry.py`, `tests/test_source_registry.py`.
- [F] Il registry operativo valorizza i nuovi campi per tutte le 11 fonti. Fonte: `config/sources/openai_sources.json`, `tests/test_source_registry.py`.
- [F] I `source_diagnostics` includono i metadata registry-level. Fonte: `radar/live_snapshot.py`.
- [F] Nessun URL nuovo viene aggiunto dal 0420. Fonte: `config/sources/openai_sources.json`.
- [F] Nessuna nuova dipendenza viene aggiunta dal 0420. Fonte: `pyproject.toml`.

## D. Lettura Operativa

- [F] `github_api_openai_codex_releases` e' `P0`, `github_api_releases`, `scheduler_readiness=ready`. Fonte: `config/sources/openai_sources.json`.
- [F] `openai_codex_changelog` e' `P1`, `codex_changelog_markdown`, `scheduler_readiness=warn`. Fonte: `config/sources/openai_sources.json`.
- [F] Le fonti ufficiali HTML senza parser sono marcate `unsupported_diagnostic` o `future_candidate`. Fonte: `config/sources/openai_sources.json`.
- [F] Le fonti candidate/manual review sono marcate `manual_review_only` e `scheduler_readiness=hold`. Fonte: `config/sources/openai_sources.json`.
- [INT] Con questa matrice il registry spiega perche' una fonte fetchata puo' restare non parsata senza generare falso PASS. Base: `docs/architecture/0410_SOURCE_COVERAGE_V1_2_IMPLEMENTATION.md`.

## E. Esito

- [F] Registry quality hardening completato con loader validation, metadata nel registry operativo e test offline. Fonte: `radar/source_registry.py`, `config/sources/openai_sources.json`, `tests/test_source_registry.py`.
- [PROP] Usare questi metadata nella manual review queue e nella scheduler readiness review degli step successivi.
