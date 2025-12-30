# PowerShell script to compile LaTeX paper to PDF
# Requires: MiKTeX or TeX Live installation

Write-Host "Compiling LaTeX paper to PDF..." -ForegroundColor Green

# Check if pdflatex is available
$pdflatex = Get-Command pdflatex -ErrorAction SilentlyContinue

if (-not $pdflatex) {
    Write-Host "ERROR: pdflatex not found!" -ForegroundColor Red
    Write-Host "Please install MiKTeX (Windows) or TeX Live" -ForegroundColor Yellow
    Write-Host "Download MiKTeX from: https://miktex.org/download" -ForegroundColor Yellow
    exit 1
}

# Get current directory
$currentDir = Get-Location

# Compile LaTeX (run twice for references)
Write-Host "First compilation pass..." -ForegroundColor Cyan
& pdflatex -interaction=nonstopmode -output-directory=$currentDir research_paper.tex | Out-Null

Write-Host "Second compilation pass (for references)..." -ForegroundColor Cyan
& pdflatex -interaction=nonstopmode -output-directory=$currentDir research_paper.tex | Out-Null

# Check if PDF was created
if (Test-Path "research_paper.pdf") {
    $pdfSize = (Get-Item "research_paper.pdf").Length / 1MB
    Write-Host "SUCCESS! PDF generated: research_paper.pdf" -ForegroundColor Green
    Write-Host "File size: $([math]::Round($pdfSize, 2)) MB" -ForegroundColor Green
    Write-Host "Opening PDF..." -ForegroundColor Cyan
    Start-Process "research_paper.pdf"
} else {
    Write-Host "ERROR: PDF generation failed. Check research_paper.log for errors." -ForegroundColor Red
    exit 1
}

