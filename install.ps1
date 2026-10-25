<#
.SYNOPSIS
    One-click installer for Suno Battle MV Architect AI Agent Skill.
.DESCRIPTION
    Installs suno-battle-mv-architect into Antigravity, Claude Code, Cursor, and Codex skills directories.
.USAGE
    # Remote one-liner (PowerShell):
    irm https://raw.githubusercontent.com/JeffreyHo0520/suno-battle-mv-architect/main/install.ps1 | iex

    # Local execution:
    .\install.ps1
    .\install.ps1 -Workspace
    .\install.ps1 -Dest "C:\custom\skills"
    .\install.ps1 -Force
#>
[CmdletBinding()]
param(
    [string]$Dest,
    [switch]$Workspace,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$repoUrl = "https://github.com/JeffreyHo0520/suno-battle-mv-architect.git"
$skillName = "suno-battle-mv-architect"
$isRemote = -not $PSScriptRoot -or ($PSScriptRoot -eq "")

if ($isRemote) {
    Write-Host ">>> [$skillName] Detected remote execution via web. Cloning temporary repository..." -ForegroundColor Cyan
    $tempDir = Join-Path $env:TEMP ("$skillName-" + [System.Guid]::NewGuid().ToString("N"))
    git clone --depth 1 $repoUrl $tempDir
    $scriptDir = $tempDir
} else {
    $scriptDir = $PSScriptRoot
}

try {
    Write-Host "=================================================================" -ForegroundColor Cyan
    Write-Host " 🎤 Installing Suno Battle MV Architect AI Agent Skill          " -ForegroundColor Cyan
    Write-Host "    - Speaker-Adaptive Theme Engine (HUD, Pills, Spectrum)      " -ForegroundColor Cyan
    Write-Host "    - Audio-Reactive Bass & 64-Band Smoothed Spectrum           " -ForegroundColor Cyan
    Write-Host "    - Zero-Tofu Glyph & Unicode-Safe OpenCV I/O                 " -ForegroundColor Cyan
    Write-Host "    - Intel QSV (-pix_fmt nv12) Accelerated 1080p / Shorts      " -ForegroundColor Cyan
    Write-Host "=================================================================" -ForegroundColor Cyan

    $destDirs = @()
    if ($Dest) {
        $destDirs += $Dest
    } elseif ($Workspace) {
        $destDirs += Join-Path (Get-Location) ".agents\skills"
        $destDirs += Join-Path (Get-Location) ".gemini\skills"
        $destDirs += Join-Path (Get-Location) ".claude\skills"
    } else {
        $userHome = $env:USERPROFILE
        $destDirs += Join-Path $userHome ".gemini\config\skills"
        $codexSkills = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME "skills" } else { Join-Path $userHome ".codex\skills" }
        $claudeSkills = Join-Path $userHome ".claude\skills"
        $agentsSkills = Join-Path $userHome ".agents\skills"
        $destDirs += $codexSkills
        $destDirs += $claudeSkills
        $destDirs += $agentsSkills
    }

    $srcSkillPath = Join-Path $scriptDir "skills\$skillName"
    if (-not (Test-Path $srcSkillPath)) {
        # Fallback to current folder if structured as flat skill
        if (Test-Path (Join-Path $scriptDir "SKILL.md")) {
            $srcSkillPath = $scriptDir
        } else {
            throw "Source skill directory not found in: $scriptDir"
        }
    }

    foreach ($skillsRoot in $destDirs) {
        if (-not (Test-Path $skillsRoot)) {
            New-Item -ItemType Directory -Path $skillsRoot -Force | Out-Null
        }

        Write-Host "`n>>> Target Skills Root: $skillsRoot" -ForegroundColor Yellow
        $targetPath = Join-Path $skillsRoot $skillName

        if (Test-Path $targetPath) {
            if (-not $Force) {
                Write-Host "  [-] $skillName already exists at: $targetPath (Use -Force to overwrite)" -ForegroundColor DarkGray
                continue
            }
            $timestamp = (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ")
            $backup = "$targetPath.backup.$timestamp"
            Move-Item -Path $targetPath -Destination $backup -Force
            Write-Host "  [*] Backed up previous $skillName to: $backup" -ForegroundColor DarkCyan
        }

        New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
        Copy-Item (Join-Path $srcSkillPath "*") -Destination $targetPath -Recurse -Force

        # Clean up __pycache__
        Get-ChildItem -Path $targetPath -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

        Write-Host "  [+] Installed $skillName successfully!" -ForegroundColor Green
    }

    # Prerequisites Check
    Write-Host "`n-----------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "🔍 Environment Prerequisites Check:" -ForegroundColor Cyan
    Write-Host "-----------------------------------------------------------------" -ForegroundColor Cyan

    $pyCmd = Get-Command python -ErrorAction SilentlyContinue
    if ($pyCmd) {
        Write-Host "  [✓] Python is available: $(python --version)" -ForegroundColor Green
    } else {
        Write-Host "  [!] Python not found. Install via: winget install Python.Python.3.11" -ForegroundColor Yellow
    }

    $ffCmd = Get-Command ffmpeg -ErrorAction SilentlyContinue
    if ($ffCmd) {
        Write-Host "  [✓] ffmpeg is available." -ForegroundColor Green
    } else {
        Write-Host "  [!] ffmpeg not found. Install via: winget install Gyan.FFmpeg" -ForegroundColor Yellow
    }

    # Python packages check
    if ($pyCmd) {
        $packages = @("requests", "cv2", "numpy", "PIL")
        foreach ($pkg in $packages) {
            $check = python -c "import $pkg" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "  [✓] Python package '$pkg' is installed." -ForegroundColor Green
            } else {
                Write-Host "  [!] Python package '$pkg' missing. Run: pip install requests opencv-python numpy pillow" -ForegroundColor Yellow
            }
        }
    }

    # Groq API Key check
    $hasGroqKey = ($env:GROQ_API_KEY -ne $null -and $env:GROQ_API_KEY -ne "") -or (Test-Path "$HOME\.groq_api_key")
    if ($hasGroqKey) {
        Write-Host "  [✓] Groq API Key detected for Whisper transcription." -ForegroundColor Green
    } else {
        Write-Host "  [!] Note: Set GROQ_API_KEY env or save your key to ~/.groq_api_key for Whisper transcription." -ForegroundColor DarkYellow
    }

    Write-Host "`n✨ Installation completed successfully! You can now use /suno-battle-mv-architect in your AI agent." -ForegroundColor Green
}
finally {
    if ($isRemote -and (Test-Path $tempDir)) {
        Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}
