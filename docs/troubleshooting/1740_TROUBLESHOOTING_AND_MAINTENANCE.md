# 1740) Troubleshooting and Maintenance Guide

## Dashboard Non Parte

- [F] Comando dashboard: `python -m radar_web.app --host 127.0.0.1 --port 8787`. Fonte: `radar_web/app.py`.
- [PROP] Se la porta e' occupata, usare una porta libera e annotarla nello smoke evidence.
- [F] La dashboard e' locale e legge il Bridge configurato. Fonte: `radar_web/config.py`.

## Porta Occupata

```powershell
netstat -ano | findstr :8787
```

- [PROP] Non terminare processi senza identificare PID e proprietario.
- [PROP] Per smoke Codex temporaneo usare una porta alternativa e chiudere il processo avviato dallo smoke.

## Scheduler Senza Run

- [F] Lo scheduler V1 e' dry-report supervisionato. Fonte: `docs/decisions/0510_L3_SCHEDULER_DRY_REPORT_CONSENT.md`.
- [F] La dashboard legge stato scheduler in read-only. Fonte: `radar_web/scheduler_status.py`.
- [PROP] Verificare `scheduler_logs` nel Bridge e non modificare trigger/orari da questo troubleshooting.

## Lock Attivo O Stale

- [F] Il trigger manuale usa lock per evitare esecuzioni concorrenti. Fonte: `radar_web/manual_trigger.py`.
- [PROP] Non cancellare lock durante uno step Codex salvo autorizzazione esplicita.
- [PROP] Se il lock sembra stale, raccogliere path, timestamp e processo prima di decidere.

## Fonti 403

- [F] HTTP 401/403 viene classificato come manual review. Fonte: `radar/live_snapshot.py`.
- [F] V1 non bypassa 403 con cookie, token, login o browser automation. Fonte: `AGENTS.md`.
- [PROP] Cercare solo alternative ufficiali machine-readable.

## Source Coverage Bassa

- [F] Il gate finale usa `parsed_count_target=3`, classificazione completa e `fragile_parser_count=0`. Fonte: `radar/source_coverage.py`.
- [PROP] Non introdurre parser HTML fragile per aumentare artificialmente `parsed_count`.
- [PROP] Aggiornare fixture e test prima di promuovere una fonte a parsed.

## Daily Review Pack Mancante

- [F] Il pack si genera con `python -m radar.cli daily-review-pack --run-dir <run-dir> --output-dir <Bridge-daily-review-pack-dir> --scheduler-log <scheduler-log>`. Fonte: `radar/cli.py`.
- [F] L'output directory deve stare fuori repository e non usare nomi `LAST-*` o `latest-*`. Fonte: `radar/daily_review_pack.py`.

## Manutenzione Programmata

- [PROP] Verificare mensilmente registry, endpoint GitHub API e fonte Markdown deprecations.
- [PROP] Rieseguire test parser e source coverage dopo ogni modifica a `config/sources/openai_sources.json`.
- [PROP] Tenere tag/release come decisione manuale separata, non automatizzata.
