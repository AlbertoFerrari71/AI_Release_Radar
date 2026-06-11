# 0580) Scheduler Run Index and Retention

## A. Scopo

- [F] Lo step 0580 richiede una policy per run index e conservazione output scheduler. Fonte: prompt `0510-0600` salvato nel Bridge.
- [F] In questo step non e' autorizzata cancellazione automatica degli output runtime. Fonte: prompt `0510-0600`.

## B. Run Index

- [F] Ogni `daily-sim` produce `runs_index.jsonl` nella directory del run. Fonte: output verificato nello step 0560.
- [F] La run schedulata verificata contiene `runs_index.jsonl`. Fonte: `docs/architecture/0560_SCHEDULED_RUN_OUTPUT_VERIFICATION.md`.
- [INT] Il run index resta append-only per la fase dry-report; non deve essere riscritto o compattato automaticamente dal task.
- [F] Il task non modifica il repository e scrive output runtime nel Bridge. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.

## C. Naming

- [F] Directory run datate: `0320_0400_daily_sim_<stamp>`. Fonte: output `daily-sim` verificato nello step 0560.
- [F] Log scheduler datati: `scheduler_dry_report_<stamp>.log`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Command output scheduler datato: `scheduler_dry_report_<stamp>.command_output.txt`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Stdout scheduler datato: `scheduler_dry_report_<stamp>.stdout.txt`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Stderr scheduler datato: `scheduler_dry_report_<stamp>.stderr.txt`. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] File `LAST-*` e `latest-*` sono vietati. Fonte: `AGENTS.md` e prompt `0510-0600`.

## D. Retention Corrente

- [F] Nessuna retention automatica e' implementata in questo step. Fonte: prompt `0510-0600` e script versionato.
- [F] Nessuna cancellazione automatica dei run e' implementata. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.
- [F] Nessuna cancellazione automatica dei log scheduler e' implementata. Fonte: `scripts/scheduler/ai_release_radar_daily_dry_report.ps1`.

## E. Retention Futura Proposta

- [PROP] Valutare una retention futura di 90 giorni per run e log scheduler.
- [PROP] Prima di introdurre retention automatica, creare uno step dedicato con:
  - dry-run list dei file candidati;
  - soglia temporale esplicita;
  - esclusione del run index corrente;
  - test offline;
  - conferma umana prima della prima cancellazione reale.

## F. Recupero Run

- [PROP] Per il comando operativo "Radar fatto", recuperare l'ultimo run da `runs_index.jsonl` o dal path specifico prodotto dal log scheduler.
- [PROP] Se ci sono dubbi sull'ultimo run, preferire il path esplicito nel log scheduler piu' recente rispetto a un puntatore `latest-*`, che resta vietato.

## G. Guardrail

- [F] Output runtime fuori repo: obbligatorio. Fonte: prompt `0510-0600`.
- [F] No `LAST-*`: obbligatorio. Fonte: prompt `0510-0600`.
- [F] No `latest-*`: obbligatorio. Fonte: prompt `0510-0600`.
- [F] No cleanup distruttivo in questo step. Fonte: prompt `0510-0600`.
