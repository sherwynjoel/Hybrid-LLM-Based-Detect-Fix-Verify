# Setup CodeLlama (Ollama)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up CodeLlama 13B (Local)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Ollama is installed
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✅ Ollama is installed" -ForegroundColor Green
    Write-Host "   Version: $ollamaVersion" -ForegroundColor White
    Write-Host ""
    
    # Check if CodeLlama model exists
    Write-Host "Checking for CodeLlama model..." -ForegroundColor Yellow
    $models = ollama list 2>&1
    
    if ($models -match "codellama") {
        Write-Host "✅ CodeLlama model found!" -ForegroundColor Green
    } else {
        Write-Host "❌ CodeLlama model not found" -ForegroundColor Red
        Write-Host ""
        Write-Host "Downloading CodeLlama 13B model..." -ForegroundColor Yellow
        Write-Host "This may take several minutes (model is ~7GB)..." -ForegroundColor Yellow
        Write-Host ""
        
        $download = Read-Host "Download now? (Y/N)"
        if ($download -eq "Y" -or $download -eq "y") {
            Write-Host ""
            Write-Host "Running: ollama pull codellama:13b" -ForegroundColor Yellow
            ollama pull codellama:13b
            Write-Host ""
            Write-Host "✅ CodeLlama setup complete!" -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "To download manually, run:" -ForegroundColor Yellow
            Write-Host "  ollama pull codellama:13b" -ForegroundColor White
        }
    }
    
} catch {
    Write-Host "❌ Ollama is not installed" -ForegroundColor Red
    Write-Host ""
    Write-Host "To install Ollama:" -ForegroundColor Yellow
    Write-Host "1. Download from: https://ollama.ai" -ForegroundColor White
    Write-Host "2. Install the Windows version"
    Write-Host "3. Run this script again"
    Write-Host ""
    Write-Host "Or install via winget:" -ForegroundColor Yellow
    Write-Host "  winget install Ollama.Ollama" -ForegroundColor White
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

