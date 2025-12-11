"""Compare framework with baseline methods"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import json
from typing import Dict, List
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class ComparisonAnalyzer:
    """Compare framework performance with baselines"""
    
    def compare(self, framework_results: str, baseline_results: Dict[str, str]) -> Dict:
        """Compare framework with multiple baselines"""
        
        with open(framework_results, 'r') as f:
            framework = json.load(f)
        
        comparisons = {}
        
        for baseline_name, baseline_path in baseline_results.items():
            with open(baseline_path, 'r') as f:
                baseline = json.load(f)
            
            comparison = self._compare_single(framework, baseline)
            comparisons[baseline_name] = comparison
        
        return {
            'framework': framework.get('metrics', {}),
            'comparisons': comparisons
        }
    
    def _compare_single(self, framework: Dict, baseline: Dict) -> Dict:
        """Compare framework with single baseline"""
        framework_metrics = framework.get('metrics', {})
        baseline_metrics = baseline.get('metrics', {})
        
        return {
            'accuracy_improvement': (
                framework_metrics.get('accuracy', 0) - 
                baseline_metrics.get('accuracy', 0)
            ),
            'precision_improvement': (
                framework_metrics.get('precision', 0) - 
                baseline_metrics.get('precision', 0)
            ),
            'recall_improvement': (
                framework_metrics.get('recall', 0) - 
                baseline_metrics.get('recall', 0)
            ),
            'f1_improvement': (
                framework_metrics.get('f1_score', 0) - 
                baseline_metrics.get('f1_score', 0)
            ),
            'speed_improvement': (
                baseline_metrics.get('average_processing_time', 0) / 
                max(framework_metrics.get('average_processing_time', 1), 0.001)
            )
        }
    
    def generate_comparison_report(self, comparison: Dict, output_path: str):
        """Generate comparison report"""
        report = {
            'framework_metrics': comparison['framework'],
            'baseline_comparisons': comparison['comparisons']
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate visualization
        self._plot_comparison(comparison, output_path.replace('.json', '_comparison.png'))
    
    def _plot_comparison(self, comparison: Dict, output_path: str):
        """Generate comparison plots"""
        baselines = list(comparison['comparisons'].keys())
        metrics = ['accuracy', 'precision', 'recall', 'f1_score']
        
        framework_values = [
            comparison['framework'].get(m, 0) for m in metrics
        ]
        
        baseline_values = {
            name: [
                comparison['framework'].get(m, 0) + 
                comparison['comparisons'][name].get(f'{m}_improvement', 0)
                for m in metrics
            ]
            for name in baselines
        }
        
        # Create comparison plot
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x = range(len(metrics))
        width = 0.35
        
        ax.bar([i - width/2 for i in x], framework_values, width, 
              label='Our Framework', alpha=0.8)
        
        for i, baseline_name in enumerate(baselines):
            offset = width/2 + (i+1) * width / len(baselines)
            ax.bar([i + offset for i in x], baseline_values[baseline_name], 
                  width/len(baselines), label=baseline_name, alpha=0.8)
        
        ax.set_xlabel('Metrics')
        ax.set_ylabel('Score')
        ax.set_title('Framework Comparison')
        ax.set_xticks(x)
        ax.set_xticklabels(metrics)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()


def main():
    """CLI for comparison"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Compare framework with baselines')
    parser.add_argument('--framework', '-f', required=True,
                       help='Framework results JSON')
    parser.add_argument('--baselines', '-b', nargs='+', required=True,
                       help='Baseline results JSON files (format: name:path)')
    parser.add_argument('--output', '-o', required=True,
                       help='Output path for comparison report')
    
    args = parser.parse_args()
    
    # Parse baseline arguments
    baseline_dict = {}
    for baseline_arg in args.baselines:
        if ':' in baseline_arg:
            name, path = baseline_arg.split(':', 1)
            baseline_dict[name] = path
        else:
            baseline_dict[baseline_arg] = baseline_arg
    
    analyzer = ComparisonAnalyzer()
    comparison = analyzer.compare(args.framework, baseline_dict)
    analyzer.generate_comparison_report(comparison, args.output)
    
    print(f"Comparison report saved to {args.output}")
    print("\nImprovements:")
    for baseline_name, comp in comparison['comparisons'].items():
        print(f"\n{baseline_name}:")
        print(f"  Accuracy: {comp['accuracy_improvement']:+.2%}")
        print(f"  F1 Score: {comp['f1_improvement']:+.2f}")
        print(f"  Speed: {comp['speed_improvement']:.2f}x")


if __name__ == '__main__':
    main()

