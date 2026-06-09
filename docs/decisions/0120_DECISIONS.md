# 0120) Controlled Live URL Check Review and Registry Hardening Decisions

## Decisioni Tecniche

- [F] Il source registry e' stato esteso con campi opzionali backward-compatible. Fonte: `radar/source_registry.py`.
- [F] Il verifier live classifica redirect, timeout, unreachable, unexpected status, invalid URL e disabled. Fonte: `radar/url_verifier.py`.
- [F] La review dei risultati live produce recommendation deterministica. Fonte: `radar/live_url_check.py`.
- [F] Le fixture 0120 coprono registry nuovo/vecchio formato e risultati URL classificati. Fonte: `examples/fixtures/0120_registry_hardening_cases.json`, `examples/fixtures/0120_url_verification_cases.json`, `examples/fixtures/0120_live_check_review_expected.json`.

## Modifiche Al Registry

- [F] Ogni fonte in `config/sources/openai_sources.json` ora include `expected_status_codes`, `allow_redirects`, `timeout_seconds`, `live_check_enabled` e `manual_review_required`. Fonte: `config/sources/openai_sources.json`.
- [F] Nessuna fonte esistente e' stata rimossa. Fonte: `config/sources/openai_sources.json`.
- [F] Le fonti release notes candidate restano `verification_status=pending_manual_review` e `manual_review_required=true`. Fonte: `config/sources/openai_sources.json`.

## Gestione Status

- [F] Quando `expected_status_codes` e' presente, il verifier richiede uno status incluso in quella lista. Fonte: `radar/url_verifier.py`.
- [F] Quando `expected_status_codes` non e' presente, resta valido il default 200-399. Fonte: `radar/url_verifier.py`.
- [F] Gli status inattesi impostano `unexpected_status=true`. Fonte: `radar/url_verifier.py`.

## Gestione Redirect

- [F] Un final URL diverso dall'URL iniziale imposta `redirected=true`. Fonte: `radar/url_verifier.py`.
- [F] Se `allow_redirects=false`, il redirect rende il risultato unexpected. Fonte: `radar/url_verifier.py`, `tests/test_url_verifier.py`.

## Gestione Timeout

- [F] `timeout_seconds` puo' essere definito per fonte. Fonte: `radar/source_registry.py`, `radar/url_verifier.py`.
- [F] Timeout reali o simulati impostano `timeout=true`. Fonte: `radar/url_verifier.py`, `tests/test_url_verifier.py`.
- [INT] Una review con soli timeout consiglia `network_unstable_retry`. Fonte: `radar/live_url_check.py`.

## Gestione Disabled e Manual Review

- [F] `live_check_enabled=false` restituisce un risultato disabled senza rete. Fonte: `radar/url_verifier.py`, `tests/test_url_verifier.py`.
- [F] `manual_review_required` non blocca il live check, ma documenta che una fonte candidate richiede review umana. Fonte: `config/sources/openai_sources.json`.

## Risultato Live Smoke Sintetico

- [F] Il live smoke 0120 e' stato eseguito fuori repo con `--max-sources 5`. Fonte: output comando `python -m radar.cli check-urls`.
- [F] Risultato live smoke: `Total=5`, `OK=5`, `Failed=0`, `Redirected=0`, `Timeout=0`, `Unreachable=0`, `Unexpected status=0`, `Recommendation=registry_ok`. Fonte: output comando `python -m radar.cli check-urls`.

## MERGE_RECOMMENDATION

- [INT] `MERGE_RECOMMENDATION = YES` perche' test offline e diff-check passano, il live smoke non mostra problemi strutturali, non sono stati modificati file high-risk e non sono stati introdotti parsing live, snapshot live, segreti o dipendenze. Fonte: output comandi finali 0120, `radar/url_verifier.py`, `radar/live_url_check.py`.

## No Auto-Merge

- [F] Lo step 0120 e' L2. Fonte: prompt `0120-A) AI Release Radar - Controlled Live URL Check Review and Source Registry Hardening`.
- [F] Gli step L2 non consentono auto-merge. Fonte: `AGENTS.md`.
- [F] Il prompt 0120 vieta `gh pr ready` e `gh pr merge`. Fonte: prompt `0120-A) AI Release Radar - Controlled Live URL Check Review and Source Registry Hardening`.

## Prossimo Step Consigliato

- [F] Il prossimo step consigliato e' `0130) Source Fetcher Skeleton Without Parsing`. Fonte: prompt `0120-A) AI Release Radar - Controlled Live URL Check Review and Source Registry Hardening`.
