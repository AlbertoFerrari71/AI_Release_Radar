# 1180) Translation Glossary

Fonte primaria: prompt `AI Release Radar - ASF Mega-Step 1110-1250` fornito da Alberto il 2026-06-11.

Regola generale:

- [F] Non tradurre `AI Release Radar`, `Codex`, `Bridge`, `Prompt` e `HAG` nei cataloghi UI o nei prompt pack. Fonte: prompt 1110-1250.
- [INT] I termini tecnici possono avere descrizioni localizzate, ma il token operativo resta stabile per ridurre ambiguita' tra UI, report e prompt pack.

| Term | EN | IT | FR | DE | ES | Rule |
| --- | --- | --- | --- | --- | --- | --- |
| AI Release Radar | AI Release Radar | AI Release Radar | AI Release Radar | AI Release Radar | AI Release Radar | do not translate |
| Action Center | Action Center | Centro Azioni | Centre d'actions | Aktionszentrum | Centro de acciones | UI may localize label |
| Action Inbox | Action Inbox | Action Inbox | Action Inbox | Action Inbox | Action Inbox | keep token |
| Bridge | Bridge | Bridge | Bridge | Bridge | Bridge | do not translate |
| Codex | Codex | Codex | Codex | Codex | Codex | do not translate |
| Prompt | Prompt | Prompt | Prompt | Prompt | Prompt | do not translate |
| Gate | Gate | Gate | Gate | Gate | Gate | keep token unless descriptive copy needs local context |
| HAG | HAG | HAG | HAG | HAG | HAG | do not translate; describe as human approval gate |
| Backlog | Backlog | Backlog | Backlog | Backlog | Backlog | keep token |
| Scheduler | Scheduler | Scheduler | Scheduler | Scheduler | Scheduler | keep token |
| Dry report | Dry report | dry report | dry report | Dry report | dry report | keep operational token |
| Manual trigger | Manual trigger | trigger manuale | déclencheur manuel | manueller Trigger | disparador manual | localize descriptive label |
| No auto-action | no auto-action | nessuna auto-azione | aucune auto-action | keine Auto-Aktion | sin auto-acción | localize label, preserve safety meaning |
| Human approval | human approval | approvazione umana | approbation humaine | menschliche Freigabe | aprobación humana | localize label |

## Prompt Pack Usage

- [F] `radar/translation_prompt_pack.py` includes the glossary terms in generated translation prompts. Fonte: `radar/translation_prompt_pack.py`.
- [F] Prompt packs instruct the model to preserve product names, model names, CLI commands, paths, links and version numbers. Fonte: `radar/translation_prompt_pack.py`.

## QA Usage

- [F] `tests/test_translation_prompt_pack.py` verifies that glossary terms are included in the generated prompt pack. Fonte: `tests/test_translation_prompt_pack.py`.
- [F] `tests/test_news_translation.py` verifies preservation checks for links, version numbers, commands and paths. Fonte: `tests/test_news_translation.py`.
