# Architecture Documentation

## Overview

The Hybrid LLM-Based Detect–Fix–Verify Framework is designed with a modular architecture that enables intelligent routing between local and cloud-based LLMs for automated vulnerability repair.

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Input: Source Code                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Static Analysis Layer       │
        │  (Bandit, SonarQube, etc.)    │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Vulnerability Detection      │
        │   (CWE Classification)         │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   LLM Router (Intelligent)    │
        │  - Complexity Analysis         │
        │  - Privacy Check              │
        │  - Resource Availability      │
        └───────┬───────────────┬───────┘
                │               │
                ▼               ▼
    ┌──────────────────┐  ┌──────────────────┐
    │  CodeLlama 13B   │  │   ChatGPT-4      │
    │   (Local)        │  │   (Cloud)        │
    └────────┬─────────┘  └────────┬─────────┘
             │                     │
             └──────────┬──────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Fix Generation              │
        │   (Context-Aware Prompts)     │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Multi-Iteration Refinement  │
        │   - Static Analysis Check     │
        │   - Code Quality Metrics      │
        │   - Feedback Loop             │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Exploit-Based Verification  │
        │   - PoC Exploit Generation    │
        │   - Vulnerability Testing      │
        │   - Fix Validation            │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │   Output: Fixed Code + Report │
        └───────────────────────────────┘
```

## Core Components

### 1. Detection Module (`src/detection/`)

- **VulnerabilityDetector**: Integrates static analysis tools (Bandit, Semgrep)
- **CWE Classification**: Maps vulnerabilities to Common Weakness Enumeration
- **Context Extraction**: Extracts code context around vulnerabilities

### 2. LLM Router (`src/llm_router/`)

- **Intelligent Routing**: Selects between local and cloud models
- **Complexity Analysis**: Calculates code complexity scores
- **Privacy Detection**: Identifies sensitive code requiring local processing
- **Fallback Mechanism**: Automatic fallback to cloud if local fails

### 3. LLM Models (`src/llm_models/`)

- **CodeLlamaLocal**: Local CodeLlama 13B via Ollama or Transformers
- **ChatGPTCloud**: ChatGPT-4 API integration
- **PromptEngine**: Context-aware prompt generation

### 4. Repair Module (`src/repair/`)

- **FixGenerator**: Generates fixes using selected LLM
- **RefinementLoop**: Multi-iteration refinement with feedback
- **CodeQualityAnalyzer**: Calculates code quality metrics

### 5. Verification Module (`src/verification/`)

- **ExploitGenerator**: Generates PoC exploits for testing
- **VulnerabilityTester**: Executes exploits in sandbox
- **FixValidator**: Comprehensive fix validation

### 6. Utilities (`src/utils/`)

- **CodeParser**: Multi-language code parsing
- **MetricsCalculator**: Evaluation metrics calculation
- **Config**: Configuration management

## Key Features

### Hybrid LLM Architecture

The framework intelligently routes between:
- **Local (CodeLlama 13B)**: Fast, private, cost-effective for simple vulnerabilities
- **Cloud (ChatGPT-4)**: Powerful, accurate for complex vulnerabilities

Routing decisions based on:
- Code complexity
- Privacy requirements
- Vulnerability severity
- Resource availability

### Exploit-Based Verification

- Generates Proof-of-Concept exploits
- Tests original code (should be vulnerable)
- Tests fixed code (should not be vulnerable)
- Validates fix effectiveness beyond static analysis

### Multi-Iteration Refinement

- Iterative improvement based on feedback
- Convergence detection
- Quality metrics tracking
- Maximum iteration limits

## Configuration

See `config.yaml` for detailed configuration options:
- Router thresholds
- Refinement settings
- Verification settings
- Performance tuning

## API Usage

```python
from src.main import VulnerabilityRepairFramework

framework = VulnerabilityRepairFramework()
result = framework.process_file('vulnerable_code.py', language='python')
```

## Evaluation

Use `evaluation/benchmark_runner.py` to run comprehensive benchmarks:

```bash
python evaluation/benchmark_runner.py --dataset datasets/benchmark.json --output results.json
```

