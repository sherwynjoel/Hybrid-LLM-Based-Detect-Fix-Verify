# PowerShell script to setup pre-commit hook

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up Pre-Commit Hook" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if pre-commit is installed
Write-Host "Checking pre-commit installation..." -ForegroundColor Yellow
try {
    $preCommitVersion = python -m pre_commit --version 2>&1
    Write-Host "Pre-commit found: $preCommitVersion" -ForegroundColor Green
} catch {
    Write-Host "Installing pre-commit..." -ForegroundColor Yellow
    python -m pip install pre-commit
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Failed to install pre-commit" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "Installing pre-commit hook..." -ForegroundColor Yellow
python -m pre_commit install

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "✅ Pre-commit hook installed successfully!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "The hook will now run automatically on every commit." -ForegroundColor Cyan
    Write-Host "To test: pre-commit run --all-files" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "ERROR: Failed to install pre-commit hook" -ForegroundColor Red
    exit 1
}


