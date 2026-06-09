"""Command line interface for offline AI Release Radar dry-runs."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from radar.json_utils import read_json
from radar.report_engine import (
    ReportInput,
    load_report_input,
    render_compact_markdown_report,
    render_full_markdown_report,
    render_report_status,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DRY_RUN_INPUT_PATH = REPO_ROOT / "examples" / "fixtures" / "0080_report_input.json"
FULL_REPORT_FILENAME = "0090_dry_run_report_full.md"
COMPACT_REPORT_FILENAME = "0090_dry_run_report_compact.md"
SUMMARY_FILENAME = "0090_dry_run_summary.txt"
NEXT_STEP_RECOMMENDATION = "0100) OpenAI Source Registry and URL Verification"


def build_dry_run_report_input() -> ReportInput:
    """Load the deterministic offline fixture used by the dry-run CLI."""
    return load_report_input(read_json(DRY_RUN_INPUT_PATH))


def run_dry_run(output_dir: str, full: bool = True, compact: bool = True) -> dict[str, str]:
    """Run the offline dry-run and write requested outputs to output_dir."""
    if not full and not compact:
        raise ValueError("at least one report output must be enabled.")

    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    report_input = build_dry_run_report_input()
    full_report_path = target_dir / FULL_REPORT_FILENAME
    compact_report_path = target_dir / COMPACT_REPORT_FILENAME
    summary_path = target_dir / SUMMARY_FILENAME

    full_report = str(full_report_path) if full else "skipped"
    compact_report = str(compact_report_path) if compact else "skipped"

    if full:
        _write_text(full_report_path, render_full_markdown_report(report_input))
    if compact:
        _write_text(compact_report_path, render_compact_markdown_report(report_input))

    summary = build_summary(
        status=render_report_status(report_input),
        full_report=full_report,
        compact_report=compact_report,
        summary=str(summary_path),
    )
    _write_text(summary_path, summary)

    return {
        "full_report": full_report,
        "compact_report": compact_report,
        "summary": str(summary_path),
    }


def build_summary(
    *,
    status: str,
    full_report: str,
    compact_report: str,
    summary: str,
) -> str:
    """Build the deterministic console and file summary."""
    lines = [
        "AI Release Radar dry-run completed",
        f"Status: {status}",
        f"Full report: {full_report}",
        f"Compact report: {compact_report}",
        f"Summary: {summary}",
        f"Next step: {NEXT_STEP_RECOMMENDATION}",
    ]
    return "\n".join(lines) + "\n"


def build_arg_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="python -m radar.cli",
        description="AI Release Radar offline CLI.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    dry_run = subparsers.add_parser(
        "dry-run",
        help="Run the deterministic offline dry-run from local fixtures.",
    )
    dry_run.add_argument(
        "--output-dir",
        required=True,
        help="Explicit directory where dry-run outputs are written.",
    )
    dry_run.add_argument(
        "--compact-only",
        action="store_true",
        help="Write only compact report and summary.",
    )
    dry_run.add_argument(
        "--full-only",
        action="store_true",
        help="Write only full report and summary.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint returning a process-style exit code."""
    parser = build_arg_parser()
    try:
        args = parser.parse_args(argv)
        if args.command == "dry-run":
            if args.compact_only and args.full_only:
                parser.error("--compact-only and --full-only cannot be used together.")
            result = run_dry_run(
                args.output_dir,
                full=not args.compact_only,
                compact=not args.full_only,
            )
            summary = Path(result["summary"]).read_text(encoding="utf-8")
            sys.stdout.write(summary)
            return 0
        parser.error(f"unsupported command: {args.command}")
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 1
    except Exception as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1
    return 1


def _write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    raise SystemExit(main())
