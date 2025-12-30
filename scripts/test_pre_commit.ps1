# Test pre-commit hook

Write-Host "Testing pre-commit hook..." -ForegroundColor Cyan
Write-Host ""

# Test on all files
python -m pre_commit run --all-files

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Pre-commit hook test passed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️ Pre-commit hook found issues" -ForegroundColor Yellow
    Write-Host "This is expected if vulnerabilities are found in your code." -ForegroundColor Yellow
}


