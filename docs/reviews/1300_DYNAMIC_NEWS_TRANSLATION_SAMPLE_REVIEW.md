# 1300) Dynamic News Translation Sample and Cache Review

Fonte primaria: prompt `AI Release Radar - ASF Mega-Step 1260-1350` fornito da Alberto il 2026-06-11.

## Run Usato

- [F] Run usato: `0320_0400_daily_sim_20260611_062420`. Fonte: Bridge `runs/0320_0400_daily_sim_20260611_062420`.
- [F] Il run contiene snapshot `github_api_openai_codex_releases` con 10 item. Fonte: `0170-Snapshot_github_api_openai_codex_releases.json`.
- [F] Sample limitato a 5 source item. Fonte: cache Bridge generata in `translations/0320_0400_daily_sim_20260611_062420`.

## Output Bridge

- [F] Cache scritte: `translated_items.en.json`, `translated_items.it.json`, `translated_items.fr.json`, `translated_items.de.json`, `translated_items.es.json`. Fonte: `radar/news_translation.py` e Bridge `translations/0320_0400_daily_sim_20260611_062420`.
- [F] Index e report scritti: `translation_index.json`, `translation_report.md`. Fonte: `radar/news_translation.py`.
- [F] Prompt pack scritto: `1200-Translation_Prompt_it_balanced.md`, `1200-Translation_Prompt_fr_balanced.md`, `1200-Translation_Prompt_de_balanced.md`, `1200-Translation_Prompt_es_balanced.md`. Fonte: `radar/translation_prompt_pack.py`.
- [F] Prompt index scritto: `1200-Translation_Prompt_Index.json` con `llm_executed=false`. Fonte: `radar/translation_prompt_pack.py`.

## Verifiche Cache

- [F] Ogni locale EN/IT/FR/DE/ES contiene 5 item e stato cache `cached`. Fonte: `translation_cache_status()` eseguito il 2026-06-11.
- [F] `source_item_id` preservato per tutti gli item verificati. Fonte: `validate_translation_item()` eseguito il 2026-06-11.
- [F] `links_preserved=true` e `version_numbers_preserved=true` sui sample verificati. Fonte: `preservation_report()` e cache normalizzata.
- [F] EN usa copia/originale. Fonte: cache `translated_items.en.json`.
- [F] IT/FR/DE/ES usano `translation_status=needs_review` e `review_required=true` per evidenziare review umana/madrelingua futura. Fonte: cache `translated_items.it|fr|de|es.json`.
- [F] Nessun LLM runtime dashboard eseguito. Fonte: `radar_web/app.py`, `radar/news_translation.py`.

## Dashboard

- [F] `/api/actions?lang=de` carica cache e produce payload Action Center senza crash. Fonte: `1290-Api_Actions_DE.json`.
- [F] Se una traduzione manca, `apply_translation_cache_to_actions()` mantiene originale EN e badge `missing`. Fonte: `radar/news_translation.py` e `tests/test_news_translation.py`.
- [F] Cache corrotta gestita come cache vuota senza crash. Fonte: `tests/test_news_translation.py`.

## Limiti

- [INT] Le traduzioni sample sono state generate da Codex nella sessione, non da un traduttore madrelingua.
- [INT] Il sample serve a verificare schema/cache/UI, non a certificare qualita' editoriale completa.

## Esito

- [F] Esito 1300: PASS_WITH_NOTES. Fonte: verifiche cache 1300 e test mirati 26 passed il 2026-06-11.
