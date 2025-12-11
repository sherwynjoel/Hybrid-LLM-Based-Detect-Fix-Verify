# Accuracy Evaluation Guide

## Current Status

The framework has been fully implemented but requires evaluation on benchmark datasets to determine actual accuracy metrics.

## Expected Accuracy

Based on research and design goals:

- **Target**: >30% improvement over baseline (VulnRepairEval's 21.7%)
- **Expected Range**: 50-60% accuracy (vs 21.7% baseline)
- **Improvement Factors**:
  - Hybrid LLM routing (local + cloud)
  - Exploit-based verification
  - Multi-iteration refinement

## How to Measure Accuracy

### Step 1: Prepare Benchmark Dataset

Create or use a benchmark dataset in JSON format:

```json
[
  {
    "id": "vuln_001",
    "language": "python",
    "vulnerable_code": "...",
    "fixed_code": "...",
    "cwe": "CWE-89"
  }
]
```

### Step 2: Run Benchmark Evaluation

```bash
python evaluation/benchmark_runner.py \
  --dataset datasets/benchmark.json \
  --output results.json
```

### Step 3: Calculate Metrics

```bash
python evaluation/metrics_calculator.py \
  --results results.json \
  --output metrics.json
```

### Step 4: Compare with Baselines

```bash
python evaluation/comparison.py \
  --framework results.json \
  --baselines LLM4CVE:baseline_llm4cve.json SecureFixAgent:baseline_securefix.json \
  --output comparison.json
```

## Accuracy Metrics Explained

### Primary Metrics

1. **Accuracy**: Percentage of successfully fixed vulnerabilities
   - Formula: (Successful Repairs) / (Total Repairs)
   - Successful = Exploit test passed AND Static analysis passed

2. **Precision**: True positives / (True positives + False positives)
   - Measures correctness of fixes

3. **Recall**: True positives / (True positives + False negatives)
   - Measures completeness of fixes

4. **F1 Score**: Harmonic mean of precision and recall
   - Balanced metric

### Secondary Metrics

- **Code Similarity**: How similar fixed code is to original
- **Fix Quality Score**: Weighted combination of similarity, exploit test, static analysis
- **Average Iterations**: Number of refinement iterations needed
- **Processing Time**: Time per vulnerability repair

## Baseline Comparisons

### Existing Frameworks

| Framework | Accuracy/Success Rate | Notes |
|-----------|----------------------|-------|
| VulnRepairEval | 21.7% | Exploit-based evaluation |
| SecureFixAgent | 13.51% improvement | Over static analysis baseline |
| LLM4CVE | 8.51/10 quality | Human-verified quality score |

### Our Framework (Expected)

- **Target**: >30% improvement over VulnRepairEval
- **Expected**: 50-60% accuracy
- **Improvements**:
  - Hybrid routing (local + cloud)
  - Exploit verification
  - Multi-iteration refinement

## Factors Affecting Accuracy

### Positive Factors

1. **Hybrid LLM Routing**: Uses best model for each vulnerability
2. **Exploit Verification**: Validates fixes beyond static analysis
3. **Multi-Iteration Refinement**: Improves fix quality iteratively
4. **Context-Aware Prompts**: Better understanding of vulnerabilities

### Limitations

1. **Exploit Generation**: May not cover all vulnerability types
2. **Model Limitations**: LLMs may not understand complex vulnerabilities
3. **Static Analysis**: Tool limitations affect detection accuracy
4. **Dataset Quality**: Evaluation depends on benchmark quality

## Running Your Own Evaluation

### Quick Test

```bash
# Test on sample dataset
python evaluation/benchmark_runner.py \
  --dataset datasets/sample_benchmark.json \
  --output test_results.json

# View results
python evaluation/metrics_calculator.py \
  --results test_results.json
```

### Full Evaluation

1. **Prepare Dataset**: Use CVE-based or SARD datasets
2. **Run Benchmarks**: Process all vulnerabilities
3. **Calculate Metrics**: Generate accuracy reports
4. **Compare Baselines**: Compare with existing frameworks
5. **Analyze Results**: Identify strengths and weaknesses

## Interpreting Results

### Good Accuracy Indicators

- Accuracy > 50%
- Precision > 0.7
- Recall > 0.6
- F1 Score > 0.65
- Exploit test pass rate > 60%

### Areas for Improvement

- Low accuracy: Improve prompt engineering or model selection
- Low precision: Reduce false positives in detection
- Low recall: Improve vulnerability detection coverage
- High iterations: Optimize refinement convergence

## Next Steps

1. **Run Evaluation**: Execute benchmarks on your datasets
2. **Analyze Results**: Identify accuracy bottlenecks
3. **Fine-tune**: Adjust prompts, thresholds, or models
4. **Re-evaluate**: Measure improvements
5. **Document**: Record actual accuracy metrics

## Example Output

```
Benchmark completed: datasets/benchmark.json
Total items: 100
Accuracy: 58.00%
F1 Score: 0.62
Average iterations: 2.3
Average processing time: 4.5s

Comparison with baseline:
  Accuracy improvement: +36.30%
  F1 improvement: +0.15
```

