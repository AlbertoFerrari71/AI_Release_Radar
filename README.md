# AI Release Radar

Sistema giornaliero supervisionato per monitorare novità OpenAI, Codex, GPT e futuri strumenti AI, trasformandole in raccomandazioni operative per i progetti software di Alberto.

## Principio operativo

Il radar osserva, confronta, classifica e propone.

Non aggiorna automaticamente repository, skill, script, modelli, scheduler o configurazioni.

## V1 manuale

- [F] La V1 manuale si esegue con `python -m radar.cli real-run --profile manual --output-dir <directory-fuori-repo>`. Fonte: `radar/cli.py`.
- [F] `--output-dir` resta esplicito e deve puntare fuori repository. Fonte: `radar/cli.py`, `radar/real_run.py`.
- [F] Gli output runtime non devono usare file o directory `LAST-*` o `latest-*`. Fonte: `AGENTS.md`, `radar/real_run.py`.
- [F] Il run produce full report, compact report, run summary e `runs_index.jsonl`. Fonte: `radar/real_run.py`.
- [F] Il runbook operativo V1 e' `docs/runbooks/0230_V1_MANUAL_RUN_RUNBOOK.md`. Fonte: `docs/runbooks/0230_V1_MANUAL_RUN_RUNBOOK.md`.

## V1.1 actionable radar

- [F] La V1.1 aggiunge source diagnostics piu' esplicite per `parsed`, `fetched_but_unsupported`, `manual_review_required` e `fetch_failed`. Fonte: `radar/live_snapshot.py`.
- [F] Gli impatti progetto distinguono `direct_action`, `monitor_only` e `no_action`. Fonte: `radar/project_impact.py`.
- [F] Le azioni consigliate includono titolo, motivo di rilevanza e prossimo passo deterministico. Fonte: `radar/project_impact.py`.
- [F] Il report reale include una scorecard e il run summary serializza i conteggi action type. Fonte: `radar/real_run.py`, `radar/report_scorecard.py`.
- [F] Il closure pack V1.1 e' `docs/architecture/0300_ACTIONABLE_RADAR_V1_1_CLOSURE_PACK.md`. Fonte: `docs/architecture/0300_ACTIONABLE_RADAR_V1_1_CLOSURE_PACK.md`.

## Comandi principali

```powershell
python -m radar.cli --help
python -m radar.cli real-run --help
python -m radar.cli real-run --profile manual --output-dir "<directory-fuori-repo>"
```

- [F] Non esiste scheduler attivo nella V1 manuale. Fonte: `radar/cli.py`, `AGENTS.md`.
