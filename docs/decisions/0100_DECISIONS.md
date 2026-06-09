# 0100) OpenAI Source Registry and URL Verification Decisions

## Decisioni Tecniche

- [F] Il registry fonti e' in `config/sources/openai_sources.json`. Fonte: `config/sources/openai_sources.json`.
- [F] Il modello `SourceDefinition` e le funzioni di caricamento sono in `radar/source_registry.py`. Fonte: `radar/source_registry.py`.
- [F] Il verificatore URL e' in `radar/url_verifier.py`. Fonte: `radar/url_verifier.py`.
- [F] Le fixture 0100 sono in `examples/fixtures/0100_*`. Fonte: `examples/fixtures/0100_openai_sources_valid.json`, `examples/fixtures/0100_openai_sources_invalid.json`, `examples/fixtures/0100_url_verification_expected.json`.

## Fonti Iniziali OpenAI/Codex

- [F] Il registry include Codex changelog, CLI reference, AGENTS.md guide e skills. Fonte: `config/sources/openai_sources.json`.
- [F] Il registry include API changelog e API deprecations. Fonte: `config/sources/openai_sources.json`.
- [F] Il registry include OpenAI release notes hub, ChatGPT release notes e model release notes come candidate pending manual review. Fonte: `config/sources/openai_sources.json`.
- [F] Il registry include GitHub releases e GitHub API releases per `openai/codex`. Fonte: `config/sources/openai_sources.json`.

## Scelta No Auto-Merge

- [F] Lo step 0100 e' L2 nel prompt dello step. Fonte: prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.
- [F] Gli step L2 non consentono auto-merge. Fonte: `AGENTS.md`.
- [INT] Lo step deve fermarsi a commit, push branch e PR draft per review manuale. Fonte: prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`, `AGENTS.md`.

## Scelta Live Test Opt-In

- [F] Il test live richiede `AI_RELEASE_RADAR_RUN_LIVE_TESTS=1`. Fonte: `tests/test_url_verifier.py`.
- [F] La suite `python -m unittest discover -s tests` non esegue verifiche live di default. Fonte: `tests/test_url_verifier.py`.
- [INT] Il gate default resta offline e ripetibile. Fonte: prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.

## Scelta Standard Library

- [F] Il verifier usa `urllib` della standard library. Fonte: `radar/url_verifier.py`.
- [F] Il registry usa `dataclasses`, `re`, `pathlib`, `typing` e `urllib.parse` della standard library, oltre a `radar.json_utils`. Fonte: `radar/source_registry.py`.
- [F] Nessuna dipendenza esterna e' aggiunta nello step 0100. Fonte: `pyproject.toml`, `radar/source_registry.py`, `radar/url_verifier.py`.

## Limiti

- [F] 0100 non implementa fetch produttivo. Fonte: prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.
- [F] 0100 non implementa parsing live. Fonte: prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.
- [F] 0100 non salva snapshot live. Fonte: prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.
- [F] 0100 non crea scheduler. Fonte: prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.

## Prossimo Step Consigliato

- [F] Il prossimo step consigliato e' `0110) First Controlled Live URL Check`. Fonte: prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.
