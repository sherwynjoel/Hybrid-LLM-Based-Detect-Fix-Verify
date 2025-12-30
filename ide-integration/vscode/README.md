# VS Code Extension: Hybrid LLM Vulnerability Repair

## Features

- ✅ **Real-time Analysis**: Automatically detects vulnerabilities as you type
- ✅ **In-Editor Fixes**: Apply fixes directly from the editor
- ✅ **Code Actions**: Quick fix suggestions for vulnerabilities
- ✅ **Workspace Analysis**: Analyze entire workspace
- ✅ **Privacy-First Mode**: Toggle between privacy-first and efficiency modes
- ✅ **Vulnerability Report**: View comprehensive vulnerability reports

## Installation

### From VS Code Marketplace (Coming Soon)
1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "Hybrid LLM Vulnerability Repair"
4. Click Install

### From Source
1. Clone the repository
2. Open terminal in `ide-integration/vscode/`
3. Run `npm install`
4. Run `npm run compile`
5. Press F5 to launch extension in new window

## Configuration

Add to VS Code settings.json:

```json
{
  "hybridLLM.enable": true,
  "hybridLLM.privacyFirstMode": true,
  "hybridLLM.apiUrl": "http://localhost:8501/api",
  "hybridLLM.autoFix": false,
  "hybridLLM.showInlineDiagnostics": true
}
```

## Usage

### Analyze Current File
- Command Palette (Ctrl+Shift+P) → "Analyze File for Vulnerabilities"
- Or use keyboard shortcut (if configured)

### Analyze Workspace
- Command Palette → "Analyze Workspace"
- Analyzes all supported files in workspace

### Fix Vulnerability
1. Hover over vulnerability diagnostic
2. Click "Quick Fix" or press Ctrl+.
3. Select "Fix [Vulnerability Type]"
4. Review fix in diff view
5. Apply if satisfied

### Toggle Privacy Mode
- Command Palette → "Toggle Privacy-First Mode"
- Switches between privacy-first and efficiency modes

## Commands

- `hybridLLM.analyzeFile` - Analyze current file
- `hybridLLM.analyzeWorkspace` - Analyze entire workspace
- `hybridLLM.fixVulnerability` - Fix selected vulnerability
- `hybridLLM.togglePrivacyMode` - Toggle privacy-first mode
- `hybridLLM.showReport` - Show vulnerability report

## Requirements

- Hybrid LLM Framework must be running on configured API URL
- Supported languages: Python, JavaScript, TypeScript, Java, C/C++

## Troubleshooting

### Extension not working
1. Check if framework is running: `http://localhost:8501/api`
2. Verify API URL in settings
3. Check Output panel for errors

### No vulnerabilities detected
1. Ensure file language is supported
2. Check framework logs
3. Verify API connection


