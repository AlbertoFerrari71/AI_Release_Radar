# 1190) Dynamic News Translation Contract

Fonte primaria: prompt `AI Release Radar - ASF Mega-Step 1110-1250` fornito da Alberto il 2026-06-11.

## Scope

- [F] Le traduzioni delle news dinamiche sono output runtime Bridge-only. Fonte: prompt 1110-1250.
- [F] Il codice di supporto e' in `radar/news_translation.py`. Fonte: `radar/news_translation.py`.
- [F] La dashboard legge cache esistenti per `/actions?lang=...` ma non genera traduzioni. Fonte: `radar_web/app.py`.
- [F] Il prompt pack si genera con `radar/translation_prompt_pack.py` e non esegue LLM. Fonte: `radar/translation_prompt_pack.py`.

## Bridge Output

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\translations\<run_id>\
  translated_items.en.json
  translated_items.it.json
  translated_items.fr.json
  translated_items.de.json
  translated_items.es.json
  translation_index.json
  translation_report.md
```

- [F] `save_translation_cache()` scrive `translated_items.<locale>.json`, aggiorna `translation_index.json` e `translation_report.md`. Fonte: `radar/news_translation.py`.
- [F] `load_translation_cache()` e `translation_cache_status()` sono robusti se i file mancano. Fonte: `radar/news_translation.py`, `tests/test_news_translation.py`.

## Item Schema

```json
{
  "run_id": "...",
  "source_item_id": "...",
  "target_locale": "it",
  "source_locale": "en",
  "title_translated": "...",
  "summary_translated": "...",
  "technical_terms_preserved": true,
  "links_preserved": true,
  "version_numbers_preserved": true,
  "translation_model_profile": "balanced",
  "translation_status": "translated|missing|needs_review|failed",
  "review_required": false,
  "created_at": "..."
}
```

- [F] `validate_translation_item()` verifica campi richiesti, status, locale e profilo. Fonte: `radar/news_translation.py`.
- [F] I profili ammessi sono `cheap`, `balanced`, `quality`; il default e' `balanced`. Fonte: `radar/news_translation.py`.

## Preservation Rules

- [F] Link, version numbers, path e comandi CLI hanno helper di estrazione e QA deterministico. Fonte: `radar/news_translation.py`.
- [F] `preservation_report()` verifica che link, version numbers, path e comandi presenti nella fonte siano ancora presenti nella traduzione. Fonte: `radar/news_translation.py`.
- [F] I test coprono preservation rules senza valutare semanticamente la qualita' linguistica. Fonte: `tests/test_news_translation.py`.

## Action Center Behavior

- [F] Se la cache per la lingua contiene `source_item_id`, `/actions` mostra titolo e sintesi tradotti. Fonte: `radar/news_translation.py`, `radar_web/templates/actions.html`.
- [F] Se la cache manca, `/actions` mostra titolo e sintesi originali con badge `translation missing`. Fonte: `radar/news_translation.py`, `radar_web/templates/actions.html`.
- [F] L'originale EN resta visibile in un blocco espandibile quando viene mostrata una lingua diversa dalla sorgente. Fonte: `radar_web/templates/actions.html`.

## Safety

- [F] Nessuna funzione in `radar/news_translation.py` chiama LLM, rete, email, scheduler o altri repository. Fonte: `radar/news_translation.py`.
- [F] Le funzioni rifiutano path con parti `LAST-*` o `latest-*`. Fonte: `radar/news_translation.py`.
- [INT] La responsabilita' di passare un `bridge_root` esterno al repo resta del chiamante; la dashboard usa `DashboardConfig.bridge_root`, gia' validato per output Bridge. Fonte: `radar_web/config.py`.

## Future Work

- [PROP] Aggiungere un comando CLI esplicito per generare prompt pack di traduzione da un run selezionato, senza eseguire il prompt.
- [PROP] Aggiungere QA semantica manuale per campioni IT/FR/DE/ES prima di usare traduzioni in report operativi esterni.
