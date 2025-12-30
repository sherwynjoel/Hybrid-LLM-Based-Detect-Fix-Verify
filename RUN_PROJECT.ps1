# PowerShell script to run the Hybrid LLM Framework

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Hybrid LLM Framework" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starting Streamlit Web UI..." -ForegroundColor Yellow
Write-Host ""
Write-Host "The web UI will open in your browser at:" -ForegroundColor Cyan
Write-Host "  http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start Streamlit
python -m streamlit run ui/app.py


