# 1350) Decisions

Fonte primaria: prompt `AI Release Radar - ASF Mega-Step 1260-1350` fornito da Alberto il 2026-06-11.

## Decisioni

- [F] La review finale multilingua resta L1/L2 e non autorizza auto-merge. Fonte: prompt 1260-1350.
- [F] La PR deve restare draft. Fonte: prompt 1260-1350.
- [F] Gli output runtime restano Bridge-only e non versionati nel repo. Fonte: `AGENTS.md` e prompt 1260-1350.
- [F] La cache sample traduzioni viene generata nel Bridge per `0320_0400_daily_sim_20260611_062420`. Fonte: `docs/reviews/1300_DYNAMIC_NEWS_TRANSLATION_SAMPLE_REVIEW.md`.
- [F] Le traduzioni sample IT/FR/DE/ES sono marcate `review_required=true`. Fonte: cache Bridge 1300.
- [F] Il fallback HTML/API e' accettato per smoke quando screenshot PNG non sono disponibili. Fonte: prompt 1260-1350.

## Fix Accettati

- [F] Test cataloghi e cache corrotta aggiunti come copertura L1 offline. Fonte: `tests/test_i18n.py`, `tests/test_news_translation.py`.
- [F] Micro-correzioni linguistiche FR/DE/ES applicate ai cataloghi. Fonte: `radar_web/locales/*.json`.
- [F] Micro-polish CSS applicato senza framework o dipendenze. Fonte: `radar_web/static/style.css`, `pyproject.toml`.

## Merge Recommendation

- [PROP] MERGE_RECOMMENDATION: YES dopo review manuale di Alberto della PR draft e degli output Bridge.
- [PROP] Non auto-mergiare questa PR: include L2 smoke/cache Bridge e la policy dello step richiede NO AUTO-MERGE.
