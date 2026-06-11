# 1310) Action Center Multilingual UX Review

Fonte primaria: prompt `AI Release Radar - ASF Mega-Step 1260-1350` fornito da Alberto il 2026-06-11.

## Pagine Verificate

- [F] `/actions?lang=en`, `/actions?lang=it`, `/actions?lang=fr`, `/actions?lang=de`, `/actions?lang=es` salvate come HTML nel Bridge smoke 1290. Fonte: `D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\web_smoke\1260_1350_20260611_095537`.
- [F] `/api/actions?lang=de` salvata come JSON. Fonte: `1290-Api_Actions_DE.json`.

## UX Multilingua

- [F] UI localizzata tramite `t()` e cataloghi EN/IT/FR/DE/ES. Fonte: `radar_web/templates/actions.html`, `radar_web/locales/*.json`.
- [F] Decision buttons localizzati: approve prompt, defer, ignore, backlog, request review e generate prompt pack. Fonte: `radar_web/locales/*.json`.
- [F] Translation status visibile con badge `source`, `cached`, `needs review`, `missing` o `translation failed`. Fonte: `radar_web/templates/actions.html` e `radar/news_translation.py`.
- [F] Originale EN accessibile via `<details>` quando la traduzione non e' source EN. Fonte: `radar_web/templates/actions.html`.
- [F] Nessuna azione automatica proposta: `no_auto_action=true` nel payload. Fonte: `radar_web/action_center.py`.
- [F] Prompt generation resta dietro decisione umana e scrive nel Bridge. Fonte: `radar_web/action_center.py`, `radar/action_inbox.py`.

## Layout

- [F] Card Action Center usano griglia responsive e wrapping su titoli, summary, path e badge. Fonte: `radar_web/static/style.css`.
- [F] Bottoni e filter tab hanno wrapping controllato dopo il micro-polish 1320. Fonte: `radar_web/static/style.css`.
- [INT] DE/FR non mostrano segnali di rottura nei file HTML/API smoke; la verifica visuale PNG non e' stata disponibile. Fonte: Bridge smoke 1290 e limite browser plugin.

## Esito

- [F] Esito 1310: PASS_WITH_NOTES. Fonte: HTML/API smoke 1290 e review template/CSS.
