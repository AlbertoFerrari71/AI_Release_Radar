# 0320) Source Coverage V1.2 Planning

## A. Stato Attuale Fonti

- [F] Il registry operativo contiene 11 fonti abilitate per il controllo live. Fonte: `config/sources/openai_sources.json`.
- [F] La review 0310 ha analizzato un run reale V1.1 con `source_count=11`, `parsed_count=1`, `skipped_count=10`, `failed_count=0`, `item_count=10`, `direct_action_count=10`, `monitor_only_action_count=50`, `unsupported_source_count=10` e `scorecard_status=PASS`. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] La review 0310 ha contato i diagnostic status `parsed=1`, `fetched_but_unsupported=7` e `manual_review_required=3`. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] La fonte parsata utile nel run 0310 e' `github_api_openai_codex_releases`. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [F] La scorecard 0280 valuta qualita' e leggibilita' del report, non la readiness completa dello scheduler. Fonte: `docs/architecture/0280_REPORT_REVIEW_SCORECARD.md`, `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [INT] Il problema principale non e' l'esecuzione del fetch, ma la bassa copertura parser rispetto alle fonti controllate. Base: `failed_count=0`, `parsed_count=1` e `source_count=11` in `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.

## B. Fonti Parsed / Unsupported / Manual Review Required

| state | conteggio V1.1 osservato | fonte / criterio | interpretazione operativa |
|---|---:|---|---|
| `parsed` | 1 | [F] `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md` | [INT] Segnale strutturato usabile per report e azioni, ma copertura insufficiente da sola. |
| `fetched_but_unsupported` | 7 | [F] `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md` | [INT] Fonte raggiunta, ma senza parser sicuro; non deve generare falso verde. |
| `manual_review_required` | 3 | [F] `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md` | [INT] Fonte utile per Alberto, ma non affidabile come input automatico senza review. |
| `fetch_failed` | 0 nel run 0310 | [F] `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md` | [INT] Non e' stato il limite principale del run analizzato. |
| `not_checked` | 0 nel registry corrente | [F] Tutte le fonti in `config/sources/openai_sources.json` hanno `live_check_enabled=true`. | [INT] Stato da mantenere nel modello per fonti disabilitate o fuori perimetro in step futuri. |

## C. Rischio Di Automatizzare Con Parsed Count Basso

- [F] Il run 0310 produce report leggibile e scorecard `PASS` con una sola fonte parsata su 11. Fonte: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [INT] Automatizzare un run giornaliero senza warning coverage renderebbe ripetibile un segnale sbilanciato verso `github_api_openai_codex_releases`. Base: `parsed_count=1` e fonte parsata unica in `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [INT] Un `PASS` pieno sarebbe fuorviante quando `unsupported_source_count=10`, perche' il report puo' essere leggibile ma non completo lato fonti. Base: `unsupported_source_count=10` e scorecard `PASS` in `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.
- [INT] La readiness scheduler deve separare tre segnali: qualita' report, coverage fonti e rumore azioni. Base: critica scorecard in `docs/decisions/0310_DECISIONS.md`.

## D. Priorita' V1.2

1. [PROP] Mantenere `github_api_openai_codex_releases` come P0 strutturata e gia' parsata. Fonte: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.
2. [PROP] Cercare una seconda fonte strutturata o semi-strutturata solo se il formato e' stabile e testabile offline. Fonte: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.
3. [PROP] Non aggiungere parser HTML aggressivi per fonti OpenAI ufficiali finche' non esiste una struttura stabile o fixture controllata. Fonte: `docs/architecture/0240_SOURCE_COVERAGE_PRIORITIZATION.md`.
4. [PROP] Esporre sempre `parsed`, `fetched_but_unsupported`, `manual_review_required`, `fetch_failed` e `not_checked` nei report/gate. Fonte: `radar/live_snapshot.py`.
5. [PROP] Introdurre un automation gate che impedisca `PASS` pieno quando coverage e report quality non superano soglie distinte. Fonte: `docs/decisions/0310_DECISIONS.md`.

## E. Soglia Minima Consigliata Per Scheduler Readiness

- [PROP] Soglia minima per readiness scheduler senza warning: almeno 50% fonti parsate oppure almeno 3 fonti prioritarie parsate, con `report_scorecard_status=PASS`, `failed_count=0` e `manual_review_required_count=0`.
- [PROP] Soglia minima per `PASS_WITH_WARNINGS`: run completo fuori repo, `source_count>0`, `parsed_count>0`, file output presenti, `runs_index.jsonl` valido, ma coverage sotto soglia o fonti manual review presenti.
- [PROP] Soglia di blocco: `parsed_count=0`, summary mancante, report mancante, output dentro repo, index corrotto o scheduler non autorizzato.
- [INT] Con `parsed_count=1/11`, la readiness puo' essere solo warning/review, non scheduler pieno. Base: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`.

## F. Strategia: Coverage O PASS_WITH_WARNINGS

- [PROP] La strategia V1.2 e' migliorare coverage dove esiste una fonte strutturata sicura, ma accettare temporaneamente `PASS_WITH_WARNINGS` per daily simulation controllata.
- [PROP] La simulazione giornaliera deve leggere coverage, output e scorecard, non solo il codice di uscita del comando.
- [PROP] Lo scheduler reale resta rimandato finche' il gate non distingue in modo deterministico coverage bassa, manual review e rumore monitor-only.
- [INT] Con `parsed_count=1/11`, scheduler reale non e' ancora consigliato come prossimo salto automatico. Base: `docs/reviews/0310_MANUAL_V1_1_REAL_SMOKE_REVIEW.md`, `docs/decisions/0310_DECISIONS.md`.
