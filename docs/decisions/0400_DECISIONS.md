# 0400) Automation Readiness Decisions

## Decisione Presa

- [F] Il super-step 0320-0400 aggiunge contratto run, simulatore daily, automation gate, failure injection, Bridge retrieval contract, readiness review e closure pack. Fonte: `docs/architecture/0400_AUTOMATION_READINESS_CLOSURE_PACK.md`.
- [F] La strategia PR scelta e' batch PR unica con commit separati per step. Fonte: prompt `0320-0400` salvato nel Bridge.
- [F] Nessuno scheduler reale viene introdotto. Fonte: `radar/cli.py`.
- [F] Nessun task Windows viene creato. Fonte: `radar/cli.py`.
- [F] Nessuna chiamata LLM automatica viene introdotta. Fonte: `radar/cli.py`, `radar/real_run.py`.

## Perche' PR Batch

- [INT] Gli step 0340, 0350, 0360, 0380, 0390 e 0400 sono intrecciati: contratto, simulatore, gate, failure tests e readiness review si validano insieme. Base: file citati in `docs/architecture/0400_AUTOMATION_READINESS_CLOSURE_PACK.md`.
- [INT] PR separate avrebbero creato transizioni intermedie meno utili, ad esempio simulatore senza gate o policy senza simulazione finale. Base: dipendenze tra `radar/cli.py`, `radar/automation_gate.py` e `tests/test_automation_gate.py`.
- [F] I commit restano separati per step. Fonte: cronologia Git del branch `step-0320-0400-automation-readiness`.

## Decisione Scheduler

- [F] La review 0390 conclude `HOLD` per scheduler reale. Fonte: `docs/reviews/0390_DAILY_RUN_READINESS_REVIEW.md`.
- [F] Il repo vieta scheduler salvo istruzione esplicita. Fonte: `AGENTS.md`.
- [INT] La simulazione daily e' ammessa come run controllato fuori repo, non come scheduler. Base: `radar/cli.py`, `docs/reviews/0390_DAILY_RUN_READINESS_REVIEW.md`.

## Decisione Gate

- [F] `FAIL` blocca automazione se output o metriche minime non sono affidabili. Fonte: `radar/automation_gate.py`.
- [F] `PASS_WITH_WARNINGS` rende esplicita coverage bassa o fonti da review. Fonte: `radar/automation_gate.py`.
- [F] `ACTION_REVIEW_REQUIRED` segnala direct actions e richiede review umana. Fonte: `radar/automation_gate.py`.
- [INT] `report_scorecard_status=PASS` resta qualita' report e non readiness scheduler. Base: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.

## Merge Recommendation

- [PROP] MERGE_RECOMMENDATION: YES dopo review manuale della draft PR e con gate CI/locali PASS.
- [F] NO AUTO-MERGE: confirmed. Fonte: prompt `0320-0400` salvato nel Bridge, `AGENTS.md`.
- [F] Auto-merge non applicabile per fase prudenziale L1/L2 e PR draft. Fonte: prompt `0320-0400` salvato nel Bridge.

## Prossimo Step Consigliato

- [PROP] `0410) Source Coverage V1.2 Implementation`: valutare una seconda fonte strutturata solo con fixture offline, fallback sicuro e nessun parser HTML aggressivo.
