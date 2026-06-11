# 1250) Multilingual Runbook

Fonte primaria: prompt `AI Release Radar - ASF Mega-Step 1110-1250` fornito da Alberto il 2026-06-11.

## Avvio Dashboard

```powershell
python -m radar_web.app --host 127.0.0.1 --port 8787
```

- [F] Host di default: `127.0.0.1`. Fonte: `radar_web/app.py`.
- [F] Porta di default: `8787`. Fonte: `radar_web/app.py`.
- [F] Non usare bind `0.0.0.0` per questo flusso. Fonte: prompt 1110-1250.

## Lingue UI

Aprire:

```text
http://127.0.0.1:8787/?lang=en
http://127.0.0.1:8787/?lang=it
http://127.0.0.1:8787/?lang=fr
http://127.0.0.1:8787/?lang=de
http://127.0.0.1:8787/?lang=es
```

- [F] Lingua non supportata: fallback EN. Fonte: `radar_web/i18n.py`.
- [F] I link interni preservano `lang`. Fonte: `radar_web/templates/*.html`.

## Cache Traduzioni News

Percorso Bridge:

```text
D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\translations\<run_id>\
```

File attesi:

```text
translated_items.en.json
translated_items.it.json
translated_items.fr.json
translated_items.de.json
translated_items.es.json
translation_index.json
translation_report.md
```

- [F] La dashboard legge cache esistenti ma non la genera. Fonte: `radar_web/app.py`.
- [F] Se manca la cache per una lingua, l'Action Center mostra originale e badge `translation missing`. Fonte: `radar/news_translation.py`.

## Generare Prompt Pack Traduzione

Uso Python controllato da shell o test harness, senza eseguire il prompt:

```python
from pathlib import Path
from radar.translation_prompt_pack import write_translation_prompt_pack

write_translation_prompt_pack(
    run_id="RUN_ID",
    items=[{"source_item_id": "item-1", "title": "...", "summary": "..."}],
    bridge_root=Path(r"D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar"),
    locales=["it", "fr", "de", "es"],
    profile="balanced",
)
```

- [F] Profili ammessi: `cheap`, `balanced`, `quality`. Fonte: `radar/news_translation.py`.
- [F] Default: `balanced`. Fonte: `radar/news_translation.py`, `radar/translation_prompt_pack.py`.
- [F] Il prompt pack contiene `llm_executed=false` nell'indice. Fonte: `radar/translation_prompt_pack.py`.

## Salvare Cache Traduzioni

Uso controllato dopo traduzione approvata:

```python
from pathlib import Path
from radar.news_translation import save_translation_cache

save_translation_cache(
    run_id="RUN_ID",
    locale="it",
    items=[{
        "source_item_id": "item-1",
        "title_translated": "...",
        "summary_translated": "...",
        "translation_status": "translated",
        "review_required": False,
    }],
    bridge_root=Path(r"D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar"),
)
```

- [F] La funzione aggiorna cache, index e report nel Bridge. Fonte: `radar/news_translation.py`.
- [F] Non usare path `LAST-*` o `latest-*`. Fonte: `radar/news_translation.py`, `AGENTS.md`.

## Verifiche Rapide

```powershell
python -m pytest tests/test_i18n.py tests/test_news_translation.py tests/test_translation_prompt_pack.py
python -m pytest
git --no-pager diff --check
```

- [F] I test dedicati coprono cataloghi, fallback, render template, cache, preservation rules e prompt pack. Fonte: `tests/test_i18n.py`, `tests/test_news_translation.py`, `tests/test_translation_prompt_pack.py`.

## Stop Policy

- [F] Fermarsi se i test falliscono. Fonte: prompt 1110-1250.
- [F] Fermarsi se compaiono file `LAST-*` o `latest-*` nel repo. Fonte: prompt 1110-1250 e `AGENTS.md`.
- [F] Non eseguire LLM, email, scheduler o azioni automatiche da questa pipeline. Fonte: prompt 1110-1250.
