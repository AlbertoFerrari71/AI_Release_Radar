# 0060) Decisions

## Decisioni Tecniche

- [F] La classificazione e' implementata in `radar/classification.py`. Fonte: `radar/classification.py`.
- [F] Lo scoring e' implementato in `radar/scoring.py`. Fonte: `radar/scoring.py`.
- [F] I nuovi oggetti `ItemClassification` e `RelevanceScore` sono esportati da `radar/__init__.py`. Fonte: `radar/__init__.py`.
- [F] Le fixture 0060 sono artificiali e si trovano in `examples/fixtures/0060_scoring_*.json`. Fonte: `examples/fixtures/0060_scoring_items.json`, `examples/fixtures/0060_scoring_diff.json`, `examples/fixtures/0060_scoring_expected.json`.

## Regola Keyword-Based

- [F] La V1 usa keyword statiche su `title` ed `evidence`. Fonte: `radar/classification.py`.
- [F] Il matching e' case-insensitive. Fonte: `radar/classification.py`.
- [F] Le keyword matchate sono deduplicate e ordinate per auditabilita'. Fonte: `radar/classification.py`.
- [INT] Questa scelta mantiene lo step offline e ripetibile, coerente con il vincolo low-risk. Fonte: prompt `0060-A) AI Release Radar - Classification and Relevance Scoring`, `radar/classification.py`.

## Regola Di Severita'

- [F] Le severita' sono valutate secondo priorita': `critical`, `high`, `medium`, `low`, `ignored`, `info`. Fonte: `radar/classification.py`.
- [F] Le keyword di vulnerabilita', exploit o data loss producono `critical`. Fonte: `radar/classification.py`.
- [F] Le keyword di deprecation, breaking, removal, retirement, sunset, no-longer o security producono almeno `high`, salvo match `critical`. Fonte: `radar/classification.py`.
- [F] Se nessuna keyword di severita' matcha, il fallback e' `info`. Fonte: `radar/classification.py`.

## Formula Score

- [F] Lo score totale e' la somma di `severity_score`, `keyword_score`, `confidence_score`, `novelty_score` e `category_score`. Fonte: `radar/scoring.py`.
- [F] `keyword_score` e' limitato a 20 punti. Fonte: `radar/scoring.py`.
- [F] `confidence_score` deriva da `round(item.confidence * 10)`. Fonte: `radar/scoring.py`.
- [F] Lo score totale e' intero. Fonte: `radar/scoring.py`, `tests/test_scoring.py`.

## Gestione Unknown

- [F] Se nessuna categoria matcha, `classify_category_from_text` restituisce `unknown`. Fonte: `radar/classification.py`.
- [F] `unknown` ha `category_score` pari a `0`. Fonte: `radar/scoring.py`.
- [INT] Il fallback `unknown` evita classificazioni inventate quando il testo non contiene segnali espliciti. Fonte: `radar/classification.py`.

## Gestione Removed

- [F] `score_diff_items` include gli ID in `DiffResult.removed_items`. Fonte: `radar/scoring.py`.
- [F] Un item rimosso puo' essere score-ato quando l'item precedente e' presente in `items_by_id`. Fonte: `radar/scoring.py`.
- [F] Se l'item rimosso non e' disponibile, `score_diff_items` lo salta senza generare errore. Fonte: `radar/scoring.py`, `tests/test_scoring.py`.
- [INT] Questa scelta consente di usare snapshot precedenti quando disponibili senza inventare dati per item assenti. Fonte: `radar/scoring.py`.

## Auto-Merge Trial Low-Risk

- [F] Il prompt 0060-A autorizza commit, push, PR draft e auto-merge solo se tutti i gate low-risk sono PASS. Fonte: prompt `0060-A) AI Release Radar - Classification and Relevance Scoring`.
- [F] Le condizioni richieste includono test PASS, diff-check PASS, nessun file `LAST-*` o `latest-*`, nessun segreto, nessun fetch live introdotto, nessuna nuova dipendenza, nessuna modifica a `.githooks/pre-push`, `AGENTS.md` o `pyproject.toml`, branch pushato, PR draft creata e working tree pulito. Fonte: prompt `0060-A) AI Release Radar - Classification and Relevance Scoring`.
- [F] Se una condizione non e' vera, lo step deve fermarsi a PR draft senza ready e senza merge. Fonte: prompt `0060-A) AI Release Radar - Classification and Relevance Scoring`.
- [INT] La natura offline, standard-library e fixture-only dello step e' la motivazione tecnica per il trial low-risk. Fonte: prompt `0060-A) AI Release Radar - Classification and Relevance Scoring`, `radar/classification.py`, `radar/scoring.py`.

## Prossimo Step

- [F] Il prossimo step consigliato e' `0070) Project Impact Mapping`. Fonte: prompt `0060-A) AI Release Radar - Classification and Relevance Scoring`.
