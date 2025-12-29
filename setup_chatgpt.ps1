# Setup ChatGPT API Key

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setting up ChatGPT-4 API Key" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "To use ChatGPT-4, you need an OpenAI API key." -ForegroundColor Yellow
Write-Host ""
Write-Host "Steps:" -ForegroundColor Green
Write-Host "1. Go to: https://platform.openai.com/api-keys" -ForegroundColor White
Write-Host "2. Sign up or log in"
Write-Host "3. Create a new API key"
Write-Host "4. Copy your API key"
Write-Host ""

$apiKey = Read-Host "Enter your OpenAI API key (or press Enter to skip)"

if ($apiKey) {
    # Set for current session
    $env:OPENAI_API_KEY = $apiKey
    Write-Host ""
    Write-Host "✅ API key set for this session" -ForegroundColor Green
    Write-Host ""
    Write-Host "To make it permanent, add this to your PowerShell profile:" -ForegroundColor Yellow
    Write-Host '  $env:OPENAI_API_KEY = "your-key-here"' -ForegroundColor White
    Write-Host ""
    Write-Host "Or set it in Windows Environment Variables:" -ForegroundColor Yellow
    Write-Host "  System Properties > Environment Variables > New" -ForegroundColor White
} else {
    Write-Host ""
    Write-Host "⚠️  No API key entered. ChatGPT will not be available." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

