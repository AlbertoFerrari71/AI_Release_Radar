# 0640) Source Coverage Improvement Candidate

## A. Decisione

- [F] Lo step 0640 vieta parser HTML fragile e nuove dipendenze. Fonte: prompt `0610-0750`.
- [F] Il registry corrente contiene una sola fonte machine-readable pronta: `github_api_openai_codex_releases`. Fonte: `config/sources/openai_sources.json`.
- [F] Diverse fonti P1/P2 indicano `machine_readable_preferred=true`, ma restano `future_candidate`, `unsupported_diagnostic` o `manual_review_only`. Fonte: `config/sources/openai_sources.json`.
- [INT] Il miglior miglioramento conservativo ora e' non forzare un parser live non stabile e usare la diagnostica coverage come segnale esplicito. Base: `config/sources/openai_sources.json`, `radar/automation_gate.py`.

## B. Candidate Preferite

- [PROP] Priorita' futura 1: cercare endpoint strutturati per `openai_api_changelog` e `openai_api_deprecations`. Base: `coverage_priority=P1`, `recommended_follow_up=evaluate_structured_endpoint` in `config/sources/openai_sources.json`.
- [PROP] Priorita' futura 2: mantenere `openai_release_notes_hub` in manual review finche' il formato resta fragile. Base: `manual_review_required=true` in `config/sources/openai_sources.json`.
- [PROP] Priorita' futura 3: non usare scraping HTML generico per incrementare artificialmente `parsed_count`. Base: prompt `0610-0750`.

## C. Esito Step

- [F] Nessun parser HTML nuovo e nessuna dipendenza nuova sono stati introdotti nello step 0640. Fonte: diff dello step 0640.
- [F] La coverage bassa resta visibile tramite automation gate e daily quality gate v2. Fonte: `radar/automation_gate.py`, `radar/daily_quality_gate.py`.
