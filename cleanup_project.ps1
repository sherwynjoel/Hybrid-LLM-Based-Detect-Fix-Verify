# Cleanup Project - Remove Unnecessary Files
# This script removes ~95 unnecessary files

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Project Cleanup - Removing Unnecessary Files" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$deletedCount = 0
$errors = 0

# Function to safely delete files
function Remove-FileSafely {
    param($FilePath, $Description)
    try {
        if (Test-Path $FilePath) {
            Remove-Item $FilePath -Force -ErrorAction Stop
            Write-Host "  [OK] Deleted: $Description" -ForegroundColor Green
            $script:deletedCount++
            return $true
        }
    } catch {
        Write-Host "  [ERROR] Failed to delete: $Description" -ForegroundColor Red
        $script:errors++
        return $false
    }
    return $false
}

# Function to safely delete multiple files
function Remove-FilesSafely {
    param($Pattern, $Description)
    $files = Get-ChildItem -File -Include $Pattern -ErrorAction SilentlyContinue
    if ($files) {
        Write-Host "  Deleting $($files.Count) $Description..." -ForegroundColor Yellow
        foreach ($file in $files) {
            Remove-FileSafely $file.FullName $file.Name
        }
    }
}

Write-Host "[1/6] Deleting test files..." -ForegroundColor Yellow
Remove-FilesSafely "test_*.py" "test files"
Remove-FilesSafely "verify_*.py" "verify files"
Remove-FileSafely "test_input.bat" "test input batch"
Remove-FileSafely "test_input.ps1" "test input script"

Write-Host ""
Write-Host "[2/6] Deleting fix/troubleshooting files..." -ForegroundColor Yellow
Remove-FilesSafely "FIX_*.md" "fix markdown files"
Remove-FilesSafely "FIX_*.txt" "fix text files"
Remove-FilesSafely "FIX_*.ps1" "fix PowerShell scripts"
Remove-FilesSafely "FIX_*.bat" "fix batch files"
Remove-FilesSafely "QUICK_FIX_*.ps1" "quick fix scripts"
Remove-FilesSafely "QUICK_FIX_*.md" "quick fix markdown"
Remove-FileSafely "fix_model_detection.py" "fix model detection"
Remove-FileSafely "fix_ollama_port.ps1" "fix ollama port"
Remove-FileSafely "MANUAL_FIX_INSTRUCTIONS.md" "manual fix instructions"
Remove-FileSafely "FINAL_INSTRUCTIONS.txt" "final instructions"
Remove-FileSafely "SIMPLE_CODELLAMA_FIX.txt" "simple codellama fix"
Remove-FileSafely "CODELLAMA_FIXED.txt" "codellama fixed"

Write-Host ""
Write-Host "[3/6] Deleting duplicate scripts..." -ForegroundColor Yellow
# Keep: start_web_ui.ps1, start_ollama_server.ps1
Remove-FileSafely "start_web_ui.bat" "duplicate web UI batch"
Remove-FileSafely "start_web_ui_with_port.ps1" "duplicate web UI with port"
Remove-FileSafely "start_ollama.ps1" "duplicate ollama start"
Remove-FileSafely "START_OLLAMA_NOW.bat" "duplicate ollama batch"
Remove-FileSafely "setup_codellama_only.ps1" "duplicate codellama setup"
Remove-FileSafely "setup.bat" "duplicate setup batch"
Remove-FileSafely "START_CODELLAMA.bat" "duplicate codellama start"
Remove-FileSafely "START_CODELLAMA_NOW.ps1" "duplicate codellama start"
Remove-FileSafely "START_CODELLAMA_FIXED.ps1" "duplicate codellama fixed"
Remove-FileSafely "quick_start_codellama.bat" "duplicate quick start"
Remove-FileSafely "quick_start_codellama.ps1" "duplicate quick start"
Remove-FileSafely "run_streamlit.bat" "duplicate run streamlit"
Remove-FileSafely "run_ui.bat" "duplicate run UI"
Remove-FileSafely "run_example.bat" "duplicate run example"
Remove-FileSafely "run_tests.bat" "duplicate run tests"
Remove-FileSafely "run_tests.ps1" "duplicate run tests"
Remove-FileSafely "push_to_github.bat" "duplicate push to github"
Remove-FileSafely "set_ollama_port.ps1" "set ollama port"
Remove-FileSafely "DIAGNOSE_AND_FIX.bat" "diagnose and fix"
Remove-FileSafely "FIX_NOW.bat" "fix now batch"
Remove-FileSafely "analyze_sample.bat" "analyze sample batch"
Remove-FileSafely "analyze_sample.ps1" "analyze sample script"
Remove-FileSafely "quick_test.bat" "quick test batch"
Remove-FileSafely "quick_test.ps1" "quick test script"

Write-Host ""
Write-Host "[4/6] Deleting analysis/documentation files..." -ForegroundColor Yellow
Remove-FileSafely "PROJECT_ANALYSIS.md" "project analysis"
Remove-FileSafely "FILE_STRUCTURE_ANALYSIS.md" "file structure analysis"
Remove-FileSafely "ANALYSIS_SUMMARY.md" "analysis summary"
Remove-FileSafely "WHY_ITS_DIFFICULT.md" "why its difficult"
Remove-FileSafely "MAKE_IT_EASIER.md" "make it easier"
Remove-FileSafely "PROJECT_STRUCTURE.md" "project structure"
Remove-FileSafely "PROJECT_SUMMARY.md" "project summary"
Remove-FileSafely "STRUCTURE_SUMMARY.md" "structure summary"
Remove-FileSafely "REQUIRED_FILES.md" "required files"
Remove-FileSafely "WHAT_YOU_NEED.md" "what you need"
Remove-FileSafely "UNNECESSARY_FILES_LIST.md" "unnecessary files list"
Remove-FileSafely "FILES_TO_DELETE.md" "files to delete"
Remove-FileSafely "CHATGPT_SPEED_COMPARISON.txt" "chatgpt speed comparison"
Remove-FileSafely "CODELLAMA_SETUP_GUIDE.txt" "codellama setup guide"
Remove-FileSafely "FINAL_SETUP_COMPLETE.txt" "final setup complete"
Remove-FileSafely "HOW_TO_USE_INPUT.txt" "how to use input"
Remove-FileSafely "HOW_VULNERABILITY_DETECTION_WORKS.txt" "how vulnerability detection works"
Remove-FileSafely "SIMPLE_START_GUIDE.txt" "simple start guide"
Remove-FileSafely "SPEED_UP_ANALYSIS.txt" "speed up analysis"
Remove-FileSafely "START_CODELLAMA.txt" "start codellama text"
Remove-FileSafely "QUICK_START_CODELLAMA.md" "quick start codellama"
Remove-FileSafely "QUICK_START.md" "quick start"
Remove-FileSafely "FINAL_SOLUTION.md" "final solution"

Write-Host ""
Write-Host "[5/6] Deleting example/utility files..." -ForegroundColor Yellow
Remove-FileSafely "command_injection.py" "command injection example"
Remove-FileSafely "sql_injection.py" "sql injection example"
Remove-FileSafely "hardcoded_creds.py" "hardcoded creds example"
Remove-FileSafely "weak_crypto.py" "weak crypto example"
Remove-FileSafely "xss.py" "xss example"
Remove-FileSafely "analyze_sample_vulnerabilities.py" "analyze sample vulnerabilities"
Remove-FileSafely "fast_analysis.py" "fast analysis"
Remove-FileSafely "how_to_input.py" "how to input"
Remove-FileSafely "quick_input_example.py" "quick input example"
Remove-FileSafely "quick_test_files.py" "quick test files"

Write-Host ""
Write-Host "[6/6] Deleting temporary files..." -ForegroundColor Yellow
if (Test-Path "temp") {
    Remove-Item -Recurse -Force "temp" -ErrorAction SilentlyContinue
    Write-Host "  [OK] Deleted: temp/ directory" -ForegroundColor Green
    $deletedCount++
}

# Delete Python cache (will regenerate automatically)
Get-ChildItem -Recurse -Directory -Filter "__pycache__" -ErrorAction SilentlyContinue | ForEach-Object {
    Remove-Item $_.FullName -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "  [OK] Deleted: $($_.FullName)" -ForegroundColor Green
    $deletedCount++
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Cleanup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Files deleted: $deletedCount" -ForegroundColor Green
if ($errors -gt 0) {
    Write-Host "Errors: $errors" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "Project is now cleaner!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan

