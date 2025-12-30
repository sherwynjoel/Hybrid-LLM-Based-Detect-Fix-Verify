@echo off
echo ========================================
echo Stopping LLM Services
echo ========================================
echo.

echo Stopping Ollama server...
taskkill /F /IM ollama.exe 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Ollama server stopped successfully
) else (
    echo Ollama server was not running
)

echo.
echo Stopping any Python processes running LLM...
taskkill /F /FI "WINDOWTITLE eq *streamlit*" 2>nul
tasklist | findstr /I "python" >nul
if %ERRORLEVEL% EQU 0 (
    echo Warning: Python processes may still be running
    echo Check Task Manager if needed
) else (
    echo No Python processes found
)

echo.
echo ========================================
echo LLM Services Stopped
echo ========================================
echo.
pause


