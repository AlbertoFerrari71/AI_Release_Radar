# 0030) Core Item Model and Snapshot Format

Fonte principale: prompt operativo `0030-A) AI Release Radar - Core Item Model and Snapshot Format` fornito da Alberto il 2026-06-09.

## 1. Scopo

- [F] Lo step 0030 introduce il primo nucleo tecnico deterministico del radar: `Item`, `SourceSnapshot`, `DiffResult`, `RunIndexEntry`, funzioni JSON/hash, fixture offline e test unitari. Fonte: prompt 0030-A.
- [F] Lo step 0030 e' offline-only: non implementa fetch HTTP, parser HTML reali, source registry reale, scheduler, API key, rete o LLM/API. Fonte: prompt 0030-A.
- [INT] Il confine architetturale di questo step e' il formato dei dati persistenti, non il processo di raccolta live.

## 2. Item come unita' di verita'

- [F] `Item` contiene i campi minimi richiesti: `item_id`, `source_id`, `provider`, `category`, `severity`, `title`, `published_at`, `url`, `evidence`, `content_hash`, `first_seen`, `confidence`. Fonte: prompt 0030-A.
- [F] `confidence` deve stare tra 0 e 1; `item_id` e `content_hash` non possono essere vuoti. Fonte: prompt 0030-A.
- [INT] Il radar confronta il mondo a livello di item per evitare che cambiamenti di pagina non pertinenti producano falsi positivi.
- [INT] `Item` include `schema_version` per rendere serializzabile anche la fixture standalone `examples/fixtures/0030_items.json`.

## 3. `item_id` e `content_hash`

- [F] `item_id` e' stabile e deriva da `source_id` piu' una chiave naturale normalizzata. Fonte: prompt 0030-A.
- [F] `content_hash` deriva da campi normalizzati rilevanti e non dall'intero dizionario volatile. Fonte: prompt 0030-A.
- [INT] `item_id` identifica lo stesso fatto osservato nel tempo.
- [INT] `content_hash` identifica il contenuto osservabile dell'item e non include `first_seen`.
- [INT] In `radar/hash_utils.py`, `content_hash` include `source_id`, `provider`, `category`, `severity`, `title`, `published_at`, `url`, `evidence`.

## 4. `page_hash` diagnostico

- [F] `page_hash` non deve decidere `new_items`, `changed_items` o `removed_items`. Fonte: prompt 0030-A.
- [INT] `page_hash` serve come indizio diagnostico per capire se la pagina sorgente e' cambiata, ma il diff resta centrato sugli item.

## 5. Formato snapshot

- [F] `SourceSnapshot` contiene `schema_version`, `source_id`, `provider`, `fetched_at`, `fetch_status`, `http_status`, `items`, `page_hash`. Fonte: prompt 0030-A.
- [F] Gli snapshot 0030 sono fixture artificiali/offline e non derivano da fetch live. Fonte: prompt 0030-A.
- [INT] `items` e' una lista di `Item` validati e senza `item_id` duplicati nello stesso snapshot.

## 6. Formato diff

- [F] `diff_snapshots(previous, current)` produce `DiffResult`. Fonte: prompt 0030-A.
- [F] Se `previous` e' `None`, tutti gli item correnti sono `new_items`. Fonte: prompt 0030-A.
- [F] Un item e' nuovo se il suo `item_id` non era nello snapshot precedente. Fonte: prompt 0030-A.
- [F] Un item e' cambiato se ha lo stesso `item_id` ma `content_hash` diverso. Fonte: prompt 0030-A.
- [F] Un item e' rimosso se era nello snapshot precedente ma non e' nello snapshot corrente. Fonte: prompt 0030-A.
- [F] Le liste di output devono essere ordinate deterministicamente. Fonte: prompt 0030-A.

## 7. Formato `runs_index.jsonl`

- [F] `RunIndexEntry` contiene `schema_version`, `run_id`, `step`, `status`, `started_at`, `finished_at`, `duration_seconds`, `report_full`, `report_compact`, `snapshot_dir`, `notes`. Fonte: prompt 0030-A.
- [F] Il run index e' JSONL append-only, una riga per run, e include anche run falliti. Fonte: prompt 0030-A.
- [F] `get_last_run_index_entry` legge l'ultima riga valida e non richiede file `LAST-*` o `latest-*`. Fonte: prompt 0030-A.

## 8. Perche' niente `LAST-*` o `latest-*`

- [F] I file `LAST-*` e `latest-*` sono vietati nel repository. Fonte: AGENTS.md e prompt 0030-A.
- [INT] Il progetto preferisce nomi numerati/datati e, per le run future, un indice append-only per mantenere tracciabilita' senza alias mobili.

## 9. Limiti rimandati

- [F] Parser offline reale, fetch live, source registry reale, scoring avanzato, report engine, CLI dry run e scheduler sono rimandati agli step successivi. Fonte: prompt 0030-A e roadmap 0020.
- [F] Il prossimo step consigliato e' `0040) Offline Fixture Parser`. Fonte: prompt 0030-A.
