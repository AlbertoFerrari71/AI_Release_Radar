# 0110) First Controlled Live URL Check

## Scopo

- [F] Lo step 0110 introduce un layer per controlli live read-only sugli URL del registry. Fonte: `radar/live_url_check.py`.
- [F] Lo step 0110 aggiunge la CLI esplicita `check-urls`. Fonte: `radar/cli.py`.
- [F] Lo step 0110 aggiunge test offline con mock e fixture statiche. Fonte: `tests/test_live_url_check.py`, `examples/fixtures/0110_live_url_check_sample_results.json`.

## Perche 0110 E' L2

- [F] Lo step 0110 e' classificato L2 dal prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.
- [F] L2 indica network/read-only integration e non consente auto-merge. Fonte: `AGENTS.md`.
- [INT] Il rischio L2 deriva dalla prima esecuzione controllata di chiamate HTTP reali, anche se il codice non salva contenuti pagina e i test standard restano offline. Fonte: `radar/live_url_check.py`, `radar/url_verifier.py`, `tests/test_live_url_check.py`.

## Verifica URL, Fetch e Parsing

- [F] La verifica URL usa `verify_url_live` introdotto nello step 0100. Fonte: `radar/live_url_check.py`, `radar/url_verifier.py`.
- [F] Il verifier 0100 usa `HEAD` e fallback `GET` limitato a una piccola lettura quando necessario. Fonte: `radar/url_verifier.py`.
- [F] Il layer 0110 non interpreta HTML, JSON o testo delle pagine. Fonte: `radar/live_url_check.py`.
- [F] Il layer 0110 restituisce solo `UrlVerificationResult`. Fonte: `radar/live_url_check.py`.
- [INT] La verifica URL controlla raggiungibilita' e metadati HTTP minimi; il fetch/parsing di contenuti resta fuori scope. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.

## Cosa Viene Controllato

- [F] `check_sources_live` riceve una lista di `SourceDefinition`. Fonte: `radar/live_url_check.py`.
- [F] Ogni source viene verificata con timeout esplicito. Fonte: `radar/live_url_check.py`.
- [F] I risultati sono ordinati per `source_id`. Fonte: `radar/live_url_check.py`, `tests/test_live_url_check.py`.
- [F] `summarize_url_verification_results` conta `total`, `ok`, `failed` e status code. Fonte: `radar/live_url_check.py`, `tests/test_live_url_check.py`.

## Cosa NON Viene Salvato

- [F] Nessun HTML live viene salvato. Fonte: `radar/live_url_check.py`, `radar/cli.py`.
- [F] Nessuno snapshot live viene salvato. Fonte: `radar/live_url_check.py`, `radar/cli.py`.
- [F] Nessun report runtime definitivo viene salvato nel repo. Fonte: `radar/cli.py`.
- [F] La CLI scrive solo JSON risultati e summary testuale nella `--output-dir` indicata. Fonte: `radar/cli.py`.

## Timeout

- [F] `check_sources_live` richiede `timeout_seconds` positivo. Fonte: `radar/live_url_check.py`.
- [F] La CLI espone `--timeout-seconds` con default 10.0. Fonte: `radar/cli.py`.
- [INT] Timeout esplicito evita blocchi lunghi durante smoke manuali o test live opt-in. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.

## max_sources

- [F] `check_sources_live` supporta `max_sources`. Fonte: `radar/live_url_check.py`.
- [F] La CLI espone `--max-sources`. Fonte: `radar/cli.py`.
- [INT] `max_sources` limita il primo smoke live e riduce rumore, durata e rischio operativo. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.

## Gestione Errori Per Fonte

- [F] Errori o eccezioni su una singola fonte sono convertiti in `UrlVerificationResult` con `ok=false`. Fonte: `radar/live_url_check.py`, `tests/test_live_url_check.py`.
- [F] Le altre fonti continuano a essere verificate. Fonte: `tests/test_live_url_check.py`.
- [F] Se tutte le fonti falliscono, la funzione restituisce risultati falliti invece di una eccezione globale. Fonte: `radar/live_url_check.py`.

## Test Offline e Live Opt-In

- [F] I test normali usano mock e fixture statiche. Fonte: `tests/test_live_url_check.py`.
- [F] Il test live richiede `AI_RELEASE_RADAR_RUN_LIVE_TESTS=1`. Fonte: `tests/test_live_url_check.py`.
- [F] La suite standard `python -m unittest discover -s tests` non esegue rete per 0110. Fonte: `tests/test_live_url_check.py`.

## No Auto-Merge

- [F] Lo step 0110 e' L2. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.
- [F] Gli step L2 non consentono auto-merge. Fonte: `AGENTS.md`.
- [INT] La chiusura corretta dello step e' PR draft e review manuale. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`, `AGENTS.md`.

## Fuori Scope

- [F] Parsing live fuori scope. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.
- [F] Snapshot live fuori scope. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.
- [F] Source item extraction fuori scope. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.
- [F] Scheduler fuori scope. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.
- [F] Produzione report giornalieri reali fuori scope. Fonte: prompt `0110-A) AI Release Radar - First Controlled Live URL Check`.
