# 0100) OpenAI Source Registry and URL Verification

## Scopo

- [F] Lo step 0100 introduce un registry JSON per fonti OpenAI/Codex. Fonte: `config/sources/openai_sources.json`.
- [F] Lo step 0100 introduce il modello `SourceDefinition`. Fonte: `radar/source_registry.py`.
- [F] Lo step 0100 introduce un verificatore URL read-only controllato. Fonte: `radar/url_verifier.py`.
- [F] I test normali restano offline. Fonte: `tests/test_url_verifier.py`.

## Perche 0100 E' L2

- [F] Lo step e' classificato L2 dal prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.
- [F] L2 indica network/read-only integrations e non consente auto-merge. Fonte: `AGENTS.md`.
- [INT] Il rischio L2 deriva dalla presenza di fonti reali e dalla disponibilita' di una verifica HTTP opt-in, anche se la suite default non usa rete. Fonte: prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`, `radar/url_verifier.py`, `tests/test_url_verifier.py`.

## Registry, Verifica URL, Fetch e Parsing

- [F] Il registry contiene metadati statici delle fonti. Fonte: `config/sources/openai_sources.json`.
- [F] La verifica formato controlla che una URL sia `https://` e abbia host. Fonte: `radar/url_verifier.py`.
- [F] La verifica live usa HTTP solo se chiamata esplicitamente. Fonte: `radar/url_verifier.py`, `tests/test_url_verifier.py`.
- [F] Nessuna funzione 0100 salva snapshot live. Fonte: `radar/source_registry.py`, `radar/url_verifier.py`.
- [F] Nessuna funzione 0100 estrae o interpreta contenuti pagina. Fonte: `radar/url_verifier.py`.
- [INT] Il fetch produttivo e il parsing live restano passaggi successivi separati dal registry. Fonte: prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.

## Formato Source Registry

- [F] Il registry ha `schema_version`, `provider` e `sources`. Fonte: `config/sources/openai_sources.json`, `radar/source_registry.py`.
- [F] Ogni source richiede `source_id`, `provider`, `name`, `url`, `source_type`, `priority`, `reliability`, `machine_readable`, `category_hints`, `verification_status` e `notes`. Fonte: `radar/source_registry.py`.
- [F] `source_id` deve essere snake_case. Fonte: `radar/source_registry.py`, `tests/test_source_registry.py`.
- [F] `priority` deve essere intero maggiore o uguale a 1. Fonte: `radar/source_registry.py`, `tests/test_source_registry.py`.
- [F] `category_hints` deve essere una lista non vuota. Fonte: `radar/source_registry.py`.
- [F] L'output registry e' ordinato per `priority` e `source_id`. Fonte: `radar/source_registry.py`, `tests/test_source_registry.py`.

## Reliability

- [F] I valori ammessi sono `primary`, `secondary` e `candidate`. Fonte: `radar/source_registry.py`.
- [INT] `primary` e' usato per documentazione e changelog ufficiali OpenAI. Fonte: `config/sources/openai_sources.json`.
- [INT] `secondary` e' usato per GitHub/OpenAI Codex release surfaces. Fonte: `config/sources/openai_sources.json`.
- [INT] `candidate` e' usato per fonti release notes che richiedono review manuale in 0100. Fonte: `config/sources/openai_sources.json`.

## Verification Status

- [F] I valori ammessi sono `verified_url_format`, `live_verified`, `pending_manual_review`, `unreachable` e `disabled`. Fonte: `radar/source_registry.py`.
- [F] Le fonti non verificate live in questo step usano `verified_url_format` o `pending_manual_review`. Fonte: `config/sources/openai_sources.json`.
- [F] Le candidate release notes sono marcate `pending_manual_review`. Fonte: `config/sources/openai_sources.json`.

## URL Format Verification

- [F] `verify_url_format` accetta URL con schema `https` e host presente. Fonte: `radar/url_verifier.py`.
- [F] `verify_url_format` rifiuta URL `http://` e stringhe non URL. Fonte: `tests/test_url_verifier.py`.
- [F] La validazione registry richiede URL `https://`. Fonte: `radar/source_registry.py`.

## Live Verification Opzionale

- [F] `verify_url_live` usa standard library. Fonte: `radar/url_verifier.py`.
- [F] `verify_url_live` usa timeout obbligatorio con default 10 secondi. Fonte: `radar/url_verifier.py`.
- [F] La verifica live prova `HEAD` prima di `GET`. Fonte: `radar/url_verifier.py`.
- [F] Il fallback `GET` legge al massimo 1024 byte. Fonte: `radar/url_verifier.py`.
- [F] Gli errori sono restituiti in `UrlVerificationResult`. Fonte: `radar/url_verifier.py`.

## Perche I Live Test Sono Disattivati Di Default

- [F] Il test live e' decorato con `skipUnless` e richiede `AI_RELEASE_RADAR_RUN_LIVE_TESTS=1`. Fonte: `tests/test_url_verifier.py`.
- [INT] La suite default resta deterministica e non dipende da rete, DNS, rate limit o variazioni dei siti. Fonte: `tests/test_url_verifier.py`, prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.

## Fuori Scope

- [F] Parsing live fuori scope. Fonte: prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.
- [F] Snapshot live fuori scope. Fonte: prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.
- [F] Scheduler fuori scope. Fonte: prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.
- [F] Report runtime automatico fuori scope. Fonte: prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.
