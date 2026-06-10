"""Command line interface for AI Release Radar local workflows."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from radar.json_utils import read_json, write_json
from radar.live_url_check import (
    check_sources_live,
    verification_results_to_dict,
)
from radar.report_engine import (
    ReportInput,
    load_report_input,
    render_compact_markdown_report,
    render_full_markdown_report,
    render_report_status,
)
from radar.source_registry import load_source_registry_file
from radar.source_fetcher import (
    fetched_sources_to_dict,
    fetch_sources_content,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
DRY_RUN_INPUT_PATH = REPO_ROOT / "examples" / "fixtures" / "0080_report_input.json"
DEFAULT_SOURCE_REGISTRY_PATH = REPO_ROOT / "config" / "sources" / "openai_sources.json"
FULL_REPORT_FILENAME = "0090_dry_run_report_full.md"
COMPACT_REPORT_FILENAME = "0090_dry_run_report_compact.md"
SUMMARY_FILENAME = "0090_dry_run_summary.txt"
CHECK_URLS_RESULTS_FILENAME = "0110_live_url_check_results.json"
CHECK_URLS_SUMMARY_FILENAME = "0110_live_url_check_summary.txt"
FETCH_SOURCES_RESULTS_FILENAME = "0130_fetch_sources_results.json"
FETCH_SOURCES_SUMMARY_FILENAME = "0130_fetch_sources_summary.txt"
NEXT_STEP_RECOMMENDATION = "0100) OpenAI Source Registry and URL Verification"
CHECK_URLS_NEXT_STEP_RECOMMENDATION = (
    "0130) Source Fetcher Skeleton Without Parsing"
)
FETCH_SOURCES_NEXT_STEP_RECOMMENDATION = (
    "0140) Source Fetcher Review and Content Safety Hardening"
)


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


def run_check_urls(
    registry: str,
    output_dir: str,
    timeout_seconds: float = 10.0,
    max_sources: int | None = None,
) -> dict[str, str]:
    """Run the explicit live URL check and write results to output_dir."""
    target_dir = Path(output_dir).expanduser().resolve()
    target_dir.mkdir(parents=True, exist_ok=True)

    sources = load_source_registry_file(registry)
    results = check_sources_live(
        sources,
        timeout_seconds=timeout_seconds,
        max_sources=max_sources,
    )
    results_data = verification_results_to_dict(results)

    results_path = target_dir / CHECK_URLS_RESULTS_FILENAME
    summary_path = target_dir / CHECK_URLS_SUMMARY_FILENAME
    write_json(results_path, results_data)
    _write_text(
        summary_path,
        build_check_urls_summary(
            results_data["summary"],
            results_json=str(results_path),
            summary=str(summary_path),
        ),
    )
    return {
        "results_json": str(results_path),
        "summary": str(summary_path),
    }


def run_fetch_sources(
    registry: str,
    output_dir: str,
    timeout_seconds: float | None = None,
    max_sources: int | None = None,
    max_bytes: int = 4096,
) -> dict[str, str]:
    """Run the explicit live read-only bounded source content fetch."""
    target_dir = Path(output_dir).expanduser().resolve()
    if _is_path_within(target_dir, REPO_ROOT):
        raise ValueError("fetch-sources output_dir must be outside repository.")
    target_dir.mkdir(parents=True, exist_ok=True)

    sources = load_source_registry_file(registry)
    results = fetch_sources_content(
        sources,
        timeout_seconds=timeout_seconds,
        max_sources=max_sources,
        max_bytes=max_bytes,
    )
    results_data = fetched_sources_to_dict(results)

    results_path = target_dir / FETCH_SOURCES_RESULTS_FILENAME
    summary_path = target_dir / FETCH_SOURCES_SUMMARY_FILENAME
    write_json(results_path, results_data)
    _write_text(
        summary_path,
        build_fetch_sources_summary(
            results_data["summary"],
            max_bytes=max_bytes,
            results_json=str(results_path),
            summary=str(summary_path),
        ),
    )
    return {
        "results_json": str(results_path),
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


def build_check_urls_summary(
    summary_data: object,
    *,
    results_json: str,
    summary: str,
) -> str:
    """Build the console and file summary for check-urls."""
    if not isinstance(summary_data, dict):
        raise ValueError("summary_data must be a dict.")
    lines = [
        "AI Release Radar live URL check completed",
        f"Total: {summary_data.get('total')}",
        f"OK: {summary_data.get('ok')}",
        f"Failed: {summary_data.get('failed')}",
        f"Redirected: {summary_data.get('redirected')}",
        f"Timeout: {summary_data.get('timeout')}",
        f"Unreachable: {summary_data.get('unreachable')}",
        f"Unexpected status: {summary_data.get('unexpected_status')}",
        f"Disabled: {summary_data.get('disabled')}",
        f"Recommendation: {summary_data.get('recommendation')}",
        f"Results JSON: {results_json}",
        f"Summary: {summary}",
        f"Next step: {CHECK_URLS_NEXT_STEP_RECOMMENDATION}",
    ]
    return "\n".join(lines) + "\n"


def build_fetch_sources_summary(
    summary_data: object,
    *,
    max_bytes: int,
    results_json: str,
    summary: str,
) -> str:
    """Build the console and file summary for fetch-sources."""
    if not isinstance(summary_data, dict):
        raise ValueError("summary_data must be a dict.")
    lines = [
        "AI Release Radar source fetch completed",
        "Mode: live read-only bounded content fetch",
        f"Total: {summary_data.get('total')}",
        f"OK: {summary_data.get('ok')}",
        f"Failed: {summary_data.get('failed')}",
        f"Disabled: {summary_data.get('disabled')}",
        f"Truncated: {summary_data.get('truncated')}",
        f"Unexpected status: {summary_data.get('unexpected_status')}",
        f"Redirect not allowed: {summary_data.get('redirect_not_allowed')}",
        f"Max bytes: {max_bytes}",
        "Parsing: not performed",
        "Snapshot: not created",
        f"Results JSON: {results_json}",
        f"Summary: {summary}",
        f"Next step: {FETCH_SOURCES_NEXT_STEP_RECOMMENDATION}",
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
    check_urls = subparsers.add_parser(
        "check-urls",
        help="Run the explicit live read-only URL check from a source registry.",
    )
    check_urls.add_argument(
        "--registry",
        required=True,
        help=f"Source registry JSON path. Default project registry: {DEFAULT_SOURCE_REGISTRY_PATH}",
    )
    check_urls.add_argument(
        "--output-dir",
        required=True,
        help="Explicit directory where URL check outputs are written.",
    )
    check_urls.add_argument(
        "--max-sources",
        type=int,
        default=None,
        help="Optional maximum number of registry sources to check.",
    )
    check_urls.add_argument(
        "--timeout-seconds",
        type=float,
        default=10.0,
        help="Per-source timeout in seconds.",
    )
    fetch_sources = subparsers.add_parser(
        "fetch-sources",
        help="Run the explicit live read-only bounded source content fetch.",
    )
    fetch_sources.add_argument(
        "--registry",
        required=True,
        help=f"Source registry JSON path. Default project registry: {DEFAULT_SOURCE_REGISTRY_PATH}",
    )
    fetch_sources.add_argument(
        "--output-dir",
        required=True,
        help="Explicit directory where bounded source content outputs are written.",
    )
    fetch_sources.add_argument(
        "--max-sources",
        type=int,
        default=None,
        help="Optional maximum number of registry sources to fetch.",
    )
    fetch_sources.add_argument(
        "--timeout-seconds",
        type=float,
        default=None,
        help="Optional per-source timeout in seconds. Registry value or safe default is used when omitted.",
    )
    fetch_sources.add_argument(
        "--max-bytes",
        type=int,
        default=4096,
        help="Maximum number of response body bytes to read per source.",
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
        if args.command == "check-urls":
            result = run_check_urls(
                args.registry,
                args.output_dir,
                timeout_seconds=args.timeout_seconds,
                max_sources=args.max_sources,
            )
            summary = Path(result["summary"]).read_text(encoding="utf-8")
            sys.stdout.write(summary)
            return 0
        if args.command == "fetch-sources":
            result = run_fetch_sources(
                args.registry,
                args.output_dir,
                timeout_seconds=args.timeout_seconds,
                max_sources=args.max_sources,
                max_bytes=args.max_bytes,
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


def _is_path_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


if __name__ == "__main__":
    raise SystemExit(main())
