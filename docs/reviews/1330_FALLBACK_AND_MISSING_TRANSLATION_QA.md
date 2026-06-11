# 1330) Fallback, Missing Translation and Pseudo-Localization Readiness

Fonte primaria: prompt `AI Release Radar - ASF Mega-Step 1260-1350` fornito da Alberto il 2026-06-11.

## Scenari Verificati

- [F] `?lang=xx` ricade su EN. Fonte: `radar_web/i18n.py` e `tests/test_i18n.py`.
- [F] Chiave mancante in IT ricade su EN. Fonte: `tests/test_i18n.py`.
- [F] Chiave assente anche in EN torna `[missing:key]`. Fonte: `tests/test_i18n.py`.
- [F] Traduzione news mancante mantiene originale e badge `missing`. Fonte: `tests/test_news_translation.py`.
- [F] Cache traduzione corrotta non causa crash e ricade su originale con badge `missing`. Fonte: `tests/test_news_translation.py`.
- [F] Action Center senza traduzioni renderizza per tutte le lingue. Fonte: `tests/test_i18n.py`.
- [F] Dashboard senza run renderizza stato `NO_DATA`. Fonte: `tests/test_radar_web_app.py`.

## Pseudo-Localization Readiness

- [INT] La struttura a cataloghi flat JSON e fallback EN rende semplice aggiungere in futuro un catalogo pseudo-locale generato da EN. Fonte: `radar_web/i18n.py`.
- [PROP] Un futuro step puo' aggiungere un helper offline che produce un catalogo pseudo-localizzato non runtime, usato solo in test visuali.
- [PROP] Il catalogo pseudo-locale dovrebbe stressare lunghezza stringhe, placeholder `{...}`, badge e button labels senza entrare nei cataloghi produttivi.

## Esito

- [F] Esito 1330: PASS. Fonte: test mirati 26 passed il 2026-06-11.
