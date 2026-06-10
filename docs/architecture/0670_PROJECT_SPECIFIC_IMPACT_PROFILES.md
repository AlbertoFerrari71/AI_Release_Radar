# 0670) Project-Specific Impact Profiles

## A. File E Modulo

- [F] La config stabile e' `config/projects/project_profiles.json`. Fonte: `config/projects/project_profiles.json`.
- [F] Il loader e fallback deterministico sono in `radar/project_profiles.py`. Fonte: `radar/project_profiles.py`.
- [F] I test offline sono in `tests/test_project_profiles.py`. Fonte: `tests/test_project_profiles.py`.

## B. Progetti Coperti

- [F] I profili distinguono `AI Software Factory`, `Codex_Skills`, `Family Photo Organizer`, `Mansionario_Vivo`, `AggloDetect`, `DiamSign` e `ControlloGestioneExcel / eSolver`. Fonte: `config/projects/project_profiles.json`.
- [F] Ogni profilo include `direct_categories`, `monitor_categories`, `ignored_categories`, `keywords_positive`, `keywords_negative`, `review_threshold` e `prompt_generation_allowed`. Fonte: `config/projects/project_profiles.json`, `radar/project_profiles.py`.

## C. Compatibilita'

- [F] La mappa impatti esistente `examples/fixtures/0070_project_map.json` non e' stata rimossa o sostituita. Fonte: diff dello step 0670.
- [F] Se la config profili e' assente, il loader usa fallback deterministico. Fonte: `radar/project_profiles.py`, `tests/test_project_profiles.py`.
- [INT] I profili servono a triage e prompt suggestions; la vecchia mappa resta il riferimento per il calcolo base degli impatti. Base: `radar/project_impact.py`, `radar/project_profiles.py`.
