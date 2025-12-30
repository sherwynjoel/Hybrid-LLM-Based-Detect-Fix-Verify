# PowerShell script to stop LLM services

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Stopping LLM Services" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Stop Ollama processes
Write-Host "Stopping Ollama server..." -ForegroundColor Yellow
$ollamaProcesses = Get-Process | Where-Object {$_.ProcessName -like "*ollama*"}
if ($ollamaProcesses) {
    $ollamaProcesses | Stop-Process -Force
    Write-Host "✅ Ollama server stopped successfully" -ForegroundColor Green
    Write-Host "   Stopped $($ollamaProcesses.Count) process(es)" -ForegroundColor White
} else {
    Write-Host "ℹ️ Ollama server was not running" -ForegroundColor Yellow
}

Write-Host ""

# Stop Streamlit (if running)
Write-Host "Checking for Streamlit processes..." -ForegroundColor Yellow
$streamlitProcesses = Get-Process | Where-Object {
    $_.ProcessName -eq "python" -and 
    $_.CommandLine -like "*streamlit*"
} -ErrorAction SilentlyContinue

if ($streamlitProcesses) {
    $streamlitProcesses | Stop-Process -Force
    Write-Host "✅ Streamlit stopped successfully" -ForegroundColor Green
} else {
    Write-Host "ℹ️ Streamlit was not running" -ForegroundColor Yellow
}

Write-Host ""

# Verify all stopped
Write-Host "Verifying..." -ForegroundColor Yellow
$remainingOllama = Get-Process | Where-Object {$_.ProcessName -like "*ollama*"} -ErrorAction SilentlyContinue
if ($remainingOllama) {
    Write-Host "⚠️ Warning: Some Ollama processes may still be running" -ForegroundColor Yellow
    Write-Host "   Process IDs: $($remainingOllama.Id -join ', ')" -ForegroundColor White
} else {
    Write-Host "✅ All LLM services stopped successfully" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "LLM Services Stopped" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""


