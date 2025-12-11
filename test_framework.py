"""Quick test script to verify framework components are working"""

import sys
from pathlib import Path

def test_imports():
    """Test if all modules can be imported"""
    print("Testing imports...")
    
    try:
        from src.detection.vulnerability_detector import VulnerabilityDetector
        print("✅ VulnerabilityDetector imported")
    except Exception as e:
        print(f"❌ VulnerabilityDetector import failed: {e}")
        return False
    
    try:
        from src.llm_router.router import LLMRouter
        print("✅ LLMRouter imported")
    except Exception as e:
        print(f"❌ LLMRouter import failed: {e}")
        return False
    
    try:
        from src.llm_models.codellama_local import CodeLlamaLocal
        print("✅ CodeLlamaLocal imported")
    except Exception as e:
        print(f"❌ CodeLlamaLocal import failed: {e}")
        return False
    
    try:
        from src.llm_models.chatgpt_cloud import ChatGPTCloud
        print("✅ ChatGPTCloud imported")
    except Exception as e:
        print(f"❌ ChatGPTCloud import failed: {e}")
        return False
    
    try:
        from src.repair.fix_generator import FixGenerator
        print("✅ FixGenerator imported")
    except Exception as e:
        print(f"❌ FixGenerator import failed: {e}")
        return False
    
    try:
        from src.repair.refinement_loop import RefinementLoop
        print("✅ RefinementLoop imported")
    except Exception as e:
        print(f"❌ RefinementLoop import failed: {e}")
        return False
    
    try:
        from src.verification.fix_validator import FixValidator
        print("✅ FixValidator imported")
    except Exception as e:
        print(f"❌ FixValidator import failed: {e}")
        return False
    
    try:
        from src.main import VulnerabilityRepairFramework
        print("✅ VulnerabilityRepairFramework imported")
    except Exception as e:
        print(f"❌ VulnerabilityRepairFramework import failed: {e}")
        return False
    
    return True

def test_initialization():
    """Test if components can be initialized"""
    print("\nTesting initialization...")
    
    try:
        from src.detection.vulnerability_detector import VulnerabilityDetector
        detector = VulnerabilityDetector()
        print("✅ VulnerabilityDetector initialized")
    except Exception as e:
        print(f"❌ VulnerabilityDetector initialization failed: {e}")
        return False
    
    try:
        from src.llm_router.router import LLMRouter
        router = LLMRouter()
        print("✅ LLMRouter initialized")
    except Exception as e:
        print(f"❌ LLMRouter initialization failed: {e}")
        return False
    
    try:
        from src.utils.code_parser import CodeParser
        parser = CodeParser()
        print("✅ CodeParser initialized")
    except Exception as e:
        print(f"❌ CodeParser initialization failed: {e}")
        return False
    
    try:
        from src.utils.metrics import MetricsCalculator
        metrics = MetricsCalculator()
        print("✅ MetricsCalculator initialized")
    except Exception as e:
        print(f"❌ MetricsCalculator initialization failed: {e}")
        return False
    
    try:
        from src.repair.code_quality import CodeQualityAnalyzer
        quality = CodeQualityAnalyzer()
        print("✅ CodeQualityAnalyzer initialized")
    except Exception as e:
        print(f"❌ CodeQualityAnalyzer initialization failed: {e}")
        return False
    
    # Test framework initialization (may fail if API keys not set, but that's OK)
    try:
        from src.main import VulnerabilityRepairFramework
        framework = VulnerabilityRepairFramework()
        print("✅ VulnerabilityRepairFramework initialized")
    except ValueError as e:
        # Expected if API key not set
        print(f"⚠️  VulnerabilityRepairFramework: API key not set (expected): {e}")
    except Exception as e:
        print(f"❌ VulnerabilityRepairFramework initialization failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    try:
        from src.utils.code_parser import CodeParser
        parser = CodeParser()
        
        # Test language detection
        lang = parser.detect_language("test.py")
        assert lang == "python", f"Expected 'python', got '{lang}'"
        print("✅ Language detection works")
        
        # Test code parsing
        code = "def hello():\n    print('world')"
        parsed = parser.parse_code(code, "python")
        assert parsed['language'] == "python"
        assert len(parsed['functions']) > 0
        print("✅ Code parsing works")
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False
    
    try:
        from src.utils.metrics import MetricsCalculator
        calc = MetricsCalculator()
        
        # Test similarity calculation
        similarity = calc.calculate_code_similarity("def a(): pass", "def a(): pass")
        assert similarity == 1.0, f"Expected 1.0, got {similarity}"
        print("✅ Metrics calculation works")
        
    except Exception as e:
        print(f"❌ Metrics test failed: {e}")
        return False
    
    try:
        from src.detection.vulnerability_detector import VulnerabilityDetector
        detector = VulnerabilityDetector()
        
        # Test pattern-based detection
        code = "query = 'SELECT * FROM users WHERE id = ' + user_id"
        vulns = detector._pattern_based_detection(code, "python")
        assert len(vulns) > 0, "Should detect SQL injection pattern"
        print("✅ Vulnerability detection works")
        
    except Exception as e:
        print(f"❌ Vulnerability detection test failed: {e}")
        return False
    
    return True

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from src.utils.config import config
        
        # Check if config loads
        assert config is not None
        print("✅ Configuration loaded")
        
        # Check some config values
        assert hasattr(config, 'max_iterations')
        assert hasattr(config, 'local_threshold')
        print("✅ Configuration values accessible")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("=" * 60)
    print("Framework Component Test")
    print("=" * 60)
    
    all_passed = True
    
    # Test imports
    if not test_imports():
        all_passed = False
    
    # Test initialization
    if not test_initialization():
        all_passed = False
    
    # Test basic functionality
    if not test_basic_functionality():
        all_passed = False
    
    # Test configuration
    if not test_config():
        all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Framework is working correctly.")
        print("\nNote: Some components (like ChatGPT) require API keys.")
        print("      This is expected and doesn't affect core functionality.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())

