# 0290) Manual V1.1 Smoke And Comparison

## Scope

- [F] The offline comparison helper is `radar/run_comparison.py`.
- [F] The comparison accepts already available run-summary mappings and does not fetch live data.
- [F] The comparison can render deterministic Markdown with before/after metrics.
- [INT] This utility is intended for manual V1/V1.1 review, not for scheduler automation.

## Compared Metrics

The comparison reports:

- [F] `sources_checked`. Source: `radar/run_comparison.py`.
- [F] `parsed_sources`. Source: `radar/run_comparison.py`.
- [F] `items`. Source: `radar/run_comparison.py`.
- [F] `project_impacts`. Source: `radar/run_comparison.py`.
- [F] `direct_actions`. Source: `radar/run_comparison.py`.
- [F] `monitor_only_actions`. Source: `radar/run_comparison.py`.
- [F] `failed_sources`. Source: `radar/run_comparison.py`.
- [F] `unsupported_sources`. Source: `radar/run_comparison.py`.
- [F] `scorecard_result`. Source: `radar/run_comparison.py`.

## Real-Run Summary Support

- [F] `run_real_radar_report` now serializes `direct_action_count`, `monitor_only_action_count`, `no_action_count`, `unsupported_source_count`, and `project_action_counts`. Source: `radar/real_run.py`.
- [F] `run_real_radar_report` serializes `report_scorecard_status` and the full `report_scorecard`. Source: `radar/real_run.py`.
- [INT] These fields make V1.1 comparisons possible without parsing Markdown reports.

## Smoke Procedure

Manual smoke remains optional and must write outside the repository:

```powershell
$RunStamp = Get-Date -Format "yyyyMMdd_HHmmss"
$OutputDir = "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar\runs\0240_0300_manual_smoke_$RunStamp"

python -m radar.cli real-run `
  --profile manual `
  --output-dir $OutputDir
```

Rules:

- [F] Runtime output must stay outside the repository. Source: `radar/real_run.py`.
- [F] `LAST-*` and `latest-*` output directory names are rejected by `real-run`. Source: `radar/real_run.py`.
- [F] The smoke does not activate a scheduler. Source: `radar/real_run.py`.
- [F] The smoke does not call an LLM. Source: `radar/real_run.py`.

## Interpretation

- [INT] A better V1.1 comparison should normally show fewer `direct_actions` and more `monitor_only_actions` than the V1 manual baseline.
- [INT] `parsed_sources` may remain unchanged if no stable structured source is added.
- [INT] `unsupported_sources` should be explicit and diagnosed rather than hidden.
- [INT] `scorecard_result=PASS` is a quality signal, not permission to schedule or auto-merge.

## Out Of Scope

- [F] No new CLI command is required for 0290. Source: prompt `0240-0300`.
- [F] No scheduler is introduced. Source: prompt `0240-0300`.
- [F] No new dependency is introduced. Source: `pyproject.toml`.
