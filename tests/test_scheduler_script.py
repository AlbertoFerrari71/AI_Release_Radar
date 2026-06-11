from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "scheduler"
    / "ai_release_radar_daily_dry_report.ps1"
)


def test_scheduler_script_has_stale_lock_recovery_contract_markers():
    script = SCRIPT_PATH.read_text(encoding="utf-8")

    required_markers = [
        "$StaleLockMinutes = 150",
        "run_id",
        "STALE_LOCK_DETECTED",
        "ACTIVE_LOCK_DETECTED",
        "CORRUPT_LOCK_DETECTED",
        "Archive-ExistingLock",
        "Test-CurrentRunOwnsLock",
        "Get-CurrentProcessLineageIds",
        "Test-OtherSchedulerScriptProcessPresent",
        "legacy_lock_without_owner",
        "script_exit_code",
        "script_exit_reason",
    ]
    for marker in required_markers:
        assert marker in script


def test_scheduler_script_captures_stdout_and_stderr_separately():
    script = SCRIPT_PATH.read_text(encoding="utf-8")

    assert "scheduler_dry_report_$Stamp.stdout.txt" in script
    assert "scheduler_dry_report_$Stamp.stderr.txt" in script
    assert "1> $StdoutPath 2> $StderrPath" in script
    assert "Write-CombinedCommandOutput" in script


def test_scheduler_script_removes_only_current_run_lock():
    script = SCRIPT_PATH.read_text(encoding="utf-8")

    assert "Test-CurrentRunOwnsLock" in script
    assert "Remove-Item -LiteralPath $LockPath -Force" in script
    assert "lock_removed_reason=not_owned_by_current_run" in script
