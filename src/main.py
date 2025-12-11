"""Main entry point for the Hybrid LLM Vulnerability Repair Framework"""

import argparse
import json
from pathlib import Path
import time
from typing import Dict, List, Optional

from src.detection.vulnerability_detector import VulnerabilityDetector
from src.repair.fix_generator import FixGenerator
from src.repair.refinement_loop import RefinementLoop
from src.verification.fix_validator import FixValidator
from src.utils.code_parser import CodeParser
from src.utils.metrics import MetricsCalculator, RepairMetrics
from src.utils.config import config


class VulnerabilityRepairFramework:
    """Main framework orchestrator"""
    
    def __init__(self):
        self.detector = VulnerabilityDetector()
        self.fix_generator = FixGenerator()
        self.refinement_loop = RefinementLoop()
        self.validator = FixValidator()
        self.parser = CodeParser()
        self.metrics_calc = MetricsCalculator()
    
    def process_file(self, file_path: str, language: Optional[str] = None,
                    enable_refinement: bool = True,
                    enable_verification: bool = True) -> Dict:
        """Process a single file for vulnerability detection and repair"""
        
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Detect language if not provided
        if not language:
            language = self.parser.detect_language(file_path)
            if not language:
                return {
                    'success': False,
                    'error': f'Could not detect language for {file_path}'
                }
        
        # Parse code
        parsed_code = self.parser.parse_code(code, language)
        
        # Detect vulnerabilities
        vulnerabilities = self.detector.detect(code, language, file_path)
        
        if not vulnerabilities:
            return {
                'success': True,
                'vulnerabilities_found': 0,
                'message': 'No vulnerabilities detected'
            }
        
        # Process each vulnerability
        results = []
        for vuln in vulnerabilities:
            vuln_result = self._process_vulnerability(
                code, vuln, language, parsed_code,
                enable_refinement, enable_verification
            )
            results.append(vuln_result)
        
        return {
            'success': True,
            'file_path': file_path,
            'language': language,
            'vulnerabilities_found': len(vulnerabilities),
            'results': results,
            'summary': self._generate_summary(results)
        }
    
    def _process_vulnerability(self, code: str, vulnerability: Dict,
                              language: str, parsed_code: Dict,
                              enable_refinement: bool,
                              enable_verification: bool) -> Dict:
        """Process a single vulnerability"""
        
        start_time = time.time()
        
        # Extract context
        context = self.detector.extract_context(code, vulnerability)
        context_code = context.get('context', '')
        
        # Generate initial fix
        fix_result = self.fix_generator.generate_fix(
            code, vulnerability, language, context_code
        )
        
        if not fix_result.get('success', False):
            return {
                'vulnerability': vulnerability,
                'success': False,
                'error': fix_result.get('error', 'Fix generation failed')
            }
        
        initial_fix = fix_result.get('fixed_code', '')
        iterations = 1
        
        # Refinement loop
        if enable_refinement:
            refinement_result = self.refinement_loop.refine(
                code, vulnerability, language, initial_fix, context_code
            )
            
            if refinement_result.get('success', False):
                initial_fix = refinement_result.get('fixed_code', initial_fix)
                iterations = refinement_result.get('iterations', 1)
        
        # Validation
        validation_result = None
        if enable_verification:
            validation_result = self.validator.validate(
                code, initial_fix, vulnerability, language
            )
        
        processing_time = time.time() - start_time
        
        # Calculate metrics
        code_similarity = self.metrics_calc.calculate_code_similarity(code, initial_fix)
        
        exploit_passed = False
        static_passed = False
        
        if validation_result:
            exploit_passed = validation_result.get('exploit_test_passed', False)
            static_passed = validation_result.get('static_analysis_passed', False)
        
        fix_quality = self.metrics_calc.calculate_fix_quality(
            code, initial_fix, exploit_passed, static_passed
        )
        
        return {
            'vulnerability': vulnerability,
            'success': True,
            'fixed_code': initial_fix,
            'iterations': iterations,
            'processing_time': processing_time,
            'validation': validation_result,
            'metrics': {
                'code_similarity': code_similarity,
                'fix_quality_score': fix_quality,
                'exploit_test_passed': exploit_passed,
                'static_analysis_passed': static_passed
            },
            'model_used': fix_result.get('model_used', 'unknown')
        }
    
    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Generate summary of repair results"""
        successful = sum(1 for r in results if r.get('success', False))
        total = len(results)
        
        total_time = sum(r.get('processing_time', 0) for r in results)
        avg_iterations = sum(r.get('iterations', 1) for r in results) / total if total > 0 else 0
        
        exploit_passed = sum(1 for r in results 
                           if r.get('metrics', {}).get('exploit_test_passed', False))
        static_passed = sum(1 for r in results 
                          if r.get('metrics', {}).get('static_analysis_passed', False))
        
        return {
            'total_vulnerabilities': total,
            'successful_repairs': successful,
            'success_rate': successful / total if total > 0 else 0,
            'exploit_verification_passed': exploit_passed,
            'static_analysis_passed': static_passed,
            'average_iterations': avg_iterations,
            'total_processing_time': total_time,
            'average_processing_time': total_time / total if total > 0 else 0
        }


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Hybrid LLM-Based Vulnerability Repair Framework'
    )
    parser.add_argument('--input', '-i', required=True,
                       help='Input file or directory path')
    parser.add_argument('--language', '-l',
                       choices=['python', 'cpp', 'c', 'java'],
                       help='Programming language (auto-detected if not specified)')
    parser.add_argument('--output', '-o',
                       help='Output file for results (JSON)')
    parser.add_argument('--no-refinement', action='store_true',
                       help='Disable multi-iteration refinement')
    parser.add_argument('--no-verification', action='store_true',
                       help='Disable exploit-based verification')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    framework = VulnerabilityRepairFramework()
    
    input_path = Path(args.input)
    
    if input_path.is_file():
        # Process single file
        result = framework.process_file(
            str(input_path),
            language=args.language,
            enable_refinement=not args.no_refinement,
            enable_verification=not args.no_verification
        )
        
        if args.verbose:
            print(json.dumps(result, indent=2))
        else:
            summary = result.get('summary', {})
            print(f"Processed: {input_path}")
            print(f"Vulnerabilities found: {summary.get('total_vulnerabilities', 0)}")
            print(f"Successful repairs: {summary.get('successful_repairs', 0)}")
            print(f"Success rate: {summary.get('success_rate', 0):.2%}")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"Results saved to {args.output}")
    
    elif input_path.is_dir():
        # Process directory
        print(f"Processing directory: {input_path}")
        # Implementation for directory processing would go here
        print("Directory processing not yet implemented")
    
    else:
        print(f"Error: {args.input} is not a valid file or directory")


if __name__ == '__main__':
    main()

