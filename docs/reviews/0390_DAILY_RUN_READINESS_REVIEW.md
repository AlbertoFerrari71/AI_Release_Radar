# 0390) Daily Run Readiness Review

## A. Esito

- [F] Esiti ammessi da questa review: `GO`, `GO_WITH_WARNINGS`, `HOLD`, `STOP`. Fonte: prompt `0320-0400` salvato nel Bridge.
- [F] La review 0310 ha osservato `source_count=11`, `parsed_count=1`, `unsupported_source_count=10`, `manual_review_required=3`, `direct_action_count=10`, `monitor_only_action_count=50` e `scorecard_status=PASS`. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] L'automation gate 0360 produce warning quando `parsed_count/source_count` e' sotto 0.50 e non consente `PASS` pieno con coverage bassa. Fonte: `docs/architecture/0360_AUTOMATION_GATE_POLICY.md`, `radar/automation_gate.py`.
- [INT] Esito readiness scheduler: `HOLD`. Base: coverage bassa, fonti manual review, unsupported alto e direct actions da revisionare.

## B. Source Coverage

- [F] Il run 0310 ha parsato 1 fonte su 11. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] La fonte parsata e' `github_api_openai_codex_releases`. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] La pianificazione 0320 conclude che `parsed_count=1/11` non e' sufficiente per scheduler pieno. Fonte: `docs/architecture/0320_SOURCE_COVERAGE_V1_2_PLANNING.md`.
- [INT] La base informativa e' utile per review manuale, ma troppo stretta per automazione giornaliera non supervisionata. Base: `parsed_count=1`, `source_count=11`.

## C. Parser Count

- [F] `radar/live_snapshot.py` parsa `github_api` e parsa `openai_codex_changelog` solo se il contenuto e' `text/markdown` o `text/plain`. Fonte: `radar/live_snapshot.py`.
- [F] Lo step 0330 non aggiunge parser HTML aggressivi. Fonte: `docs/architecture/0330_SECOND_STRUCTURED_SOURCE_CANDIDATE.md`.
- [INT] Non e' corretto alzare la readiness con parser fragile solo per aumentare il conteggio parser. Base: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.

## D. Manual Review Sources

- [F] La review 0310 ha contato 3 fonti `manual_review_required`. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] Il gate 0360 produce warning quando `manual_review_required_count>0`. Fonte: `radar/automation_gate.py`.
- [INT] Le fonti manual review possono restare visibili nel report, ma non devono diventare segnale automatico senza Alberto. Base: `docs/architecture/0360_AUTOMATION_GATE_POLICY.md`.

## E. Unsupported Sources

- [F] La review 0310 ha contato `unsupported_source_count=10`. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] Il gate 0360 produce warning quando `unsupported_source_count/source_count>=0.50`. Fonte: `radar/automation_gate.py`.
- [INT] Unsupported alto non e' blocco per simulazione controllata, ma e' blocco per scheduler pieno. Base: `docs/architecture/0360_AUTOMATION_GATE_POLICY.md`.

## F. Scorecard

- [F] Il run 0310 ha `scorecard_status=PASS`. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] La review 0310 interpreta il PASS come qualita' report, non come readiness scheduler. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [INT] La scorecard resta utile, ma deve essere subordinata al gate automation per decisioni daily/scheduler. Base: `docs/architecture/0360_AUTOMATION_GATE_POLICY.md`.

## G. Direct Actions

- [F] Il run 0310 ha `direct_action_count=10`. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] Il gate 0360 usa `ACTION_REVIEW_REQUIRED` quando `direct_action_count>0` e non ci sono failure. Fonte: `radar/automation_gate.py`.
- [INT] Le direct actions sono utili per review manuale, ma vietano qualunque azione automatica. Base: `docs/architecture/0360_AUTOMATION_GATE_POLICY.md`.

## H. Bridge Contract

- [F] Il contratto Bridge 0370 definisce report Codex deterministici, runtime run in `...\runs\<run_folder_datata>\` e divieto `LAST-*`/`latest-*`. Fonte: `docs/architecture/0370_BRIDGE_RETRIEVAL_CONTRACT.md`.
- [F] Il contratto run 0340 richiede output fuori repo e gate leggibile. Fonte: `docs/architecture/0340_AUTOMATION_RUN_CONTRACT.md`.
- [INT] La parte retrieval e' pronta per simulazione controllata, non per scheduler senza prompt dedicato. Base: `docs/architecture/0370_BRIDGE_RETRIEVAL_CONTRACT.md`.

## I. Failure Injection Tests

- [F] I failure injection offline colpiscono summary mancante, report mancante, index corrotto, output dentro repo, 403/manual review, zero parsed, coverage bassa, zero direct action, monitor-only alto e manual review alto. Fonte: `tests/test_automation_gate.py`.
- [INT] Il gate ha una base test sufficiente per impedire falsi verdi noti in simulazione. Base: `tests/test_automation_gate.py`.

## J. Human Approval Gate

- [F] Il repo vieta merge su `main` e scheduler salvo istruzione esplicita/policy dedicata. Fonte: `AGENTS.md`.
- [F] Lo step 0320-0400 richiede `NO AUTO-MERGE`. Fonte: prompt `0320-0400` salvato nel Bridge.
- [INT] Anche con daily simulation eseguibile, attivare scheduler sarebbe step L3 e richiederebbe autorizzazione esplicita separata. Base: `AGENTS.md`.

## K. Decisione

- [INT] `GO`: non applicabile, perche' coverage e direct actions richiedono review.
- [INT] `GO_WITH_WARNINGS`: applicabile solo alla simulazione daily controllata fuori repo.
- [INT] `HOLD`: decisione per scheduler reale.
- [INT] `STOP`: non necessario se test e simulazione finale passano; i rischi sono gestiti come warning/HOLD.

## L. Raccomandazione

- [PROP] Eseguire `daily-sim` come simulazione controllata e leggere `automation_gate_status`.
- [PROP] Non attivare scheduler reale nel blocco 0320-0400.
- [PROP] Prossimo step consigliato: aumentare source coverage V1.2 con una seconda fonte strutturata solo se testabile offline e non fragile.
