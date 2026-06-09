# 0080) Report Engine

## Scopo

- [F] Lo step 0080 introduce un report engine Markdown offline per trasformare dati gia' deterministici in report full e compact. Fonte: prompt `0080-A) AI Release Radar - Report Engine`, `radar/report_engine.py`.
- [F] Il renderer riceve un `ReportInput` e restituisce stringhe Markdown senza scrivere file. Fonte: `radar/report_engine.py`.
- [F] Il prossimo step consigliato dal report e' `0090) CLI Dry Run`. Fonte: prompt `0080-A) AI Release Radar - Report Engine`, `radar/report_engine.py`.

## Relazione tra Modelli

- [F] `DiffResult` descrive item nuovi, cambiati, rimossi e conteggio invariati. Fonte: `radar/models.py`.
- [F] `ItemClassification` contiene categoria, severita', keyword matchate e ragioni della classificazione. Fonte: `radar/classification.py`.
- [F] `RelevanceScore` contiene score totale e componenti auditabili. Fonte: `radar/scoring.py`.
- [F] `ProjectImpact` collega un item a un progetto con livello impatto, ragioni e azioni suggerite. Fonte: `radar/project_impact.py`.
- [INT] `ReportInput` consolida questi modelli in un solo oggetto per evitare che il renderer debba ricostruire diff, classificazioni, score o impatti. Fonte: `radar/report_engine.py`.

## Full Report

- [F] `render_full_markdown_report` produce un report Markdown con sezioni numerate da executive summary a next step recommendation. Fonte: `radar/report_engine.py`.
- [F] Il full report include metadata run/source, diff summary, item nuovi/cambiati/rimossi, top relevance scores, project impacts, recommended actions, rischi/caveat e prossimo step. Fonte: `radar/report_engine.py`, `examples/fixtures/0080_report_expected_full.md`.
- [F] Ogni item mostrato nel full report include `item_id`, title, category, severity, score, URL ed evidence. Fonte: `radar/report_engine.py`, `examples/fixtures/0080_report_expected_full.md`.

## Compact Report

- [F] `render_compact_markdown_report` produce un report Markdown compatto. Fonte: `radar/report_engine.py`.
- [F] Il compact report include Summary, Top changes, Main project impacts e Recommended next action. Fonte: `radar/report_engine.py`, `examples/fixtures/0080_report_expected_compact.md`.
- [F] Il compact report limita i top changes a massimo 5 e gli impatti principali a massimo 7. Fonte: `radar/report_engine.py`.

## Etichette

- [F] Il renderer usa `[F]` per dati provenienti da fixture/modelli. Fonte: `radar/report_engine.py`.
- [F] Il renderer usa `[INT]` per interpretazioni deterministiche, come status, top score, score reasons e impact reasons. Fonte: `radar/report_engine.py`.
- [F] Il renderer usa `[PROP]` per azioni suggerite e prossimo step. Fonte: `radar/report_engine.py`.
- [INT] `[IP]` non viene emesso dalla fixture 0080 perche' lo step non introduce ipotesi da verificare. Fonte: prompt `0080-A) AI Release Radar - Report Engine`, `examples/fixtures/0080_report_expected_full.md`.

## Logica Status

- [F] `render_report_status` puo' restituire `NO_CHANGE`, `CHANGES_FOUND`, `ACTION_RECOMMENDED` o `CRITICAL`. Fonte: `radar/report_engine.py`.
- [F] Lo status e' `CRITICAL` se almeno una classificazione/item ha severita' critical o almeno un `ProjectImpact` e' critical. Fonte: `radar/report_engine.py`.
- [F] Lo status e' `ACTION_RECOMMENDED` se almeno un impatto e' high/critical o almeno uno score e' maggiore o uguale a 70. Fonte: `radar/report_engine.py`.
- [F] Lo status e' `CHANGES_FOUND` se sono presenti item nuovi, cambiati o rimossi e non sono scattati status superiori. Fonte: `radar/report_engine.py`.
- [F] Lo status e' `NO_CHANGE` quando non sono presenti item nuovi, cambiati o rimossi e non sono scattati status superiori. Fonte: `radar/report_engine.py`.

## Renderer Puro

- [F] Il renderer non apre file, non scrive file e non genera timestamp correnti. Fonte: `radar/report_engine.py`.
- [F] `generated_at` viene letto da `ReportInput` e riportato nel Markdown. Fonte: `radar/report_engine.py`.
- [INT] La purezza del renderer rende i golden test ripetibili e lascia la scrittura runtime a uno step successivo. Fonte: prompt `0080-A) AI Release Radar - Report Engine`, `tests/test_report_engine.py`.

## No LLM e No Fetch Live

- [F] Il prompt 0080 vieta LLM, fetch live, HTTP reali, API key e dipendenze esterne. Fonte: prompt `0080-A) AI Release Radar - Report Engine`.
- [F] `radar/report_engine.py` usa solo standard library e modelli locali del package `radar`. Fonte: `radar/report_engine.py`.
- [F] Le fixture 0080 sono file locali sotto `examples/fixtures`. Fonte: `examples/fixtures/0080_report_input.json`, `examples/fixtures/0080_report_expected_full.md`, `examples/fixtures/0080_report_expected_compact.md`.
- [INT] L'assenza di fetch live e LLM mantiene lo step nel perimetro L1 offline deterministico. Fonte: `AGENTS.md`, prompt `0080-A) AI Release Radar - Report Engine`.

## Fuori Scope

- [F] La CLI resta fuori scope dello step 0080. Fonte: prompt `0080-A) AI Release Radar - Report Engine`.
- [F] La scrittura runtime Bridge resta fuori scope dello step 0080. Fonte: prompt `0080-A) AI Release Radar - Report Engine`.
- [F] Il `runs_index` operativo resta fuori scope dello step 0080. Fonte: prompt `0080-A) AI Release Radar - Report Engine`.
- [F] Il source registry reale resta fuori scope dello step 0080. Fonte: prompt `0080-A) AI Release Radar - Report Engine`.
- [F] Scheduler e file task restano fuori scope dello step 0080. Fonte: prompt `0080-A) AI Release Radar - Report Engine`.
