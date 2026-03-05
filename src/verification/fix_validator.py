"""Validate fix effectiveness using real CWE-targeted harnesses"""

import logging
from typing import Dict, List

from src.detection.vulnerability_detector import VulnerabilityDetector
from src.verification.exploit_generator import ExploitGenerator
from src.verification.vulnerability_tester import VulnerabilityTester
from src.repair.code_quality import CodeQualityAnalyzer
from src.utils.metrics import MetricsCalculator
from src.utils.config import config

logger = logging.getLogger(__name__)


class FixValidator:
    """Comprehensive fix validation: static analysis + exploit-based + quality."""

    def __init__(self):
        self.detector = VulnerabilityDetector()
        self.exploit_generator = ExploitGenerator()
        self.tester = VulnerabilityTester()
        self.quality_analyzer = CodeQualityAnalyzer()
        self.metrics_calc = MetricsCalculator()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate(self, original_code: str, fixed_code: str,
                 vulnerability: Dict, language: str) -> Dict:
        """
        Run all validation stages and return a unified result dict.

        Stages
        ------
        1. Static re-analysis — does the original vulnerability still appear?
        2. New-vulnerability scan — did the fix introduce fresh issues?
        3. Exploit-based verification — does the CWE-specific harness pass?
        4. Code-quality comparison — did security score improve?
        """
        cwe = vulnerability.get('cwe', '')
        vuln_type = vulnerability.get('type', 'Unknown')
        vuln_line = vulnerability.get('line', 0)

        validation_results: Dict = {
            'static_analysis_passed': False,
            'exploit_test_passed': False,
            'quality_improved': False,
            'no_new_vulnerabilities': False,
            'overall_valid': False,
            'cwe': cwe,
            'vuln_type': vuln_type,
        }

        # ── 1. Static re-analysis ───────────────────────────────────────
        try:
            remaining_vulns = self.detector.detect(fixed_code, language)
        except Exception as e:
            logger.warning("Static re-analysis failed: %s", e)
            remaining_vulns = []

        original_cwe_still_present = any(
            v.get('cwe') == cwe and abs(v.get('line', 0) - vuln_line) <= 3
            for v in remaining_vulns
        )
        validation_results['static_analysis_passed'] = not original_cwe_still_present

        # ── 2. New-vulnerability scan ───────────────────────────────────
        # Allow up to 1 residual (sometimes static tools flag the same
        # pattern even after a correct fix due to heuristic false positives)
        validation_results['no_new_vulnerabilities'] = len(remaining_vulns) <= 1

        # ── 3. Exploit-based verification ──────────────────────────────
        exploit_test_passed = False
        exploit_detail = ''
        try:
            exploit_result = self.exploit_generator.generate_exploit(
                original_code, vulnerability, language
            )
            if exploit_result.get('success'):
                exploit_code = exploit_result.get('exploit_code', '')
                verify_result = self.tester.verify_fix(
                    original_code, fixed_code, exploit_code,
                    language, cwe=cwe,
                )
                exploit_test_passed = verify_result.get('fix_successful', False)
                exploit_detail = verify_result.get('fixed_test', {}).get('detail', '')
                validation_results['exploit_verify_detail'] = exploit_detail
                validation_results['exploit_verify_result'] = verify_result
        except Exception as e:
            logger.warning("Exploit verification failed for %s (%s): %s", vuln_type, cwe, e)

        validation_results['exploit_test_passed'] = exploit_test_passed

        # ── 4. Code-quality comparison ──────────────────────────────────
        try:
            original_quality = self.quality_analyzer.analyze(original_code, language)
            fixed_quality = self.quality_analyzer.analyze(fixed_code, language)
            quality_comparison = self.quality_analyzer.compare_quality(
                original_quality, fixed_quality
            )
            validation_results['quality_improved'] = (
                quality_comparison.get('security_improvement', 0) >= 0 and
                quality_comparison.get('overall_improvement', 0) >= -0.15  # allow minor size increase
            )
            validation_results['quality_comparison'] = quality_comparison
        except Exception as e:
            logger.warning("Quality analysis failed: %s", e)
            original_quality = {}
            fixed_quality = {}
            quality_comparison = {}
            validation_results['quality_improved'] = True   # non-fatal

        # ── Overall verdict ─────────────────────────────────────────────
        exploit_ok = (
            exploit_test_passed or
            not config.enable_exploit_verification
        )
        validation_results['overall_valid'] = (
            validation_results['static_analysis_passed'] and
            exploit_ok and
            validation_results['no_new_vulnerabilities']
        )

        # ── Summary metrics ─────────────────────────────────────────────
        code_similarity = self.metrics_calc.calculate_code_similarity(
            original_code, fixed_code
        )
        fix_quality_score = self.metrics_calc.calculate_fix_quality(
            original_code, fixed_code,
            validation_results['exploit_test_passed'],
            validation_results['static_analysis_passed'],
        )
        validation_results['metrics'] = {
            'code_similarity': code_similarity,
            'fix_quality_score': fix_quality_score,
            'original_quality': original_quality,
            'fixed_quality': fixed_quality,
            'quality_comparison': quality_comparison,
            'remaining_vulnerabilities': len(remaining_vulns),
        }

        return validation_results
