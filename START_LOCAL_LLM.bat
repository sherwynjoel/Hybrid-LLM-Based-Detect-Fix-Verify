@echo off
echo ========================================
echo Starting Local LLM (CodeLlama)
echo ========================================
echo.

echo Step 1: Checking Ollama installation...
ollama --version
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Ollama is not installed!
    echo.
    echo Please install Ollama from: https://ollama.ai/
    echo After installation, restart this script.
    pause
    exit /b 1
)

echo.
echo Step 2: Starting Ollama server...
start /B ollama serve
timeout /t 3 /nobreak >nul

echo.
echo Step 3: Checking if CodeLlama model is available...
ollama list | findstr /I "codellama"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo CodeLlama model not found. Downloading...
    echo This may take several minutes depending on your internet speed.
    echo.
    ollama pull codellama:13b
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Failed to download CodeLlama model
        pause
        exit /b 1
    )
)

echo.
echo Step 4: Verifying Ollama server is running...
timeout /t 2 /nobreak >nul
curl -s http://localhost:11434/api/tags >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Local LLM is running
    echo ========================================
    echo.
    echo Ollama server: http://localhost:11434
    echo CodeLlama model: Ready
    echo.
    echo You can now use the local LLM in the web UI!
) else (
    echo.
    echo WARNING: Ollama server may not be responding
    echo Try running: ollama serve
    echo Then check: http://localhost:11434/api/tags
)

echo.
pause

