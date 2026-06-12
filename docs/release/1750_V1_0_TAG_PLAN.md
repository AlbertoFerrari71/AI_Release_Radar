# 1750) V1.0 Tag Plan

## Stato

- [F] Questo documento prepara il tag consigliato `v1.0.0`; non crea tag e non crea release. Fonte: prompt 1520-2000 fornito da Alberto.
- [F] La policy repo vieta a Codex di creare tag o release senza istruzione esplicita. Fonte: `AGENTS.md`.

## Tag Consigliato

- [PROP] Nome tag: `v1.0.0`.
- [PROP] Commit candidate: merge commit dello step 1520-2000 dopo publish su `main`.
- [PROP] Annotazione consigliata: `AI Release Radar V1.0 local supervised operator product`.

## Criteri Prima Del Tag

- [F] Tutti i test richiesti devono essere PASS. Fonte: prompt 1520-2000.
- [F] `git --no-pager diff --check` deve essere PASS. Fonte: prompt 1520-2000.
- [F] Safety gate finale deve confermare no auto-action, no email, no runtime LLM, no scheduler mutation, no tag/release. Fonte: `AGENTS.md`, `radar/v1_readiness.py`.
- [F] Source coverage finale deve avere classificazione completa, `parsed_count >= 3` o warning documentato, e `fragile_parser_count=0`. Fonte: `radar/source_coverage.py`.
- [F] Final readiness gate deve essere `AI_RADAR_V1_FINAL_READY` o `AI_RADAR_V1_FINAL_READY_WITH_WARNINGS`. Fonte: `radar/v1_readiness.py`.

## Comando Manuale Futuro

```powershell
git tag -a v1.0.0 <merge-commit> -m "AI Release Radar V1.0 local supervised operator product"
git push origin v1.0.0
```

- [PROP] Eseguire questi comandi solo in uno step futuro autorizzato esplicitamente da Alberto.
- [F] Lo step 1520-2000 non deve eseguire questi comandi. Fonte: prompt 1520-2000.

## GitHub Release

- [F] Nessuna GitHub Release deve essere creata nello step 1520-2000. Fonte: prompt 1520-2000.
- [PROP] Se in futuro serve una release GitHub, preparare uno step separato con changelog, artefatti e consenso esplicito.
