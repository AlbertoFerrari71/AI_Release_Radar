# 0590) Operator Review Flow

## A. Quando usare questo runbook

- [F] Questo runbook copre la review umana dopo il task scheduler dry-report `AIReleaseRadar_DailyDryReport`. Fonte: prompt `0510-0600` salvato nel Bridge.
- [F] Il task scrive run e log nel Bridge. Fonte: `docs/architecture/0540_WINDOWS_TASK_CREATION.md`.
- [F] Il task non e' autorizzato a fare auto-azioni. Fonte: `docs/decisions/0510_L3_SCHEDULER_DRY_REPORT_CONSENT.md`.

## B. Comando operativo: "Radar fatto"

Quando Alberto scrive:

```text
Radar fatto
```

ChatGPT/Codex deve:

1. Leggere il run piu' recente dal Bridge.
2. Preferire il path esplicito nel log scheduler piu' recente, se disponibile.
3. In alternativa leggere `runs_index.jsonl` nel run piu' recente.
4. Aprire almeno:
   - `0180-Report_Compact.md`
   - `0350-Daily_Sim_Gate.md`
   - `0350-Daily_Sim_Summary.json`
   - `0180-Run_Summary.json`
   - `0710-Daily_Operator_Dashboard.md`, se presente
   - `0680-Human_Approval_Gate_Report.md`, se presente

Path base:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\scheduler_logs
```

## C. Classificazione Review

Classificare l'esito in una di queste categorie:

- [F] `nessuna azione`: nessun direct action e gate senza failure. Fonte: gate report del run.
- [F] `review manuale`: manual review queue non vuota o coverage warning. Fonte: `0350-Daily_Sim_Gate.md`.
- [F] `direct action da trasformare in prompt Codex`: direct actions presenti ma non eseguite automaticamente. Fonte: `0180-Report_Compact.md` e `0350-Daily_Sim_Summary.json`.
- [F] `source coverage issue`: parsed ratio basso, unsupported source alto o fonte manual review. Fonte: `0350-Daily_Sim_Gate.md`.

## D. ACTION_REVIEW_REQUIRED

Se il gate e':

```text
ACTION_REVIEW_REQUIRED
```

allora:

1. Non eseguire azioni automatiche.
2. Leggere la manual review queue.
3. Separare source issue da action issue.
4. Preparare, se utile, un prompt Codex dedicato per una sola direct action o per un gruppo coerente.
5. Non procedere a scheduler operativo pieno.

- [F] La run schedulata verificata nello step 0560 ha prodotto `ACTION_REVIEW_REQUIRED`. Fonte: `docs/architecture/0560_SCHEDULED_RUN_OUTPUT_VERIFICATION.md`.

## E. PASS_WITH_WARNINGS

Se il gate e':

```text
PASS_WITH_WARNINGS
```

allora:

1. Leggere tutte le warning.
2. Verificare se le warning sono source coverage, manual review, unsupported source o volume anomalo.
3. Non trattare `PASS_WITH_WARNINGS` come autorizzazione automatica.
4. Procedere solo con prompt Codex separato e approvazione umana.

## F. FAIL

Se il gate e':

```text
FAIL
```

allora:

1. Non usare il report per pianificare azioni.
2. Leggere lo scheduler log datato.
3. Leggere `0350-Daily_Sim_Gate.md`.
4. Disabilitare il task se il problema puo' ripetersi ogni giorno.
5. Aprire uno step Codex di fix mirato.

Disabilitare:

```powershell
Disable-ScheduledTask -TaskName "AIReleaseRadar_DailyDryReport"
```

## G. Task senza output

Se il task non produce output:

1. Eseguire:

```powershell
Get-ScheduledTaskInfo -TaskName "AIReleaseRadar_DailyDryReport"
```

2. Controllare `scheduler_logs`.
3. Se manca anche il log, verificare action path e permessi.
4. Disabilitare il task se l'errore e' ricorrente.
5. Aprire uno step Codex di diagnosi.

## H. Quando disabilitare il task

Disabilitare il task se:

- [F] gate `FAIL` ricorrente. Fonte: policy di failure handling dello step 0570.
- [F] output Bridge assente. Fonte: prompt `0510-0600`.
- [F] log scheduler assente o illeggibile. Fonte: prompt `0510-0600`.
- [F] compaiono segreti, token o path non autorizzati. Fonte: `AGENTS.md` e prompt `0510-0600`.
- [F] qualunque comportamento suggerisce auto-azione, email, notifica esterna o LLM. Fonte: prompt `0510-0600`.

## I. Quando aprire uno step Codex successivo

Aprire uno step Codex successivo quando:

- [PROP] una direct action e' stata verificata manualmente e deve diventare modifica repository;
- [PROP] la source coverage resta troppo bassa e serve una nuova fonte strutturata;
- [PROP] il task fallisce o non produce output;
- [PROP] si vuole introdurre retention automatica;
- [PROP] si vuole valutare il passaggio da dry-report a scheduler operativo, con nuovo consenso esplicito.

## J. V1.5 Supervised Daily Intelligence

- [F] Dal blocco 0610-0750, `daily-sim` produce anche quality gate v2, action triage, prompt suggestions, HAG report, dashboard e supervised action loop dry run. Fonte: `radar/cli.py`.
- [F] Il contratto aggiornato per `Radar fatto` e' `docs/architecture/0620_RADAR_DONE_BRIDGE_RETRIEVAL_CONTRACT.md`. Fonte: `docs/architecture/0620_RADAR_DONE_BRIDGE_RETRIEVAL_CONTRACT.md`.
- [F] Il dashboard compatto e' `0710-Daily_Operator_Dashboard.md`. Fonte: `radar/operator_dashboard.py`.
- [F] I prompt suggestions sono `suggested_only` e non devono essere eseguiti automaticamente. Fonte: `radar/prompt_suggestions.py`.
- [PROP] Quando HAG segnala `HOLD_FOR_HUMAN_APPROVAL`, scegliere una sola decisione A/B/C/D e aprire uno step separato se serve. Base: `radar/hag_report.py`.
