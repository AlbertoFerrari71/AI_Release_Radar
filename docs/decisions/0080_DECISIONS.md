# 0080) Report Engine Decisions

## Decisioni Tecniche

- [F] Il report engine e' implementato in `radar/report_engine.py`. Fonte: `radar/report_engine.py`.
- [F] `ReportInput` contiene run metadata, `DiffResult`, item, classificazioni, score, impatti progetto e note. Fonte: `radar/report_engine.py`.
- [F] `ReportInput`, `load_report_input`, `render_full_markdown_report`, `render_compact_markdown_report` e `render_report_status` sono esportati dal package. Fonte: `radar/__init__.py`.
- [F] I test 0080 sono in `tests/test_report_engine.py`. Fonte: `tests/test_report_engine.py`.

## Markdown Deterministico

- [F] I renderer ordinano score per score decrescente e `item_id`, impatti per livello impatto decrescente, `item_id` e `project_key`, e item di sezione per `item_id`. Fonte: `radar/report_engine.py`.
- [F] Ogni report termina con newline finale `\n`. Fonte: `radar/report_engine.py`, `tests/test_report_engine.py`.
- [F] Il renderer usa `generated_at` passato in input e non genera date correnti. Fonte: `radar/report_engine.py`.

## Full vs Compact

- [F] Il full report contiene sezioni numerate per summary, metadata, diff, item nuovi/cambiati/rimossi, score, impatti, azioni, rischi e prossimo step. Fonte: `radar/report_engine.py`, `examples/fixtures/0080_report_expected_full.md`.
- [F] Il compact report contiene Summary, Top changes, Main project impacts e Recommended next action. Fonte: `radar/report_engine.py`, `examples/fixtures/0080_report_expected_compact.md`.
- [F] Il compact report limita i top changes a 5 e gli impatti principali a 7. Fonte: `radar/report_engine.py`.
- [INT] Il full report serve per revisione dettagliata, mentre il compact report serve per lettura rapida e routing operativo. Fonte: `radar/report_engine.py`, prompt `0080-A) AI Release Radar - Report Engine`.

## Etichette Fact/Interpretation/Hypothesis/Proposal

- [F] `[F]` viene usato per dati derivati da modelli o fixture. Fonte: `radar/report_engine.py`.
- [F] `[INT]` viene usato per interpretazioni deterministiche. Fonte: `radar/report_engine.py`.
- [F] `[PROP]` viene usato per azioni suggerite e prossimo step. Fonte: `radar/report_engine.py`.
- [F] `[IP]` non e' presente nei golden 0080. Fonte: `examples/fixtures/0080_report_expected_full.md`, `examples/fixtures/0080_report_expected_compact.md`.
- [INT] L'assenza di `[IP]` e' coerente con il prompt perche' la fixture non introduce note ipotetiche esplicite. Fonte: prompt `0080-A) AI Release Radar - Report Engine`.

## Status Report

- [F] `render_report_status` restituisce uno tra `NO_CHANGE`, `CHANGES_FOUND`, `ACTION_RECOMMENDED` e `CRITICAL`. Fonte: `radar/report_engine.py`.
- [F] Il test della fixture 0080 accetta `ACTION_RECOMMENDED` o `CRITICAL` e la fixture corrente produce `CRITICAL`. Fonte: `tests/test_report_engine.py`, `examples/fixtures/0080_report_input.json`.
- [INT] Lo status sintetico rende possibile una futura CLI che decide se mostrare un report compatto, un report completo o un gate manuale. Fonte: prompt `0080-A) AI Release Radar - Report Engine`.

## Renderer Puro

- [F] Il renderer restituisce stringhe e non scrive file. Fonte: `radar/report_engine.py`.
- [F] `tests/test_report_engine.py` verifica che il rendering non cambi l'elenco file del repository. Fonte: `tests/test_report_engine.py`.
- [INT] La scrittura file resta fuori dal renderer per mantenere test deterministici e separare rendering da runtime output. Fonte: prompt `0080-A) AI Release Radar - Report Engine`.

## Golden Files

- [F] La fixture input e' `examples/fixtures/0080_report_input.json`. Fonte: `examples/fixtures/0080_report_input.json`.
- [F] Il golden full e' `examples/fixtures/0080_report_expected_full.md`. Fonte: `examples/fixtures/0080_report_expected_full.md`.
- [F] Il golden compact e' `examples/fixtures/0080_report_expected_compact.md`. Fonte: `examples/fixtures/0080_report_expected_compact.md`.
- [F] I test confrontano output generato e golden file attesi. Fonte: `tests/test_report_engine.py`.
- [INT] I golden file rendono visibile ogni modifica futura al formato Markdown. Fonte: `tests/test_report_engine.py`.

## Motivazione Auto-Merge Trial L1

- [F] Il prompt 0080 classifica lo step come tecnico/offline/L1 e autorizza auto-review + auto-merge se tutti i gate PASS. Fonte: prompt `0080-A) AI Release Radar - Report Engine`.
- [F] Lo step non richiede fetch live, LLM, API key, scheduler o nuove dipendenze. Fonte: prompt `0080-A) AI Release Radar - Report Engine`, `radar/report_engine.py`.
- [F] Lo step non modifica file high-risk richiesti come esclusi dal prompt. Fonte: prompt `0080-A) AI Release Radar - Report Engine`.
- [INT] Codice offline, fixture locali e test golden rendono lo step compatibile con l'auto-merge L1 se i gate finali restano PASS. Fonte: `AGENTS.md`, prompt `0080-A) AI Release Radar - Report Engine`.

## Esito Auto-Merge

- [F] L'esito operativo dell'auto-merge dipende dai gate finali e dal report finale dello step. Fonte: prompt `0080-A) AI Release Radar - Report Engine`.
- [F] Se un gate L1 fallisce, lo step deve fermarsi alla PR draft. Fonte: `AGENTS.md`, prompt `0080-A) AI Release Radar - Report Engine`.
- [F] Se tutti i gate L1 passano, il prompt autorizza ready + squash merge. Fonte: prompt `0080-A) AI Release Radar - Report Engine`.

## Prossimo Step

- [F] Il prossimo step consigliato e' `0090) CLI Dry Run`. Fonte: prompt `0080-A) AI Release Radar - Report Engine`, `radar/report_engine.py`.
