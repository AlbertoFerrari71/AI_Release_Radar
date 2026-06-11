# 1280) UI Translation Linguistic Review

Fonte primaria: prompt `AI Release Radar - ASF Mega-Step 1260-1350` fornito da Alberto il 2026-06-11.

## Ambito

- [F] Review pratica eseguita su menu, titoli pagina, card principali, scheduler card, Action Center, HAG, prompt suggestions, decision buttons, warning, empty states, manual trigger, safety label e no auto-action notice. Fonte: cataloghi `radar_web/locales/*.json` e template `radar_web/templates/*.html`.
- [F] Termini lasciati invariati dove richiesto: `AI Release Radar`, `Codex`, `Bridge`, `Prompt`, `HAG`, `run id`, path, URL e versioni. Fonte: prompt 1260-1350 e cataloghi `radar_web/locales/*.json`.

## Problemi Trovati

- [INT] FR `SUGGERE SEULEMENT` era comprensibile ma meno naturale di `SUGGERE UNIQUEMENT` per badge UI. Fonte: review manuale catalogo `fr.json`.
- [INT] FR `Manuel seulement` era comprensibile ma meno naturale di `Manuel uniquement` nel contesto UI. Fonte: review manuale catalogo `fr.json`.
- [INT] DE `Prompt Pack erzeugen` era leggibile ma meno standard di `Prompt-Pack erzeugen`. Fonte: review manuale catalogo `de.json`.
- [INT] ES `traduccion faltante` era comprensibile ma piu' naturale come `traduccion no disponible` in UI. Fonte: review manuale catalogo `es.json`.

## Correzioni Fatte

- [F] FR: aggiornati `detail.suggestion_only_badge` e `hag.suggestion_mode_value` a `SUGGERE UNIQUEMENT - non execute`. Fonte: `radar_web/locales/fr.json`.
- [F] FR: aggiornato `manual.note` a `Manuel uniquement / aucune auto-action / ecrit dans Bridge`. Fonte: `radar_web/locales/fr.json`.
- [F] DE: aggiornato `actions.generate_prompt_pack` a `Prompt-Pack erzeugen`. Fonte: `radar_web/locales/de.json`.
- [F] ES: aggiornati `actions.translation_missing` e `status_label.translation_missing` a `traduccion no disponible`. Fonte: `radar_web/locales/es.json`.

## Termini Lasciati Invariati

- [F] `Prompt`, `Bridge`, `HAG`, `Action Center`, `Action Inbox`, `run id`, versioni e URL sono stati lasciati invariati o quasi invariati per preservare terminologia operativa. Fonte: prompt 1260-1350 e `docs/i18n/1180_TRANSLATION_GLOSSARY.md`.
- [INT] Alcuni termini misti IT/EN come `review`, `prompt pack`, `scheduler` restano coerenti con il lessico usato da Alberto e con il runbook esistente. Fonte: `docs/runbooks/1250_MULTILINGUAL_RUNBOOK.md`.

## Punti Da Far Rivedere Ad Alberto

- [PROP] Confermare se in IT mantenere `review`, `prompt pack`, `scheduler`, `run` e `warning` oppure localizzarli in modo piu' italiano.
- [PROP] Confermare se `Action Inbox` deve restare nome di feature o diventare localizzato in tutte le lingue.

## Punti Da Far Rivedere A Madrelingua

- [PROP] FR/DE/ES sono adatti a una UI tecnica, ma non certificati da revisore madrelingua.
- [PROP] Una futura review madrelingua dovrebbe concentrarsi su badge brevi, decision buttons e messaggi safety/no auto-action.

## Esito

- [F] Esito 1280: PASS_WITH_NOTES. Fonte: review manuale 1280 e test mirati 26 passed il 2026-06-11.
