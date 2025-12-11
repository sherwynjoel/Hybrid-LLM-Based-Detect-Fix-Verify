# Setup Guide

## Prerequisites

- Python 3.9 or higher
- pip package manager
- Git (for cloning repository)

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "A Hybrid LLM-Based Detect–Fix–Verify"
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Static Analysis Tools

#### Bandit (Python)
```bash
pip install bandit
```

#### Semgrep
```bash
pip install semgrep
# Or use: python -m pip install semgrep
```

### 5. Setup Local LLM (CodeLlama 13B)

#### Option A: Using Ollama (Recommended)

1. Install Ollama from https://ollama.ai
2. Pull CodeLlama model:
```bash
ollama pull codellama:13b
```

3. Verify installation:
```bash
ollama list
```

#### Option B: Using Transformers

The framework will automatically use Transformers if Ollama is not available. Ensure you have sufficient GPU memory (16GB+ recommended).

### 6. Setup Cloud LLM (ChatGPT-4)

1. Get OpenAI API key from https://platform.openai.com
2. Set environment variable:
```bash
# On Windows
set OPENAI_API_KEY=your-api-key-here

# On Linux/Mac
export OPENAI_API_KEY=your-api-key-here
```

Or create a `.env` file:
```
OPENAI_API_KEY=your-api-key-here
```

### 7. Configure Framework

Edit `config.yaml` to customize:
- Router thresholds
- Refinement settings
- Verification settings
- Performance parameters

## Verification

### Test Installation

```bash
python -c "from src.main import VulnerabilityRepairFramework; print('Installation successful!')"
```

### Test CodeLlama (if using Ollama)

```bash
ollama run codellama:13b "Write a hello world program in Python"
```

### Test ChatGPT API

```bash
python -c "from src.llm_models.chatgpt_cloud import ChatGPTCloud; print('ChatGPT API configured!')"
```

## Usage Examples

### Basic Usage

```bash
python src/main.py --input vulnerable_code.py --language python
```

### With Options

```bash
python src/main.py \
  --input vulnerable_code.py \
  --language python \
  --output results.json \
  --verbose
```

### Run Benchmarks

```bash
python evaluation/benchmark_runner.py \
  --dataset datasets/benchmark.json \
  --output results.json
```

## Troubleshooting

### CodeLlama Not Available

- Ensure Ollama is running: `ollama serve`
- Check model is installed: `ollama list`
- Verify OLLAMA_URL environment variable if using custom endpoint

### ChatGPT API Errors

- Verify API key is set correctly
- Check API quota and billing
- Ensure internet connection

### Static Analysis Tools Not Found

- Install missing tools: `pip install bandit semgrep`
- Verify tools are in PATH: `bandit --version`

### Import Errors

- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt --force-reinstall`

## Next Steps

- Read [ARCHITECTURE.md](docs/ARCHITECTURE.md) for system design
- Read [API.md](docs/API.md) for API documentation
- Check [README.md](README.md) for project overview

