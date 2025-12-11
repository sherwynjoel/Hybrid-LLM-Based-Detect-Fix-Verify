# API Documentation

## VulnerabilityRepairFramework

Main framework class for vulnerability detection and repair.

### Methods

#### `process_file(file_path: str, language: Optional[str] = None, enable_refinement: bool = True, enable_verification: bool = True) -> Dict`

Process a single file for vulnerability detection and repair.

**Parameters:**
- `file_path`: Path to source code file
- `language`: Programming language (auto-detected if None)
- `enable_refinement`: Enable multi-iteration refinement
- `enable_verification`: Enable exploit-based verification

**Returns:**
Dictionary containing:
- `success`: Boolean indicating success
- `vulnerabilities_found`: Number of vulnerabilities detected
- `results`: List of repair results for each vulnerability
- `summary`: Summary statistics

## VulnerabilityDetector

Detects vulnerabilities using static analysis tools.

### Methods

#### `detect(code: str, language: str, file_path: Optional[str] = None) -> List[Dict]`

Detect vulnerabilities in code.

**Returns:**
List of vulnerability dictionaries with:
- `type`: Vulnerability type
- `severity`: Severity level (CRITICAL, HIGH, MEDIUM, LOW)
- `line`: Line number
- `message`: Description
- `cwe`: CWE classification

## LLMRouter

Intelligent router for selecting between local and cloud LLMs.

### Methods

#### `route(code: str, vulnerability: Dict, language: str) -> str`

Route to appropriate LLM model.

**Returns:**
- `'local'` or `'cloud'`

## FixGenerator

Generates vulnerability fixes using LLMs.

### Methods

#### `generate_fix(code: str, vulnerability: Dict, language: str, context: Optional[str] = None) -> Dict`

Generate fix for vulnerability.

**Returns:**
Dictionary with:
- `success`: Boolean
- `fixed_code`: Generated fix
- `model_used`: Model used for generation
- `routing_decision`: Routing decision details

## RefinementLoop

Multi-iteration refinement for improving fix quality.

### Methods

#### `refine(original_code: str, vulnerability: Dict, language: str, initial_fix: Optional[str] = None, context: Optional[str] = None) -> Dict`

Refine fix through multiple iterations.

**Returns:**
Dictionary with:
- `success`: Boolean
- `fixed_code`: Refined fix
- `iterations`: Number of iterations
- `quality_metrics`: Quality metrics
- `converged`: Whether convergence was achieved

## FixValidator

Validates fix effectiveness.

### Methods

#### `validate(original_code: str, fixed_code: str, vulnerability: Dict, language: str) -> Dict`

Comprehensive fix validation.

**Returns:**
Dictionary with:
- `static_analysis_passed`: Boolean
- `exploit_test_passed`: Boolean
- `quality_improved`: Boolean
- `overall_valid`: Boolean
- `metrics`: Detailed metrics

