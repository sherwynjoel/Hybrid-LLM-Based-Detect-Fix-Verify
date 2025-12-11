"""Validate fix effectiveness"""

from typing import Dict, List

from src.detection.vulnerability_detector import VulnerabilityDetector
from src.verification.exploit_generator import ExploitGenerator
from src.verification.vulnerability_tester import VulnerabilityTester
from src.repair.code_quality import CodeQualityAnalyzer
from src.utils.metrics import MetricsCalculator
from src.utils.config import config


class FixValidator:
    """Validate that fixes are effective"""
    
    def __init__(self):
        self.detector = VulnerabilityDetector()
        self.exploit_generator = ExploitGenerator()
        self.tester = VulnerabilityTester()
        self.quality_analyzer = CodeQualityAnalyzer()
        self.metrics_calc = MetricsCalculator()
    
    def validate(self, original_code: str, fixed_code: str, 
                vulnerability: Dict, language: str) -> Dict:
        """Comprehensive fix validation"""
        
        validation_results = {
            'static_analysis_passed': False,
            'exploit_test_passed': False,
            'quality_improved': False,
            'no_new_vulnerabilities': False,
            'overall_valid': False
        }
        
        # 1. Static analysis check
        remaining_vulns = self.detector.detect(fixed_code, language)
        original_vuln_id = vulnerability.get('cwe', '') + str(vulnerability.get('line', 0))
        
        # Check if original vulnerability is fixed
        original_fixed = not any(
            v.get('cwe') == vulnerability.get('cwe') and 
            abs(v.get('line', 0) - vulnerability.get('line', 0)) <= 2
            for v in remaining_vulns
        )
        
        # Check for new vulnerabilities
        no_new_vulns = len(remaining_vulns) <= 1  # Allow original if still present
        
        validation_results['static_analysis_passed'] = original_fixed
        validation_results['no_new_vulnerabilities'] = no_new_vulns
        
        # 2. Exploit-based verification
        try:
            exploit_result = self.exploit_generator.generate_exploit(
                original_code, vulnerability, language
            )
            
            if exploit_result.get('success', False):
                exploit_code = exploit_result.get('exploit_code', '')
                verify_result = self.tester.verify_fix(
                    original_code, fixed_code, exploit_code, language
                )
                
                validation_results['exploit_test_passed'] = verify_result.get('fix_successful', False)
        except Exception as e:
            print(f"Exploit verification failed: {e}")
            validation_results['exploit_test_passed'] = False
        
        # 3. Quality improvement check
        original_quality = self.quality_analyzer.analyze(original_code, language)
        fixed_quality = self.quality_analyzer.analyze(fixed_code, language)
        
        quality_comparison = self.quality_analyzer.compare_quality(original_quality, fixed_quality)
        validation_results['quality_improved'] = (
            quality_comparison['security_improvement'] > 0 and
            quality_comparison['overall_improvement'] >= -0.1
        )
        
        # Overall validation
        validation_results['overall_valid'] = (
            validation_results['static_analysis_passed'] and
            (validation_results['exploit_test_passed'] or not config.enable_exploit_verification) and
            validation_results['no_new_vulnerabilities']
        )
        
        # Calculate metrics
        code_similarity = self.metrics_calc.calculate_code_similarity(original_code, fixed_code)
        fix_quality_score = self.metrics_calc.calculate_fix_quality(
            original_code, fixed_code,
            validation_results['exploit_test_passed'],
            validation_results['static_analysis_passed']
        )
        
        validation_results['metrics'] = {
            'code_similarity': code_similarity,
            'fix_quality_score': fix_quality_score,
            'original_quality': original_quality,
            'fixed_quality': fixed_quality,
            'quality_comparison': quality_comparison,
            'remaining_vulnerabilities': len(remaining_vulns)
        }
        
        return validation_results

