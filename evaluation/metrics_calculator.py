"""Calculate evaluation metrics"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, List
import json

from src.utils.metrics import MetricsCalculator, RepairMetrics


class EvaluationMetricsCalculator:
    """Calculate comprehensive evaluation metrics"""
    
    def __init__(self):
        self.metrics_calc = MetricsCalculator()
    
    def calculate_from_results(self, results_path: str) -> Dict:
        """Calculate metrics from results file"""
        with open(results_path, 'r') as f:
            results = json.load(f)
        
        metrics_list = []
        
        for result in results.get('results', []):
            if result.get('success', False):
                metrics = RepairMetrics(
                    vulnerability_id=result.get('id', 'unknown'),
                    original_code=result.get('vulnerability', {}).get('code', ''),
                    fixed_code=result.get('fixed_code', ''),
                    fix_quality_score=result.get('metrics', {}).get('fix_quality_score', 0),
                    code_similarity=result.get('metrics', {}).get('code_similarity', 0),
                    exploit_test_passed=result.get('metrics', {}).get('exploit_test_passed', False),
                    static_analysis_passed=result.get('metrics', {}).get('static_analysis_passed', False),
                    iteration_count=result.get('iterations', 1),
                    processing_time=result.get('processing_time', 0)
                )
                metrics_list.append(metrics)
        
        return self.metrics_calc.generate_report(metrics_list)
    
    def compare_methods(self, results_paths: Dict[str, str]) -> Dict:
        """Compare multiple methods"""
        comparisons = {}
        
        for method_name, path in results_paths.items():
            metrics = self.calculate_from_results(path)
            comparisons[method_name] = metrics
        
        return comparisons


def main():
    """CLI for metrics calculation"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Calculate evaluation metrics')
    parser.add_argument('--results', '-r', required=True,
                       help='Path to results JSON file')
    parser.add_argument('--output', '-o',
                       help='Output path for metrics (JSON)')
    
    args = parser.parse_args()
    
    calc = EvaluationMetricsCalculator()
    metrics = calc.calculate_from_results(args.results)
    
    print("Evaluation Metrics:")
    print(f"Accuracy: {metrics['accuracy']:.2%}")
    print(f"Precision: {metrics['precision']:.2f}")
    print(f"Recall: {metrics['recall']:.2f}")
    print(f"F1 Score: {metrics['f1_score']:.2f}")
    print(f"Average iterations: {metrics['average_iterations']:.2f}")
    print(f"Average processing time: {metrics['average_processing_time']:.2f}s")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"\nMetrics saved to {args.output}")


if __name__ == '__main__':
    main()

