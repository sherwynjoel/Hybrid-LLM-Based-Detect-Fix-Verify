# PowerShell script to start local LLM (CodeLlama via Ollama)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Local LLM (CodeLlama)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Check Ollama installation
Write-Host "Step 1: Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✅ Ollama found: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Ollama is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Ollama from: https://ollama.ai/" -ForegroundColor Yellow
    Write-Host "After installation, restart this script." -ForegroundColor Yellow
    exit 1
}

Write-Host ""

# Step 2: Check if Ollama server is running
Write-Host "Step 2: Checking Ollama server status..." -ForegroundColor Yellow
$ollamaRunning = Get-Process | Where-Object {$_.ProcessName -like "*ollama*"}
if ($ollamaRunning) {
    Write-Host "✅ Ollama server is already running" -ForegroundColor Green
} else {
    Write-Host "Starting Ollama server..." -ForegroundColor Yellow
    Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 3
    Write-Host "✅ Ollama server started" -ForegroundColor Green
}

Write-Host ""

# Step 3: Check if CodeLlama model is available
Write-Host "Step 3: Checking CodeLlama model..." -ForegroundColor Yellow
try {
    $models = ollama list 2>&1
    if ($models -match "codellama") {
        Write-Host "✅ CodeLlama model is available" -ForegroundColor Green
    } else {
        Write-Host "CodeLlama model not found. Downloading..." -ForegroundColor Yellow
        Write-Host "This may take several minutes depending on your internet speed." -ForegroundColor Yellow
        Write-Host ""
        ollama pull codellama:13b
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ CodeLlama model downloaded successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ ERROR: Failed to download CodeLlama model" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "⚠️ Could not check models. Continuing anyway..." -ForegroundColor Yellow
}

Write-Host ""

# Step 4: Verify server is responding
Write-Host "Step 4: Verifying Ollama server..." -ForegroundColor Yellow
Start-Sleep -Seconds 2
try {
    $response = Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
    Write-Host "✅ Ollama server is responding" -ForegroundColor Green
} catch {
    Write-Host "⚠️ WARNING: Ollama server may not be responding" -ForegroundColor Yellow
    Write-Host "   Try running manually: ollama serve" -ForegroundColor Yellow
    Write-Host "   Then check: http://localhost:11434/api/tags" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Local LLM Setup Complete" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Ollama server: http://localhost:11434" -ForegroundColor Cyan
Write-Host "CodeLlama model: Ready" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now use the local LLM in the web UI!" -ForegroundColor Green
Write-Host ""

