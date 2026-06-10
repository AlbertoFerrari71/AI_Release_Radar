# 0660) Codex Prompt Suggestion Pack

## A. Obiettivo

- [F] Il prompt pack e' implementato in `radar/prompt_suggestions.py`. Fonte: `radar/prompt_suggestions.py`.
- [F] I test offline sono in `tests/test_prompt_suggestions.py`. Fonte: `tests/test_prompt_suggestions.py`.

## B. Contratto Output

- [F] Ogni suggestion contiene `title`, `target_project`, `reason`, `risk_class`, `suggested_step_number`, `prompt_path`, `status` e `prompt_text`. Fonte: `radar/prompt_suggestions.py`.
- [F] `status` e' sempre `suggested_only`. Fonte: `radar/prompt_suggestions.py`.
- [F] `prompt_path` resta `null` se non viene generato un file operativo separato. Fonte: `radar/prompt_suggestions.py`.
- [F] Il render Markdown dichiara `prompts_executed=false` e `other_repositories_modified=false`. Fonte: `radar/prompt_suggestions.py`.

## C. Safety

- [F] Monitor-only e ignore non generano prompt. Fonte: `radar/prompt_suggestions.py`, `tests/test_prompt_suggestions.py`.
- [F] Se il target e' ambiguo, la suggestion e' review-only e non operativa. Fonte: `radar/prompt_suggestions.py`.
- [F] I prompt suggeriti non vengono eseguiti dal daily-sim. Fonte: `radar/cli.py`.
