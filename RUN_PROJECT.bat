@echo off
echo ========================================
echo Starting Hybrid LLM Framework
echo ========================================
echo.

echo Checking Python installation...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Starting Streamlit Web UI...
echo.
echo The web UI will open in your browser at:
echo   http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

python -m streamlit run ui/app.py

pause


