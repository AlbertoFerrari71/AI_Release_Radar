# 0050) Snapshot and Diff Engine Decisions

Fonte principale: prompt operativo `0050-A) AI Release Radar - Snapshot and Diff Engine` fornito da Alberto il 2026-06-09.

## 1. Decisioni tecniche

- [F] Lo step 0050 deve aggiungere un workflow offline snapshot/diff e fixture expected deterministiche. Fonte: prompt 0050-A.
- [INT] E' stato introdotto `radar/offline_workflow.py` come strato sottile sopra parser, builder, JSON utils e diff, senza duplicare logica esistente.
- [F] Non sono state introdotte dipendenze esterne. Fonte: prompt 0050-A e `radar/offline_workflow.py`.
- [F] Il workflow usa solo fixture JSON locali. Fonte: `radar/offline_workflow.py`.

## 2. Regola diff

- [F] Il diff e' basato su presenza di `item_id` e confronto di `content_hash`. Fonte: prompt 0050-A e `radar/diff.py`.
- [F] `page_hash` non influenza `new_items`, `changed_items`, `removed_items` o `unchanged_count`. Fonte: prompt 0050-A e `tests/test_offline_workflow.py`.
- [INT] Questa regola mantiene il diff centrato sul fatto osservato, non su cambiamenti diagnostici della pagina.

## 3. Ordinamento deterministico

- [F] Parser e snapshot builder ordinano gli item per `published_at`, `title`, `item_id`. Fonte: `radar/parsers.py` e `radar/snapshot_builder.py`.
- [F] `DiffResult` ordina `new_items`, `changed_items` e `removed_items`. Fonte: `radar/models.py`.
- [F] I test 0050 verificano che il diff sia stabile anche con item in ordine diverso. Fonte: `tests/test_offline_workflow.py`.

## 4. Regola `previous is None`

- [F] Se lo snapshot precedente e' assente, tutti gli item correnti sono `new_items`. Fonte: prompt 0050-A, `radar/diff.py` e `tests/test_offline_workflow.py`.
- [INT] Questa regola copre il primo run di una fonte quando non esiste ancora baseline.

## 5. Regola duplicati

- [F] Duplicati `item_id` nello stesso `SourceSnapshot` sono vietati. Fonte: `radar/models.py`.
- [F] Il test 0050 verifica che una fixture con due item aventi stessa `natural_key` alzi un errore chiaro. Fonte: `tests/test_offline_workflow.py`.
- [INT] La policy evita ambiguita' nel diff, dove `item_id` e' la chiave di confronto.

## 6. Regola fixture offline

- [F] Le fixture 0050 sono artificiali e locali. Fonte: prompt 0050-A e `examples/fixtures/0050_*`.
- [F] Le fixture usano `https://example.invalid/...` e non URL reali. Fonte: `examples/fixtures/0050_*`.
- [F] Gli output attesi sono versionati come snapshot/diff fixture stabili, non come report runtime. Fonte: prompt 0050-A e `examples/snapshots/0050_*`.

## 7. Rimandato agli step successivi

- [F] Fetch live, scheduler, credenziali, API key e report runtime sono fuori scope. Fonte: prompt 0050-A.
- [F] Classificazione e relevance scoring sono rimandati allo step successivo consigliato. Fonte: prompt 0050-A.

## 8. Prossimo step consigliato

- [F] `0060) Classification and Relevance Scoring`. Fonte: prompt 0050-A.
