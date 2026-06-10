# 0480) Operator Runbook

## A. Scopo

- [F] Questo runbook descrive l'uso operativo di `daily-sim` senza scheduler reale. Fonte: `radar/cli.py`.
- [F] Gli output runtime devono restare fuori repository. Fonte: `AGENTS.md`, `radar/cli.py`.
- [F] "Radar fatto" e "Codex fatto" sono definiti dal Bridge retrieval contract. Fonte: `docs/architecture/0370_BRIDGE_RETRIEVAL_CONTRACT.md`.

## B. Lanciare Daily-Sim A Mano

Da PowerShell:

```powershell
Set-Location "C:\Users\alberto.ferrari\source\repos\AI_Release_Radar"
$OutputRoot = "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs"
python -m radar.cli daily-sim --output-root $OutputRoot
```

Atteso:

- [F] Il comando crea una directory datata sotto `$OutputRoot`. Fonte: `radar/cli.py`.
- [F] Il comando non crea scheduler, task Windows o chiamate LLM. Fonte: `radar/cli.py`.
- [F] Il comando scrive summary, gate JSON e gate Markdown nella directory runtime. Fonte: `radar/cli.py`.

## C. File Da Aprire Per Primi

1. [F] `0350-Daily_Sim_Summary.json`: riepilogo daily-sim, no scheduler flags e path output. Fonte: `radar/cli.py`.
2. [F] `0350-Daily_Sim_Gate.md`: lettura umana dell'automation gate. Fonte: `radar/automation_gate.py`.
3. [F] `0180-Report_Compact.md`: report radar compatto. Fonte: `radar/real_run.py`.
4. [F] `0180-Report_Full.md`: dettagli fonti, item e impatti. Fonte: `radar/real_run.py`.

## D. Leggere Automation Gate

- [F] `FAIL` significa blocco strutturale: output mancante, summary invalido, index corrotto, output nel repo, `source_count=0`, `parsed_count=0` o item zero non spiegato. Fonte: `radar/automation_gate.py`.
- [F] `PASS_WITH_WARNINGS` significa run completo con warning. Fonte: `radar/automation_gate.py`.
- [F] `ACTION_REVIEW_REQUIRED` significa che esistono direct actions da leggere manualmente. Fonte: `radar/automation_gate.py`.
- [F] `PASS` significa nessun failure, warning o direct action nel gate. Fonte: `radar/automation_gate.py`.
- [INT] Anche `PASS` non autorizza scheduler reale senza step L3 dedicato. Base: `AGENTS.md`.

## E. Leggere ACTION_REVIEW_REQUIRED

Se il gate dice `ACTION_REVIEW_REQUIRED`:

1. [F] Aprire `0350-Daily_Sim_Gate.md` e leggere `Manual Review Queue`. Fonte: `radar/automation_gate.py`.
2. [F] Aprire `0180-Report_Compact.md` per le top actions. Fonte: `radar/real_run.py`.
3. [F] Aprire `0180-Report_Full.md` per titolo, URL, source, categoria, severita' e motivi di impatto. Fonte: `radar/real_run.py`.
4. [PROP] Non trasformare le actions in commit, issue, email o modifiche automatiche senza un nuovo prompt di Alberto.

## F. Recupero Con "Radar fatto"

- [F] "Radar fatto" significa recuperare il run report atteso dalla directory runtime oppure tramite `runs_index.jsonl`. Fonte: `docs/architecture/0370_BRIDGE_RETRIEVAL_CONTRACT.md`.
- [PROP] Quando Alberto scrive "Radar fatto", usare prima il path Bridge indicato dal report Codex o dalla console daily-sim.
- [PROP] Se il path non e' noto, cercare nella root `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs` la directory datata coerente con lo step.
- [F] Non usare file `LAST-*` o `latest-*`. Fonte: `AGENTS.md`.

## G. Recupero Con "Codex fatto"

- [F] "Codex fatto" significa recuperare il report Codex atteso dal Bridge nel path deterministico dello step. Fonte: `docs/architecture/0370_BRIDGE_RETRIEVAL_CONTRACT.md`.
- [F] Per questo super-step il report atteso e' `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\codex_command\0410-0500-Report_Codex.md`. Fonte: prompt `0410-0500` salvato nel Bridge.
- [PROP] Se il report manca, trattare lo step come incompleto e non creare puntatori sovrascritti.

## H. Se Una Fonte Restituisce 403

- [F] 401/403 vengono classificati come `manual_review_required`. Fonte: `radar/live_snapshot.py`.
- [F] Fonti manual review entrano nella manual review queue. Fonte: `radar/manual_review_queue.py`.
- [PROP] Aprire la fonte manualmente nel browser solo come review umana; non aggiungere parser o bypass senza step dedicato.
- [PROP] Se il 403 e' ripetuto, valutare una fonte alternativa machine-readable o una modifica registry in step dedicato.

## I. Se `parsed_count=0`

- [F] `parsed_count=0` produce failure `parsed_count_zero`. Fonte: `radar/automation_gate.py`.
- [F] Il gate produce `scheduler_readiness_recommendation=STOP` quando ci sono failure. Fonte: `radar/automation_gate.py`.
- [PROP] Fermare ogni discorso scheduler e correggere parser/registry prima di ripetere `daily-sim`.

## J. Se Output Manca

- [F] Summary, report, run index entry o `runs_index.jsonl` mancanti producono `FAIL`. Fonte: `radar/automation_gate.py`.
- [PROP] Ripetere manualmente `daily-sim` in una nuova directory datata fuori repo.
- [PROP] Se il problema si ripete, aprire uno step di fix sul gate/output contract.

## K. Se Gate FAIL

- [F] La CLI `daily-sim` ritorna exit code 1 quando l'automation gate e' `FAIL`. Fonte: `radar/cli.py`.
- [PROP] Non procedere a scheduler, PR scheduler o task Windows.
- [PROP] Conservare il path Bridge del run fallito per diagnosi e aprire un prompt fix-only.

## L. Quando NON Procedere Allo Scheduler

Non procedere se:

- [F] `automation_gate_status=FAIL`. Fonte: `radar/automation_gate.py`.
- [F] `parsed_count=0` o `source_count=0`. Fonte: `radar/automation_gate.py`.
- [F] `scheduler_readiness_recommendation=HOLD` o `STOP`. Fonte: `radar/automation_gate.py`.
- [F] Manual review queue contiene righe bloccanti. Fonte: `radar/manual_review_queue.py`.
- [F] Output runtime e' dentro repository. Fonte: `radar/cli.py`.
- [F] Serve creare task Windows senza prompt L3 esplicito. Fonte: `AGENTS.md`.

## M. Prossimo Step Operativo

- [PROP] Usare `daily-sim` manuale e Bridge retrieval finche' Alberto non autorizza uno step L3 separato per scheduler dry/report.
