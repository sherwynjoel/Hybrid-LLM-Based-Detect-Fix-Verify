"""Evaluation metrics for vulnerability repair"""

from typing import Dict, List, Optional
import difflib
from dataclasses import dataclass


@dataclass
class RepairMetrics:
    """Metrics for a single repair"""
    vulnerability_id: str
    original_code: str
    fixed_code: str
    fix_quality_score: float
    code_similarity: float
    exploit_test_passed: bool
    static_analysis_passed: bool
    iteration_count: int
    processing_time: float


class MetricsCalculator:
    """Calculate various evaluation metrics"""
    
    def __init__(self):
        self.metrics_history: List[RepairMetrics] = []
    
    def calculate_code_similarity(self, code1: str, code2: str) -> float:
        """Calculate similarity between two code snippets"""
        return difflib.SequenceMatcher(None, code1, code2).ratio()
    
    def calculate_fix_quality(self, original: str, fixed: str, 
                             exploit_passed: bool, 
                             static_passed: bool) -> float:
        """Calculate overall fix quality score"""
        similarity = self.calculate_code_similarity(original, fixed)
        
        # Weighted scoring
        weights = {
            'similarity': 0.3,
            'exploit': 0.4,
            'static': 0.3
        }
        
        score = (
            similarity * weights['similarity'] +
            (1.0 if exploit_passed else 0.0) * weights['exploit'] +
            (1.0 if static_passed else 0.0) * weights['static']
        )
        
        return score
    
    def calculate_accuracy(self, metrics_list: List[RepairMetrics]) -> float:
        """Calculate overall accuracy (percentage of successful fixes)"""
        if not metrics_list:
            return 0.0
        
        successful = sum(1 for m in metrics_list 
                        if m.exploit_test_passed and m.static_analysis_passed)
        return successful / len(metrics_list)
    
    def calculate_precision(self, metrics_list: List[RepairMetrics]) -> float:
        """Calculate precision (true positives / (true positives + false positives))"""
        if not metrics_list:
            return 0.0
        
        true_positives = sum(1 for m in metrics_list 
                           if m.exploit_test_passed and m.static_analysis_passed)
        false_positives = sum(1 for m in metrics_list 
                            if not m.exploit_test_passed and m.static_analysis_passed)
        
        total = true_positives + false_positives
        return true_positives / total if total > 0 else 0.0
    
    def calculate_recall(self, metrics_list: List[RepairMetrics]) -> float:
        """Calculate recall (true positives / (true positives + false negatives))"""
        if not metrics_list:
            return 0.0
        
        true_positives = sum(1 for m in metrics_list 
                           if m.exploit_test_passed and m.static_analysis_passed)
        false_negatives = sum(1 for m in metrics_list 
                            if m.exploit_test_passed and not m.static_analysis_passed)
        
        total = true_positives + false_negatives
        return true_positives / total if total > 0 else 0.0
    
    def calculate_f1_score(self, precision: float, recall: float) -> float:
        """Calculate F1 score"""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    def calculate_average_iterations(self, metrics_list: List[RepairMetrics]) -> float:
        """Calculate average number of iterations per repair"""
        if not metrics_list:
            return 0.0
        return sum(m.iteration_count for m in metrics_list) / len(metrics_list)
    
    def calculate_average_time(self, metrics_list: List[RepairMetrics]) -> float:
        """Calculate average processing time per repair"""
        if not metrics_list:
            return 0.0
        return sum(m.processing_time for m in metrics_list) / len(metrics_list)
    
    def generate_report(self, metrics_list: List[RepairMetrics]) -> Dict:
        """Generate comprehensive evaluation report"""
        accuracy = self.calculate_accuracy(metrics_list)
        precision = self.calculate_precision(metrics_list)
        recall = self.calculate_recall(metrics_list)
        f1 = self.calculate_f1_score(precision, recall)
        avg_iterations = self.calculate_average_iterations(metrics_list)
        avg_time = self.calculate_average_time(metrics_list)
        
        return {
            'total_repairs': len(metrics_list),
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'average_iterations': avg_iterations,
            'average_processing_time': avg_time,
            'successful_repairs': sum(1 for m in metrics_list 
                                    if m.exploit_test_passed and m.static_analysis_passed),
            'failed_repairs': sum(1 for m in metrics_list 
                                if not (m.exploit_test_passed and m.static_analysis_passed))
        }




