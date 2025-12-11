@echo off
REM Batch script to run Streamlit UI on Windows

echo Starting Hybrid LLM Vulnerability Repair Framework Web UI...
echo.

REM Change to script directory
cd /d "%~dp0"

REM Check if streamlit is installed
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo Streamlit not found. Installing...
    pip install streamlit
)

REM Run Streamlit (using python -m to avoid PATH issues)
python -m streamlit run ui/app.py

pause

