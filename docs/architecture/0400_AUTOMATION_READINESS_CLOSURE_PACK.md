# 0400) Automation Readiness Closure Pack

## A. Cosa E' Stato Testato

- [F] Source coverage V1.2 planning documentata nello step 0320. Fonte: `docs/architecture/0320_SOURCE_COVERAGE_V1_2_PLANNING.md`.
- [F] Second structured source candidate valutata senza aggiungere parser HTML fragile nello step 0330. Fonte: `docs/architecture/0330_SECOND_STRUCTURED_SOURCE_CANDIDATE.md`.
- [F] Automation run contract definito nello step 0340. Fonte: `docs/architecture/0340_AUTOMATION_RUN_CONTRACT.md`.
- [F] `daily-sim` aggiunto come simulatore controllato senza scheduler. Fonte: `radar/cli.py`, `tests/test_cli.py`.
- [F] Automation gate implementato e documentato nello step 0360. Fonte: `radar/automation_gate.py`, `docs/architecture/0360_AUTOMATION_GATE_POLICY.md`.
- [F] Bridge retrieval contract formalizzato nello step 0370. Fonte: `docs/architecture/0370_BRIDGE_RETRIEVAL_CONTRACT.md`.
- [F] Failure injection offline aggiunti nello step 0380. Fonte: `tests/test_automation_gate.py`.
- [F] Daily run readiness review prodotta nello step 0390. Fonte: `docs/reviews/0390_DAILY_RUN_READINESS_REVIEW.md`.

## B. Cosa E' Pronto

- [F] La simulazione daily e' eseguibile con `python -m radar.cli daily-sim --output-root <Bridge\runs>`. Fonte: `radar/cli.py`.
- [F] La simulazione daily genera una directory datata `0320_0400_daily_sim_YYYYMMDD_HHMMSS`. Fonte: `radar/cli.py`.
- [F] La simulazione daily chiama la logica `real-run` con i default sicuri del profilo manuale. Fonte: `radar/cli.py`.
- [F] Il gate verifica summary, report full/compact, run index entry, `runs_index.jsonl`, output fuori repo, coverage, scorecard e action counts. Fonte: `radar/automation_gate.py`.
- [F] Il gate produce output leggibile in `0350-Daily_Sim_Gate.md` e JSON in `0350-Daily_Sim_Gate.json`. Fonte: `radar/cli.py`.
- [F] I test offline coprono `PASS`, `PASS_WITH_WARNINGS`, `FAIL`, `ACTION_REVIEW_REQUIRED` e failure injection noti. Fonte: `tests/test_automation_gate.py`.

## C. Cosa Non E' Pronto

- [F] La review 0390 conclude `HOLD` per scheduler reale. Fonte: `docs/reviews/0390_DAILY_RUN_READINESS_REVIEW.md`.
- [F] Il run 0310 resta a `parsed_count=1` su `source_count=11`. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] Lo step 0330 non aggiunge una seconda fonte strutturata live. Fonte: `docs/architecture/0330_SECOND_STRUCTURED_SOURCE_CANDIDATE.md`.
- [F] Nessun scheduler, task Windows, notifica automatica o chiamata LLM automatica viene introdotta. Fonte: `radar/cli.py`, `AGENTS.md`.
- [INT] Lo scheduler reale e' rimandato per coverage bassa, manual review sources, unsupported alto e direct actions da revisionare. Base: `docs/reviews/0390_DAILY_RUN_READINESS_REVIEW.md`.

## D. Perche' Lo Scheduler Reale E' Rimandato

- [F] `parsed_count=1/11` e' stato ritenuto insufficiente per scheduler pieno nella review 0310. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] Il gate 0360 produce warning quando coverage e' sotto 0.50. Fonte: `radar/automation_gate.py`.
- [F] Il gate 0360 produce `ACTION_REVIEW_REQUIRED` quando esistono direct actions. Fonte: `radar/automation_gate.py`.
- [INT] Un daily run puo' essere utile come simulazione controllata, ma non deve diventare scheduler finche' i warning non sono stabilizzati su piu' run e Alberto non autorizza uno step L3. Base: `AGENTS.md`, `docs/reviews/0390_DAILY_RUN_READINESS_REVIEW.md`.

## E. Come Eseguire La Simulazione Daily

Da PowerShell nel repository:

```powershell
Set-Location "C:\Users\alberto.ferrari\source\repos\AI_Release_Radar"
python -m radar.cli daily-sim --output-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs"
```

- [F] `--output-root` deve puntare fuori repository. Fonte: `radar/cli.py`.
- [F] Il comando non crea scheduler o task Windows. Fonte: `radar/cli.py`.
- [F] Il comando restituisce codice 1 solo se l'automation gate e' `FAIL`; `PASS_WITH_WARNINGS` e `ACTION_REVIEW_REQUIRED` restano esiti controllati da review. Fonte: `radar/cli.py`.

## F. Come Interpretare Il Gate

- [F] `FAIL` significa blocco strutturale: output mancante, summary non valido, index corrotto, output dentro repo, `source_count=0`, `parsed_count=0` o item zero non spiegato. Fonte: `radar/automation_gate.py`.
- [F] `PASS_WITH_WARNINGS` significa run completo ma con coverage bassa, manual review, unsupported alto, scorecard non PASS, failed source o monitor-only alto. Fonte: `radar/automation_gate.py`.
- [F] `ACTION_REVIEW_REQUIRED` significa run completo con direct actions da leggere manualmente. Fonte: `radar/automation_gate.py`.
- [F] `PASS` significa nessun failure/warning e nessuna direct action; non attiva scheduler. Fonte: `radar/automation_gate.py`, `AGENTS.md`.

## G. Prossimo Step Consigliato

- [PROP] `0410) Source Coverage V1.2 Implementation`: cercare una seconda fonte strutturata realmente stabile oppure migliorare una fonte P1 con fixture offline e fallback sicuro.
- [PROP] Non aprire scheduler finche' non esiste uno step L3 dedicato e autorizzato.
- [PROP] Usare `daily-sim` per raccogliere evidenza Bridge, non per pubblicare notifiche automatiche.
