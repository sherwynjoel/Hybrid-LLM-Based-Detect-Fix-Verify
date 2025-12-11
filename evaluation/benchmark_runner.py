"""Run benchmarks on vulnerability repair framework"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
import time
from typing import Dict, List
import pandas as pd

from src.main import VulnerabilityRepairFramework
from src.utils.metrics import MetricsCalculator, RepairMetrics


class BenchmarkRunner:
    """Run comprehensive benchmarks"""
    
    def __init__(self):
        self.framework = VulnerabilityRepairFramework()
        self.metrics_calc = MetricsCalculator()
    
    def run_benchmark(self, dataset_path: str, output_path: str = None) -> Dict:
        """Run benchmark on dataset"""
        
        dataset = self._load_dataset(dataset_path)
        
        results = []
        metrics_list = []
        
        for item in dataset:
            result = self._process_benchmark_item(item)
            results.append(result)
            
            # Create metrics object
            if result.get('success', False):
                metrics = RepairMetrics(
                    vulnerability_id=item.get('id', 'unknown'),
                    original_code=item.get('vulnerable_code', ''),
                    fixed_code=result.get('fixed_code', ''),
                    fix_quality_score=result.get('metrics', {}).get('fix_quality_score', 0),
                    code_similarity=result.get('metrics', {}).get('code_similarity', 0),
                    exploit_test_passed=result.get('metrics', {}).get('exploit_test_passed', False),
                    static_analysis_passed=result.get('metrics', {}).get('static_analysis_passed', False),
                    iteration_count=result.get('iterations', 1),
                    processing_time=result.get('processing_time', 0)
                )
                metrics_list.append(metrics)
        
        # Calculate overall metrics
        report = self.metrics_calc.generate_report(metrics_list)
        
        benchmark_result = {
            'dataset': dataset_path,
            'total_items': len(dataset),
            'results': results,
            'metrics': report,
            'timestamp': time.time()
        }
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(benchmark_result, f, indent=2)
        
        return benchmark_result
    
    def _load_dataset(self, dataset_path: str) -> List[Dict]:
        """Load benchmark dataset"""
        path = Path(dataset_path)
        
        if path.suffix == '.json':
            with open(path, 'r') as f:
                return json.load(f)
        elif path.suffix == '.jsonl':
            dataset = []
            with open(path, 'r') as f:
                for line in f:
                    dataset.append(json.loads(line))
            return dataset
        else:
            raise ValueError(f"Unsupported dataset format: {path.suffix}")
    
    def _process_benchmark_item(self, item: Dict) -> Dict:
        """Process a single benchmark item"""
        code = item.get('vulnerable_code', '')
        language = item.get('language', 'python')
        expected_fix = item.get('fixed_code', None)
        
        # Detect vulnerabilities
        vulnerabilities = self.framework.detector.detect(code, language)
        
        if not vulnerabilities:
            return {
                'id': item.get('id', 'unknown'),
                'success': False,
                'error': 'No vulnerabilities detected'
            }
        
        # Process first vulnerability (or all if needed)
        vuln = vulnerabilities[0]
        
        result = self.framework._process_vulnerability(
            code, vuln, language, {},
            enable_refinement=True,
            enable_verification=True
        )
        
        result['id'] = item.get('id', 'unknown')
        result['expected_fix'] = expected_fix
        
        # Compare with expected fix if available
        if expected_fix:
            similarity = self.metrics_calc.calculate_code_similarity(
                result.get('fixed_code', ''),
                expected_fix
            )
            result['expected_similarity'] = similarity
        
        return result
    
    def compare_with_baseline(self, results: Dict, baseline_path: str) -> Dict:
        """Compare results with baseline method"""
        with open(baseline_path, 'r') as f:
            baseline = json.load(f)
        
        comparison = {
            'framework_accuracy': results['metrics']['accuracy'],
            'baseline_accuracy': baseline.get('accuracy', 0),
            'improvement': results['metrics']['accuracy'] - baseline.get('accuracy', 0),
            'framework_f1': results['metrics']['f1_score'],
            'baseline_f1': baseline.get('f1_score', 0),
            'f1_improvement': results['metrics']['f1_score'] - baseline.get('f1_score', 0)
        }
        
        return comparison


def main():
    """CLI for benchmark runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Run vulnerability repair benchmarks')
    parser.add_argument('--dataset', '-d', required=True,
                       help='Path to benchmark dataset (JSON/JSONL)')
    parser.add_argument('--output', '-o', required=True,
                       help='Output path for results')
    parser.add_argument('--baseline', '-b',
                       help='Path to baseline results for comparison')
    
    args = parser.parse_args()
    
    runner = BenchmarkRunner()
    results = runner.run_benchmark(args.dataset, args.output)
    
    print(f"Benchmark completed: {args.dataset}")
    print(f"Total items: {results['metrics']['total_repairs']}")
    print(f"Accuracy: {results['metrics']['accuracy']:.2%}")
    print(f"F1 Score: {results['metrics']['f1_score']:.2f}")
    print(f"Average iterations: {results['metrics']['average_iterations']:.2f}")
    
    if args.baseline:
        comparison = runner.compare_with_baseline(results, args.baseline)
        print(f"\nComparison with baseline:")
        print(f"Accuracy improvement: {comparison['improvement']:.2%}")
        print(f"F1 improvement: {comparison['f1_improvement']:.2f}")


if __name__ == '__main__':
    main()

