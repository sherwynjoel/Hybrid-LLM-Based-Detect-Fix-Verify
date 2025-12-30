# 🚀 Quick Start Guide

## Running the Project

### Method 1: Batch Script (Easiest)
```batch
.\RUN_PROJECT.bat
```

### Method 2: PowerShell Script
```powershell
.\RUN_PROJECT.ps1
```

### Method 3: Manual Command
```bash
python -m streamlit run ui/app.py
```

---

## 🌐 Access the Web UI

Once started, the web UI will be available at:

**http://localhost:8501**

The browser should open automatically. If not, copy the URL above into your browser.

---

## 📋 Prerequisites

### Required:
- ✅ Python 3.9+ (You have Python 3.13.6 ✅)
- ✅ All dependencies installed (`pip install -r requirements.txt`)

### Optional (for full functionality):
- **Ollama** (for local LLM - CodeLlama 13B)
  - Install: https://ollama.ai/
  - Start: `ollama serve`
  - Pull model: `ollama pull codellama:13b`

- **OpenAI API Key** (for cloud LLM - ChatGPT-4)
  - Get key: https://platform.openai.com/api-keys
  - Set: `$env:OPENAI_API_KEY = "your-key-here"`

---

## 🎯 Using the Web UI

1. **Upload Code**: Paste code or upload a file
2. **Select Language**: Choose Python, Java, JavaScript, etc.
3. **Configure Options**:
   - Enable Privacy-First Routing (toggle)
   - Enable Multi-iteration Refinement
   - Enable Exploit-based Verification
4. **Analyze**: Click "Analyze Code"
5. **View Results**: See detected vulnerabilities
6. **Get Fixes**: Download fixed code with explanations

---

## 🛑 Stopping the Project

Press **Ctrl+C** in the terminal, or close the terminal window.

To stop LLM services:
```batch
.\STOP_LLM.bat
```

---

## 🔧 Troubleshooting

### Port Already in Use
If port 8501 is busy:
```bash
streamlit run ui/app.py --server.port 8502
```

### LLM Not Available
- **CodeLlama**: Make sure Ollama is running (`ollama serve`)
- **ChatGPT-4**: Set `OPENAI_API_KEY` environment variable

### Dependencies Missing
```bash
pip install -r requirements.txt
```

---

## 📚 Next Steps

- Read `RUN_PROJECT.md` for detailed instructions
- Check `PROJECT_COMPLETION_STATUS.md` for all features
- See `ide-integration/README.md` for IDE plugins

---

**Enjoy using the Hybrid LLM Vulnerability Repair Framework!** 🎉


