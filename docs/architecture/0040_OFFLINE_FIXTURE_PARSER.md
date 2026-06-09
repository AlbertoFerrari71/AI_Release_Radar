# 0040) Offline Fixture Parser

Fonte principale: prompt operativo `0040-A) AI Release Radar - Offline Fixture Parser` fornito da Alberto il 2026-06-09.

## 1. Scopo

- [F] Lo step 0040 implementa il primo livello di parsing offline del radar da fixture artificiali locali a `Item[]`. Fonte: prompt 0040-A.
- [F] Lo step 0040 usa i modelli `Item` e `SourceSnapshot` introdotti nello step 0030. Fonte: prompt 0040-A e `radar/models.py`.
- [F] Lo step 0040 non fa fetch HTTP, non chiama rete e non usa dipendenze esterne. Fonte: prompt 0040-A e `radar/parsers.py`.
- [INT] Il risultato serve a provare il percorso fixture -> item normalizzati -> snapshot senza introdurre ancora fonti reali.

## 2. Parser fixture e parser reali

- [F] `parse_json_items_fixture` legge un dizionario fixture con chiave `items`. Fonte: `radar/parsers.py`.
- [F] `parse_simple_html_release_fixture` legge solo il pattern artificiale `<article data-release-id=...>`. Fonte: prompt 0040-A e `radar/parsers.py`.
- [F] `parse_simple_text_release_fixture` legge blocchi controllati delimitati da `--- item ---` con righe `key: value`. Fonte: prompt 0040-A e `radar/parsers.py`.
- [F] Il parser HTML non e' adatto a HTML reale. Fonte: prompt 0040-A e docstring di `parse_simple_html_release_fixture`.
- [INT] I parser fixture sono intenzionalmente piccoli per rendere ripetibili i test e mantenere separato il problema del parsing reale.

## 3. Perche' offline-only

- [F] Lo step 0040 vieta fetch live, HTTP reali, internet, API key e credenziali. Fonte: prompt 0040-A.
- [F] Le fixture sotto `examples/fixtures` usano solo URL `example.invalid`. Fonte: `examples/fixtures/0040_*`.
- [INT] L'offline-only riduce variabilita' e consente di testare ordinamento, hash e snapshot senza dipendere da pagine o servizi esterni.

## 4. Formato fixture JSON

- [F] La fixture JSON `examples/fixtures/0040_github_releases_fixture.json` contiene una chiave `items` con due item `codex_cli`. Fonte: fixture citata.
- [F] Ogni item JSON contiene `natural_key`, `category`, `severity`, `title`, `published_at`, `url`, `evidence`, `first_seen`, `confidence`. Fonte: prompt 0040-A e fixture citata.
- [F] Il parser JSON richiede i campi obbligatori e alza `ValueError` se un campo manca. Fonte: `radar/parsers.py`.

## 5. Formato fixture HTML

- [F] La fixture HTML `examples/fixtures/0040_codex_changelog_fixture.html` contiene tre blocchi `article`. Fonte: fixture citata.
- [F] Le categorie rappresentate sono `codex_cli`, `codex_agents_md`, `codex_windows`. Fonte: fixture citata.
- [F] Le severita' rappresentate sono `medium`, `high`, `info`. Fonte: fixture citata.
- [F] `natural_key`, `first_seen` e `confidence` sono letti da attributi `data-*` dell'`article`. Fonte: fixture citata e `radar/parsers.py`.
- [F] `title`, `published_at`, `category`, `severity`, `evidence` e `url` sono letti da `h2`, `time`, `p` e `a`. Fonte: fixture citata e `radar/parsers.py`.

## 6. Formato fixture text

- [F] La fixture text `examples/fixtures/0040_api_deprecations_fixture.txt` contiene due blocchi delimitati da `--- item ---`. Fonte: fixture citata.
- [F] Le categorie rappresentate sono `api_platform` e `deprecation`. Fonte: fixture citata.
- [F] Almeno un item ha severity `high`. Fonte: fixture citata.
- [F] Il parser text legge righe `key: value` e rifiuta righe non conformi. Fonte: `radar/parsers.py`.

## 7. `item_id` e `content_hash`

- [F] `item_id` viene costruito da `source_id` e `natural_key` usando `stable_item_id`. Fonte: `radar/parsers.py` e `radar/hash_utils.py`.
- [F] `content_hash` viene calcolato con `content_hash_for_item_fields`. Fonte: `radar/parsers.py` e `radar/hash_utils.py`.
- [F] Il `content_hash` include `source_id`, `provider`, `category`, `severity`, `title`, `published_at`, `url`, `evidence`. Fonte: `radar/hash_utils.py`.
- [F] Il `content_hash` non include `first_seen` o `confidence`. Fonte: `radar/hash_utils.py`.
- [INT] Questa separazione consente di distinguere identita' stabile dell'item, contenuto osservabile e metadati di osservazione.

## 8. Costruzione `SourceSnapshot`

- [F] `build_source_snapshot_from_items` costruisce un `SourceSnapshot` da item gia' parsati. Fonte: `radar/snapshot_builder.py`.
- [F] Il builder imposta `schema_version = 1`. Fonte: `radar/snapshot_builder.py` e `radar/models.py`.
- [F] Il builder non fa fetch, non calcola HTTP e accetta `http_status=None`. Fonte: prompt 0040-A e `radar/snapshot_builder.py`.
- [F] Gli item vengono ordinati per `published_at`, `title`, `item_id`. Fonte: prompt 0040-A e `radar/snapshot_builder.py`.
- [F] Il builder valida `source_id`, `provider` e coerenza degli item con quei valori. Fonte: `radar/snapshot_builder.py`.

## 9. Snapshot fixture attesi

- [F] Gli snapshot attesi sono in `examples/snapshots/0040_codex_changelog_snapshot.json`, `examples/snapshots/0040_github_releases_snapshot.json`, `examples/snapshots/0040_api_deprecations_snapshot.json`. Fonte: prompt 0040-A e file citati.
- [F] Ogni snapshot usa `fetch_status = offline_fixture` e `http_status = null`. Fonte: file snapshot citati.
- [F] I test confrontano gli snapshot attesi con snapshot rigenerati dai parser. Fonte: `tests/test_snapshot_builder.py`.

## 10. Fuori scope

- [F] Fetch HTTP e chiamate live sono fuori scope. Fonte: prompt 0040-A.
- [F] Parsing HTML reale e' fuori scope. Fonte: prompt 0040-A.
- [F] Source registry reale e' fuori scope. Fonte: prompt 0040-A.
- [F] Classificazione avanzata e' fuori scope. Fonte: prompt 0040-A.
- [F] Report engine e' fuori scope. Fonte: prompt 0040-A.
- [F] Scheduler e' fuori scope. Fonte: prompt 0040-A.
