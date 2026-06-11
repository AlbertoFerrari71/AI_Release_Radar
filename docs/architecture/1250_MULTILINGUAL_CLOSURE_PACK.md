# 1250) Multilingual Dashboard & News Translation Pipeline Closure Pack

Fonte primaria: prompt `AI Release Radar - ASF Mega-Step 1110-1250` fornito da Alberto il 2026-06-11.

## Stato

- [F] Lingue UI supportate: EN, IT, FR, DE, ES. Fonte: `radar_web/i18n.py`, `radar_web/locales/*.json`.
- [F] La UI usa cataloghi JSON versionati e helper `t()` nei template. Fonte: `radar_web/app.py`, `radar_web/templates/*.html`.
- [F] Le news dinamiche usano contratto/cache Bridge-only. Fonte: `radar/news_translation.py`, `docs/architecture/1190_DYNAMIC_NEWS_TRANSLATION_CONTRACT.md`.
- [F] Il prompt pack traduzioni viene generato come Markdown/JSON nel Bridge e non viene eseguito. Fonte: `radar/translation_prompt_pack.py`.

## UI I18N Architecture

- [F] `SUPPORTED_LOCALES = ["en", "it", "fr", "de", "es"]`. Fonte: `radar_web/i18n.py`.
- [F] `normalize_locale()` usa EN come fallback per lingua non supportata. Fonte: `radar_web/i18n.py`.
- [F] `translate()` usa fallback chiave a EN e poi `[missing:key]`. Fonte: `radar_web/i18n.py`.
- [F] Il query parameter `?lang=` viene preservato nei link interni. Fonte: `radar_web/templates/index.html`, `radar_web/templates/actions.html`, `radar_web/templates/run_detail.html`.

## Locale Catalogs

- [F] I cataloghi sono `radar_web/locales/en.json`, `it.json`, `fr.json`, `de.json`, `es.json`. Fonte: `radar_web/locales/`.
- [F] `tests/test_i18n.py` verifica che tutte le lingue abbiano le stesse chiavi EN. Fonte: `tests/test_i18n.py`.

## Formatting

- [F] Date/time, status e bool sono formattati tramite helper locali. Fonte: `radar_web/i18n.py`.
- [F] I test coprono i formati richiesti per EN/IT/FR/DE/ES. Fonte: `tests/test_i18n.py`.

## Dynamic News Translation

- [F] Schema, cache, index e report Bridge-only sono definiti in `radar/news_translation.py`. Fonte: `radar/news_translation.py`.
- [F] `/actions?lang=` legge cache esistenti, mostra badge `cached`, `needs review`, `missing`, `source` o `failed`, e non genera traduzioni. Fonte: `radar_web/app.py`, `radar_web/templates/actions.html`.
- [F] Il prompt pack default usa profilo `balanced`. Fonte: `radar/translation_prompt_pack.py`.

## Safety Rules

- [F] Nessuna nuova dipendenza e' stata aggiunta. Fonte: `pyproject.toml`.
- [F] Nessun scheduler, email, LLM runtime o altro repository viene modificato da questa pipeline. Fonte: `radar_web/app.py`, `radar/news_translation.py`, `radar/translation_prompt_pack.py`.
- [F] I file `LAST-*` e `latest-*` restano vietati nel repo. Fonte: `AGENTS.md`, `tests/test_i18n.py`.

## QA Tests

- [F] `tests/test_i18n.py` copre cataloghi, fallback, placeholder, formattazione e render template.
- [F] `tests/test_news_translation.py` copre schema/cache/fallback/preservation rules.
- [F] `tests/test_translation_prompt_pack.py` copre prompt pack, glossario e `llm_executed=false`.

## Limiti Residui

- [INT] Le traduzioni FR/DE/ES sono professionali ma non certificate da revisore madrelingua.
- [INT] Il QA automatico verifica schema e preservation rules, non qualita' semantica completa.
- [PROP] Aggiungere pseudo-localization e visual regression in uno step futuro.

## Come Aggiungere Una Nuova Lingua

1. [PROP] Aggiungere il codice lingua a `SUPPORTED_LOCALES` in `radar_web/i18n.py`.
2. [PROP] Creare `radar_web/locales/<locale>.json` con le stesse chiavi di `en.json`.
3. [PROP] Aggiornare `docs/i18n/1180_TRANSLATION_GLOSSARY.md` con le traduzioni dei termini.
4. [PROP] Eseguire `python -m pytest tests/test_i18n.py tests/test_news_translation.py tests/test_translation_prompt_pack.py`.
5. [PROP] Eseguire smoke dashboard con `?lang=<locale>`.

## Prossimo Step Consigliato

- [PROP] `1260) Multilingual Operator Review`: review manuale UI per EN/IT/FR/DE/ES e approvazione glossario prima di estendere la traduzione a report operativi.
