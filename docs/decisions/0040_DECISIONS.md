# 0040) Offline Fixture Parser Decisions

Fonte principale: prompt operativo `0040-A) AI Release Radar - Offline Fixture Parser` fornito da Alberto il 2026-06-09.

## 1. Decisioni tecniche

- [F] Lo step 0040 deve implementare parser fixture JSON, HTML/text semplice, snapshot builder, fixture artificiali, snapshot attesi, test offline e documentazione. Fonte: prompt 0040-A.
- [INT] Sono state aggiunte funzioni pure invece di classi di parser pubbliche per mantenere l'interfaccia iniziale minimale.
- [F] I parser restituiscono sempre `list[Item]`. Fonte: prompt 0040-A e `radar/parsers.py`.
- [F] Gli output sono ordinati per `published_at`, `title`, `item_id`. Fonte: prompt 0040-A e `radar/parsers.py`.

## 2. Parser fixture-only

- [F] Il parser HTML usa solo il pattern controllato della fixture 0040. Fonte: prompt 0040-A e `radar/parsers.py`.
- [F] Il parser text usa blocchi `--- item ---` e righe `key: value`. Fonte: prompt 0040-A e `radar/parsers.py`.
- [INT] Questa scelta evita di simulare robustezza che il progetto non ha ancora richiesto per pagine reali.

## 3. Niente dipendenze esterne

- [F] Lo step 0040 vieta librerie esterne come BeautifulSoup, requests e pydantic. Fonte: prompt 0040-A.
- [F] `radar/parsers.py` usa solo standard library e moduli locali. Fonte: `radar/parsers.py`.
- [INT] La standard library e' sufficiente per fixture artificiali controllate.

## 4. Niente rete

- [F] Lo step 0040 vieta fetch live, HTTP reali e internet per il parser. Fonte: prompt 0040-A.
- [F] I parser non importano moduli di rete e i test verificano l'assenza di `requests`, `urllib`, `http.client`. Fonte: `radar/parsers.py` e `tests/test_parsers.py`.
- [INT] Gli URL restano dati osservati nell'item, non target chiamati dal codice.

## 5. Snapshot costruiti da item

- [F] `build_source_snapshot_from_items` accetta item gia' parsati e costruisce `SourceSnapshot`. Fonte: prompt 0040-A e `radar/snapshot_builder.py`.
- [F] `http_status=None` e `fetch_status=offline_fixture` sono supportati per fixture offline. Fonte: prompt 0040-A e `tests/test_snapshot_builder.py`.
- [F] `page_hash` non modifica gli item nello snapshot. Fonte: prompt 0040-A e `tests/test_snapshot_builder.py`.
- [INT] Il builder resta una cucitura deterministica tra parser e diff futuri, non un fetcher.

## 6. Formati artificiali controllati

- [F] La fixture JSON simula release GitHub con item `codex_cli`. Fonte: `examples/fixtures/0040_github_releases_fixture.json`.
- [F] La fixture HTML simula changelog Codex con categorie `codex_cli`, `codex_agents_md`, `codex_windows`. Fonte: `examples/fixtures/0040_codex_changelog_fixture.html`.
- [F] La fixture text simula deprecations/API platform con categorie `deprecation` e `api_platform`. Fonte: `examples/fixtures/0040_api_deprecations_fixture.txt`.
- [INT] I formati controllati danno copertura ai tre percorsi di parsing senza anticipare source registry o parser reali.

## 7. Prossimo step consigliato

- [F] Il prossimo step consigliato per il prompt 0040-A e' `0050) Snapshot and Diff Engine`. Fonte: prompt 0040-A.
- [INT] Lo step 0050 dovrebbe usare parser e snapshot fixture completi per confronti end-to-end e rafforzare retention/diff workflow.
