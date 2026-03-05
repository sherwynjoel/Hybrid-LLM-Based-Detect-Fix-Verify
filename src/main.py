"""Main entry point for the Hybrid LLM Vulnerability Repair Framework"""

import argparse
import json
from pathlib import Path
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

from src.detection.vulnerability_detector import VulnerabilityDetector
from src.repair.fix_generator import FixGenerator
from src.repair.refinement_loop import RefinementLoop
from src.verification.fix_validator import FixValidator
from src.utils.code_parser import CodeParser
from src.utils.metrics import MetricsCalculator, RepairMetrics
from src.utils.config import config

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%H:%M:%S',
)
logger = logging.getLogger(__name__)

# Supported source-file extensions → language name
_LANG_MAP: Dict[str, str] = {
    '.py':   'python',
    '.cpp':  'cpp',
    '.cc':   'cpp',
    '.cxx':  'cpp',
    '.c':    'c',
    '.h':    'c',
    '.java': 'java',
}


class VulnerabilityRepairFramework:
    """Main framework orchestrator"""
    
    def __init__(self):
        self.detector = VulnerabilityDetector()
        self.fix_generator = FixGenerator()
        self.refinement_loop = RefinementLoop()
        self.validator = FixValidator()
        self.parser = CodeParser()
        self.metrics_calc = MetricsCalculator()
    
    # ------------------------------------------------------------------
    # Public: single file
    # ------------------------------------------------------------------

    def process_file(self, file_path: str, language: Optional[str] = None,
                    enable_refinement: bool = True,
                    enable_verification: bool = True) -> Dict:
        """Process a single file for vulnerability detection and repair."""
        
        logger.info("Processing file: %s", file_path)

        # Read file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except OSError as e:
            return {'success': False, 'error': f'Cannot read file: {e}'}
        
        # Detect language
        if not language:
            language = self.parser.detect_language(file_path)
            if not language:
                return {
                    'success': False,
                    'error': f'Could not detect language for {file_path}',
                }
        
        # Parse code (structural info)
        parsed_code = self.parser.parse_code(code, language)
        
        # Detect vulnerabilities
        vulnerabilities = self.detector.detect(code, language, file_path)
        logger.info("Detected %d vulnerability/ies in %s", len(vulnerabilities), file_path)

        if not vulnerabilities:
            return {
                'success': True,
                'file_path': file_path,
                'language': language,
                'vulnerabilities_found': 0,
                'message': 'No vulnerabilities detected',
            }
        
        # Process each vulnerability
        results = []
        for vuln in vulnerabilities:
            vuln_result = self._process_vulnerability(
                code, vuln, language, parsed_code,
                enable_refinement, enable_verification,
            )
            results.append(vuln_result)
        
        return {
            'success': True,
            'file_path': file_path,
            'language': language,
            'original_code': code,
            'vulnerabilities_found': len(vulnerabilities),
            'results': results,
            'summary': self._generate_summary(results),
        }
    
    # ------------------------------------------------------------------
    # Public: directory
    # ------------------------------------------------------------------

    def process_directory(self, dir_path: str,
                          language: Optional[str] = None,
                          enable_refinement: bool = True,
                          enable_verification: bool = True,
                          recursive: bool = True,
                          parallel_workers: int = 1) -> Dict:
        """
        Scan every source file in *dir_path* for vulnerabilities.

        Parameters
        ----------
        dir_path          : Root directory to scan.
        language          : Force a language; auto-detected when None.
        enable_refinement : Whether to apply multi-iteration refinement.
        enable_verification: Whether to run exploit-based verification.
        recursive         : Descend into sub-directories.
        parallel_workers  : Number of threads for parallel file processing.
        """
        root = Path(dir_path)
        if not root.is_dir():
            return {'success': False, 'error': f'{dir_path} is not a directory'}

        # Collect matching files
        glob_fn = root.rglob if recursive else root.glob
        source_files: List[Path] = [
            p for p in glob_fn('*')
            if p.is_file() and p.suffix.lower() in _LANG_MAP
        ]

        if not source_files:
            return {
                'success': True,
                'directory': dir_path,
                'files_scanned': 0,
                'message': 'No supported source files found.',
            }

        logger.info("Found %d source file(s) in %s", len(source_files), dir_path)

        file_results: List[Dict] = []
        start_ts = time.time()

        if parallel_workers > 1:
            with ThreadPoolExecutor(max_workers=parallel_workers) as pool:
                futures = {
                    pool.submit(
                        self.process_file,
                        str(fp),
                        language or _LANG_MAP.get(fp.suffix.lower()),
                        enable_refinement,
                        enable_verification,
                    ): fp
                    for fp in source_files
                }
                for future in as_completed(futures):
                    fp = futures[future]
                    try:
                        result = future.result()
                    except Exception as exc:
                        logger.error("Error processing %s: %s", fp, exc)
                        result = {'success': False, 'file_path': str(fp), 'error': str(exc)}
                    file_results.append(result)
        else:
            for fp in source_files:
                lang = language or _LANG_MAP.get(fp.suffix.lower())
                result = self.process_file(
                    str(fp), lang, enable_refinement, enable_verification
                )
                file_results.append(result)

        elapsed = time.time() - start_ts

        return {
            'success': True,
            'directory': dir_path,
            'files_scanned': len(source_files),
            'files_with_vulnerabilities': sum(
                1 for r in file_results if r.get('vulnerabilities_found', 0) > 0
            ),
            'total_vulnerabilities': sum(
                r.get('vulnerabilities_found', 0) for r in file_results
            ),
            'total_processing_time': elapsed,
            'file_results': file_results,
            'directory_summary': self._generate_directory_summary(file_results),
        }

    # ------------------------------------------------------------------
    # Internal: single vulnerability
    # ------------------------------------------------------------------

    def _process_vulnerability(self, code: str, vulnerability: Dict,
                              language: str, parsed_code: Dict,
                              enable_refinement: bool,
                              enable_verification: bool) -> Dict:
        """Process a single vulnerability through the full pipeline."""
        
        start_time = time.time()
        vuln_type = vulnerability.get('type', 'Unknown')
        cwe = vulnerability.get('cwe', '')
        logger.debug("Processing %s (%s)", vuln_type, cwe)
        
        # Extract surrounding context
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
                'error': fix_result.get('error', 'Fix generation failed'),
            }
        
        current_fix = fix_result.get('fixed_code', '')
        iterations = 1
        
        # Multi-iteration refinement
        if enable_refinement:
            refinement_result = self.refinement_loop.refine(
                code, vulnerability, language, current_fix, context_code
            )
            
            if refinement_result.get('success', False):
                current_fix = refinement_result.get('fixed_code', current_fix)
                iterations = refinement_result.get('iterations', 1)
        
        # Exploit-based verification
        validation_result = None
        if enable_verification:
            validation_result = self.validator.validate(
                code, current_fix, vulnerability, language
            )
        
        processing_time = time.time() - start_time
        
        # Metrics
        code_similarity = self.metrics_calc.calculate_code_similarity(code, current_fix)
        
        exploit_passed = False
        static_passed = False
        
        if validation_result:
            exploit_passed = validation_result.get('exploit_test_passed', False)
            static_passed = validation_result.get('static_analysis_passed', False)
        
        fix_quality = self.metrics_calc.calculate_fix_quality(
            code, current_fix, exploit_passed, static_passed
        )
        
        logger.info(
            "Finished %s (%s) | static=%s exploit=%s iter=%d time=%.1fs",
            vuln_type, cwe, static_passed, exploit_passed, iterations, processing_time,
        )

        return {
            'vulnerability': vulnerability,
            'success': True,
            'fixed_code': current_fix,
            'full_response': fix_result.get('full_response', ''),
            'iterations': iterations,
            'processing_time': processing_time,
            'validation': validation_result,
            'metrics': {
                'code_similarity': code_similarity,
                'fix_quality_score': fix_quality,
                'exploit_test_passed': exploit_passed,
                'static_analysis_passed': static_passed
            },
            'model_used': fix_result.get('model_used', 'unknown'),
            'routing_decision': fix_result.get('routing_decision', {}),
        }
    
    # ------------------------------------------------------------------
    # Summaries
    # ------------------------------------------------------------------

    def _generate_summary(self, results: List[Dict]) -> Dict:
        """Aggregate metrics for a single file."""
        successful = sum(1 for r in results if r.get('success', False))
        total = len(results)
        
        total_time = sum(r.get('processing_time', 0) for r in results)
        avg_iterations = (
            sum(r.get('iterations', 1) for r in results) / total if total > 0 else 0
        )
        
        exploit_passed = sum(
            1 for r in results 
            if r.get('metrics', {}).get('exploit_test_passed', False)
        )
        static_passed = sum(
            1 for r in results 
            if r.get('metrics', {}).get('static_analysis_passed', False)
        )
        
        return {
            'total_vulnerabilities': total,
            'successful_repairs': successful,
            'success_rate': successful / total if total > 0 else 0,
            'exploit_verification_passed': exploit_passed,
            'static_analysis_passed': static_passed,
            'average_iterations': avg_iterations,
            'total_processing_time': total_time,
            'average_processing_time': total_time / total if total > 0 else 0,
        }

    def _generate_directory_summary(self, file_results: List[Dict]) -> Dict:
        """Aggregate metrics across all files in a directory scan."""
        all_results = []
        for fr in file_results:
            all_results.extend(fr.get('results', []))

        summary = self._generate_summary(all_results) if all_results else {}
        summary['files_processed'] = len(file_results)
        summary['files_clean'] = sum(
            1 for fr in file_results if fr.get('vulnerabilities_found', 0) == 0
        )
        return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Hybrid LLM-Based Vulnerability Repair Framework',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python src/main.py --input vuln.py --language python\n"
            "  python src/main.py --input ./my_project/ --recursive --workers 4\n"
            "  python src/main.py --input vuln.py --output results.json --verbose\n"
        ),
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
    parser.add_argument('--recursive', '-r', action='store_true', default=True,
                        help='Recurse into sub-directories (default: True)')
    parser.add_argument('--workers', '-w', type=int, default=1,
                        help='Number of parallel workers for directory mode (default: 1)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    framework = VulnerabilityRepairFramework()
    
    input_path = Path(args.input)
    
    # ── Single file ──────────────────────────────────────────────────────
    if input_path.is_file():
        result = framework.process_file(
            str(input_path),
            language=args.language,
            enable_refinement=not args.no_refinement,
            enable_verification=not args.no_verification,
        )
        
        if args.verbose:
            print(json.dumps(result, indent=2, default=str))
        else:
            summary = result.get('summary', {})
            print(f"\n{'='*60}")
            print(f"File : {input_path}")
            print(f"Lang : {result.get('language', 'unknown')}")
            print(f"{'='*60}")
            print(f"Vulnerabilities found   : {summary.get('total_vulnerabilities', 0)}")
            print(f"Successful repairs      : {summary.get('successful_repairs', 0)}")
            print(f"Success rate            : {summary.get('success_rate', 0):.1%}")
            print(f"Static analysis passed  : {summary.get('static_analysis_passed', 0)}")
            print(f"Exploit tests passed    : {summary.get('exploit_verification_passed', 0)}")
            print(f"Avg iterations          : {summary.get('average_iterations', 0):.1f}")
            print(f"Total time              : {summary.get('total_processing_time', 0):.2f}s")
            print(f"{'='*60}\n")
    
    # ── Directory ────────────────────────────────────────────────────────
    elif input_path.is_dir():
        print(f"\nScanning directory: {input_path}")
        result = framework.process_directory(
            str(input_path),
            language=args.language,
            enable_refinement=not args.no_refinement,
            enable_verification=not args.no_verification,
            recursive=args.recursive,
            parallel_workers=args.workers,
        )

        if args.verbose:
            print(json.dumps(result, indent=2, default=str))
        else:
            ds = result.get('directory_summary', {})
            print(f"\n{'='*60}")
            print(f"Directory : {input_path}")
            print(f"{'='*60}")
            print(f"Files scanned           : {result.get('files_scanned', 0)}")
            print(f"Files with vulns        : {result.get('files_with_vulnerabilities', 0)}")
            print(f"Files clean             : {ds.get('files_clean', 0)}")
            print(f"Total vulnerabilities   : {result.get('total_vulnerabilities', 0)}")
            print(f"Successful repairs      : {ds.get('successful_repairs', 0)}")
            print(f"Success rate            : {ds.get('success_rate', 0):.1%}")
            print(f"Exploit tests passed    : {ds.get('exploit_verification_passed', 0)}")
            print(f"Total time              : {result.get('total_processing_time', 0):.2f}s")
            print(f"{'='*60}\n")
    
    else:
        print(f"Error: '{args.input}' is not a valid file or directory.")
        raise SystemExit(1)

    # ── Save JSON output ─────────────────────────────────────────────────
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"Results saved to {args.output}")


if __name__ == '__main__':
    main()
