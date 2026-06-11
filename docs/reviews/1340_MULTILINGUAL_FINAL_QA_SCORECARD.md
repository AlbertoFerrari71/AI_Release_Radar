# 1340) Multilingual Final QA Scorecard

Fonte primaria: prompt `AI Release Radar - ASF Mega-Step 1260-1350` fornito da Alberto il 2026-06-11.

## Scorecard

| Area | Stato | Fonte |
| --- | --- | --- |
| UI catalog completeness | PASS | `tests/test_i18n.py`, diagnostica JSON 1270 |
| Linguistic clarity EN | PASS | review manuale `radar_web/locales/en.json` |
| Linguistic clarity IT | PASS_WITH_NOTES | review manuale `radar_web/locales/it.json` |
| Linguistic sanity FR | PASS_WITH_NOTES | review manuale e fix `radar_web/locales/fr.json` |
| Linguistic sanity DE | PASS_WITH_NOTES | review manuale e fix `radar_web/locales/de.json` |
| Linguistic sanity ES | PASS_WITH_NOTES | review manuale e fix `radar_web/locales/es.json` |
| Layout resilience | PASS_WITH_NOTES | `radar_web/static/style.css`, smoke HTML/API 1290 |
| Action Center multilingual | PASS_WITH_NOTES | `1290-Actions_*.html`, `1290-Api_Actions_DE.json` |
| News translation cache | PASS_WITH_NOTES | Bridge `translations/0320_0400_daily_sim_20260611_062420` |
| Prompt pack | PASS | `radar/translation_prompt_pack.py`, Bridge prompt files |
| Safety | PASS | `AGENTS.md`, prompt 1260-1350, tests |
| No LLM runtime | PASS | `radar_web/app.py`, `radar/news_translation.py` |
| No scheduler change | PASS | diff 1260-1350 and scheduler preflight |
| No auto-action | PASS | `radar_web/action_center.py`, `radar_web/manual_trigger.py` |

## Blocker Classification

- [F] Nessun catalogo con chiavi mancanti rilevato. Fonte: 1270.
- [F] Nessuna pagina smoke ha fallito render nelle lingue testate. Fonte: `1290-Smoke_Manifest.json`.
- [F] Action Center renderizza EN/IT/FR/DE/ES e API DE risponde. Fonte: Bridge smoke 1290.
- [F] Fallback i18n e translation cache fallback coperti da test. Fonte: `tests/test_i18n.py`, `tests/test_news_translation.py`.
- [F] Nessun LLM automatico, scheduler change o auto-action introdotti. Fonte: diff 1260-1350 e codice `radar_web/`.

## Blocker Attivi

- [F] Blocker attivi: nessuno rilevato. Fonte: scorecard 1340.

## Warning

- [INT] PNG non prodotti per errore browser in-app; fallback HTML/API ammesso dal prompt e completato. Fonte: `1290-Smoke_Manifest.json`.
- [INT] FR/DE/ES non sono certificati da madrelingua. Fonte: review 1280.
- [INT] Translation cache sample e' valida per schema/UI, ma `review_required=true` per IT/FR/DE/ES. Fonte: cache Bridge 1300.

## Merge Recommendation

- [PROP] MERGE_RECOMMENDATION: YES dopo review manuale di Alberto sulla PR draft e sugli output Bridge, con nota madrelingua futura opzionale.
