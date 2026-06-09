# 0090) CLI Dry Run

## Scopo

- [F] Lo step 0090 introduce una CLI locale `python -m radar.cli dry-run`. Fonte: `radar/cli.py`.
- [F] La CLI esegue un dry-run offline usando fixture locali e il report engine introdotto nello step 0080. Fonte: `radar/cli.py`, `radar/report_engine.py`.
- [F] Il prossimo step consigliato dalla CLI e' `0100) OpenAI Source Registry and URL Verification`. Fonte: `radar/cli.py`.

## Cosa Fa la CLI Dry-Run

- [F] `dry-run` carica `examples/fixtures/0080_report_input.json`. Fonte: `radar/cli.py`.
- [F] Il comando costruisce un `ReportInput` tramite `load_report_input`. Fonte: `radar/cli.py`, `radar/report_engine.py`.
- [F] Il comando genera report full e compact tramite `render_full_markdown_report` e `render_compact_markdown_report`. Fonte: `radar/cli.py`, `radar/report_engine.py`.
- [F] Il comando genera un summary deterministico e lo stampa su stdout. Fonte: `radar/cli.py`, `tests/test_cli.py`.

## Perche Usa Fixture 0080

- [F] Il prompt 0090 richiede Strategia A come default: usare `examples/fixtures/0080_report_input.json` e il report engine 0080. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`.
- [INT] Questa scelta stabilizza la CLI e riduce il rischio dello step, perche' non ricostruisce nello stesso step parser, snapshot, diff, score e impatti. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`, `radar/cli.py`.
- [INT] La pipeline completa da parser resta disponibile per uno step successivo. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`.

## No Fetch Live

- [F] `radar/cli.py` usa solo standard library, `radar.json_utils` e `radar.report_engine`. Fonte: `radar/cli.py`.
- [F] La CLI non importa client HTTP o moduli di rete. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] I test CLI verificano l'assenza di pattern client/fetch nel modulo CLI. Fonte: `tests/test_cli.py`.

## Output Generati

- [F] La CLI richiede `--output-dir` esplicito. Fonte: `radar/cli.py`.
- [F] La directory output viene creata se non esiste. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] Il report full viene scritto come `0090_dry_run_report_full.md`. Fonte: `radar/cli.py`.
- [F] Il report compact viene scritto come `0090_dry_run_report_compact.md`. Fonte: `radar/cli.py`.
- [F] Il summary viene scritto come `0090_dry_run_summary.txt`. Fonte: `radar/cli.py`.
- [F] La CLI non usa nomi `LAST-*` o `latest-*`. Fonte: `radar/cli.py`.

## Full, Compact e Summary

- [F] Il report full e' il Markdown completo prodotto dal report engine. Fonte: `radar/report_engine.py`, `examples/fixtures/0090_cli_expected_full.md`.
- [F] Il report compact e' il Markdown compatto prodotto dal report engine. Fonte: `radar/report_engine.py`, `examples/fixtures/0090_cli_expected_compact.md`.
- [F] Il summary e' un file testo breve con stato, path dei report, path summary e prossimo step. Fonte: `radar/cli.py`, `examples/fixtures/0090_cli_expected_summary.txt`.
- [F] `--compact-only` genera solo compact report e summary. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] `--full-only` genera solo full report e summary. Fonte: `radar/cli.py`, `tests/test_cli.py`.

## Exit Code

- [F] `main` restituisce `0` se il dry-run termina correttamente. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] `main` restituisce un codice non zero se il parsing argomenti fallisce o se avviene un errore. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] `--compact-only` e `--full-only` insieme producono errore non zero. Fonte: `radar/cli.py`, `tests/test_cli.py`.

## Limiti CLI V1

- [F] La CLI V1 non ricostruisce l'intera pipeline da parser/snapshot/diff. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`, `radar/cli.py`.
- [F] La CLI V1 non scrive un Bridge runtime definitivo. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`.
- [F] La CLI V1 non aggiorna `runs_index` operativo. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`.

## Fuori Scope

- [F] Source registry reale fuori scope. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`.
- [F] Fetch HTTP fuori scope. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`.
- [F] Bridge runtime definitivo fuori scope. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`.
- [F] Scheduler fuori scope. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`.
- [F] Packaging/install fuori scope. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`.
- [F] Comando `radar last` fuori scope. Fonte: prompt `0090-A) AI Release Radar - CLI Dry Run`.
