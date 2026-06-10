Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$TaskName = "AIReleaseRadar_DailyDryReport"
$RepoRoot = "C:\Users\alberto.ferrari\source\repos\AI_Release_Radar"
$BridgeRoot = "D:\FG-SAB Dropbox\Alberto Ferrari\ChatGPT_Bridge\AI_Release_Radar"
$RunsRoot = Join-Path $BridgeRoot "runs"
$LogRoot = Join-Path $BridgeRoot "scheduler_logs"
$LockRoot = Join-Path $BridgeRoot "scheduler_locks"
$LockPath = Join-Path $LockRoot "$TaskName.lock.json"
$LockTimeoutMinutes = 120
$StartedAtUtc = (Get-Date).ToUniversalTime()
$Stamp = $StartedAtUtc.ToString("yyyyMMdd_HHmmss")
$LogPath = Join-Path $LogRoot "scheduler_dry_report_$Stamp.log"
$CommandOutputPath = Join-Path $LogRoot "scheduler_dry_report_$Stamp.command_output.txt"
$LockCreated = $false

function Write-LogLine {
    param(
        [string] $Message
    )
    $line = "{0} {1}" -f (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK"), $Message
    $encoding = New-Object System.Text.UTF8Encoding($false)
    for ($attempt = 1; $attempt -le 10; $attempt++) {
        try {
            [System.IO.File]::AppendAllText($LogPath, $line + [Environment]::NewLine, $encoding)
            return
        } catch [System.IO.IOException] {
            if ($attempt -eq 10) {
                throw
            }
            Start-Sleep -Milliseconds (200 * $attempt)
        }
    }
}

function Exit-WithCode {
    param(
        [int] $Code
    )
    if ($LockCreated -and (Test-Path -LiteralPath $LockPath)) {
        Remove-Item -LiteralPath $LockPath -Force
    }
    Write-LogLine ("exit_code={0}" -f $Code)
    exit $Code
}

try {
    New-Item -ItemType Directory -Force -Path $RunsRoot, $LogRoot, $LockRoot | Out-Null
    Write-LogLine "task_name=$TaskName"
    Write-LogLine "mode=dry-report"
    Write-LogLine "repo_root=$RepoRoot"
    Write-LogLine "runs_root=$RunsRoot"
    Write-LogLine "no_auto_action=confirmed"
    Write-LogLine "no_email=confirmed"
    Write-LogLine "no_external_notification=confirmed"
    Write-LogLine "no_llm=confirmed"
    Write-LogLine "no_git_commit_push=confirmed"

    if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
        Write-LogLine "error=repo_root_missing"
        Exit-WithCode 1
    }

    $repoResolved = (Resolve-Path -LiteralPath $RepoRoot).Path
    $runsResolved = (Resolve-Path -LiteralPath $RunsRoot).Path
    if ($runsResolved.StartsWith($repoResolved, [System.StringComparison]::OrdinalIgnoreCase)) {
        Write-LogLine "error=runs_root_inside_repository"
        Exit-WithCode 1
    }
    if ($RunsRoot -like "*\LAST-*" -or $RunsRoot -like "*\latest-*") {
        Write-LogLine "error=runs_root_uses_forbidden_name"
        Exit-WithCode 1
    }
    if ($LogRoot -like "*\LAST-*" -or $LogRoot -like "*\latest-*") {
        Write-LogLine "error=log_root_uses_forbidden_name"
        Exit-WithCode 1
    }

    if (Test-Path -LiteralPath $LockPath) {
        $lockText = Get-Content -LiteralPath $LockPath -Raw -Encoding UTF8
        $lockData = $null
        try {
            $lockData = $lockText | ConvertFrom-Json
        } catch {
            Write-LogLine "warning=lock_file_invalid_json"
        }
        $lockStartedAt = $null
        if ($null -ne $lockData -and $lockData.PSObject.Properties.Name -contains "started_at_utc") {
            $lockStartedAt = [datetime]::Parse([string] $lockData.started_at_utc).ToUniversalTime()
        }
        if ($null -ne $lockStartedAt) {
            $ageMinutes = ($StartedAtUtc - $lockStartedAt).TotalMinutes
            if ($ageMinutes -lt $LockTimeoutMinutes) {
                Write-LogLine ("error=lock_present age_minutes={0:N1}" -f $ageMinutes)
                Exit-WithCode 2
            }
        }
        $staleLockPath = Join-Path $LockRoot ("$TaskName.stale_$Stamp.lock.json")
        Move-Item -LiteralPath $LockPath -Destination $staleLockPath -Force
        Write-LogLine "warning=stale_lock_archived"
        Write-LogLine "stale_lock_path=$staleLockPath"
    }

    $lockDataToWrite = [ordered]@{
        task_name = $TaskName
        started_at_utc = $StartedAtUtc.ToString("o")
        repo_root = $RepoRoot
        runs_root = $RunsRoot
        log_path = $LogPath
    }
    $lockDataToWrite | ConvertTo-Json -Depth 3 | Set-Content -LiteralPath $LockPath -Encoding UTF8
    $LockCreated = $true

    Set-Location -LiteralPath $RepoRoot
    $pythonCommand = Get-Command python -ErrorAction Stop
    Write-LogLine ("python={0}" -f $pythonCommand.Source)
    Write-LogLine "command=python -m radar.cli daily-sim --output-root <BridgeRunsRoot>"

    & $pythonCommand.Source -m radar.cli daily-sim --output-root $RunsRoot *> $CommandOutputPath
    $dailySimExitCode = $LASTEXITCODE
    Write-LogLine ("daily_sim_exit_code={0}" -f $dailySimExitCode)
    Write-LogLine "command_output_path=$CommandOutputPath"
    if (Test-Path -LiteralPath $CommandOutputPath) {
        Get-Content -LiteralPath $CommandOutputPath -Encoding UTF8 | ForEach-Object {
            Write-LogLine ("daily_sim_output={0}" -f $_)
        }
    }
    Exit-WithCode $dailySimExitCode
} catch {
    try {
        Write-LogLine ("error={0}" -f $_.Exception.Message)
    } catch {
    }
    Exit-WithCode 1
}
