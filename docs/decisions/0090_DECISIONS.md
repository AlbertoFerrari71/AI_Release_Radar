# 0090) CLI Dry Run Decisions

## Decisioni Tecniche

- [F] La CLI e' implementata in `radar/cli.py`. Fonte: `radar/cli.py`.
- [F] Il comando supportato in questo step e' `dry-run`. Fonte: `radar/cli.py`.
- [F] Le funzioni testabili sono `build_dry_run_report_input`, `run_dry_run`, `build_arg_parser` e `main`. Fonte: `radar/cli.py`.
- [F] I test CLI sono in `tests/test_cli.py`. Fonte: `tests/test_cli.py`.

## Scelta argparse

- [F] La CLI usa `argparse` della standard library. Fonte: `radar/cli.py`.
- [INT] `argparse` mantiene lo step senza dipendenze esterne e rende `python -m radar.cli --help` disponibile senza packaging aggiuntivo. Fonte: `radar/cli.py`.

## Scelta Fixture 0080 Come Input

- [F] Il dry-run carica `examples/fixtures/0080_report_input.json`. Fonte: `radar/cli.py`.
- [F] Il prompt 0090 richiede Strategia A come default. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`.
- [INT] La scelta evita di rifare nello step 0090 la pipeline completa da parser, snapshot, diff, classificazione, scoring e impatti. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`.

## Output File Naming

- [F] Il report full viene scritto come `0090_dry_run_report_full.md`. Fonte: `radar/cli.py`.
- [F] Il report compact viene scritto come `0090_dry_run_report_compact.md`. Fonte: `radar/cli.py`.
- [F] Il summary viene scritto come `0090_dry_run_summary.txt`. Fonte: `radar/cli.py`.
- [F] Le fixture expected CLI sono `examples/fixtures/0090_cli_expected_summary.txt`, `examples/fixtures/0090_cli_expected_full.md` e `examples/fixtures/0090_cli_expected_compact.md`. Fonte: `examples/fixtures/0090_cli_expected_summary.txt`, `examples/fixtures/0090_cli_expected_full.md`, `examples/fixtures/0090_cli_expected_compact.md`.

## No LAST/latest

- [F] Nessun output CLI usa nomi `LAST-*` o `latest-*`. Fonte: `radar/cli.py`.
- [F] I test cercano file `LAST-*` e `latest-*` nel repository. Fonte: `tests/test_cli.py`.
- [INT] Nomi datati/numerati o step-specifici evitano ambiguita' e rispettano ASF Pilot Mode. Fonte: `AGENTS.md`, prompt `0090-A) AI Release Radar - CLI Dry Run`.

## output_dir Esplicita

- [F] `dry-run` richiede `--output-dir`. Fonte: `radar/cli.py`.
- [F] La directory viene creata se non esiste. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] I test usano `tempfile.TemporaryDirectory`. Fonte: `tests/test_cli.py`.
- [INT] Una output directory esplicita evita report runtime nel repository per default. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`, `tests/test_cli.py`.

## Auto-Merge L1

- [F] Il prompt 0090 classifica lo step come tecnico/offline/L1/CLI e autorizza auto-review + auto-merge se tutti i gate PASS. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`.
- [F] Lo step non richiede fetch live, API key, dipendenze esterne, scheduler o file high-risk. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`, `radar/cli.py`.
- [INT] CLI offline, fixture locali e test deterministici rendono lo step compatibile con auto-merge L1 se i gate finali restano PASS. Fonte: `AGENTS.md`, prompt `0090-A) AI Release Radar - CLI Dry Run`.

## Prossimo Step Consigliato

- [F] Il prossimo step consigliato e' `0100) OpenAI Source Registry and URL Verification`. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`, `radar/cli.py`.
