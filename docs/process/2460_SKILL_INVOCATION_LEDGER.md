# 2460 Skill Invocation Ledger v0

## Scopo

- [F] Lo Skill Invocation Ledger registra metadati di skill ispezionate o usate durante uno step Codex. Fonte: prompt `2460-2600`.
- [F] Il registro effettivo e' JSONL append-only fuori repository, nel Bridge. Fonte: prompt `2460-2600`.
- [F] Questo repository contiene solo schema, validatore leggero e documentazione stabile. Fonte: `radar/skill_ledger.py`.

## Percorsi Bridge

- [F] Registro globale: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\_skill_usage\skill_invocations.jsonl`. Fonte: prompt `2460-2600`.
- [F] Copia specifica step: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\codex_command\2460-2600-Skill_Invocation_Ledger.jsonl`. Fonte: prompt `2460-2600`.
- [F] Nessun file runtime del ledger deve essere versionato nel repository. Fonte: `AGENTS.md`.

## Schema JSONL

Ogni riga JSONL contiene un oggetto con questi campi obbligatori:

- [F] `timestamp_utc`. Fonte: `radar/skill_ledger.py`.
- [F] `project`. Fonte: `radar/skill_ledger.py`.
- [F] `repo_path`. Fonte: `radar/skill_ledger.py`.
- [F] `step_id`. Fonte: `radar/skill_ledger.py`.
- [F] `process`. Fonte: `radar/skill_ledger.py`.
- [F] `phase`. Fonte: `radar/skill_ledger.py`.
- [F] `skill_name`. Fonte: `radar/skill_ledger.py`.
- [F] `skill_path`. Fonte: `radar/skill_ledger.py`.
- [F] `caller`. Fonte: `radar/skill_ledger.py`.
- [F] `purpose`. Fonte: `radar/skill_ledger.py`.
- [F] `input_scope`. Fonte: `radar/skill_ledger.py`.
- [F] `output_scope`. Fonte: `radar/skill_ledger.py`.
- [F] `result`. Fonte: `radar/skill_ledger.py`.
- [F] `confidence`. Fonte: `radar/skill_ledger.py`.
- [F] `notes`. Fonte: `radar/skill_ledger.py`.

## Valori `result`

- [F] `used`. Fonte: `radar/skill_ledger.py`.
- [F] `inspected_not_used`. Fonte: `radar/skill_ledger.py`.
- [F] `skill_missing`. Fonte: `radar/skill_ledger.py`.
- [F] `failed`. Fonte: `radar/skill_ledger.py`.

## Regole Privacy

- [F] Il ledger registra solo metadati e non prompt lunghi, file completi, token, API key o dati privati. Fonte: prompt `2460-2600`.
- [F] `confidence` deve essere un numero fra 0 e 1. Fonte: `radar/skill_ledger.py`.

## Validazione

```powershell
python -m pytest tests/test_skill_invocation_ledger.py
```

- [F] Il test valida parse JSONL, campi obbligatori e valori `result`. Fonte: `tests/test_skill_invocation_ledger.py`.

## Stato

- [F] Questo e' un v0 locale ad AI Release Radar. Fonte: prompt `2460-2600`.
- [PROP] Un futuro step ASF/Codex_Skills puo' promuovere lo schema a convenzione comune.
