# IDE Integration: PyCharm Plugin

## 🎯 Overview

PyCharm plugin for real-time vulnerability detection and repair in PyCharm IDE.

---

## 📦 Components

### 1. **PyCharm Plugin**
- IntelliJ-based plugin
- Python-focused
- Real-time inspections
- In-editor fixes

### 2. **Backend API Server**
- RESTful API for the PyCharm plugin
- Unified backend service

---

## 🚀 Quick Start

### Step 1: Start Backend API Server

```bash
# Install dependencies
cd ide-integration/backend
pip install -r requirements.txt
# Also install main project requirements
cd ../..
pip install -r requirements.txt

# Start API server
python ide-integration/backend/api_server.py
```

Server runs on: `http://localhost:8502/api` (port 8502 to avoid conflict with Streamlit UI on 8501)

### Step 2: Install PyCharm Plugin

1. **Build the plugin**:
   ```bash
   cd ide-integration/pycharm
   ./gradlew buildPlugin
   ```

2. **Install in PyCharm**:
   - File → Settings → Plugins
   - Click the gear icon → Install Plugin from Disk
   - Select the JAR file from `ide-integration/pycharm/build/distributions/`
   - Restart PyCharm

---

## 📋 Features

### Real-Time Analysis
- ✅ Automatically detects vulnerabilities as you type
- ✅ Shows inline diagnostics
- ✅ Highlights vulnerable code

### In-Editor Fixes
- ✅ Quick fix suggestions
- ✅ One-click fix application
- ✅ Diff view for review

### Workspace Analysis
- ✅ Analyze entire project
- ✅ Batch processing
- ✅ Comprehensive reports

### Privacy-First Mode
- ✅ Toggle privacy-first routing
- ✅ Sensitive code stays local
- ✅ Normal code uses cloud

---

## 🔧 Configuration

### PyCharm Settings

- File → Settings → Tools → Hybrid LLM
- Configure API URL (default: `http://localhost:8502/api`)
- Enable/disable features
- Toggle privacy-first mode

---

## 📖 Usage

### PyCharm

1. **Analyze File**:
   - Tools → Analyze File for Vulnerabilities
   - Or use keyboard shortcut: `Ctrl+Alt+A`

2. **Analyze Project**:
   - Tools → Analyze Project for Vulnerabilities
   - Analyzes all supported files in the project

3. **Fix Vulnerability**:
   - Place cursor on vulnerable code
   - Press `Alt+Enter` (or click the lightbulb icon)
   - Select "Fix vulnerability"
   - Review the fix in diff view
   - Apply if satisfied

4. **Toggle Privacy Mode**:
   - Tools → Toggle Privacy-First Mode
   - Switches between privacy-first and efficiency modes

---

## 🔌 API Endpoints

### POST `/api/analyze`
Analyze code for vulnerabilities

**Request**:
```json
{
  "code": "def get_user(user_id):\n    query = \"SELECT * FROM users WHERE id = \" + user_id",
  "language": "python",
  "privacy_first_mode": true
}
```

**Response**:
```json
{
  "success": true,
  "vulnerabilities": [
    {
      "type": "SQL Injection",
      "severity": "HIGH",
      "line": 2,
      "message": "SQL injection vulnerability",
      "cwe": "CWE-89",
      "fix_available": true
    }
  ],
  "total": 1
}
```

### POST `/api/fix`
Generate fix for vulnerability

**Request**:
```json
{
  "code": "...",
  "vulnerability": {...},
  "language": "python"
}
```

**Response**:
```json
{
  "success": true,
  "fixed_code": "...",
  "model_used": "chatgpt-4",
  "routing_decision": {...}
}
```

### GET `/api/status`
Get framework status

**Response**:
```json
{
  "codellama_available": true,
  "chatgpt_available": true,
  "privacy_first_mode": true
}
```

### POST `/api/analyze-file`
Analyze file from path

**Request**:
```json
{
  "file_path": "/path/to/file.py"
}
```

---

## 🛠️ Development

### Building the Plugin

```bash
cd ide-integration/pycharm
./gradlew buildPlugin
```

The plugin JAR will be created in `build/distributions/`

### Backend API

```bash
cd ide-integration/backend
pip install -r requirements.txt
python api_server.py
```

---

## 📝 Requirements

- PyCharm IDE (2020.3 or later)
- Hybrid LLM Framework running
- Backend API server on port 8502 (Streamlit UI uses 8501)
- Supported languages: Python, JavaScript, TypeScript, Java, C/C++

---

## ✅ Status

- ✅ PyCharm Plugin: Implemented
- ✅ Backend API: Implemented

---

**See `pycharm/README.md` for detailed setup instructions.**
