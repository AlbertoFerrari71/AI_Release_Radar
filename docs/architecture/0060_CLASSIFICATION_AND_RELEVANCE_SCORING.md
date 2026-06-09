# 0060) Classification and Relevance Scoring

## Scopo

- [F] Lo step 0060 aggiunge classificazione deterministica e scoring di rilevanza per gli `Item` del radar. Fonte: prompt `0060-A) AI Release Radar - Classification and Relevance Scoring`.
- [F] L'implementazione vive in `radar/classification.py` e `radar/scoring.py`. Fonte: `radar/classification.py`, `radar/scoring.py`.
- [F] Lo step resta offline e usa solo standard library Python. Fonte: `radar/classification.py`, `radar/scoring.py`, prompt `0060-A) AI Release Radar - Classification and Relevance Scoring`.

## Determinismo

- [F] La classificazione usa keyword statiche e matching case-insensitive su `title` ed `evidence`. Fonte: `radar/classification.py`.
- [F] Le priorita' di categoria e severita' sono definite come tuple ordinate. Fonte: `radar/classification.py`.
- [F] Le keyword matchate sono deduplicate e ordinate. Fonte: `radar/classification.py`.
- [F] Lo score e' una somma di componenti intere. Fonte: `radar/scoring.py`.
- [F] L'output di `score_diff_items` e' ordinato per `score` decrescente e poi `item_id` crescente. Fonte: `radar/scoring.py`.

## Oggetti

- [F] `Item` resta il modello normalizzato di input e non viene modificato dalla classificazione. Fonte: `radar/models.py`, `radar/classification.py`.
- [F] `ItemClassification` contiene `item_id`, `category`, `severity`, `matched_keywords` e `reasons`. Fonte: `radar/classification.py`.
- [F] `RelevanceScore` contiene score totale, componenti dello score e motivazioni. Fonte: `radar/scoring.py`.
- [F] La classificazione produce un oggetto separato invece di sovrascrivere `Item.category` o `Item.severity`. Fonte: `radar/classification.py`.

## Regole Di Categoria

- [F] Le categorie supportate includono `codex_cli`, `codex_app`, `codex_cloud`, `codex_ide`, `codex_review`, `codex_windows`, `codex_agents_md`, `codex_skills`, `codex_mcp`, `codex_plugins`, `gpt_models`, `chatgpt`, `api_platform`, `deprecation`, `billing`, `security`, `image_vision`, `web_search`, `data_analysis` e `unknown`. Fonte: `radar/classification.py`.
- [F] Se nessuna keyword di categoria viene trovata, la categoria e' `unknown`. Fonte: `radar/classification.py`.
- [F] Se piu' categorie matchano, vince la prima secondo `CATEGORY_PRIORITY`. Fonte: `radar/classification.py`.
- [F] Le categorie `deprecation` e `security` hanno priorita' alta per rendere espliciti i casi piu' critici. Fonte: `radar/classification.py`.

## Regole Di Severita'

- [F] Le severita' supportate sono `critical`, `high`, `medium`, `low`, `ignored` e `info`. Fonte: `radar/classification.py`.
- [F] Se nessuna keyword di severita' viene trovata, la severita' e' `info`. Fonte: `radar/classification.py`.
- [F] Le keyword `critical`, `security vulnerability`, `exploit` e `data loss` portano a `critical`. Fonte: `radar/classification.py`.
- [F] Le keyword di deprecation, breaking, removal, retirement, sunset, no-longer e security portano almeno a `high`, salvo match `critical`. Fonte: `radar/classification.py`.

## Regole Di Scoring

- [F] Severity score: `critical=50`, `high=40`, `medium=25`, `low=10`, `info=5`, `ignored=0`. Fonte: `radar/scoring.py`.
- [F] Novelty score: `new=15`, `changed=10`, `removed=12`, `unchanged=0`. Fonte: `radar/scoring.py`.
- [F] Confidence score: `round(item.confidence * 10)`. Fonte: `radar/scoring.py`.
- [F] Keyword score: `min(20, matched_keyword_count * 4)`. Fonte: `radar/scoring.py`.
- [F] Category score: categorie ad alto impatto valgono `10`, categorie intermedie valgono `7`, altre categorie note valgono `5`, `unknown` vale `0`. Fonte: `radar/scoring.py`.
- [F] Formula totale: `severity_score + keyword_score + confidence_score + novelty_score + category_score`. Fonte: `radar/scoring.py`.

## Novelty

- [F] `score_item` accetta `new`, `changed`, `removed` e `unchanged`. Fonte: `radar/scoring.py`.
- [F] `score_diff_items` valuta gli ID in `new_items`, `changed_items` e `removed_items` di un `DiffResult`. Fonte: `radar/scoring.py`.
- [F] Un item `removed` viene score-ato se l'`Item` precedente e la sua classificazione sono disponibili in input. Fonte: `radar/scoring.py`.
- [F] Se un item rimosso non e' disponibile in `items_by_id` o manca la classificazione, viene saltato senza crash. Fonte: `radar/scoring.py`, `tests/test_scoring.py`.

## Limiti V1

- [F] Le regole sono keyword-based e non inferiscono sinonimi non elencati. Fonte: `radar/classification.py`.
- [F] Il matching non usa LLM, embedding o chiamate remote. Fonte: `radar/classification.py`, `radar/scoring.py`.
- [F] Lo scoring non considera impatto per progetto, owner o canale di distribuzione. Fonte: prompt `0060-A) AI Release Radar - Classification and Relevance Scoring`.
- [F] La mappatura dell'impatto progetto resta fuori scope per lo step 0060. Fonte: prompt `0060-A) AI Release Radar - Classification and Relevance Scoring`.

## Nessun LLM E Nessun Fetch Live

- [F] Il codice 0060 non importa client HTTP e non effettua chiamate di rete. Fonte: `radar/classification.py`, `radar/scoring.py`.
- [F] Le fixture 0060 sono artificiali e offline. Fonte: `examples/fixtures/0060_scoring_items.json`, `examples/fixtures/0060_scoring_diff.json`.
- [F] L'uso di LLM e fetch live e' escluso dallo step. Fonte: prompt `0060-A) AI Release Radar - Classification and Relevance Scoring`.

## Fuori Scope

- [F] Non sono introdotte dipendenze esterne. Fonte: `pyproject.toml`, `radar/classification.py`, `radar/scoring.py`.
- [F] Non sono introdotti scheduler, credenziali o integrazioni con servizi terzi. Fonte: prompt `0060-A) AI Release Radar - Classification and Relevance Scoring`, diff dello step 0060.
- [F] Il prossimo step consigliato e' `0070) Project Impact Mapping`. Fonte: prompt `0060-A) AI Release Radar - Classification and Relevance Scoring`.
