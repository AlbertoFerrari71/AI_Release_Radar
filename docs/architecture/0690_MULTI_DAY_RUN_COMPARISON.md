# 0690) Multi-Day Run Comparison

## A. Obiettivo

- [F] Il confronto multi-day estende `radar/run_comparison.py`. Fonte: `radar/run_comparison.py`.
- [F] I test offline sono in `tests/test_run_comparison.py`. Fonte: `tests/test_run_comparison.py`.

## B. Output

- [F] `new_today` contiene item presenti nel run piu' recente e non nei precedenti. Fonte: `radar/run_comparison.py`.
- [F] `repeated_items` contiene item gia' visti. Fonte: `radar/run_comparison.py`.
- [F] `stale_actions` segnala direct actions ripetute. Fonte: `radar/run_comparison.py`.
- [F] `persistent_source_warnings` raggruppa warning fonte persistenti. Fonte: `radar/run_comparison.py`.
- [F] `coverage_unchanged` confronta coppia `source_count/parsed_count` tra ultimo e penultimo run. Fonte: `radar/run_comparison.py`.

## C. Uso

- [INT] Il confronto multi-day e' un filtro anti-rumore, non un filtro di sicurezza. Base: `radar/run_comparison.py`.
- [PROP] Un item ripetuto va raggruppato nel dashboard, ma non nascosto se resta rischio o blocco HAG. Base: prompt `0610-0750`.
