# 0030) Core Item Model and Snapshot Format Decisions

Fonte principale: prompt operativo `0030-A) AI Release Radar - Core Item Model and Snapshot Format` fornito da Alberto il 2026-06-09.

## 1. Decisioni tecniche prese

- [F] Lo step 0030 deve implementare modelli dati, funzioni JSON/hash, diff, run index JSONL, fixture offline, test e documentazione tecnica. Fonte: prompt 0030-A.
- [INT] Sono state usate dataclass frozen con metodi espliciti `to_dict()` e `from_dict()` per mantenere serializzazione deterministica senza dipendenze esterne.
- [F] Non sono state introdotte dipendenze esterne; il codice usa solo Python standard library. Fonte: prompt 0030-A.
- [INT] `Item` include `schema_version` anche se il prompt elenca il campo soprattutto sui contenitori persistenti, per rendere versionate anche le fixture standalone.

## 2. Schema dei modelli

- [F] `Item`: `schema_version`, `item_id`, `source_id`, `provider`, `category`, `severity`, `title`, `published_at`, `url`, `evidence`, `content_hash`, `first_seen`, `confidence`. Fonte: prompt 0030-A.
- [F] `SourceSnapshot`: `schema_version`, `source_id`, `provider`, `fetched_at`, `fetch_status`, `http_status`, `items`, `page_hash`. Fonte: prompt 0030-A.
- [F] `DiffResult`: `schema_version`, `source_id`, `new_items`, `changed_items`, `removed_items`, `unchanged_count`. Fonte: prompt 0030-A.
- [F] `RunIndexEntry`: `schema_version`, `run_id`, `step`, `status`, `started_at`, `finished_at`, `duration_seconds`, `report_full`, `report_compact`, `snapshot_dir`, `notes`. Fonte: prompt 0030-A.

## 3. Regola `item_id`

- [F] `item_id` deve essere stabile e derivato da `source_id` piu' chiave naturale normalizzata. Fonte: prompt 0030-A.
- [INT] L'implementazione usa JSON compatto e ordinato dei due campi normalizzati, poi SHA-256 con prefisso `item_`.

## 4. Regola `content_hash`

- [F] `content_hash` deve derivare dai campi normalizzati rilevanti e non dall'intero dizionario volatile. Fonte: prompt 0030-A.
- [INT] L'implementazione include `source_id`, `provider`, `category`, `severity`, `title`, `published_at`, `url`, `evidence`.
- [INT] L'implementazione esclude `item_id`, `content_hash`, `first_seen`, `confidence` e `schema_version` per evitare che metadati osservativi o di persistenza cambino il contenuto osservato.

## 5. Regola diff

- [F] `previous is None` produce tutti gli item correnti come nuovi. Fonte: prompt 0030-A.
- [F] `new_items`, `changed_items`, `removed_items` dipendono da presenza `item_id` e differenza `content_hash`. Fonte: prompt 0030-A.
- [F] `page_hash` non partecipa alla decisione del diff. Fonte: prompt 0030-A.
- [INT] Le liste di output vengono ordinate per stabilita' e leggibilita'.

## 6. Regola run index append-only

- [F] Il run index deve essere JSONL append-only, una riga per run, senza riscrivere l'intero file. Fonte: prompt 0030-A.
- [F] Il run index deve includere anche run falliti. Fonte: prompt 0030-A.
- [F] Se il file non esiste, la lettura ritorna lista vuota o `None` dove opportuno. Fonte: prompt 0030-A.
- [INT] L'helper rifiuta nomi di file `LAST-*` o `latest-*` per impedire alias mobili.

## 7. Rimandato agli step successivi

- [F] Fetch HTTP live, parser HTML reali, OpenAI source registry reale, scheduler, API key, rete e LLM/API non sono parte dello step 0030. Fonte: prompt 0030-A.
- [F] Parser offline su fixture e' rimandato allo step `0040) Offline Fixture Parser`. Fonte: prompt 0030-A.

## 8. Prossimo step consigliato

- [F] `0040) Offline Fixture Parser`. Fonte: prompt 0030-A.
