# Quick Start Guide

## Installation

### 1. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 2. Install Streamlit (for Web UI)

```powershell
pip install streamlit
```

Or install from UI requirements:

```powershell
pip install -r ui/requirements.txt
```

## Running the Framework

### Option 1: Command Line Interface (CLI)

```powershell
# Basic usage
python src/main.py --input vulnerable_code.py --language python

# With options
python src/main.py --input vulnerable_code.py --language python --output results.json --verbose
```

### Option 2: Web User Interface

```powershell
streamlit run ui/app.py
```

The UI will open in your browser at `http://localhost:8501`

### Option 3: Example Script

```powershell
# Make sure you're in the project root directory
python examples/example_usage.py
```

## Common Issues & Solutions

### Issue 1: ModuleNotFoundError: No module named 'src'

**Solution**: Make sure you're running from the project root directory:

```powershell
# Check current directory
pwd

# Navigate to project root if needed
cd "C:\Users\Sherwyn joel\OneDrive\Desktop\FINAL SEM PROJECT\A Hybrid LLM-Based Detect–Fix–Verify"
```

### Issue 2: streamlit not recognized

**Solution**: Install streamlit:

```powershell
pip install streamlit
```

### Issue 3: OpenAI API Key Error

**Solution**: Set the environment variable (optional - framework works without it):

```powershell
# PowerShell
$env:OPENAI_API_KEY = "your-api-key-here"

# Or create .env file in project root:
# OPENAI_API_KEY=your-api-key-here
```

### Issue 4: CodeLlama Not Available

**Solution**: Install Ollama and pull the model (optional):

```powershell
# Download Ollama from https://ollama.ai
# Then run:
ollama pull codellama:13b
```

## Testing the Framework

### Quick Import Test

```powershell
python -c "from src.main import VulnerabilityRepairFramework; print('✅ Imports work!')"
```

### Test Basic Functionality

```powershell
python test_framework.py
```

### Test with Sample Code

Create a test file `test_vuln.py`:

```python
import sqlite3

def get_user(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()
```

Then run:

```powershell
python src/main.py --input test_vuln.py --language python
```

## Project Structure

```
A Hybrid LLM-Based Detect–Fix–Verify/
├── src/                    # Main source code
├── ui/                     # Web UI (Streamlit)
├── examples/               # Example scripts
├── evaluation/             # Evaluation tools
├── datasets/               # Benchmark datasets
└── docs/                   # Documentation
```

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Install Streamlit**: `pip install streamlit` (for web UI)
3. **Test imports**: `python -c "from src.main import VulnerabilityRepairFramework; print('✅')"`
4. **Run web UI**: `streamlit run ui/app.py`
5. **Or use CLI**: `python src/main.py --input file.py --language python`

## Need Help?

- See `SETUP.md` for detailed setup instructions
- See `docs/API.md` for API documentation
- See `docs/ARCHITECTURE.md` for system architecture
- See `STATUS_CHECK.md` for component status

