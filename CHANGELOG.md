# Changelog

## 0100) OpenAI Source Registry and URL Verification

- [F] Aggiunto registry fonti OpenAI/Codex. Fonte: `config/sources/openai_sources.json`.
- [F] Aggiunto modello `SourceDefinition`. Fonte: `radar/source_registry.py`.
- [F] Aggiunto URL verifier read-only. Fonte: `radar/url_verifier.py`.
- [F] Aggiunti test offline. Fonte: `tests/test_source_registry.py`, `tests/test_url_verifier.py`.
- [F] Aggiunte fixture registry e URL verification. Fonte: `examples/fixtures/0100_openai_sources_valid.json`, `examples/fixtures/0100_openai_sources_invalid.json`, `examples/fixtures/0100_url_verification_expected.json`.
- [F] Nessun parsing live introdotto. Fonte: `radar/url_verifier.py`.
- [F] Nessuno scheduler introdotto. Fonte: `radar/source_registry.py`, `radar/url_verifier.py`.
- [F] Auto-merge non consentito per step L2. Fonte: `AGENTS.md`, prompt `0100-A) AI Release Radar - OpenAI Source Registry and URL Verification`.

## 0090) CLI Dry Run

- [F] Aggiunta CLI `python -m radar.cli dry-run`. Fonte: `radar/cli.py`.
- [F] Aggiunto output full/compact/summary. Fonte: `radar/cli.py`.
- [F] Aggiunti test CLI. Fonte: `tests/test_cli.py`.
- [F] Aggiunte fixture expected CLI. Fonte: `examples/fixtures/0090_cli_expected_summary.txt`, `examples/fixtures/0090_cli_expected_full.md`, `examples/fixtures/0090_cli_expected_compact.md`.
- [F] Nessun fetch live introdotto. Fonte: `radar/cli.py`.
- [F] Auto-merge trial L1 documentato. Fonte: `docs/decisions/0090_DECISIONS.md`.

## 0080) Report Engine

- [F] Aggiunto report engine Markdown. Fonte: `radar/report_engine.py`.
- [F] Aggiunto report full. Fonte: `radar/report_engine.py`, `examples/fixtures/0080_report_expected_full.md`.
- [F] Aggiunto report compact. Fonte: `radar/report_engine.py`, `examples/fixtures/0080_report_expected_compact.md`.
- [F] Aggiunto status report. Fonte: `radar/report_engine.py`.
- [F] Aggiunti golden test. Fonte: `tests/test_report_engine.py`, `examples/fixtures/0080_report_expected_full.md`, `examples/fixtures/0080_report_expected_compact.md`.
- [F] Nessun fetch live introdotto. Fonte: `radar/report_engine.py`.
- [F] Auto-merge trial L1 documentato. Fonte: `docs/decisions/0080_DECISIONS.md`.

## 0070) Project Impact Mapping

- [F] Aggiunto mapping impatto progetti. Fonte: `radar/project_impact.py`.
- [F] Aggiunto `ProjectImpact`. Fonte: `radar/project_impact.py`.
- [F] Aggiunta project map offline. Fonte: `examples/fixtures/0070_project_map.json`.
- [F] Aggiunte fixture impatti. Fonte: `examples/fixtures/0070_impact_*.json`.
- [F] Aggiunti test offline. Fonte: `tests/test_project_impact.py`.
- [F] Nessun fetch live introdotto. Fonte: `radar/project_impact.py`.
- [F] Auto-merge trial L1 documentato. Fonte: `docs/decisions/0070_DECISIONS.md`.

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
