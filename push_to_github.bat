@echo off
REM Script to push project to GitHub

echo ========================================
echo Pushing to GitHub Repository
echo ========================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Remove git lock file if exists
if exist "C:\Users\Sherwyn joel\.git\index.lock" (
    echo Removing git lock file...
    del "C:\Users\Sherwyn joel\.git\index.lock"
)

REM Initialize git in project directory if not already done
if not exist ".git" (
    echo Initializing git repository...
    git init
)

REM Set remote URL
echo Setting remote URL...
git remote remove origin 2>nul
git remote add origin https://github.com/sherwynjoel/A-Hybrid-LLM-Based-Detect-Fix-Verify-Framework-for-Automated-Vulnerability-Repair-.git

REM Add all files
echo Adding all files...
git add .

REM Commit
echo Committing changes...
git commit -m "Complete Hybrid LLM-Based Detect-Fix-Verify Framework implementation

- Full framework implementation with hybrid LLM routing
- CodeLlama 13B local and ChatGPT-4 cloud integration
- Exploit-based verification system
- Multi-iteration refinement
- Web UI with Streamlit
- Evaluation and benchmarking tools
- Comprehensive documentation"

REM Push to GitHub
echo Pushing to GitHub...
git branch -M main
git push -u origin main --force

echo.
echo ========================================
echo Done! Check your GitHub repository:
echo https://github.com/sherwynjoel/A-Hybrid-LLM-Based-Detect-Fix-Verify-Framework-for-Automated-Vulnerability-Repair-
echo ========================================
pause

