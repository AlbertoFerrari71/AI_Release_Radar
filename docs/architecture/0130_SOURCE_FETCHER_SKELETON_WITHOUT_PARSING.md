# 0130) Source Fetcher Skeleton Without Parsing

## Scopo

- [F] Lo step 0130 introduce `FetchedSourceContent`. Fonte: `radar/source_fetcher.py`.
- [F] Lo step 0130 introduce un fetcher read-only che legge un campione limitato del response body. Fonte: `radar/source_fetcher.py`.
- [F] Lo step 0130 aggiunge il comando CLI `fetch-sources`. Fonte: `radar/cli.py`.
- [F] Lo step 0130 aggiunge test offline/mock e fixture sintetiche. Fonte: `tests/test_source_fetcher.py`, `examples/fixtures/0130_fetcher_sample_results.json`.

## Perche 0130 E' L2

- [F] Il prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing` classifica lo step come L2.
- [F] Gli step L2 sono network/read-only integrations e non consentono auto-merge. Fonte: `AGENTS.md`.
- [INT] Il rischio L2 deriva dal fatto che il fetcher puo' leggere contenuti live, anche se in modo bounded, read-only e senza parsing. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`, `radar/source_fetcher.py`.

## URL Verification vs Source Fetcher

- [F] Il live URL check verifica raggiungibilita', status, redirect e categorie di errore senza salvare contenuto pagina. Fonte: `radar/url_verifier.py`, `radar/live_url_check.py`.
- [F] Il source fetcher esegue una richiesta GET e conserva solo un `body_sample` limitato. Fonte: `radar/source_fetcher.py`.
- [INT] Il source fetcher e' lo step intermedio tra verifica URL e futuri parser: prepara diagnostica controllata, ma non interpreta il contenuto. Fonte: `radar/source_fetcher.py`, prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.

## No Parsing

- [F] `radar/source_fetcher.py` non importa `radar.parsers`. Fonte: `radar/source_fetcher.py`, `tests/test_source_fetcher.py`.
- [F] `radar/source_fetcher.py` non crea `Item` e non crea `SourceSnapshot`. Fonte: `radar/source_fetcher.py`, `tests/test_source_fetcher.py`.
- [F] Il comando CLI `fetch-sources` scrive solo risultati fetch e summary, non snapshot e non report runtime definitivo. Fonte: `radar/cli.py`.
- [INT] Il divieto di parsing riduce il rischio di trasformare contenuti live in dati applicativi prima della review di sicurezza del prossimo step. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.

## Perche max_bytes E' Obbligatorio

- [F] `fetch_source_content` accetta `max_bytes` e valida che sia un intero >= 1. Fonte: `radar/source_fetcher.py`.
- [F] Il fetcher chiama `read(max_bytes)` e quindi non legge l'intero response body. Fonte: `radar/source_fetcher.py`.
- [F] `truncated=true` viene impostato quando `content_length` supera `max_bytes` oppure quando il campione letto raggiunge il limite senza content length disponibile. Fonte: `radar/source_fetcher.py`.
- [INT] Il limite obbligatorio evita di salvare o maneggiare nel processo contenuti live completi. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`, `radar/source_fetcher.py`.

## FetchedSourceContent

- [F] `FetchedSourceContent` contiene `source_id`, `url`, `ok`, `status_code`, `final_url`, `content_type`, `content_length`, `body_sample`, `truncated` ed `error`. Fonte: `radar/source_fetcher.py`.
- [F] `body_sample` e' un piccolo campione diagnostico e viene serializzato solo nei risultati del fetcher. Fonte: `radar/source_fetcher.py`.
- [F] `fetched_sources_to_dict` produce uno shape deterministico con `schema_version`, `summary` e `results`. Fonte: `radar/source_fetcher.py`.

## Disabled, Error e Truncated

- [F] Una fonte con `live_check_enabled=false` restituisce `error=live_check_disabled` senza chiamare rete. Fonte: `radar/source_fetcher.py`, `tests/test_source_fetcher.py`.
- [F] Un errore di rete su una fonte produce un risultato errore e non blocca il batch. Fonte: `radar/source_fetcher.py`, `tests/test_source_fetcher.py`.
- [F] Status non attesi e redirect non consentiti rendono `ok=false` con errore classificato. Fonte: `radar/source_fetcher.py`.
- [F] `summarize_fetched_sources` conta total, ok, failed, disabled e truncated. Fonte: `radar/source_fetcher.py`, `tests/test_source_fetcher.py`.

## Live Smoke Fuori Repo

- [F] Il comando `fetch-sources` richiede `--output-dir`. Fonte: `radar/cli.py`.
- [F] Il comando `fetch-sources` rifiuta una `--output-dir` interna al repository. Fonte: `radar/cli.py`, `tests/test_source_fetcher.py`.
- [F] Lo smoke live 0130 deve scrivere fuori repo, ad esempio sotto `$env:TEMP`. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.
- [F] I test standard restano offline/mock. Fonte: `tests/test_source_fetcher.py`.
- [INT] L'output live non va versionato perche' contiene diagnostica runtime e potenziali campioni di contenuto reale. Fonte: `AGENTS.md`, prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.

## No Auto-Merge

- [F] Lo step 0130 e' L2. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.
- [F] Gli step L2 non consentono auto-merge. Fonte: `AGENTS.md`.
- [F] Il prompt 0130 vieta `gh pr ready` e `gh pr merge`. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.
- [INT] La chiusura corretta e' branch di step, commit, push, PR draft, auto-review locale, merge recommendation e stop senza merge. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`, `AGENTS.md`.

## Fuori Scope

- [F] Parsing live fuori scope. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.
- [F] Item extraction fuori scope. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.
- [F] Snapshot live fuori scope. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.
- [F] Scheduler fuori scope. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.
- [F] Report giornaliero automatico fuori scope. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.
