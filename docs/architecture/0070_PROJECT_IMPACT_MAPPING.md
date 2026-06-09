# 0070) Project Impact Mapping

## Scopo

- [F] Lo step 0070 aggiunge mapping deterministico tra item del radar e progetti reali di Alberto. Fonte: prompt `0070-A) AI Release Radar - Project Impact Mapping`.
- [F] L'implementazione vive in `radar/project_impact.py`. Fonte: `radar/project_impact.py`.
- [F] Lo step resta offline e usa solo standard library Python. Fonte: `radar/project_impact.py`, `pyproject.toml`.

## Relazione Tra Oggetti

- [F] `Item` resta il modello normalizzato della novita' osservata. Fonte: `radar/models.py`.
- [F] `ItemClassification` contiene categoria, severita', keyword matchate e motivazioni di classificazione. Fonte: `radar/classification.py`.
- [F] `RelevanceScore` contiene score totale e componenti auditabili. Fonte: `radar/scoring.py`.
- [F] `ProjectImpact` collega un item a un progetto, con `impact_level`, `reasons` e `suggested_actions`. Fonte: `radar/project_impact.py`.
- [F] `ProjectImpact` e' derivato da `Item`, `ItemClassification`, `RelevanceScore` e project map offline. Fonte: `radar/project_impact.py`.

## Project Map

- [F] La project map offline e' in `examples/fixtures/0070_project_map.json`. Fonte: `examples/fixtures/0070_project_map.json`.
- [F] `load_project_map` valida una lista di progetti e normalizza per `project_key`. Fonte: `radar/project_impact.py`.
- [F] Ogni progetto dichiara `project_key`, `project_name`, categorie rilevanti, keyword opzionali, flag `sensitive` e azioni suggerite. Fonte: `examples/fixtures/0070_project_map.json`, `radar/project_impact.py`.
- [F] La V1 include AI Software Factory, Codex_Skills, Family Photo Organizer, Mansionario_Vivo, AggloDetect, DiamSign e ControlloGestioneExcel / eSolver. Fonte: `examples/fixtures/0070_project_map.json`.

## Regole Impact Level

- [F] I livelli supportati sono `critical`, `high`, `medium`, `low` e `none`. Fonte: `radar/project_impact.py`.
- [F] Un progetto non rilevante produce `none` e non viene incluso nell'output finale. Fonte: `radar/project_impact.py`.
- [F] `critical` viene assegnato per severita' critical su progetto rilevante o per `security`/`deprecation` con score almeno 80. Fonte: `radar/project_impact.py`.
- [F] `high` viene assegnato per severita' high o score almeno 70 su progetto rilevante. Fonte: `radar/project_impact.py`.
- [F] `medium` viene assegnato per severita' medium o score almeno 45 su progetto rilevante. Fonte: `radar/project_impact.py`.
- [F] `low` viene assegnato quando la categoria e' rilevante ma lo score resta basso. Fonte: `radar/project_impact.py`.
- [F] L'output e' ordinato per `item_id` ascendente, `impact_level` discendente e `project_key` ascendente. Fonte: `radar/project_impact.py`.

## Regole Speciali

- [F] `security` aumenta almeno a `high` l'impatto sui progetti sensibili. Fonte: `radar/project_impact.py`.
- [F] `deprecation` aumenta almeno a `high` l'impatto sui progetti API/platform. Fonte: `radar/project_impact.py`.
- [F] `image_vision` aumenta almeno a `medium` l'impatto su AggloDetect, DiamSign e Family Photo Organizer se lo score e' almeno 40. Fonte: `radar/project_impact.py`.
- [F] `codex_agents_md` aumenta almeno a `high` l'impatto su AI Software Factory e Codex_Skills. Fonte: `radar/project_impact.py`.
- [F] `billing` aumenta almeno a `medium` l'impatto su AI Software Factory. Fonte: `radar/project_impact.py`.

## Azioni Suggerite

- [F] Le azioni suggerite sono definite per progetto nella project map offline. Fonte: `examples/fixtures/0070_project_map.json`.
- [F] Ogni `ProjectImpact` include una copia delle azioni del progetto. Fonte: `radar/project_impact.py`.
- [INT] Nella V1 le azioni sono project-level, non ancora filtrate per categoria. Fonte: `radar/project_impact.py`.

## Limiti V1

- [F] La project map e' statica e offline. Fonte: `examples/fixtures/0070_project_map.json`.
- [F] Le regole sono deterministiche e non inferiscono relazioni semantiche non dichiarate nella mappa. Fonte: `radar/project_impact.py`.
- [F] Non vengono interrogati repository esterni, issue tracker, scheduler o servizi live. Fonte: `radar/project_impact.py`.
- [F] Non vengono modificati progetti target diversi da `AI_Release_Radar`. Fonte: prompt `0070-A) AI Release Radar - Project Impact Mapping`.

## Nessun LLM E Nessun Fetch Live

- [F] Il codice non importa client HTTP e non effettua chiamate di rete. Fonte: `radar/project_impact.py`.
- [F] Non viene usato nessun LLM per decidere gli impatti. Fonte: `radar/project_impact.py`.
- [F] Tutte le fixture 0070 sono artificiali e offline. Fonte: `examples/fixtures/0070_*`.

## Fuori Scope

- [F] La generazione di report utente resta fuori scope per 0070. Fonte: prompt `0070-A) AI Release Radar - Project Impact Mapping`.
- [F] Il prossimo step consigliato e' `0080) Report Engine`. Fonte: prompt `0070-A) AI Release Radar - Project Impact Mapping`.
