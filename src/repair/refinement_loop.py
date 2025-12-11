"""Multi-iteration refinement loop"""

from typing import Dict, List, Optional
import time

from src.repair.fix_generator import FixGenerator
from src.repair.code_quality import CodeQualityAnalyzer
from src.detection.vulnerability_detector import VulnerabilityDetector
from src.utils.config import config
from src.utils.metrics import MetricsCalculator


class RefinementLoop:
    """Multi-iteration refinement for improving fix quality"""
    
    def __init__(self):
        self.fix_generator = FixGenerator()
        self.quality_analyzer = CodeQualityAnalyzer()
        self.detector = VulnerabilityDetector()
        self.metrics_calc = MetricsCalculator()
    
    def refine(self, original_code: str, vulnerability: Dict, language: str,
              initial_fix: Optional[str] = None, context: Optional[str] = None) -> Dict:
        """Refine fix through multiple iterations"""
        
        start_time = time.time()
        iteration = 0
        current_fix = initial_fix
        feedback_history = []
        quality_history = []
        
        # Calculate original quality
        original_quality = self.quality_analyzer.analyze(original_code, language)
        
        while iteration < config.max_iterations:
            iteration += 1
            
            # Generate or refine fix
            if iteration == 1 and current_fix:
                # Use initial fix
                fixed_code = current_fix
            elif iteration == 1:
                # Generate initial fix
                result = self.fix_generator.generate_fix(
                    original_code, vulnerability, language, context
                )
                if not result.get('success', False):
                    return {
                        'success': False,
                        'error': result.get('error', 'Fix generation failed'),
                        'iterations': iteration
                    }
                fixed_code = result.get('fixed_code', '')
            else:
                # Refine based on feedback
                if self.fix_generator.codellama.is_available():
                    result = self.fix_generator.codellama.refine_fix(
                        original_code, current_fix, feedback_history, language
                    )
                else:
                    result = self.fix_generator.chatgpt.refine_fix(
                        original_code, current_fix, feedback_history, language
                    )
                
                if not result.get('success', False):
                    break
                
                fixed_code = result.get('fixed_code', '')
            
            # Analyze quality
            fixed_quality = self.quality_analyzer.analyze(fixed_code, language)
            quality_history.append(fixed_quality)
            
            # Check for vulnerabilities in fixed code
            remaining_vulns = self.detector.detect(fixed_code, language)
            
            # Generate feedback
            feedback = self._generate_feedback(
                original_code, fixed_code, vulnerability,
                remaining_vulns, fixed_quality, original_quality, language
            )
            
            feedback_history.extend(feedback)
            
            # Check convergence
            if iteration > 1:
                prev_quality = quality_history[-2]['overall_score']
                curr_quality = fixed_quality['overall_score']
                
                if abs(curr_quality - prev_quality) < (1 - config.convergence_threshold):
                    # Converged
                    break
            
            # Check if fix is good enough
            if (not remaining_vulns and 
                fixed_quality['security_score'] >= config.convergence_threshold):
                break
            
            current_fix = fixed_code
        
        processing_time = time.time() - start_time
        
        return {
            'success': True,
            'fixed_code': current_fix or fixed_code,
            'iterations': iteration,
            'quality_metrics': quality_history[-1] if quality_history else {},
            'quality_history': quality_history,
            'feedback_history': feedback_history,
            'remaining_vulnerabilities': remaining_vulns,
            'processing_time': processing_time,
            'converged': iteration < config.max_iterations
        }
    
    def _generate_feedback(self, original_code: str, fixed_code: str,
                          original_vuln: Dict, remaining_vulns: List[Dict],
                          fixed_quality: Dict, original_quality: Dict,
                          language: str) -> List[str]:
        """Generate feedback for refinement"""
        feedback = []
        
        # Check for remaining vulnerabilities
        if remaining_vulns:
            feedback.append(f"Fix still contains {len(remaining_vulns)} vulnerabilities")
            for vuln in remaining_vulns[:3]:  # Limit to first 3
                feedback.append(f"- {vuln.get('type', 'Unknown')} at line {vuln.get('line', 0)}")
        
        # Quality feedback
        quality_comparison = self.quality_analyzer.compare_quality(original_quality, fixed_quality)
        
        if quality_comparison['security_improvement'] < 0:
            feedback.append("Security score decreased - review security practices")
        
        if quality_comparison['readability_improvement'] < -0.1:
            feedback.append("Code readability decreased - improve code structure")
        
        if quality_comparison['complexity_change'] > 5:
            feedback.append("Code complexity increased significantly - simplify logic")
        
        # Specific feedback based on vulnerability type
        cwe = original_vuln.get('cwe', '')
        if cwe == 'CWE-89' and 'parameterized' not in fixed_code.lower():
            feedback.append("Use parameterized queries for SQL operations")
        
        if cwe == 'CWE-79' and 'escape' not in fixed_code.lower() and 'sanitize' not in fixed_code.lower():
            feedback.append("Ensure user input is properly escaped/sanitized")
        
        if cwe == 'CWE-119' and language == 'cpp':
            if 'strcpy' in fixed_code or 'strcat' in fixed_code:
                feedback.append("Replace unsafe string functions with safe alternatives (strncpy, strncat)")
        
        return feedback

