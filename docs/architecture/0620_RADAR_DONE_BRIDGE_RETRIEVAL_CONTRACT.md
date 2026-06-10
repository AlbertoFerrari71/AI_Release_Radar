# 0620) Radar Done Bridge Retrieval Contract

## A. Input Utente

- [F] Gli input equivalenti sono `Radar fatto`, `Controlla radar`, `Recupera ultimo radar` e `Radar giornaliero fatto`. Fonte: prompt `0610-0750` fornito da Alberto il 2026-06-10.
- [F] Il retrieval deve usare il Bridge operativo `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar`. Fonte: prompt `0610-0750`.

## B. Contratto Di Recupero

Quando Alberto scrive uno degli input sopra, ChatGPT deve:

1. [F] Cercare l'ultimo run schedulato o `daily-sim` in `runs_index.jsonl` o nella cartella `runs`. Fonte: prompt `0610-0750`, `radar/run_index.py`.
2. [F] Leggere `0180-Report_Compact.md`. Fonte: prompt `0610-0750`, `radar/real_run.py`.
3. [F] Leggere `0180-Run_Summary.json`. Fonte: prompt `0610-0750`, `radar/real_run.py`.
4. [F] Leggere `0350-Daily_Sim_Gate.md` e `0350-Daily_Sim_Gate.json`. Fonte: prompt `0610-0750`, `radar/cli.py`.
5. [F] Leggere scheduler log se presente. Fonte: prompt `0610-0750`, `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
6. [F] Sintetizzare stato, azioni, gate, rischi e next step. Fonte: prompt `0610-0750`.
7. [F] Chiedere file/output ad Alberto solo se il Bridge non e' accessibile o incoerente. Fonte: prompt `0610-0750`.

## C. Scelta Del Run

- [F] Preferire l'indice append-only e directory datate. Fonte: prompt `0610-0750`, `radar/run_index.py`.
- [F] Non usare file `LAST-*` o `latest-*`. Fonte: `AGENTS.md`.
- [F] Se piu' run sono candidati, scegliere quello schedulato piu' recente coerente con `LastRunTime` e log scheduler. Fonte: prompt `0610-0750`.
- [F] Se i candidati sono ambigui, segnalare ambiguita' invece di inventare un ultimo run. Fonte: prompt `0610-0750`.

## D. Output Atteso Della Risposta

- [F] Stato run e gate. Fonte: prompt `0610-0750`.
- [F] Source coverage, action triage, prompt suggestions, HAG e dashboard quando disponibili. Fonte: `radar/cli.py`.
- [F] Conferma `no auto-action`, `no email`, `no LLM`, `no other repo`. Fonte: `radar/cli.py`, `docs/decisions/0510_L3_SCHEDULER_DRY_REPORT_CONSENT.md`.
- [PROP] Se `ACTION_REVIEW_REQUIRED`, proporre una sola decisione HAG alla volta, non una catena di azioni. Base: `radar/hag_report.py`.
