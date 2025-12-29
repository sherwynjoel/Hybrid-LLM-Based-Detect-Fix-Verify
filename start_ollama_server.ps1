# Start Ollama Server for Framework

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Ollama Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Ollama server is already running
Write-Host "Checking if Ollama server is running..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "[OK] Ollama server is already running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "CodeLlama should now be available in the framework." -ForegroundColor Green
    Write-Host "Refresh your web UI page to see the updated status." -ForegroundColor Yellow
    exit 0
} catch {
    Write-Host "[FAIL] Ollama server is not running" -ForegroundColor Red
    Write-Host ""
}

# Start Ollama server
Write-Host "Starting Ollama server..." -ForegroundColor Yellow
Write-Host "This will run in the background." -ForegroundColor Yellow
Write-Host ""

# Try to start Ollama serve
try {
    # Start Ollama in a new window so user can see it
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Normal
    
    Write-Host "Ollama server is starting..." -ForegroundColor Green
    Write-Host "Waiting 5 seconds for it to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    
    # Check if it's running now
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -TimeoutSec 5 -ErrorAction Stop
        Write-Host ""
        Write-Host "[SUCCESS] Ollama server is now running!" -ForegroundColor Green
        Write-Host ""
        
        # Check for CodeLlama model
        $models = ($response.Content | ConvertFrom-Json).models
        $codellama = $models | Where-Object { $_.name -like "*codellama*" }
        
        if ($codellama) {
            Write-Host "[OK] CodeLlama model found: $($codellama.name)" -ForegroundColor Green
        } else {
            Write-Host "[WARNING] CodeLlama model not found in server" -ForegroundColor Yellow
            Write-Host "Run: ollama pull codellama:13b" -ForegroundColor Cyan
        }
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "NEXT STEPS" -ForegroundColor Cyan
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "1. Keep the Ollama window open (don't close it)" -ForegroundColor Yellow
        Write-Host "2. Refresh your web UI page (F5)" -ForegroundColor Yellow
        Write-Host "3. CodeLlama should now show as 'Available'" -ForegroundColor Green
        Write-Host ""
        Write-Host "To stop Ollama: Close the Ollama window" -ForegroundColor Gray
        Write-Host "========================================" -ForegroundColor Cyan
        
    } catch {
        Write-Host ""
        Write-Host "[WARNING] Server may still be starting..." -ForegroundColor Yellow
        Write-Host "Wait a few more seconds and check the Ollama window." -ForegroundColor Yellow
        Write-Host ""
        Write-Host "You should see Ollama running in a separate window." -ForegroundColor White
        Write-Host "Keep that window open while using the framework." -ForegroundColor White
    }
    
} catch {
    Write-Host ""
    Write-Host "[FAIL] Could not start Ollama automatically" -ForegroundColor Red
    Write-Host ""
    Write-Host "MANUAL STEPS:" -ForegroundColor Yellow
    Write-Host "1. Open a NEW terminal/PowerShell window" -ForegroundColor White
    Write-Host "2. Run this command:" -ForegroundColor White
    Write-Host "   ollama serve" -ForegroundColor Cyan
    Write-Host "3. Keep that window open" -ForegroundColor White
    Write-Host "4. Refresh your web UI page" -ForegroundColor White
}

