# 0370) Bridge Retrieval Contract

## A. Scopo

- [F] Il repository vieta report di step e output runtime versionati nel repo. Fonte: `AGENTS.md`.
- [F] Il repository vieta file `LAST-*` e `latest-*`. Fonte: `AGENTS.md`.
- [F] La V1 manuale scrive output runtime fuori repository. Fonte: `radar/real_run.py`, `docs/runbooks/0230_V1_MANUAL_RUN_RUNBOOK.md`.
- [INT] Il Bridge e' il canale operativo per prompt Codex, report Codex e runtime run quando lo step lo autorizza. Base: prompt `0320-0400` salvato nel Bridge.

## B. Definizioni Operative

- [F] "Codex fatto" significa che ChatGPT recupera il report Codex atteso dal Bridge nel path deterministico dello step. Fonte: prompt `0320-0400` salvato nel Bridge.
- [F] "Radar fatto" significa che ChatGPT recupera il run report atteso dalla directory runtime oppure lo individua tramite `runs_index.jsonl`. Fonte: `docs/architecture/0340_AUTOMATION_RUN_CONTRACT.md`.
- [INT] Se esistono piu' run compatibili, ChatGPT deve preferire il run con step/stamp piu' coerente con la richiesta prima di chiedere copia/incolla ad Alberto. Base: vincolo di evitare puntatori `LAST-*`/`latest-*` in `AGENTS.md`.

## C. Path Codex Command

Prompt singolo:

```text
...\codex_command\NNNN-Prompt_Codex.md
```

Report singolo:

```text
...\codex_command\NNNN-Report_Codex.md
```

Prompt/report multistep:

```text
...\codex_command\NNNN-MMMM-Prompt_Codex_SuperStep.md
...\codex_command\NNNN-MMMM-Report_Codex.md
```

- [F] Lo step 0320-0400 usa `0320-0400-Prompt_Codex_SuperStep.md` e `0320-0400-Report_Codex.md`. Fonte: prompt `0320-0400` salvato nel Bridge.
- [F] Non devono essere creati `LAST-*` o `latest-*`. Fonte: `AGENTS.md`.

## D. Path Runtime Run

Runtime run:

```text
...\runs\<run_folder_datata>\
```

Esempio step 0320-0400:

```text
...\runs\0320_0400_daily_sim_YYYYMMDD_HHMMSS\
```

File attesi nel run daily simulation:

- [F] `0180-Run_Summary.json`. Fonte: `radar/real_run.py`.
- [F] `0180-Report_Compact.md`. Fonte: `radar/real_run.py`.
- [F] `0180-Report_Full.md`. Fonte: `radar/real_run.py`.
- [F] `0180-Run_Index_Entry.json`. Fonte: `radar/real_run.py`.
- [F] `runs_index.jsonl`. Fonte: `radar/real_run.py`, `radar/run_index.py`.
- [F] `0350-Daily_Sim_Summary.json`. Fonte: `radar/cli.py`.
- [F] `0350-Daily_Sim_Gate.json`. Fonte: `radar/cli.py`, `radar/automation_gate.py`.
- [F] `0350-Daily_Sim_Gate.md`. Fonte: `radar/cli.py`, `radar/automation_gate.py`.

## E. Regole Di Recupero

1. [F] Per "Codex fatto", cercare prima `...\codex_command\NNNN-Report_Codex.md` o `...\codex_command\NNNN-MMMM-Report_Codex.md`. Fonte: prompt `0320-0400` salvato nel Bridge.
2. [F] Per "Radar fatto", cercare prima il run folder datato indicato dal report Codex. Fonte: `docs/architecture/0340_AUTOMATION_RUN_CONTRACT.md`.
3. [F] Se il run folder non e' indicato, leggere `runs_index.jsonl` nella directory `...\runs\...` candidata. Fonte: `radar/run_index.py`.
4. [INT] Se la richiesta e' ambigua, selezionare il file piu' coerente per numero step, timestamp e contenuto prima di chiedere ad Alberto di incollare output. Base: regola deterministica in `AGENTS.md`.
5. [F] Non usare puntatori sovrascritti, `LAST-*` o `latest-*`. Fonte: `AGENTS.md`.

## F. Responsabilita'

- [F] Codex deve scrivere report finale Bridge quando lo step lo richiede. Fonte: prompt `0320-0400` salvato nel Bridge.
- [F] Codex non deve salvare output runtime/live nel repository. Fonte: `AGENTS.md`.
- [F] ChatGPT deve recuperare gli artifact Bridge attesi invece di chiedere copia/incolla quando il path e' deterministico. Fonte: prompt `0320-0400` salvato nel Bridge.
- [PROP] Alberto approva eventuali merge o scheduler in step dedicati; il Bridge non sostituisce review manuale.

## G. Errori E Fallback

- [F] Se `0180-Run_Summary.json` manca, l'automation gate produce `FAIL`. Fonte: `radar/automation_gate.py`.
- [F] Se `runs_index.jsonl` e' corrotto, l'automation gate produce `FAIL`. Fonte: `radar/automation_gate.py`.
- [PROP] Se manca il report Codex, classificare lo step come incompleto e chiedere generazione/ripristino del report deterministico, non creare un `latest-*`.
- [PROP] Se il run output non e' nel Bridge o e' dentro repo, classificare come blocco di contratto e non procedere verso scheduler.
