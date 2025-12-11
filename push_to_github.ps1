# PowerShell script to push project to GitHub

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Pushing to GitHub Repository" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "Current directory: $scriptPath" -ForegroundColor Yellow

# Check if .git exists in project directory
if (-not (Test-Path ".git")) {
    Write-Host "Initializing git repository in project directory..." -ForegroundColor Yellow
    git init
}

# Remove lock file if exists
$lockFile = "$env:USERPROFILE\.git\index.lock"
if (Test-Path $lockFile) {
    Write-Host "Removing git lock file..." -ForegroundColor Yellow
    Remove-Item $lockFile -Force
}

# Set remote URL
Write-Host "Setting remote URL..." -ForegroundColor Yellow
git remote remove origin 2>$null
git remote add origin https://github.com/sherwynjoel/Hybrid-LLM-Based-Detect-Fix-Verify.git

# Add all files
Write-Host "Adding all files..." -ForegroundColor Yellow
git add .

# Commit
Write-Host "Committing changes..." -ForegroundColor Yellow
git commit -m "Complete Hybrid LLM-Based Detect-Fix-Verify Framework implementation

- Full framework implementation with hybrid LLM routing
- CodeLlama 13B local and ChatGPT-4 cloud integration  
- Exploit-based verification system
- Multi-iteration refinement
- Web UI with Streamlit
- Evaluation and benchmarking tools
- Comprehensive documentation"

# Push to GitHub
Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
git branch -M main
git push -u origin main --force

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Done! Check your GitHub repository:" -ForegroundColor Green
Write-Host "https://github.com/sherwynjoel/Hybrid-LLM-Based-Detect-Fix-Verify" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green
