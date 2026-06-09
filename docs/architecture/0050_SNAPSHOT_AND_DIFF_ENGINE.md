# 0050) Snapshot and Diff Engine

Fonte principale: prompt operativo `0050-A) AI Release Radar - Snapshot and Diff Engine` fornito da Alberto il 2026-06-09.

## 1. Scopo

- [F] Lo step 0050 implementa il primo workflow end-to-end offline del radar: fixture -> parser -> `SourceSnapshot` -> diff -> output fixture atteso. Fonte: prompt 0050-A.
- [F] Lo step 0050 collega il parser JSON fixture dello step 0040, lo snapshot builder dello step 0040 e `diff_snapshots` dello step 0030. Fonte: prompt 0050-A e `radar/offline_workflow.py`.
- [F] Lo step 0050 resta offline e deterministico: non fa fetch live, non chiama HTTP e non usa dipendenze esterne. Fonte: prompt 0050-A e `radar/offline_workflow.py`.
- [INT] Il workflow rende testabile il comportamento reale del diff prima di introdurre fetcher, registry o report engine.

## 2. Workflow offline end-to-end

- [F] `load_items_fixture_snapshot` legge una fixture JSON, chiama `parse_json_items_fixture` e costruisce uno snapshot con `build_source_snapshot_from_items`. Fonte: `radar/offline_workflow.py`.
- [F] `build_snapshot_and_diff_from_item_fixtures` costruisce snapshot previous/current e poi chiama `diff_snapshots`. Fonte: `radar/offline_workflow.py`.
- [F] `build_diff_from_snapshot_files` legge snapshot persistiti e produce un `DiffResult`. Fonte: `radar/offline_workflow.py`.
- [F] `write_snapshot`, `read_snapshot`, `write_diff_result`, `read_diff_result` usano JSON deterministico. Fonte: `radar/offline_workflow.py` e `radar/json_utils.py`.

## 3. Relazione tra parser, snapshot builder e diff engine

- [F] Il parser JSON fixture trasforma dati artificiali in `Item[]`. Fonte: `radar/parsers.py`.
- [F] Lo snapshot builder incapsula item gia' parsati in `SourceSnapshot` con `fetch_status=offline_fixture` e `http_status=None`. Fonte: `radar/snapshot_builder.py` e `radar/offline_workflow.py`.
- [F] Il diff engine confronta due `SourceSnapshot` usando `item_id` e `content_hash`. Fonte: `radar/diff.py`.
- [INT] Questa separazione mantiene chiari tre confini: parsing dati, persistenza snapshot, confronto item.

## 4. Significato dei campi diff

- [F] `new_items` contiene gli `item_id` presenti nello snapshot corrente e assenti nello snapshot precedente. Fonte: `radar/diff.py`.
- [F] `changed_items` contiene gli `item_id` presenti in entrambi gli snapshot ma con `content_hash` diverso. Fonte: `radar/diff.py`.
- [F] `removed_items` contiene gli `item_id` presenti nello snapshot precedente e assenti nello snapshot corrente. Fonte: `radar/diff.py`.
- [F] `unchanged_count` conta gli item presenti in entrambi gli snapshot con stesso `content_hash`. Fonte: `radar/diff.py`.
- [F] Le liste di output sono ordinate deterministicamente. Fonte: `radar/diff.py` e `radar/models.py`.

## 5. Fixture 0050

- [F] `examples/fixtures/0050_previous_items_fixture.json` contiene quattro item: due invariati, uno cambiato nel current e uno rimosso. Fonte: fixture citata.
- [F] `examples/fixtures/0050_current_items_fixture.json` contiene quattro item: due invariati, uno cambiato e uno nuovo. Fonte: fixture citata.
- [F] Le fixture usano URL `https://example.invalid/...`. Fonte: fixture citate.
- [F] Gli snapshot attesi sono `0050_previous_snapshot.json`, `0050_current_snapshot.json` e `0050_diff_result.json`. Fonte: `examples/snapshots/0050_*`.

## 6. `page_hash` diagnostico

- [F] `page_hash` viene salvato nello snapshot ma non partecipa al diff item-level. Fonte: prompt 0050-A e `radar/diff.py`.
- [F] I test verificano che due snapshot con stessi item e `page_hash` diverso non producano `changed_items`. Fonte: `tests/test_offline_workflow.py`.
- [INT] `page_hash` resta utile per capire se il contenitore sorgente e' cambiato, ma non decide impatti sul radar.

## 7. Duplicati `item_id`

- [F] `SourceSnapshot` rifiuta duplicati `item_id` nello stesso snapshot con `ValueError`. Fonte: `radar/models.py`.
- [F] Il workflow 0050 eredita questa policy quando una fixture JSON contiene due item con la stessa chiave naturale. Fonte: `tests/test_offline_workflow.py`.
- [INT] Vietare duplicati evita che il dizionario di confronto del diff nasconda un item sovrascrivendone un altro.

## 8. Assenza di fetch live

- [F] Lo step 0050 vieta fetch live, HTTP reali, internet, API key e credenziali. Fonte: prompt 0050-A.
- [F] `radar/offline_workflow.py` legge solo file JSON locali tramite `read_json`. Fonte: `radar/offline_workflow.py`.
- [INT] Le URL nelle fixture sono evidenza sintetica, non destinazioni chiamate dal workflow.

## 9. Assenza di report engine

- [F] Lo step 0050 richiede snapshot/diff fixture e test, non report runtime versionati. Fonte: prompt 0050-A.
- [INT] Il diff result serializzato e' l'output tecnico minimo su cui un report engine potra' lavorare in uno step successivo.

## 10. Fuori scope

- [F] Fetch HTTP live e scheduler sono fuori scope. Fonte: prompt 0050-A.
- [F] API key, credenziali e chiamate a servizi terzi sono fuori scope. Fonte: prompt 0050-A.
- [F] Report engine e output runtime nel repo sono fuori scope. Fonte: prompt 0050-A.
- [F] Classificazione/scoring avanzati sono fuori scope dello step 0050. Fonte: prompt 0050-A.
- [F] Il prossimo step consigliato e' `0060) Classification and Relevance Scoring`. Fonte: prompt 0050-A.
