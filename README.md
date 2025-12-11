# Hybrid LLM-Based Detect–Fix–Verify Framework for Automated Vulnerability Repair

A novel hybrid framework that combines local (CodeLlama 13B) and cloud-based (ChatGPT-4) LLMs for automated vulnerability detection, repair, and verification.

## Features

- **Hybrid LLM Architecture**: Intelligent routing between CodeLlama 13B (local) and ChatGPT-4 (cloud)
- **Exploit-Based Verification**: PoC exploit generation and testing to validate repairs
- **Multi-Iteration Refinement**: Adaptive feedback loops for improved fix quality
- **Multi-Language Support**: Python, C/C++, Java with language-specific optimizations
- **Performance Optimization**: Parallel processing, caching, and intelligent model selection

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Set up OpenAI API key for ChatGPT-4:
```bash
export OPENAI_API_KEY="your-api-key"
```

2. Install Ollama and pull CodeLlama 13B:
```bash
ollama pull codellama:13b
```

Or use Transformers library for local deployment.

## Usage

### Command Line Interface (CLI)

```bash
python src/main.py --input code_file.py --language python
```

### Web User Interface (UI)

Start the Streamlit web UI:

```bash
streamlit run ui/app.py
```

The UI will open in your browser at `http://localhost:8501`

Features:
- 📝 Paste code or upload files
- 📊 Real-time analysis and visualization
- 📥 Download fixed code and results
- ⚙️ Configurable settings

## Project Structure

```
├── src/
│   ├── detection/          # Vulnerability detection
│   ├── llm_router/         # Intelligent LLM routing
│   ├── llm_models/         # LLM integrations
│   ├── repair/             # Fix generation and refinement
│   ├── verification/       # Exploit-based verification
│   └── utils/              # Utilities
├── datasets/               # Benchmark datasets
├── evaluation/             # Evaluation scripts
├── notebooks/              # Research analysis
└── docs/                   # Documentation
```

## Research Paper

This project implements novel contributions to automated vulnerability repair:
- Hybrid local/cloud LLM routing
- Exploit-based verification (addressing VulnRepairEval's 21.7% limitation)
- Multi-iteration refinement with convergence detection

## License

MIT License

