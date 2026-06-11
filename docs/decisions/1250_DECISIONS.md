# 1250) Decisions

Fonte primaria: prompt `AI Release Radar - ASF Mega-Step 1110-1250` fornito da Alberto il 2026-06-11.

## Decisioni

- [F] UI i18n implementata con cataloghi JSON locali senza nuove dipendenze. Fonte: `radar_web/i18n.py`, `radar_web/locales/*.json`, `pyproject.toml`.
- [F] Fluent/ICU restano riferimenti concettuali e non sono introdotti come dipendenza runtime in questo step. Fonte: `docs/architecture/1110_I18N_ARCHITECTURE_REVIEW.md`, `pyproject.toml`.
- [F] Il parametro `?lang=` e' supportato da home, detail e Action Center. Fonte: `radar_web/app.py`, `radar_web/templates/*.html`.
- [F] Le traduzioni news restano Bridge-only e vengono solo lette dalla dashboard se gia' presenti. Fonte: `radar/news_translation.py`, `radar_web/app.py`.
- [F] Il prompt pack traduzioni viene generato ma non eseguito. Fonte: `radar/translation_prompt_pack.py`.
- [F] Nessuna auto-azione, nessuna email, nessun LLM runtime, nessun nuovo scheduler e nessun altro repository sono introdotti. Fonte: `radar_web/app.py`, `radar/news_translation.py`, `radar/translation_prompt_pack.py`.

## Rischio

- [F] Classificazione step: L1/L2. Fonte: prompt 1110-1250.
- [F] Auto-merge non consentito; PR finale deve restare draft. Fonte: prompt 1110-1250 e `AGENTS.md`.

## Merge Recommendation

- [PROP] Merge consigliato solo dopo review manuale della PR draft, verifica smoke Bridge e conferma che nessun output runtime sia stato versionato.
