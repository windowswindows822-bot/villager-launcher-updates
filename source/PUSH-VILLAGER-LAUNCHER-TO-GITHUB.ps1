param(
    [string]$Message = ""
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$RepoUrl = "https://github.com/windowswindows822-bot/villager-launcher-updates.git"
$Branch = "main"
$DestinationFolder = "source"
$MaxFileSizeMB = 25

function Pause-End {
    Write-Host ""
    Read-Host "Press Enter to close"
}

function Run-Git {
    param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)

    & git @GitArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Git command failed: git $($GitArgs -join ' ')"
    }
}

function Is-BlockedPath {
    param([string]$FullPath, [string]$ProjectRoot)

    $relative = $FullPath.Substring($ProjectRoot.Length).TrimStart('\', '/')
    $parts = $relative -split '[\\/]'

    $blockedDirectories = @(
        "bin","obj",".vs",".git","Backups","MigrationBackups",
        "VillagerLauncher-ProjectBackups","RepairReports","packages","TestResults"
    )

    foreach ($part in $parts) {
        if ($blockedDirectories -contains $part) { return $true }
    }

    $name = [IO.Path]::GetFileName($FullPath)

    $blockedExactNames = @(".env","secrets.json","launchSettings.json")
    if ($blockedExactNames -contains $name) { return $true }

    $blockedPatterns = @(
        ".env.*","appsettings*.json","*.pfx","*.p12","*.key",
        "*.pem","*.snk","*.user","*.suo","*.cache"
    )

    foreach ($pattern in $blockedPatterns) {
        if ($name -like $pattern) { return $true }
    }

    return $false
}

try {
    $ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host " Villager Launcher - ONE COMMAND GITHUB PUSH" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green

    if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
        throw "Git is not installed or not in PATH. Install Git for Windows first."
    }

    $Project = Get-ChildItem -Path $ScriptRoot -Filter *.csproj -File -Recurse -ErrorAction SilentlyContinue |
        Where-Object {
            $_.FullName -notmatch '\\(bin|obj|Backups|MigrationBackups|VillagerLauncher-ProjectBackups|RepairReports)\\'
        } |
        Sort-Object {
            if (Test-Path (Join-Path $_.Directory.FullName "MainWindow.xaml")) { 0 } else { 1 }
        }, @{Expression={$_.FullName.Length}} |
        Select-Object -First 1

    if (-not $Project) {
        throw "No Villager Launcher .csproj found. Put this script somewhere inside the launcher project tree."
    }

    $ProjectRoot = $Project.Directory.FullName

    Write-Host ""
    Write-Host "Launcher project:" -ForegroundColor Cyan
    Write-Host $ProjectRoot

    $SyncRoot = Join-Path $env:TEMP "VillagerLauncher-GitHub-Sync"
    $CloneRoot = Join-Path $SyncRoot "repo"

    if (Test-Path $SyncRoot) {
        Remove-Item $SyncRoot -Recurse -Force
    }

    New-Item -ItemType Directory -Path $SyncRoot -Force | Out-Null

    Write-Host ""
    Write-Host "[1/6] Cloning GitHub repo..." -ForegroundColor Yellow
    Run-Git clone --branch $Branch --single-branch $RepoUrl $CloneRoot

    $SourceDestination = Join-Path $CloneRoot $DestinationFolder

    if (Test-Path $SourceDestination) {
        Remove-Item $SourceDestination -Recurse -Force
    }

    New-Item -ItemType Directory -Path $SourceDestination -Force | Out-Null

    Write-Host "[2/6] Copying launcher source safely..." -ForegroundColor Yellow

    $copied = 0
    $skipped = 0
    $skippedLarge = New-Object System.Collections.Generic.List[string]

    Get-ChildItem -Path $ProjectRoot -File -Recurse -Force | ForEach-Object {
        $file = $_

        if (Is-BlockedPath -FullPath $file.FullName -ProjectRoot $ProjectRoot) {
            $script:skipped++
            return
        }

        $sizeMb = $file.Length / 1MB
        if ($sizeMb -gt $MaxFileSizeMB) {
            $script:skipped++
            $script:skippedLarge.Add(
                "$([Math]::Round($sizeMb, 1)) MB - $($file.FullName.Substring($ProjectRoot.Length).TrimStart('\','/'))"
            )
            return
        }

        $relative = $file.FullName.Substring($ProjectRoot.Length).TrimStart('\', '/')
        $target = Join-Path $SourceDestination $relative
        $targetDir = Split-Path -Parent $target

        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }

        Copy-Item -LiteralPath $file.FullName -Destination $target -Force
        $script:copied++
    }

    $readme = @"
# Villager Launcher Source

This folder contains the current C# / WinUI 3 Villager Launcher source synchronized from the development project.

The repository root updater files are intentionally kept separate.
Generated build folders and local/private files are excluded automatically.
"@

    [IO.File]::WriteAllText(
        (Join-Path $SourceDestination "README.md"),
        $readme,
        (New-Object Text.UTF8Encoding($false))
    )

    Write-Host "      Copied: $copied files" -ForegroundColor Green
    Write-Host "      Skipped: $skipped files" -ForegroundColor DarkGray

    if ($skippedLarge.Count -gt 0) {
        Write-Host ""
        Write-Host "Large files skipped (> $MaxFileSizeMB MB):" -ForegroundColor Yellow
        foreach ($item in $skippedLarge) {
            Write-Host "  $item" -ForegroundColor Yellow
        }
    }

    Set-Location $CloneRoot

    Write-Host ""
    Write-Host "[3/6] Preparing commit..." -ForegroundColor Yellow

    Run-Git config user.name "windowswindows822-bot"
    Run-Git config user.email "windowswindows822-bot@users.noreply.github.com"

    Run-Git add -A

    & git diff --cached --quiet
    $HasChanges = ($LASTEXITCODE -ne 0)

    if (-not $HasChanges) {
        Write-Host ""
        Write-Host "Nothing changed. GitHub already matches the current launcher source." -ForegroundColor Green
        Set-Location $ScriptRoot
        Remove-Item $SyncRoot -Recurse -Force
        Pause-End
        exit 0
    }

    if ([string]::IsNullOrWhiteSpace($Message)) {
        $Message = "Villager Launcher source update " + (Get-Date -Format "yyyy-MM-dd HH:mm")
    }

    Write-Host "[4/6] Committing..." -ForegroundColor Yellow
    Run-Git commit -m $Message

    Write-Host "[5/6] Pushing to GitHub..." -ForegroundColor Yellow
    Write-Host "      If GitHub asks you to sign in, finish the browser sign-in." -ForegroundColor Cyan

    Run-Git push origin $Branch

    Write-Host "[6/6] Cleaning temporary files..." -ForegroundColor Yellow
    Set-Location $ScriptRoot

    if (Test-Path $SyncRoot) {
        Remove-Item $SyncRoot -Recurse -Force
    }

    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host " PUSHED VILLAGER LAUNCHER TO GITHUB" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Uploaded to:" -ForegroundColor Cyan
    Write-Host "https://github.com/windowswindows822-bot/villager-launcher-updates"
    Write-Host ""
    Write-Host "Launcher source folder on GitHub: source/" -ForegroundColor Cyan
    Write-Host "Existing launcher.py and version.json were not touched." -ForegroundColor Green
}
catch {
    Write-Host ""
    Write-Host "GITHUB PUSH FAILED" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "If GitHub authentication was the problem, sign in when Git Credential Manager opens and run this script again." -ForegroundColor Yellow
}

Pause-End
