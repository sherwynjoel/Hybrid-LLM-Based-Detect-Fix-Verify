# Benchmark Datasets

This directory contains benchmark datasets for evaluating the vulnerability repair framework.

## Dataset Format

Datasets should be in JSON or JSONL format with the following structure:

### JSON Format
```json
[
  {
    "id": "vuln_001",
    "language": "python",
    "vulnerable_code": "...",
    "fixed_code": "...",
    "cwe": "CWE-89",
    "description": "SQL Injection vulnerability"
  }
]
```

### JSONL Format
One JSON object per line:
```jsonl
{"id": "vuln_001", "language": "python", "vulnerable_code": "...", "fixed_code": "...", "cwe": "CWE-89"}
{"id": "vuln_002", "language": "cpp", "vulnerable_code": "...", "fixed_code": "...", "cwe": "CWE-119"}
```

## Sources

- **CVE Database**: Real-world vulnerabilities from Common Vulnerabilities and Exposures
- **SARD**: NIST Software Assurance Reference Dataset
- **Custom Benchmarks**: Curated vulnerability samples for Python, C/C++, Java

## Usage

```bash
python evaluation/benchmark_runner.py --dataset datasets/benchmark.json --output results.json
```

