# IDE Integration: VS Code, PyCharm, IntelliJ

## 🎯 Overview

IDE plugins for real-time vulnerability detection and repair in your favorite IDE.

---

## 📦 Components

### 1. **VS Code Extension**
- Real-time analysis
- In-editor fixes
- Code actions
- Workspace analysis

### 2. **PyCharm Plugin**
- IntelliJ-based plugin
- Python-focused
- Real-time inspections

### 3. **IntelliJ Plugin**
- Java-focused
- Full IntelliJ platform support

### 4. **Backend API Server**
- RESTful API for all IDE plugins
- Unified backend service

---

## 🚀 Quick Start

### Step 1: Start Backend API Server

```bash
# Install dependencies
pip install flask flask-cors

# Start API server
python ide-integration/backend/api_server.py
```

Server runs on: `http://localhost:8501/api`

### Step 2: Install IDE Plugin

#### VS Code:
```bash
cd ide-integration/vscode
npm install
npm run compile
# Press F5 to launch extension
```

#### PyCharm/IntelliJ:
- Build plugin using IntelliJ SDK
- Install from disk

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

### VS Code Settings

```json
{
  "hybridLLM.enable": true,
  "hybridLLM.privacyFirstMode": true,
  "hybridLLM.apiUrl": "http://localhost:8501/api",
  "hybridLLM.autoFix": false
}
```

### PyCharm/IntelliJ Settings

- File → Settings → Tools → Hybrid LLM
- Configure API URL
- Enable/disable features

---

## 📖 Usage

### VS Code

1. **Analyze File**: 
   - Command Palette (Ctrl+Shift+P) → "Analyze File for Vulnerabilities"
   
2. **Fix Vulnerability**:
   - Hover over diagnostic
   - Click "Quick Fix" or press Ctrl+.
   - Select fix option

3. **Analyze Workspace**:
   - Command Palette → "Analyze Workspace"

### PyCharm

1. **Analyze File**:
   - Tools → Analyze File for Vulnerabilities
   - Or Ctrl+Alt+A

2. **Fix Vulnerability**:
   - Alt+Enter on highlighted code
   - Select "Fix vulnerability"

### IntelliJ

1. **Analyze File**:
   - Tools → Analyze File for Vulnerabilities

2. **Fix Vulnerability**:
   - Alt+Enter → Quick fix

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

---

## 🛠️ Development

### VS Code Extension

```bash
cd ide-integration/vscode
npm install
npm run compile
npm run watch  # For development
```

### Backend API

```bash
cd ide-integration/backend
pip install -r requirements.txt
python api_server.py
```

---

## 📝 Requirements

- Hybrid LLM Framework running
- Backend API server on port 8501
- Supported languages: Python, JavaScript, TypeScript, Java, C/C++

---

## ✅ Status

- ✅ VS Code Extension: Implemented
- ✅ Backend API: Implemented
- ⚠️ PyCharm Plugin: Structure created (needs IntelliJ SDK)
- ⚠️ IntelliJ Plugin: Structure created (needs IntelliJ SDK)

---

**See individual README files in each IDE folder for detailed setup instructions.**


