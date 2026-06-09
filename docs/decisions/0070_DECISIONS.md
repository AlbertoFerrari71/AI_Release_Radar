# 0070) Project Impact Mapping

## Decisioni Tecniche

- [F] Il mapping impatto progetto e' implementato in `radar/project_impact.py`. Fonte: `radar/project_impact.py`.
- [F] `ProjectImpact` contiene `item_id`, `project_key`, `project_name`, `impact_level`, `reasons` e `suggested_actions`. Fonte: `radar/project_impact.py`.
- [F] `ProjectImpact` e' esportato da `radar/__init__.py`. Fonte: `radar/__init__.py`.
- [F] Le fixture 0070 sono in `examples/fixtures/0070_*`. Fonte: `examples/fixtures/0070_project_map.json`, `examples/fixtures/0070_impact_items.json`, `examples/fixtures/0070_impact_classifications.json`, `examples/fixtures/0070_impact_scores.json`, `examples/fixtures/0070_impact_expected.json`.

## Project Map Offline

- [F] La project map e' un file JSON offline. Fonte: `examples/fixtures/0070_project_map.json`.
- [F] `load_project_map` valida presenza di progetti, chiavi univoche, categorie, keyword, flag `sensitive` e azioni suggerite. Fonte: `radar/project_impact.py`.
- [F] La mappa include AI Software Factory, Codex_Skills, Family Photo Organizer, Mansionario_Vivo, AggloDetect, DiamSign e ControlloGestioneExcel / eSolver. Fonte: `examples/fixtures/0070_project_map.json`.
- [INT] Una mappa offline mantiene lo step L1 perche' non richiede discovery live dei repository target. Fonte: prompt `0070-A) AI Release Radar - Project Impact Mapping`, `radar/project_impact.py`.

## Regole Impatto

- [F] La rilevanza progetto e' basata su categoria classificata e keyword matchate. Fonte: `radar/project_impact.py`.
- [F] Il livello impatto usa severita' classificata e score di rilevanza. Fonte: `radar/project_impact.py`.
- [F] I livelli sono ordinati come `critical > high > medium > low > none`. Fonte: `radar/project_impact.py`.
- [F] Gli impatti `none` non sono inclusi nell'output finale. Fonte: `radar/project_impact.py`.
- [F] L'output e' ordinato in modo deterministico per `item_id`, `impact_level` e `project_key`. Fonte: `radar/project_impact.py`.

## Gestione Progetti Sensibili

- [F] La project map include un flag booleano `sensitive`. Fonte: `examples/fixtures/0070_project_map.json`.
- [F] `security` aumenta almeno a `high` l'impatto sui progetti marcati sensibili. Fonte: `radar/project_impact.py`.
- [INT] Il flag `sensitive` evita di trattare allo stesso modo progetti con dati o workflow piu' delicati e progetti puramente tecnici. Fonte: `examples/fixtures/0070_project_map.json`.

## Regole Specifiche

- [F] `security` aumenta almeno a `high` sui progetti sensibili. Fonte: `radar/project_impact.py`.
- [F] `deprecation` aumenta almeno a `high` sui progetti API/platform. Fonte: `radar/project_impact.py`.
- [F] `image_vision` aumenta almeno a `medium` su AggloDetect, DiamSign e Family Photo Organizer se score >= 40. Fonte: `radar/project_impact.py`.
- [F] `codex_agents_md` aumenta almeno a `high` su AI Software Factory e Codex_Skills. Fonte: `radar/project_impact.py`.
- [F] `billing` aumenta almeno a `medium` su AI Software Factory. Fonte: `radar/project_impact.py`.

## Motivazione Auto-Merge Trial L1

- [F] Il prompt 0070 classifica lo step come tecnico/offline/L1 e autorizza auto-review + auto-merge se tutti i gate PASS. Fonte: prompt `0070-A) AI Release Radar - Project Impact Mapping`.
- [F] Lo step non richiede fetch live, API key, dipendenze esterne, scheduler o modifica a file high-risk. Fonte: prompt `0070-A) AI Release Radar - Project Impact Mapping`, `radar/project_impact.py`.
- [INT] La combinazione di codice offline, fixture artificiali e test deterministici rende lo step adatto al trial L1 definito in `AGENTS.md`. Fonte: `AGENTS.md`, `radar/project_impact.py`, `tests/test_project_impact.py`.

## Esito Auto-Merge

- [F] L'esito operativo dell'auto-merge dipende dai gate finali dello step e dal report finale di esecuzione. Fonte: prompt `0070-A) AI Release Radar - Project Impact Mapping`.
- [F] Il repository non deve versionare report runtime dello step. Fonte: `AGENTS.md`, prompt `0070-A) AI Release Radar - Project Impact Mapping`.

## Prossimo Step

- [F] Il prossimo step consigliato e' `0080) Report Engine`. Fonte: prompt `0070-A) AI Release Radar - Project Impact Mapping`.
