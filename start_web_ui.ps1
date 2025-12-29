Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Web UI" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Starting Streamlit web interface..." -ForegroundColor Yellow
Write-Host "The browser will open automatically at http://localhost:8501" -ForegroundColor Green
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m streamlit run ui/app.py

