# Changelog

## 0065) ASF Auto-Merge Policy Clarification

- [F] Chiarita policy auto-merge ASF. Fonte: `AGENTS.md`.
- [F] Definite classi rischio L0-L4. Fonte: `AGENTS.md`.
- [F] Definiti file high-risk. Fonte: `AGENTS.md`.
- [F] Chiarito che modifiche a `AGENTS.md` non sono auto-mergeable. Fonte: `AGENTS.md`.
- [F] Documentata lesson learned dallo step 0060. Fonte: `docs/decisions/0065_DECISIONS.md`.

## 0060) Classification and Relevance Scoring

- [F] Aggiunta classificazione deterministica keyword-based. Fonte: `radar/classification.py`.
- [F] Aggiunto scoring di rilevanza con componenti auditabili. Fonte: `radar/scoring.py`.
- [F] Aggiunte fixture scoring artificiali offline. Fonte: `examples/fixtures/0060_scoring_*.json`.
- [F] Aggiunti test offline per classificazione e scoring. Fonte: `tests/test_classification.py`, `tests/test_scoring.py`.
- [F] Nessun fetch live introdotto. Fonte: `radar/classification.py`, `radar/scoring.py`.
- [F] Primo trial auto-review/auto-merge low-risk documentato. Fonte: `docs/decisions/0060_DECISIONS.md`.

## 0050) Snapshot and Diff Engine

- [F] Aggiunto workflow offline snapshot/diff. Fonte: `radar/offline_workflow.py`.
- [F] Aggiunte fixture previous/current. Fonte: `examples/fixtures/0050_*`.
- [F] Aggiunti snapshot e diff attesi. Fonte: `examples/snapshots/0050_*`.
- [F] Rafforzato il workflow diff con test su `page_hash`, ordine input, previous assente e duplicati. Fonte: `tests/test_offline_workflow.py`.
- [F] Aggiunti test end-to-end offline. Fonte: `tests/test_offline_workflow.py`.
- [F] Nessun fetch live introdotto. Fonte: prompt 0050-A e `radar/offline_workflow.py`.

## 0040) Offline Fixture Parser

- [F] Aggiunti parser fixture offline JSON/HTML/text. Fonte: `radar/parsers.py`.
- [F] Aggiunto snapshot builder da item gia' parsati. Fonte: `radar/snapshot_builder.py`.
- [F] Aggiunte fixture artificiali per changelog Codex, release GitHub e API deprecations. Fonte: `examples/fixtures/0040_*`.
- [F] Aggiunti snapshot fixture attesi. Fonte: `examples/snapshots/0040_*`.
- [F] Aggiunti test offline per parser e snapshot builder. Fonte: `tests/test_parsers.py` e `tests/test_snapshot_builder.py`.
- [F] Nessun fetch live introdotto. Fonte: prompt 0040-A e `radar/parsers.py`.

## 0030) Core Item Model and Snapshot Format

- [F] Aggiunti modelli core `Item`, `SourceSnapshot`, `DiffResult`, `RunIndexEntry`.
- [F] Aggiunte utility deterministiche per JSON, hash contenuto, `item_id` stabile, diff snapshot e run index JSONL append-only.
- [F] Aggiunte fixture offline 0030, test unitari offline e documentazione tecnica schema/decisioni.

## 0010) AI Release Radar Repository Foundation

- Creazione repository dedicato.
- Impostazione struttura iniziale.
- Regola deterministica: nessun file LAST-* o latest-*.
