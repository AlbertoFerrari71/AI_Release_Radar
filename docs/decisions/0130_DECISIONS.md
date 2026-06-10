# 0130) Source Fetcher Skeleton Without Parsing Decisions

## Decisioni Tecniche

- [F] E' stato aggiunto `radar/source_fetcher.py`. Fonte: `radar/source_fetcher.py`.
- [F] E' stata aggiunta la dataclass `FetchedSourceContent`. Fonte: `radar/source_fetcher.py`.
- [F] Sono state aggiunte funzioni per fetch singolo, fetch batch, summary e serializzazione deterministica. Fonte: `radar/source_fetcher.py`.
- [F] E' stato aggiunto il comando CLI `fetch-sources`. Fonte: `radar/cli.py`.
- [F] Sono stati aggiunti test offline/mock. Fonte: `tests/test_source_fetcher.py`.

## Standard Library Only

- [F] Il fetcher usa `urllib.request`, `urllib.error`, `socket`, `dataclasses` e tipi standard. Fonte: `radar/source_fetcher.py`.
- [F] Non sono state aggiunte dipendenze esterne. Fonte: `pyproject.toml` non modificato nello step 0130.

## Limite max_bytes

- [F] `max_bytes` e' validato come intero >= 1. Fonte: `radar/source_fetcher.py`.
- [F] Il fetcher legge il response body con `read(max_bytes)`. Fonte: `radar/source_fetcher.py`.
- [F] Il comando CLI espone `--max-bytes`. Fonte: `radar/cli.py`.
- [INT] Il limite mantiene il live smoke diagnostico e impedisce di usare il fetcher come download completo. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`, `radar/source_fetcher.py`.

## No Parsing

- [F] Il fetcher non importa parser del progetto. Fonte: `radar/source_fetcher.py`, `tests/test_source_fetcher.py`.
- [F] Il fetcher non crea `Item`. Fonte: `radar/source_fetcher.py`, `tests/test_source_fetcher.py`.
- [F] Il fetcher non crea `SourceSnapshot`. Fonte: `radar/source_fetcher.py`, `tests/test_source_fetcher.py`.

## No Snapshot Live

- [F] `fetch-sources` scrive `0130_fetch_sources_results.json` e `0130_fetch_sources_summary.txt` nella directory esplicita. Fonte: `radar/cli.py`.
- [F] `fetch-sources` rifiuta output directory interne al repository. Fonte: `radar/cli.py`, `tests/test_source_fetcher.py`.
- [F] `fetch-sources` non chiama `write_snapshot` e non usa `SourceSnapshot`. Fonte: `radar/cli.py`.

## Gestione body_sample

- [F] `body_sample` contiene solo i byte letti entro `max_bytes`, decodificati UTF-8 con replacement. Fonte: `radar/source_fetcher.py`.
- [F] `body_sample` non viene passato a parser o scoring. Fonte: `radar/source_fetcher.py`, `radar/cli.py`.
- [INT] `body_sample` e' diagnostico per smoke live fuori repo, non una sorgente applicativa persistente. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`, `radar/source_fetcher.py`.

## Live Smoke Sintetico

- [F] Le fixture 0130 sono sintetiche e coprono source ok, failed, disabled e truncated. Fonte: `examples/fixtures/0130_fetcher_sample_results.json`, `examples/fixtures/0130_fetcher_expected_summary.json`.
- [F] Il live smoke reale dello step deve scrivere fuori repo. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.

## MERGE_RECOMMENDATION

- [INT] `MERGE_RECOMMENDATION` deve essere emessa nel report finale dello step 0130 dopo test offline, diff-check, controllo file vietati, controllo segreti, live smoke opzionale e auto-review locale. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.

## No Auto-Merge

- [F] Lo step 0130 e' L2. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.
- [F] Gli step L2 non consentono auto-merge. Fonte: `AGENTS.md`.
- [F] Il prompt 0130 vieta `gh pr ready` e `gh pr merge`. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.

## Prossimo Step Consigliato

- [F] Il prossimo step consigliato e' `0140) Source Fetcher Review and Content Safety Hardening`. Fonte: prompt `0130-A) AI Release Radar - Source Fetcher Skeleton Without Parsing`.
