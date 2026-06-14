# 2460 Daily Intelligence Brief Contract

## Scopo

- [F] `daily-brief` produce un riepilogo giornaliero deterministico da artifact Bridge esistenti. Fonte: `radar/daily_intelligence.py`.
- [F] La feature non introduce chiamate LLM runtime, fetch live, email, notifiche, scheduler mutation o auto-action. Fonte: `radar/daily_intelligence.py`, `radar_web/app.py`.
- [F] Easy Mode mostra `Oggi in 30 secondi` come sintesi alta della giornata. Fonte: `radar_web/templates/easy_index.html`.

## Invarianti Safety

- [F] Il radar osserva e propone; l'umano decide. Fonte: `AGENTS.md`.
- [F] Le azioni suggerite sono `manual_only` e `not_executed`. Fonte: `radar/daily_intelligence.py`.
- [F] HAG e Action Center restano preservati; nessun endpoint nuovo esegue decisioni operative. Fonte: `radar_web/app.py`, `radar_web/templates/actions.html`.
- [F] Gli output runtime sono scritti solo nel Bridge `daily_briefs`. Fonte: `radar/daily_intelligence.py`.

## Modello Dati

### HumanDailyBrief

- [F] Campi principali: `date`, `run_id`, `generated_at_utc`, `overall_status`, `traffic_light`, `one_sentence_summary`, `top_items`, `source_cards`, `project_impacts`, `suggested_manual_actions`, `hag_status`, `forbidden_actions`, `evidence_paths`. Fonte: `radar/daily_intelligence.py`.

### AIModelPacket

- [F] Campi principali: `packet_type`, `date`, `run_id`, `generated_at_utc`, `overall_status`, `facts`, `inferences`, `project_impacts`, `suggested_prompts`, `forbidden_actions`, `evidence_paths`, `confidence`. Fonte: `radar/daily_intelligence.py`.
- [F] `facts` e `inferences` sono liste separate. Fonte: `radar/daily_intelligence.py`.

### ProjectImpactMap

- [F] La mappa configurabile e' `config/project_impact_map.json`. Fonte: `config/project_impact_map.json`.
- [F] Ogni progetto contiene `project_id`, `display_name`, `keywords`, `impact_types`, `default_action`, `priority`. Fonte: `config/project_impact_map.json`.
- [INT] La mappa e' euristica: keyword e target-project match producono impatto `none`, `low`, `medium` o `high`.

## Flusso

1. [F] La CLI legge un run Bridge esistente sotto `runs`. Fonte: `radar/daily_intelligence.py`.
2. [F] Il generatore produce Human Brief, AI Model Packet e Project Impact Map in memoria. Fonte: `radar/daily_intelligence.py`.
3. [F] La CLI scrive Markdown e JSON in `Bridge/AI_Release_Radar/daily_briefs`. Fonte: `radar/daily_intelligence.py`.
4. [F] La web app espone GET read-only per Easy Mode. Fonte: `radar_web/app.py`.
5. [F] Easy Mode e Action Center leggono il brief in memoria se il file giornaliero non e' ancora stato generato. Fonte: `radar_web/app.py`.

## CLI

```powershell
python -m radar.cli daily-brief --run-id latest
python -m radar.cli daily-brief --run-id <RUN_ID>
python -m radar.cli daily-brief --bridge-root "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar"
```

## API Read-Only

- [F] `GET /api/easy/latest/brief` restituisce HumanDailyBrief. Fonte: `radar_web/app.py`.
- [F] `GET /api/easy/days/{run_id}/brief` restituisce HumanDailyBrief per run. Fonte: `radar_web/app.py`.
- [F] `GET /api/easy/latest/model-packet` restituisce AIModelPacket. Fonte: `radar_web/app.py`.

## UI Acceptance

- [F] Easy Mode deve mostrare `Oggi in 30 secondi`, semaforo, novita utili, azioni urgenti, progetti interessati, fonti manual-review e HAG preservato. Fonte: `radar_web/templates/easy_index.html`.
- [F] Action Center mostra il contesto brief come manual-only. Fonte: `radar_web/templates/actions.html`.
- [F] La navigazione verso Expert Mode resta disponibile. Fonte: `radar_web/templates/easy_index.html`.

## Output Bridge

Pattern deterministic:

- `YYYY-MM-DD-<run_id>-Human_Brief.md`
- `YYYY-MM-DD-<run_id>-Human_Brief.json`
- `YYYY-MM-DD-<run_id>-AI_Model_Packet.md`
- `YYYY-MM-DD-<run_id>-AI_Model_Packet.json`
- `YYYY-MM-DD-<run_id>-Project_Impact_Map.json`

## Limiti

- [INT] La qualita' degli impatti dipende dagli artifact run disponibili e dalla mappa keyword configurata.
- [INT] Il brief e' una sintesi operativa, non un sostituto della review Expert quando il semaforo e' rosso, giallo o grigio.
