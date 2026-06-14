# 2650 Web App Navigation UX Skill Handoff

## Skill Proposta

- [PROP] Nome candidato: `as-common-web-app-navigation-ux-gate`.
- [F] Questa proposta non modifica il repository Codex Skills. Fonte: prompt 2650.

## Scopo

- [PROP] Rendere riusabile il gate "CTA umano non punta a JSON macchina" su web app locali e dashboard operative.
- [PROP] Verificare Home link, separazione HTML/API, label JSON tecnico e manual-only/HAG dove presenti.

## Trigger

- [PROP] Usare la skill quando una web app introduce CTA, route HTML, endpoint JSON o pagine secondarie.
- [PROP] Usare la skill quando un operatore segnala confusione tra pagina umana e endpoint macchina.

## Checklist Candidata

1. [PROP] Audit link: `href` verso `/api/*`, label visibile, CTA primari.
2. [PROP] Route split: HTML umano separato da JSON macchina.
3. [PROP] Home nav: link visibile in alto a sinistra su pagine secondarie.
4. [PROP] Test: HTML content-type, JSON content-type, POST 405, Home link, safe-click.
5. [PROP] UI smoke: desktop/mobile su porta reale, screenshot Bridge.
6. [PROP] Safety: no runtime LLM, no auto-action, no scheduler mutation, no clipboard automatica.

## Progetti Candidati

- [PROP] AI Release Radar.
- [PROP] ASF Blueprint Studio.
- [PROP] Family Photo Organizer ASF.
- [PROP] Conti Chiari AI.
- [PROP] Mansionario Vivo.

## Nota Di Implementazione

- [F] La skill va implementata nel progetto Codex Skills con step separato, non in questo repository. Fonte: prompt 2650.
