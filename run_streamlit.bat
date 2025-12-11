@echo off
REM Run Streamlit UI using python -m (avoids PATH issues)

echo Starting Hybrid LLM Vulnerability Repair Framework Web UI...
echo.

REM Change to script directory
cd /d "%~dp0"

REM Run using python -m streamlit (works even if streamlit not in PATH)
python -m streamlit run ui/app.py

pause

