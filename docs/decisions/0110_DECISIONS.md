# 0110) First Controlled Live URL Check Decisions

## Decisioni Tecniche

- [F] Il layer live URL check e' implementato in `radar/live_url_check.py`. Fonte: `radar/live_url_check.py`.
- [F] Il layer usa `verify_url_live` dello step 0100. Fonte: `radar/live_url_check.py`, `radar/url_verifier.py`.
- [F] La serializzazione stabile dei risultati e' in `verification_results_to_dict`. Fonte: `radar/live_url_check.py`.
- [F] Le fixture statiche sono `examples/fixtures/0110_live_url_check_sample_results.json` e `examples/fixtures/0110_live_url_check_expected.json`. Fonte: fixture 0110.

## Live URL Check Read-Only

- [F] `check_sources_live` accetta `SourceDefinition`, timeout e `max_sources`. Fonte: `radar/live_url_check.py`.
- [F] `check_sources_live` restituisce `UrlVerificationResult`. Fonte: `radar/live_url_check.py`.
- [F] Gli errori per singola fonte non interrompono il batch. Fonte: `radar/live_url_check.py`, `tests/test_live_url_check.py`.

## No Parsing

- [F] `radar/live_url_check.py` non contiene parser HTML, JSON o text content live. Fonte: `radar/live_url_check.py`.
- [F] Il codice 0110 non salva contenuti pagina. Fonte: `radar/live_url_check.py`, `radar/cli.py`.
- [INT] Il parsing di contenuti live richiede uno step successivo con nuovi gate. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.

## No Snapshot Live

- [F] `radar/live_url_check.py` non crea `SourceSnapshot`. Fonte: `radar/live_url_check.py`.
- [F] La CLI `check-urls` scrive solo risultati URL e summary nella output directory esplicita. Fonte: `radar/cli.py`.

## Test Live Opt-In

- [F] Il test live richiede `AI_RELEASE_RADAR_RUN_LIVE_TESTS=1`. Fonte: `tests/test_live_url_check.py`.
- [F] I test offline usano `unittest.mock`. Fonte: `tests/test_live_url_check.py`.
- [INT] Questa scelta preserva una suite default deterministica e consente smoke live controllati solo quando richiesti. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.

## CLI check-urls

- [F] La CLI include `check-urls`. Fonte: `radar/cli.py`.
- [F] Il comando richiede `--registry` e `--output-dir`. Fonte: `radar/cli.py`.
- [F] Il comando supporta `--max-sources` e `--timeout-seconds`. Fonte: `radar/cli.py`.
- [F] Gli output sono `0110_live_url_check_results.json` e `0110_live_url_check_summary.txt`. Fonte: `radar/cli.py`.

## No Auto-Merge

- [F] Lo step 0110 e' L2. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.
- [F] Gli step L2 non consentono auto-merge. Fonte: `AGENTS.md`.
- [INT] Lo step deve fermarsi a PR draft e review manuale. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`, `AGENTS.md`.

## Prossimo Step Consigliato

- [F] Il prossimo step consigliato e' `0120) Controlled Live URL Check Review and Source Registry Hardening`. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.
- [INT] Dopo il primo smoke live conviene rivedere risultati, timeout e registry prima di introdurre fetcher successivi. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.
