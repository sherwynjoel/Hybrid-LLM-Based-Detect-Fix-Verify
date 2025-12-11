@echo off
REM Setup script for Windows

echo ========================================
echo Hybrid LLM Vulnerability Repair Framework
echo Setup Script
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

echo [1/3] Installing Python dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo [2/3] Installing Streamlit (for Web UI)...
pip install streamlit
if errorlevel 1 (
    echo WARNING: Failed to install Streamlit. Web UI will not be available.
)

echo.
echo [3/3] Verifying installation...
python -c "from src.main import VulnerabilityRepairFramework; print('✅ Core framework installed successfully!')"
if errorlevel 1 (
    echo ERROR: Framework verification failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run Web UI: run_ui.bat
echo 2. Run Example: run_example.bat
echo 3. Or use CLI: python src/main.py --input file.py --language python
echo.
echo Optional setup:
echo - Install Ollama and CodeLlama: ollama pull codellama:13b
echo - Set OpenAI API key: $env:OPENAI_API_KEY = "your-key"
echo.
pause

