# 0280) Report Review Scorecard

## Scope

- [F] The deterministic scorecard implementation is `radar/report_scorecard.py`.
- [F] The scorecard evaluates prepared `ReportInput` data plus optional live-run evidence.
- [F] The scorecard does not fetch network data, call an LLM, or write runtime outputs.
- [INT] The scorecard is a report-quality gate, not a replacement for human review.

## Status Model

| Status | Meaning |
|---|---|
| PASS | Required report-quality signals are present |
| WARN | The report is usable, but evidence is incomplete or weaker |
| FAIL | A required quality condition is broken |

Overall status is deterministic:

- [F] Any failed finding makes the scorecard `FAIL`. Source: `radar/report_scorecard.py`.
- [F] If there are no failures but at least one warning, the scorecard is `WARN`. Source: `radar/report_scorecard.py`.
- [F] If all findings pass, the scorecard is `PASS`. Source: `radar/report_scorecard.py`.

## Checks

| Check | Purpose | PASS signal | WARN/FAIL signal |
|---|---|---|---|
| `has_readable_titles` | Avoid item-id-only report content | Changed items have readable titles | FAIL if changed item titles are unreadable |
| `has_source_links` | Keep evidence traceable | Changed items have HTTP source links | WARN if changed items lack links |
| `has_parsed_source_count` | Make source coverage visible | `parsed_count` is available | WARN/FAIL if missing or invalid |
| `has_source_diagnostics` | Distinguish parsed/unsupported/failed sources | Source diagnostics include `diagnostic_status` | WARN if missing or incomplete |
| `has_actionable_project_actions` | Ensure impacts produce useful action posture | Project impacts include valid actions and action types | WARN/FAIL if actions are absent or only no-action |
| `has_no_item_id_only_top_actions` | Prevent noisy top actions | Actions are descriptive | FAIL if an action is only an item id |
| `has_noise_control` | Confirm V1.1 noise reducers are present | Both `action_type` and `diagnostic_status` are available | WARN/FAIL when signals are missing |
| `has_next_step` | Keep the run operationally useful | A next step is provided | WARN if absent |

## Real-Run Usage

- [F] `run_real_radar_report` evaluates the scorecard after building `ReportInput`. Source: `radar/real_run.py`.
- [F] The full real-run report renders a `Report Review Scorecard` section. Source: `radar/real_run.py`.
- [F] The real-run summary includes the serialized scorecard. Source: `radar/real_run.py`.
- [INT] A WARN scorecard should be reviewed before scheduling work, even if tests pass.
- [INT] A FAIL scorecard means the report is too weak for V1.1 closure until corrected.

## Out Of Scope

- [F] No new CLI command is required for 0280. Source: prompt `0240-0300`.
- [F] No scheduler is introduced. Source: prompt `0240-0300`.
- [F] No new dependency is introduced. Source: `pyproject.toml`.
