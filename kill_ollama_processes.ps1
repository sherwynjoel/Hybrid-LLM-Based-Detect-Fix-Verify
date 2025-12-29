# Kill all Ollama processes to free ports

Write-Host "Stopping all Ollama processes..." -ForegroundColor Yellow

$processes = Get-Process | Where-Object {$_.ProcessName -like "*ollama*"}

if ($processes) {
    foreach ($proc in $processes) {
        Write-Host "Stopping: $($proc.ProcessName) (PID: $($proc.Id))" -ForegroundColor White
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Write-Host "[OK] All Ollama processes stopped" -ForegroundColor Green
    Start-Sleep -Seconds 2
} else {
    Write-Host "[OK] No Ollama processes found" -ForegroundColor Green
}

Write-Host ""
Write-Host "Now you can start Ollama fresh:" -ForegroundColor Yellow
Write-Host "  ollama serve" -ForegroundColor Cyan



