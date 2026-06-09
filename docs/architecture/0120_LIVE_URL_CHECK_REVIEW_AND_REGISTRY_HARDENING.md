# 0120) Live URL Check Review and Registry Hardening

## Scopo

- [F] Lo step 0120 rafforza il source registry con metadati opzionali per live URL check. Fonte: `radar/source_registry.py`, `config/sources/openai_sources.json`.
- [F] Lo step 0120 rafforza la classificazione dei risultati URL live/read-only. Fonte: `radar/url_verifier.py`, `radar/live_url_check.py`.
- [F] Lo step 0120 aggiunge fixture e test per redirect, timeout, unreachable, unexpected status e disabled. Fonte: `examples/fixtures/0120_url_verification_cases.json`, `tests/test_url_verifier.py`, `tests/test_live_url_check.py`.

## Perche 0120 E' L2

- [F] Lo step 0120 e' classificato L2 dal prompt `0120-A) AI Release Radar - Controlled Live URL Check Review and Source Registry Hardening`.
- [F] Gli step L2 non consentono auto-merge. Fonte: `AGENTS.md`.
- [INT] Il rischio L2 deriva dal lavoro su fonti reali, policy di live check e live smoke controllato, anche se i test standard restano offline. Fonte: prompt `0120-A) AI Release Radar - Controlled Live URL Check Review and Source Registry Hardening`, `tests/test_live_url_check.py`.

## Cosa E' Stato Imparato Dal Live Smoke 0110

- [F] Lo step 0110 ha introdotto `check-urls` e il primo live smoke controllato. Fonte: `radar/cli.py`, `docs/decisions/0110_DECISIONS.md`.
- [INT] Il primo smoke ha mostrato che servono metadati espliciti per status attesi, redirect, timeout, fonti disabilitate e fonti candidate/manual review. Fonte: prompt `0120-A) AI Release Radar - Controlled Live URL Check Review and Source Registry Hardening`, `radar/source_registry.py`.

## Registry Hardening

- [F] `SourceDefinition` supporta `expected_status_codes`, `allow_redirects`, `timeout_seconds`, `live_check_enabled` e `manual_review_required`. Fonte: `radar/source_registry.py`.
- [F] Il vecchio formato registry resta valido perche' i nuovi campi sono opzionali con default. Fonte: `radar/source_registry.py`, `tests/test_source_registry.py`.
- [F] `config/sources/openai_sources.json` include i nuovi campi per le 11 fonti esistenti. Fonte: `config/sources/openai_sources.json`.
- [F] Le fonti candidate release notes restano `manual_review_required=true`. Fonte: `config/sources/openai_sources.json`.

## Nuovi Campi

- [F] `expected_status_codes` definisce gli status HTTP accettati quando fornito. Fonte: `radar/source_registry.py`, `radar/url_verifier.py`.
- [F] `allow_redirects` indica se un redirect osservato e' accettabile. Fonte: `radar/source_registry.py`, `radar/url_verifier.py`.
- [F] `timeout_seconds` consente timeout per fonte. Fonte: `radar/source_registry.py`, `radar/url_verifier.py`.
- [F] `live_check_enabled=false` restituisce un risultato disabled senza chiamare rete. Fonte: `radar/url_verifier.py`, `tests/test_url_verifier.py`.
- [F] `manual_review_required` marca fonti candidate che richiedono review anche se raggiungibili. Fonte: `config/sources/openai_sources.json`.

## Gestione Status, Redirect, Timeout e Unreachable

- [F] `UrlVerificationResult` distingue `redirected`, `unreachable`, `timeout`, `unexpected_status`, `invalid_url` e `disabled`. Fonte: `radar/url_verifier.py`.
- [F] Un redirect con `allow_redirects=false` viene classificato come unexpected. Fonte: `radar/url_verifier.py`, `tests/test_url_verifier.py`.
- [F] Timeout e unreachable sono classificati separatamente. Fonte: `radar/url_verifier.py`, `tests/test_url_verifier.py`.
- [F] Status HTTP non attesi sono classificati come `unexpected_status`. Fonte: `radar/url_verifier.py`, `tests/test_url_verifier.py`.

## Live Check Opt-In

- [F] I test live restano dietro `AI_RELEASE_RADAR_RUN_LIVE_TESTS=1`. Fonte: `tests/test_url_verifier.py`, `tests/test_live_url_check.py`.
- [F] La suite standard `python -m unittest discover -s tests` non esegue rete. Fonte: `tests/test_live_url_check.py`.

## No Parsing Live

- [F] `radar/url_verifier.py` non interpreta contenuti pagina. Fonte: `radar/url_verifier.py`.
- [F] `radar/live_url_check.py` produce solo risultati e summary strutturati. Fonte: `radar/live_url_check.py`.
- [F] Nessun HTML live viene salvato nel repo. Fonte: prompt `0120-A) AI Release Radar - Controlled Live URL Check Review and Source Registry Hardening`, `radar/cli.py`.

## No Auto-Merge

- [F] Lo step 0120 e' L2. Fonte: prompt `0120-A) AI Release Radar - Controlled Live URL Check Review and Source Registry Hardening`.
- [F] Gli step L2 non consentono auto-merge. Fonte: `AGENTS.md`.
- [INT] La chiusura corretta e' PR draft, auto-review locale e merge recommendation, senza `gh pr ready` e senza merge. Fonte: prompt `0120-A) AI Release Radar - Controlled Live URL Check Review and Source Registry Hardening`.

## Fuori Scope

- [F] Parsing contenuti live fuori scope. Fonte: prompt `0120-A) AI Release Radar - Controlled Live URL Check Review and Source Registry Hardening`.
- [F] Snapshot live fuori scope. Fonte: prompt `0120-A) AI Release Radar - Controlled Live URL Check Review and Source Registry Hardening`.
- [F] Scheduler fuori scope. Fonte: prompt `0120-A) AI Release Radar - Controlled Live URL Check Review and Source Registry Hardening`.
- [F] Report giornaliero automatico fuori scope. Fonte: prompt `0120-A) AI Release Radar - Controlled Live URL Check Review and Source Registry Hardening`.
