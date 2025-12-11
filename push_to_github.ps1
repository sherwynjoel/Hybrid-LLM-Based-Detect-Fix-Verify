# PowerShell script to push project to GitHub

# Error handling: Stop on errors
$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pushing to GitHub Repository" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if git is installed
try {
    $gitVersion = git --version 2>&1
    Write-Host "Git found: $gitVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Git is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Git from https://git-scm.com/" -ForegroundColor Yellow
    exit 1
}

# Get script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "Current directory: $scriptPath" -ForegroundColor Yellow
Write-Host ""

# Check if .git exists in project directory
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repository..." -ForegroundColor Yellow
    git init
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to initialize git repository" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Git repository already initialized" -ForegroundColor Green
}

# Remove lock file if exists (check in project directory, not user profile)
$lockFile = Join-Path $scriptPath ".git\index.lock"
if (Test-Path $lockFile) {
    Write-Host "Removing git lock file..." -ForegroundColor Yellow
    Remove-Item $lockFile -Force -ErrorAction SilentlyContinue
}

# Set remote URL
Write-Host "Setting remote URL..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin https://github.com/sherwynjoel/Hybrid-LLM-Based-Detect-Fix-Verify.git
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to set remote URL" -ForegroundColor Red
    exit 1
}

# Check for changes
Write-Host "Checking for changes..." -ForegroundColor Yellow
$status = git status --porcelain
if ([string]::IsNullOrWhiteSpace($status)) {
    Write-Host "No changes to commit. Checking if already pushed..." -ForegroundColor Yellow
    $localCommit = git rev-parse HEAD 2>$null
    $remoteCommit = git ls-remote origin main 2>$null | Select-Object -First 1
    if ($localCommit -and $remoteCommit -and $remoteCommit -match $localCommit) {
        Write-Host "Everything is already up to date!" -ForegroundColor Green
        exit 0
    }
}

# Add all files
Write-Host "Adding all files..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to add files" -ForegroundColor Red
    exit 1
}

# Commit
Write-Host "Committing changes..." -ForegroundColor Yellow
$commitMessage = @"
Complete Hybrid LLM-Based Detect-Fix-Verify Framework implementation

- Full framework implementation with hybrid LLM routing
- CodeLlama 13B local and ChatGPT-4 cloud integration  
- Exploit-based verification system
- Multi-iteration refinement
- Web UI with Streamlit
- Evaluation and benchmarking tools
- Comprehensive documentation
"@

git commit -m $commitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARNING: Commit failed (may be no changes to commit)" -ForegroundColor Yellow
}

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git branch -M main 2>$null
git push -u origin main --force
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to push to GitHub" -ForegroundColor Red
    Write-Host "Make sure you have:"
    Write-Host "  1. Internet connection"
    Write-Host "  2. GitHub credentials configured"
    Write-Host "  3. Access to the repository" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "SUCCESS! Code pushed to GitHub" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Repository URL:" -ForegroundColor Cyan
Write-Host "https://github.com/sherwynjoel/Hybrid-LLM-Based-Detect-Fix-Verify" -ForegroundColor Cyan
Write-Host ""
