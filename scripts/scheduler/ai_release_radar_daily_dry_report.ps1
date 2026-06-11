Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$TaskName = "AIReleaseRadar_DailyDryReport"
$RepoRoot = "C:\Users\alberto.ferrari\source\repos\AI_Release_Radar"
$BridgeRoot = "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar"
$RunsRoot = Join-Path $BridgeRoot "runs"
$LogRoot = Join-Path $BridgeRoot "scheduler_logs"
$LockRoot = Join-Path $BridgeRoot "scheduler_locks"
$LockPath = Join-Path $LockRoot "$TaskName.lock.json"
$StaleLockMinutes = 150
$RunId = [System.Guid]::NewGuid().ToString("N")
$StartedAtUtc = (Get-Date).ToUniversalTime()
$Stamp = $StartedAtUtc.ToString("yyyyMMdd_HHmmss")
$LogPath = Join-Path $LogRoot "scheduler_dry_report_$Stamp.log"
$CommandOutputPath = Join-Path $LogRoot "scheduler_dry_report_$Stamp.command_output.txt"
$StdoutPath = Join-Path $LogRoot "scheduler_dry_report_$Stamp.stdout.txt"
$StderrPath = Join-Path $LogRoot "scheduler_dry_report_$Stamp.stderr.txt"
$LockCreated = $false
$ScriptExitCode = 1
$ScriptExitReason = "unhandled_error"
$InitialCwd = (Get-Location).Path
$Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding($false)

function Format-Bool {
    param(
        [bool] $Value
    )
    if ($Value) {
        return "true"
    }
    return "false"
}

function Format-Decimal1 {
    param(
        [double] $Value
    )
    return $Value.ToString("N1", [System.Globalization.CultureInfo]::InvariantCulture)
}

function Write-LogLine {
    param(
        [string] $Message
    )
    $line = "{0} {1}" -f (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK"), $Message
    for ($attempt = 1; $attempt -le 10; $attempt++) {
        try {
            [System.IO.File]::AppendAllText($LogPath, $line + [Environment]::NewLine, $Utf8NoBomEncoding)
            return
        } catch [System.IO.IOException] {
            if ($attempt -eq 10) {
                throw
            }
            Start-Sleep -Milliseconds (200 * $attempt)
        }
    }
}

function Write-LogTextBlock {
    param(
        [string] $Prefix,
        [string] $Text
    )
    if ([string]::IsNullOrEmpty($Text)) {
        Write-LogLine ("{0}=<empty>" -f $Prefix)
        return
    }
    foreach ($textLine in ($Text -split "\r?\n")) {
        Write-LogLine ("{0}={1}" -f $Prefix, $textLine)
    }
}

function Test-ForbiddenLatestOrLastPath {
    param(
        [string] $PathValue
    )
    return ($PathValue -like "*\LAST-*" -or $PathValue -like "*\latest-*")
}

function Get-JsonPropertyValue {
    param(
        [object] $Data,
        [string] $PropertyName
    )
    if ($null -eq $Data) {
        return $null
    }
    if ($Data.PSObject.Properties.Name -contains $PropertyName) {
        return $Data.$PropertyName
    }
    return $null
}

function Archive-ExistingLock {
    param(
        [string] $Kind,
        [string] $LockText
    )
    $archivePath = Join-Path $LockRoot ("{0}.{1}_{2}.lock.json" -f $TaskName, $Kind, $Stamp)
    Move-Item -LiteralPath $LockPath -Destination $archivePath -Force
    Write-LogLine ("{0}_lock_archived_path={1}" -f $Kind, $archivePath)
    Write-LogTextBlock ("{0}_lock_content" -f $Kind) $LockText
    return $archivePath
}

function New-CurrentRunLock {
    param(
        [object] $LockData
    )
    $lockJson = $LockData | ConvertTo-Json -Depth 4
    $lockBytes = $Utf8NoBomEncoding.GetBytes($lockJson + [Environment]::NewLine)
    $stream = $null
    try {
        $stream = [System.IO.File]::Open(
            $LockPath,
            [System.IO.FileMode]::CreateNew,
            [System.IO.FileAccess]::Write,
            [System.IO.FileShare]::None
        )
        $stream.Write($lockBytes, 0, $lockBytes.Length)
        return $true
    } catch [System.IO.IOException] {
        return $false
    } finally {
        if ($null -ne $stream) {
            $stream.Dispose()
        }
    }
}

function Test-CurrentRunOwnsLock {
    if (-not (Test-Path -LiteralPath $LockPath -PathType Leaf)) {
        return $false
    }
    try {
        $currentLockText = Get-Content -LiteralPath $LockPath -Raw -Encoding UTF8
        $currentLockData = $currentLockText | ConvertFrom-Json
        $currentRunId = Get-JsonPropertyValue $currentLockData "run_id"
        return ([string] $currentRunId -eq $RunId)
    } catch {
        Write-LogLine ("warning=current_lock_unreadable_for_cleanup message={0}" -f $_.Exception.Message)
        return $false
    }
}

function Get-ScheduledTaskStateText {
    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction Stop
        return [string] $task.State
    } catch {
        Write-LogLine ("warning=scheduled_task_state_unavailable message={0}" -f $_.Exception.Message)
        return "unavailable"
    }
}

function Get-CurrentProcessLineageIds {
    $lineageIds = New-Object "System.Collections.Generic.HashSet[int]"
    [void] $lineageIds.Add([int] $PID)
    try {
        $currentProcess = Get-CimInstance Win32_Process -Filter ("ProcessId = {0}" -f $PID)
        while ($null -ne $currentProcess -and $null -ne $currentProcess.ParentProcessId) {
            $parentProcessId = [int] $currentProcess.ParentProcessId
            if ($parentProcessId -le 0 -or $lineageIds.Contains($parentProcessId)) {
                break
            }
            [void] $lineageIds.Add($parentProcessId)
            $currentProcess = Get-CimInstance Win32_Process -Filter ("ProcessId = {0}" -f $parentProcessId)
        }
    } catch {
        Write-LogLine ("warning=process_lineage_unavailable message={0}" -f $_.Exception.Message)
    }
    return $lineageIds
}

function Test-OtherSchedulerScriptProcessPresent {
    try {
        $scriptName = Split-Path -Leaf $PSCommandPath
        $currentLineageIds = Get-CurrentProcessLineageIds
        $matches = Get-CimInstance Win32_Process |
            Where-Object {
                -not $currentLineageIds.Contains([int] $_.ProcessId) -and
                $null -ne $_.CommandLine -and
                $_.CommandLine -like "*$scriptName*"
            }
        return ($null -ne $matches)
    } catch {
        Write-LogLine ("warning=process_owner_check_unavailable message={0}" -f $_.Exception.Message)
        return $true
    }
}

function Write-CombinedCommandOutput {
    $lines = @()
    $lines += "stdout_path=$StdoutPath"
    $lines += "stderr_path=$StderrPath"
    $lines += "stdout_begin"
    if (Test-Path -LiteralPath $StdoutPath -PathType Leaf) {
        $lines += Get-Content -LiteralPath $StdoutPath -Encoding UTF8
    }
    $lines += "stdout_end"
    $lines += "stderr_begin"
    if (Test-Path -LiteralPath $StderrPath -PathType Leaf) {
        $lines += Get-Content -LiteralPath $StderrPath -Encoding UTF8
    }
    $lines += "stderr_end"
    [System.IO.File]::WriteAllText(
        $CommandOutputPath,
        ($lines -join [Environment]::NewLine) + [Environment]::NewLine,
        $Utf8NoBomEncoding
    )
}

try {
    New-Item -ItemType Directory -Force -Path $RunsRoot, $LogRoot, $LockRoot | Out-Null

    Write-LogLine "task_name=$TaskName"
    Write-LogLine "mode=dry-report"
    Write-LogLine "run_id=$RunId"
    Write-LogLine ("started_at_utc={0}" -f $StartedAtUtc.ToString("o"))
    Write-LogLine "repo_root=$RepoRoot"
    Write-LogLine "runs_root=$RunsRoot"
    Write-LogLine "log_path=$LogPath"
    Write-LogLine "stdout_path=$StdoutPath"
    Write-LogLine "stderr_path=$StderrPath"
    Write-LogLine "command_output_path=$CommandOutputPath"
    Write-LogLine "lock_path=$LockPath"
    Write-LogLine "cwd_initial=$InitialCwd"
    Write-LogLine ("ps_version={0}" -f $PSVersionTable.PSVersion.ToString())
    Write-LogLine ("stale_lock_minutes={0}" -f $StaleLockMinutes)
    Write-LogLine "no_auto_action=confirmed"
    Write-LogLine "no_email=confirmed"
    Write-LogLine "no_external_notification=confirmed"
    Write-LogLine "no_llm=confirmed"
    Write-LogLine "no_git_commit_push=confirmed"

    foreach ($pathToCheck in @($RunsRoot, $LogRoot, $LockRoot, $LogPath, $CommandOutputPath, $StdoutPath, $StderrPath, $LockPath)) {
        if (Test-ForbiddenLatestOrLastPath $pathToCheck) {
            Write-LogLine ("error=forbidden_last_or_latest_path path={0}" -f $pathToCheck)
            $ScriptExitReason = "forbidden_last_or_latest_path"
            $ScriptExitCode = 1
            throw "Forbidden LAST/latest path detected: $pathToCheck"
        }
    }

    $repoRootExists = Test-Path -LiteralPath $RepoRoot -PathType Container
    $runsRootExists = Test-Path -LiteralPath $RunsRoot -PathType Container
    Write-LogLine ("repo_root_exists={0}" -f (Format-Bool $repoRootExists))
    Write-LogLine ("runs_root_exists={0}" -f (Format-Bool $runsRootExists))
    if (-not $repoRootExists) {
        Write-LogLine "error=repo_root_missing"
        $ScriptExitReason = "repo_root_missing"
        $ScriptExitCode = 1
        throw "Repository root missing: $RepoRoot"
    }

    $repoResolved = (Resolve-Path -LiteralPath $RepoRoot).Path
    $runsResolved = (Resolve-Path -LiteralPath $RunsRoot).Path
    if ($runsResolved.StartsWith($repoResolved, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-LogLine "error=runs_root_inside_repository"
        $ScriptExitReason = "runs_root_inside_repository"
        $ScriptExitCode = 1
        throw "Runs root cannot be inside the repository."
    }

    $lockExistsBefore = Test-Path -LiteralPath $LockPath -PathType Leaf
    $lockAgeMinutesText = "not_applicable"
    $staleLockDetected = $false
    $activeLockDetected = $false
    $corruptLockDetected = $false
    $scheduledTaskState = Get-ScheduledTaskStateText
    $otherSchedulerProcessDetected = Test-OtherSchedulerScriptProcessPresent
    Write-LogLine ("scheduled_task_state={0}" -f $scheduledTaskState)
    Write-LogLine ("other_scheduler_process_detected={0}" -f (Format-Bool $otherSchedulerProcessDetected))
    Write-LogLine ("lock_exists_before={0}" -f (Format-Bool $lockExistsBefore))

    if ($lockExistsBefore) {
        $lockText = Get-Content -LiteralPath $LockPath -Raw -Encoding UTF8
        $lockData = $null
        $lockStartedAtUtc = $null
        try {
            $lockData = $lockText | ConvertFrom-Json
        } catch {
            $corruptLockDetected = $true
            Write-LogLine ("CORRUPT_LOCK_DETECTED reason=invalid_json message={0}" -f $_.Exception.Message)
        }

        if (-not $corruptLockDetected) {
            $lockStartedAtRaw = Get-JsonPropertyValue $lockData "started_at_utc"
            $lockRunIdRaw = Get-JsonPropertyValue $lockData "run_id"
            $lockHasRunId = -not [string]::IsNullOrWhiteSpace([string] $lockRunIdRaw)
            if ($null -eq $lockStartedAtRaw -or [string]::IsNullOrWhiteSpace([string] $lockStartedAtRaw)) {
                $corruptLockDetected = $true
                Write-LogLine "CORRUPT_LOCK_DETECTED reason=missing_started_at_utc"
            } else {
                try {
                    $lockStartedAtUtc = [System.DateTimeOffset]::Parse(
                        [string] $lockStartedAtRaw,
                        [System.Globalization.CultureInfo]::InvariantCulture
                    ).UtcDateTime
                    $lockAgeMinutes = ($StartedAtUtc - $lockStartedAtUtc).TotalMinutes
                    $lockAgeMinutesText = Format-Decimal1 $lockAgeMinutes
                    if ($lockAgeMinutes -gt $StaleLockMinutes) {
                        $staleLockDetected = $true
                        Write-LogLine ("STALE_LOCK_DETECTED lock_age_minutes={0} threshold_minutes={1}" -f $lockAgeMinutesText, $StaleLockMinutes)
                    } elseif (-not $lockHasRunId -and $scheduledTaskState -ne "Running" -and -not $otherSchedulerProcessDetected) {
                        $staleLockDetected = $true
                        Write-LogLine ("STALE_LOCK_DETECTED reason=legacy_lock_without_owner lock_age_minutes={0} scheduled_task_state={1}" -f $lockAgeMinutesText, $scheduledTaskState)
                    } else {
                        $activeLockDetected = $true
                        Write-LogLine ("ACTIVE_LOCK_DETECTED lock_age_minutes={0} threshold_minutes={1}" -f $lockAgeMinutesText, $StaleLockMinutes)
                        Write-LogTextBlock "active_lock_content" $lockText
                    }
                } catch {
                    $corruptLockDetected = $true
                    $lockAgeMinutesText = "not_available"
                    Write-LogLine ("CORRUPT_LOCK_DETECTED reason=invalid_started_at_utc message={0}" -f $_.Exception.Message)
                }
            }
        }

        Write-LogLine ("lock_age_minutes={0}" -f $lockAgeMinutesText)
        Write-LogLine ("stale_lock_detected={0}" -f (Format-Bool $staleLockDetected))
        Write-LogLine ("active_lock_detected={0}" -f (Format-Bool $activeLockDetected))
        Write-LogLine ("corrupt_lock_detected={0}" -f (Format-Bool $corruptLockDetected))

        if ($activeLockDetected) {
            $ScriptExitCode = 2
            $ScriptExitReason = "active_lock_detected"
        } elseif ($staleLockDetected) {
            [void] (Archive-ExistingLock "stale" $lockText)
        } elseif ($corruptLockDetected) {
            [void] (Archive-ExistingLock "corrupt" $lockText)
        }
    } else {
        Write-LogLine "lock_age_minutes=not_applicable"
        Write-LogLine "stale_lock_detected=false"
        Write-LogLine "active_lock_detected=false"
        Write-LogLine "corrupt_lock_detected=false"
    }

    if (-not $activeLockDetected) {
        $lockDataToWrite = [ordered]@{
            task_name = $TaskName
            run_id = $RunId
            started_at_utc = $StartedAtUtc.ToString("o")
            repo_root = $RepoRoot
            runs_root = $RunsRoot
            log_path = $LogPath
            stdout_path = $StdoutPath
            stderr_path = $StderrPath
        }
        $LockCreated = New-CurrentRunLock $lockDataToWrite
        if (-not $LockCreated) {
            Write-LogLine "ACTIVE_LOCK_DETECTED reason=concurrent_lock_create"
            Write-LogLine "active_lock_detected=true"
            $ScriptExitCode = 2
            $ScriptExitReason = "concurrent_lock_create"
        }
    }

    if ($LockCreated) {
        Set-Location -Path $RepoRoot
        Write-LogLine ("cwd_after_set_location={0}" -f (Get-Location).Path)

        $pythonCommand = Get-Command python -ErrorAction Stop
        $pythonPath = $pythonCommand.Source
        $pythonVersion = (& $pythonPath --version 2>&1 | Out-String).Trim()
        Write-LogLine ("python_path={0}" -f $pythonPath)
        Write-LogLine ("python_version={0}" -f $pythonVersion)
        Write-LogLine "command=python -m radar.cli daily-sim --output-root <BridgeRunsRoot>"

        $commandStartedAtUtc = (Get-Date).ToUniversalTime()
        Write-LogLine ("command_start={0}" -f $commandStartedAtUtc.ToString("o"))
        & $pythonPath -m radar.cli daily-sim --output-root $RunsRoot 1> $StdoutPath 2> $StderrPath
        $dailySimExitCode = $LASTEXITCODE
        $commandEndedAtUtc = (Get-Date).ToUniversalTime()
        $durationSeconds = ($commandEndedAtUtc - $commandStartedAtUtc).TotalSeconds

        Write-CombinedCommandOutput
        Write-LogLine ("command_end={0}" -f $commandEndedAtUtc.ToString("o"))
        Write-LogLine ("command_exit_code={0}" -f $dailySimExitCode)
        Write-LogLine ("duration_seconds={0}" -f (Format-Decimal1 $durationSeconds))
        Write-LogLine ("daily_sim_exit_code={0}" -f $dailySimExitCode)
        Write-LogLine "command_output_path=$CommandOutputPath"
        Write-LogLine "stdout_path=$StdoutPath"
        Write-LogLine "stderr_path=$StderrPath"
        if (Test-Path -LiteralPath $StdoutPath -PathType Leaf) {
            Get-Content -LiteralPath $StdoutPath -Encoding UTF8 | ForEach-Object {
                Write-LogLine ("stdout={0}" -f $_)
            }
        }
        if (Test-Path -LiteralPath $StderrPath -PathType Leaf) {
            Get-Content -LiteralPath $StderrPath -Encoding UTF8 | ForEach-Object {
                Write-LogLine ("stderr={0}" -f $_)
            }
        }

        $ScriptExitCode = $dailySimExitCode
        $ScriptExitReason = "daily_sim_exit_code"
    }
} catch {
    try {
        Write-LogLine ("error={0}" -f $_.Exception.Message)
    } catch {
    }
    if ($ScriptExitReason -eq "unhandled_error") {
        $ScriptExitReason = "script_exception"
    }
    if ($ScriptExitCode -eq 0) {
        $ScriptExitCode = 1
    }
} finally {
    try {
        if ($LockCreated) {
            if (Test-CurrentRunOwnsLock) {
                Remove-Item -LiteralPath $LockPath -Force
                Write-LogLine "lock_removed=true"
            } else {
                Write-LogLine "lock_removed=false"
                Write-LogLine "lock_removed_reason=not_owned_by_current_run"
            }
        } else {
            Write-LogLine "lock_removed=false"
            Write-LogLine "lock_removed_reason=no_current_run_lock"
        }
        Write-LogLine ("script_exit_code={0}" -f $ScriptExitCode)
        Write-LogLine ("script_exit_reason={0}" -f $ScriptExitReason)
    } catch {
    }
}

exit $ScriptExitCode
