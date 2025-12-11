Write-Host "Testing Project..." -ForegroundColor Cyan
Write-Host ""

python test_project.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Running Framework Test..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
python test_framework.py

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

