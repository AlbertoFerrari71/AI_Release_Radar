# 0700) Noise Reduction and Deduplication

## A. Regole

- [F] Lo step 0700 richiede riduzione rumore senza nascondere rischi. Fonte: prompt `0610-0750`.
- [F] Il confronto multi-day produce `repeated_items`, `stale_actions` e `persistent_source_warnings`. Fonte: `radar/run_comparison.py`.
- [F] Il dashboard 0710 mostra conteggi compatti invece di riesporre tutto il dettaglio. Fonte: `radar/operator_dashboard.py`.

## B. Comportamento

- [PROP] Non ripetere ogni giorno la stessa direct action come nuova: segnalarla come `stale_actions`. Base: `radar/run_comparison.py`.
- [PROP] Se un item e' gia' visto, raggrupparlo in `repeated_items` e mantenerlo visibile. Base: `radar/run_comparison.py`.
- [PROP] Se un warning fonte persiste, raggrupparlo in `persistent_source_warnings`. Base: `radar/run_comparison.py`.
- [PROP] Mostrare nel dashboard le azioni nuove e mettere il resto nel report full o HAG. Base: prompt `0610-0750`, `radar/operator_dashboard.py`.

## C. Safety

- [F] Nessun rischio viene eliminato dal gate; gate, HAG e full report restano disponibili nel Bridge. Fonte: `radar/cli.py`, `radar/hag_report.py`.
