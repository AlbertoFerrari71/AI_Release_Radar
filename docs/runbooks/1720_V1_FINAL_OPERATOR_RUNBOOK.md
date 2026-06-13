# 1720) V1 Final Operator Runbook

## Scopo

- [F] AI Release Radar V1 finale e' un prodotto locale supervisionato: raccoglie evidenze, mostra dashboard, prepara Daily Review Pack, Action Center e HAG, ma non esegue decisioni. Fonte: `README.md`, `radar/daily_review_pack.py`, `radar_web/app.py`.
- [F] Nessuna email, nessuna chiamata LLM runtime, nessuna auto-action e nessuna modifica scheduler sono parte del flusso V1 finale. Fonte: `AGENTS.md`, `radar/daily_review_pack.py`, `radar_web/manual_trigger.py`.

## Prerequisiti

- [F] Repository locale: `C:\Users\alberto.ferrari\source\repos\AI_Release_Radar`. Fonte: `AGENTS.md`.
- [F] Bridge locale: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar`. Fonte: `radar_web/config.py`.
- [F] Dashboard locale: `python -m radar_web.app --host 127.0.0.1 --port 8787`. Fonte: `radar_web/app.py`.
- [F] Il Daily Review Pack e i run output sono Bridge-only, non repo output. Fonte: `radar/daily_review_pack.py`, `radar/cli.py`.

## Flusso Giornaliero

1. [F] Lo scheduler dry-report produce output nel Bridge senza auto-action. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`, `docs/decisions/0510_L3_SCHEDULER_DRY_REPORT_CONSENT.md`.
2. [F] L'operatore apre la dashboard locale su `http://127.0.0.1:8787/`. Fonte: `radar_web/app.py`, `docs/architecture/0760_WEB_DASHBOARD_ARCHITECTURE.md`.
3. [F] L'operatore legge ultimo run, source coverage, Action Center, HAG e prompt suggestions. Fonte: `radar_web/templates/index.html`, `radar_web/templates/run_detail.html`, `radar_web/templates/actions.html`.
4. [F] I prompt suggestions restano `suggested_only` e non vengono eseguiti automaticamente. Fonte: `radar/prompt_suggestions.py`, `radar/action_inbox.py`.
5. [PROP] Alberto decide manualmente se aprire uno step separato di manutenzione o implementazione.

## Operator Acceptance Gate

- [F] Per modifiche UI-facing, il Verification Gate non sostituisce l'Acceptance Gate operatore. Fonte: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`.
- [F] L'Acceptance Gate deve verificare accesso reale, primo utilizzo, navigazione Easy Mode/Expert Mode/Action Center/Source Matrix/run detail e porta operatore `127.0.0.1:8787`, salvo diversa configurazione documentata. Fonte: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`, `docs/web/2270_EASY_MODE_UI_CONTRACT.md`.
- [F] I click automatizzati restano limitati a link GET interni, controlli visuali e preferenze UI locali testate; HAG, decisioni operative, scheduler, run trigger, email, notifiche e azioni esterne restano manual-only. Fonte: `docs/quality/2390_OPERATOR_ACCEPTANCE_LESSON_LEARNED.md`, `docs/web/2270_EASY_MODE_UI_CONTRACT.md`.

## Comandi Manuali

```powershell
python -m radar.cli --help
python -m radar.cli daily-sim --help
python -m radar.cli daily-review-pack --help
python -m radar.cli v1-readiness-gate --help
python -m radar_web.app --host 127.0.0.1 --port 8787
```

- [F] Questi comandi non creano tag, release o merge. Fonte: `radar/cli.py`, `radar_web/app.py`.
- [F] `daily-sim` scrive solo in output root esplicito fuori repo. Fonte: `radar/cli.py`.

## Lettura Operativa

- [F] HAG `HOLD_FOR_HUMAN_APPROVAL` significa che il run corrente richiede decisione umana prima di qualunque azione. Fonte: `radar/hag_report.py`.
- [F] Action Center distingue decisioni storiche e run corrente; decisioni storiche non approvano il run corrente. Fonte: `radar/action_inbox.py`, `radar_web/action_center.py`.
- [F] Source matrix mostra parser, fetch, HTTP, manual review, stato V1 finale e follow-up. Fonte: `radar/source_coverage.py`.
- [F] Daily Review Pack include safety summary, scheduler evidence, HAG, action summary, prompt suggestions e source matrix. Fonte: `radar/daily_review_pack.py`.

## Stop

- [F] Fermarsi se test, smoke, safety gate o final readiness gate falliscono. Fonte: `radar/v1_readiness.py`, `radar/source_coverage.py`.
- [F] Fermarsi se compare rischio di email, LLM runtime, scheduler mutation, tag/release o auto-action. Fonte: `AGENTS.md`.

## Aggiornamento Futuro

- [PROP] Aggiornare questo runbook solo con step manutentivi dedicati, dopo test e smoke locali.
