# 0300) Actionable Radar V1.1 Closure Pack

## Stato V1.1

- [F] V1.1 mantiene il comando manuale `python -m radar.cli real-run --profile manual --output-dir <directory-fuori-repo>`. Fonte: `radar/cli.py`.
- [F] V1.1 non introduce scheduler, task Windows, notifiche automatiche o chiamate LLM. Fonte: `radar/real_run.py`, `AGENTS.md`.
- [F] Gli output runtime restano fuori repository e i nomi `LAST-*` e `latest-*` sono rifiutati. Fonte: `radar/real_run.py`, `radar/live_snapshot.py`.
- [INT] La V1.1 e' un incremento qualitativo della V1 manuale, non un passaggio ad automazione L3.

## Migliorie Rispetto A V1 Manuale

- [F] La priorita' fonti V1.1 e' documentata in `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.
- [F] Le source diagnostics distinguono `parsed`, `fetched_but_unsupported`, `manual_review_required`, `fetch_failed` e stati conservativi equivalenti. Fonte: `radar/live_snapshot.py`.
- [F] `ProjectImpact` distingue `direct_action`, `monitor_only` e `no_action`. Fonte: `radar/project_impact.py`.
- [F] Le azioni consigliate includono titolo leggibile, motivo di rilevanza e prossimo passo deterministico. Fonte: `radar/project_impact.py`.
- [F] Il real-run include una report scorecard e la serializza nel run summary. Fonte: `radar/real_run.py`, `radar/report_scorecard.py`.
- [F] Il confronto offline V1/V1.1 e' disponibile in `radar/run_comparison.py`. Fonte: `radar/run_comparison.py`.

## Fonti Prioritarie

- [F] `github_api_openai_codex_releases` resta la fonte P0 strutturata e parsata. Fonte: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`, `radar/live_snapshot.py`.
- [PROP] `openai_codex_changelog` resta P1 solo con parser text/markdown conservativo. Fonte: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`, `radar/live_snapshot.py`.
- [PROP] API changelog, API deprecations, Codex CLI reference, Codex AGENTS.md e Codex Skills restano P1/P2 diagnosticate finche' non esiste una forma stabile strutturata. Fonte: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.
- [PROP] Release notes hub, ChatGPT release notes e model release notes restano manual-review o monitoraggio fragile. Fonte: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.

## Fonti Unsupported

- [F] Una fonte fetchata ma non parsata puo' essere classificata `fetched_but_unsupported`. Fonte: `radar/live_snapshot.py`.
- [F] Una fonte 401/403 o marcata manual review puo' essere classificata `manual_review_required`. Fonte: `radar/live_snapshot.py`.
- [INT] Unsupported non significa fallimento del radar se almeno una fonte utile e' parsata, ma deve restare visibile nel report.

## Action Type

| action_type | Interpretazione |
|---|---|
| `direct_action` | [F] Il segnale e' diretto per il progetto e puo' aprire una review/azione tecnica deterministica. Fonte: `radar/project_impact.py`. |
| `monitor_only` | [F] Il progetto resta visibile, ma non deve aprire lavoro implementativo senza segnale diretto. Fonte: `radar/project_impact.py`. |
| `no_action` | [F] Il segnale non giustifica task di progetto. Fonte: `radar/project_impact.py`. |

## Scorecard

- [F] La scorecard valuta otto check: titoli leggibili, link fonte, parsed source count, source diagnostics, project actions, no item-id-only actions, noise control e next step. Fonte: `radar/report_scorecard.py`.
- [F] La scorecard produce `PASS`, `WARN` o `FAIL`. Fonte: `radar/report_scorecard.py`.
- [INT] `PASS` indica qualita' report sufficiente per review manuale; non autorizza scheduler o merge automatico.
- [INT] `WARN` richiede attenzione manuale prima di usare il report come base operativa.
- [INT] `FAIL` indica che il report non e' adeguato per closure V1.1 finche' il problema non viene corretto.

## Confronto V1/V1.1

- [F] `radar/run_comparison.py` confronta sources checked, parsed sources, items, project impacts, direct actions, monitor-only actions, failed sources, unsupported sources e scorecard result. Fonte: `radar/run_comparison.py`.
- [F] `run_real_radar_report` serializza i conteggi action type e unsupported source count nel run summary. Fonte: `radar/real_run.py`.
- [INT] Un confronto V1.1 migliore dovrebbe mostrare meno direct actions generiche e piu' monitor-only dove il segnale non e' diretto.

## Cosa Resta Fuori

- [F] Non viene introdotto parsing HTML aggressivo. Fonte: `radar/live_snapshot.py`, `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.
- [F] Non vengono aggiunte dipendenze esterne. Fonte: `pyproject.toml`.
- [F] Non viene introdotto scheduler. Fonte: `radar/cli.py`, `AGENTS.md`.
- [F] Non vengono eseguite chiamate LLM automatiche. Fonte: `radar/real_run.py`.
- [INT] Parser coverage OpenAI resta il principale limite funzionale della V1.1.

## Perche' Lo Scheduler Non E' Il Prossimo Passo Obbligato

- [F] Lo scheduler e' classificabile L3 per policy ASF. Fonte: `AGENTS.md`.
- [F] V1.1 migliora qualita' report e diagnostica ma lascia ancora molte fonti ufficiali non parsate. Fonte: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.
- [INT] Prima di schedulare serve una policy dedicata su frequenza, retention output Bridge, gestione fallimenti parziali e revisione umana.

## Prossimo Step Consigliato

- [PROP] 0310) Manual V1.1 Review On Real Smoke Output: eseguire o rivedere un smoke manuale fuori repo, confrontarlo con la baseline V1 e decidere se il prossimo incremento deve essere parser coverage, source registry quality o scheduler readiness.
