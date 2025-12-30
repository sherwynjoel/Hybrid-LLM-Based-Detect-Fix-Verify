d# IntelliJ IDEA Plugin - Hybrid LLM Vulnerability Repair

## Overview

IntelliJ IDEA plugin for real-time vulnerability detection and repair using the Hybrid LLM framework.

## Features

- ✅ **Real-time Analysis**: Analyze files and projects for vulnerabilities
- ✅ **In-Editor Fixes**: Quick fixes directly in the editor
- ✅ **Privacy-First Routing**: Toggle between privacy-first and efficiency-based routing
- ✅ **Multi-Language Support**: Java, Python, JavaScript, TypeScript, C/C++
- ✅ **Tool Window**: View vulnerability results in a dedicated tool window

## Installation

### Prerequisites

1. **IntelliJ IDEA 2023.1 or later** (Community or Ultimate)
2. **IntelliJ Platform SDK** (included with IntelliJ IDEA)
3. **Backend API Server** running (see `ide-integration/backend/`)

### Build from Source

```bash
cd ide-integration/intellij
./gradlew buildPlugin
```

This creates a `.zip` file in `build/distributions/` that can be installed in IntelliJ IDEA.

### Install in IntelliJ IDEA

1. Open IntelliJ IDEA
2. Go to **File → Settings → Plugins**
3. Click **⚙️ → Install Plugin from Disk...**
4. Select the `.zip` file from `build/distributions/`
5. Restart IntelliJ IDEA

## Usage

### Analyze File

1. Right-click on a file in the project tree
2. Select **Tools → Analyze File for Vulnerabilities**
3. Or use keyboard shortcut: `Ctrl+Alt+A`

### Analyze Project

1. Go to **Tools → Analyze Project**
2. The plugin will scan all supported files in your project
3. Results appear in the **Hybrid LLM Vulnerabilities** tool window

### Toggle Privacy Mode

1. Go to **Tools → Toggle Privacy-First Mode**
2. When enabled:
   - Sensitive code → Local LLM
   - Normal code → Cloud LLM

### View Results

1. Open the **Hybrid LLM Vulnerabilities** tool window (View → Tool Windows)
2. See all detected vulnerabilities with:
   - Line number
   - Vulnerability type
   - Severity (Critical/High/Medium/Low)
   - CWE identifier
   - Description

## Configuration

The plugin connects to the backend API at `http://localhost:8501/api` by default.

To change the API URL:
1. Go to **File → Settings → Tools → Hybrid LLM**
2. Set the **API URL** field

## Development

### Project Structure

```
intellij/
├── src/main/java/com/hybridllm/
│   ├── actions/          # Menu actions
│   ├── api/              # API client
│   ├── inspection/       # Code inspections
│   ├── intention/        # Quick fixes
│   ├── model/            # Data models
│   └── ui/               # UI components
├── build.gradle          # Build configuration
└── plugin.xml            # Plugin manifest
```

### Build Commands

```bash
# Build plugin
./gradlew buildPlugin

# Run tests
./gradlew test

# Run plugin in sandbox
./gradlew runIde
```

## Troubleshooting

### Plugin Not Loading

- Check IntelliJ IDEA version (requires 2023.1+)
- Check IntelliJ Platform SDK is configured
- View logs: **Help → Show Log in Files**

### Cannot Connect to API

- Ensure backend API is running: `python ide-integration/backend/api_server.py`
- Check API URL in settings
- Verify firewall/network settings

### No Vulnerabilities Found

- Ensure file is supported (Java, Python, JS, TS, C/C++)
- Check backend API is responding
- View API logs for errors

## Support

For issues and questions:
- GitHub: https://github.com/sherwynjoel/Hybrid-LLM-Based-Detect-Fix-Verify
- Check `ide-integration/README.md` for general IDE integration info

