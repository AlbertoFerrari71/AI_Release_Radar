# 1110) I18N Architecture Review

Fonte primaria: prompt `AI Release Radar - ASF Mega-Step 1110-1250` fornito da Alberto il 2026-06-11.

## Scope

- [F] La UI dashboard supporta le lingue EN, IT, FR, DE ed ES tramite cataloghi JSON versionati in `radar_web/locales/`. Fonte: prompt 1110-1250 e `radar_web/i18n.py`.
- [F] Le traduzioni delle news dinamiche sono output runtime Bridge-only sotto `translations/<run_id>/`. Fonte: prompt 1110-1250 e `radar/news_translation.py`.
- [F] Nessuna chiamata LLM viene eseguita a runtime dalla dashboard. Fonte: prompt 1110-1250, `radar_web/app.py`, `radar/translation_prompt_pack.py`.

## UI Translations Vs Dynamic News Translations

- [F] Le stringhe UI sono stabili, deterministiche, testabili e versionate nel repository. Fonte: prompt 1110-1250, `radar_web/locales/en.json`.
- [F] Le news raccolte cambiano per run e item; la loro traduzione viene trattata come cache runtime nel Bridge, non come codice sorgente. Fonte: prompt 1110-1250, `docs/architecture/1190_DYNAMIC_NEWS_TRANSLATION_CONTRACT.md`.
- [INT] Separare le due pipeline evita di confondere contenuto operativo mutevole con UI stabile e riduce il rischio di committare output runtime.

## Perche' La UI Sta Nel Repo

- [F] I cataloghi UI hanno le stesse chiavi per tutte le lingue supportate e sono verificati dai test. Fonte: `tests/test_i18n.py`.
- [F] Il fallback lingua usa EN se il parametro `lang` non e' supportato. Fonte: `radar_web/i18n.py`.
- [F] Il fallback chiave usa EN e, se manca anche EN, rende `[missing:<key>]`. Fonte: `radar_web/i18n.py`.
- [INT] Versionare i cataloghi rende review, diff e regressioni di interfaccia verificabili senza LLM.

## Perche' Le News Stanno Nel Bridge

- [F] Le traduzioni news sono salvate in `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\translations\<run_id>\`. Fonte: prompt 1110-1250 e `radar/news_translation.py`.
- [F] La dashboard puo' leggere cache esistenti, ma non genera traduzioni. Fonte: `radar_web/app.py`.
- [INT] Il Bridge e' il confine corretto per output runtime, QA e prompt pack non versionati.

## Niente Traduzione UI Al Volo

- [F] Il prompt vieta traduzioni UI via AI runtime. Fonte: prompt 1110-1250.
- [F] `radar_web/i18n.py` carica solo JSON locali e non contiene client LLM o rete. Fonte: `radar_web/i18n.py`.
- [INT] La traduzione runtime della UI introdurrebbe latenza, costo, variabilita' e superfici di failure non necessarie.

## Locale Query Parameter

- [F] La dashboard usa `?lang=en|it|fr|de|es`. Fonte: `radar_web/app.py`.
- [F] I link interni home, Action Center e run detail preservano `lang`. Fonte: `radar_web/templates/index.html`, `radar_web/templates/actions.html`, `radar_web/templates/run_detail.html`.
- [F] Un valore non valido torna a EN. Fonte: `radar_web/i18n.py`.

## Date, Status E Boolean

- [F] `format_datetime_for_locale` formatta EN come `YYYY-MM-DD HH:MM`, DE come `DD.MM.YYYY HH:MM`, IT/FR/ES come `DD/MM/YYYY HH:MM`. Fonte: `radar_web/i18n.py`.
- [F] `format_bool_for_locale` rende Yes/No, Si/No, Oui/Non, Ja/Nein, Si/No secondo catalogo. Fonte: `radar_web/locales/*.json`.
- [F] `format_status_for_locale` usa label di catalogo quando disponibili e altrimenti conserva il valore tecnico. Fonte: `radar_web/i18n.py`.

## Glossary

- [F] Il glossario operativo e' in `docs/i18n/1180_TRANSLATION_GLOSSARY.md`. Fonte: prompt 1110-1250.
- [INT] I termini tecnici ricorrenti restano coerenti tra UI, prompt pack e QA.

## Missing-Key Tests

- [F] `tests/test_i18n.py` verifica caricamento cataloghi, parita' chiavi, fallback lingua/chiave, placeholder, render template e assenza di file `LAST-*`/`latest-*`. Fonte: `tests/test_i18n.py`.

## Pseudo-Localization

- [PROP] Aggiungere in uno step futuro un catalogo pseudo-locale non utente, per esempio `zz`, escluso da `SUPPORTED_LOCALES`, usato solo nei test per scoprire overflow, concatenazioni fragili e stringhe hardcoded.

## Riferimenti Concettuali

- [INT] ICU/CLDR e Fluent restano riferimenti avanzati per pluralizzazione, genere, formati locali estesi e messaggi complessi.
- [F] Questo step non introduce ICU, CLDR runtime o Fluent come dipendenza. Fonte: `pyproject.toml`, `radar_web/i18n.py`.
- [INT] Il catalogo JSON pragmatico e' sufficiente per la UI attuale perche' le stringhe sono brevi, prevedibili e non richiedono pluralizzazione avanzata.
