"""Quick test to verify the project is working"""

import sys
from pathlib import Path

print("=" * 60)
print("Testing Project Components")
print("=" * 60)

# Test 1: Check Python version
print("\n1. Checking Python version...")
print(f"   Python {sys.version}")
if sys.version_info < (3, 8):
    print("   [WARNING] Python 3.8+ recommended")
else:
    print("   [OK] Python version OK")

# Test 2: Check required packages
print("\n2. Checking required packages...")
required_packages = [
    'yaml', 'requests', 'streamlit', 'numpy', 'scikit-learn'
]
missing = []
for pkg in required_packages:
    try:
        __import__(pkg.replace('-', '_'))
        print(f"   [OK] {pkg}")
    except ImportError:
        print(f"   [FAIL] {pkg} - MISSING")
        missing.append(pkg)

if missing:
    print(f"\n   Install missing packages: pip install {' '.join(missing)}")

# Test 3: Test imports
print("\n3. Testing module imports...")
try:
    from src.detection.vulnerability_detector import VulnerabilityDetector
    print("   [OK] VulnerabilityDetector")
except Exception as e:
    print(f"   [FAIL] VulnerabilityDetector: {e}")

try:
    from src.llm_router.router import LLMRouter
    print("   [OK] LLMRouter")
except Exception as e:
    print(f"   [FAIL] LLMRouter: {e}")

try:
    from src.repair.fix_generator import FixGenerator
    print("   [OK] FixGenerator")
except Exception as e:
    print(f"   [FAIL] FixGenerator: {e}")

try:
    from src.verification.fix_validator import FixValidator
    print("   [OK] FixValidator")
except Exception as e:
    print(f"   [FAIL] FixValidator: {e}")

try:
    from src.main import VulnerabilityRepairFramework
    print("   [OK] VulnerabilityRepairFramework")
except Exception as e:
    print(f"   [FAIL] VulnerabilityRepairFramework: {e}")

# Test 4: Test initialization
print("\n4. Testing component initialization...")
try:
    from src.utils.code_parser import CodeParser
    parser = CodeParser()
    lang = parser.detect_language("test.py")
    if lang == "python":
        print("   [OK] CodeParser works")
    else:
        print(f"   [WARNING] CodeParser: Expected 'python', got '{lang}'")
except Exception as e:
    print(f"   [FAIL] CodeParser: {e}")

try:
    from src.utils.metrics import MetricsCalculator
    calc = MetricsCalculator()
    similarity = calc.calculate_code_similarity("def a(): pass", "def a(): pass")
    if similarity == 1.0:
        print("   [OK] MetricsCalculator works")
    else:
        print(f"   [WARNING] MetricsCalculator: Expected 1.0, got {similarity}")
except Exception as e:
    print(f"   [FAIL] MetricsCalculator: {e}")

try:
    from src.detection.vulnerability_detector import VulnerabilityDetector
    detector = VulnerabilityDetector()
    code = "query = 'SELECT * FROM users WHERE id = ' + user_id"
    vulns = detector._pattern_based_detection(code, "python")
    if len(vulns) > 0:
        print("   [OK] VulnerabilityDetector works")
    else:
        print("   [WARNING] VulnerabilityDetector: No vulnerabilities detected")
except Exception as e:
    print(f"   [FAIL] VulnerabilityDetector: {e}")

# Test 5: Check config file
print("\n5. Checking configuration...")
config_file = Path("config.yaml")
if config_file.exists():
    print("   [OK] config.yaml exists")
    try:
        import yaml
        with open(config_file) as f:
            config = yaml.safe_load(f)
        print("   [OK] config.yaml is valid")
    except Exception as e:
        print(f"   [FAIL] config.yaml error: {e}")
else:
    print("   [FAIL] config.yaml not found")

# Test 6: Check project structure
print("\n6. Checking project structure...")
required_dirs = [
    "src/detection",
    "src/repair", 
    "src/verification",
    "src/llm_models",
    "src/utils"
]
all_exist = True
for dir_path in required_dirs:
    if Path(dir_path).exists():
        print(f"   [OK] {dir_path}/")
    else:
        print(f"   [FAIL] {dir_path}/ - MISSING")
        all_exist = False

print("\n" + "=" * 60)
print("Test Summary")
print("=" * 60)
print("\nIf all tests show [OK], your project is working!")
print("\nTo run a full test:")
print("  python test_framework.py")
print("\nTo test with example code:")
print("  python examples/example_usage.py")
print("\nTo use the CLI:")
print("  python src/main.py --input your_file.py")
print("=" * 60)

