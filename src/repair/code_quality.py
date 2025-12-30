"""Code quality metrics calculation"""

from typing import Dict, List
import re


class CodeQualityAnalyzer:
    """Analyze code quality metrics"""
    
    def analyze(self, code: str, language: str) -> Dict:
        """Analyze code quality metrics"""
        metrics = {
            'readability_score': self._calculate_readability(code, language),
            'maintainability_score': self._calculate_maintainability(code, language),
            'complexity': self._calculate_complexity(code, language),
            'security_score': self._calculate_security_score(code, language)
        }
        
        metrics['overall_score'] = (
            metrics['readability_score'] * 0.3 +
            metrics['maintainability_score'] * 0.3 +
            metrics['security_score'] * 0.4
        )
        
        return metrics
    
    def _calculate_readability(self, code: str, language: str) -> float:
        """Calculate code readability score (0-1)"""
        lines = code.split('\n')
        if not lines:
            return 0.0
        
        score = 1.0
        
        # Penalize very long lines
        long_lines = sum(1 for line in lines if len(line) > 120)
        score -= (long_lines / len(lines)) * 0.2
        
        # Penalize very long functions
        if language == 'python':
            function_count = code.count('def ')
            if function_count > 0:
                avg_function_length = len(lines) / function_count
                if avg_function_length > 50:
                    score -= 0.2
        
        # Reward comments
        comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
        if len(lines) > 0:
            comment_ratio = comment_lines / len(lines)
            score += min(comment_ratio * 0.3, 0.3)
        
        return max(0.0, min(1.0, score))
    
    def _calculate_maintainability(self, code: str, language: str) -> float:
        """Calculate maintainability score (0-1)"""
        score = 1.0
        
        # Penalize high cyclomatic complexity indicators
        if language == 'python':
            nested_depth = code.count('    ') / max(code.count('\n'), 1)
            if nested_depth > 3:
                score -= 0.2
            
            # Check for magic numbers
            magic_numbers = len(re.findall(r'\b\d{3,}\b', code))
            if magic_numbers > 5:
                score -= 0.1
        
        # Reward consistent naming
        # Simple heuristic: check for consistent naming patterns
        if language == 'python':
            functions = re.findall(r'def\s+(\w+)', code)
            if functions:
                # Check naming consistency
                snake_case = sum(1 for f in functions if '_' in f or f.islower())
                consistency = snake_case / len(functions)
                score += consistency * 0.2
        
        return max(0.0, min(1.0, score))
    
    def _calculate_complexity(self, code: str, language: str) -> int:
        """Calculate code complexity"""
        complexity = 0
        
        # Count control flow statements
        if language == 'python':
            complexity += code.count('if ')
            complexity += code.count('elif ')
            complexity += code.count('for ')
            complexity += code.count('while ')
            complexity += code.count('except')
            complexity += code.count('try:')
        elif language in ['cpp', 'c', 'java']:
            complexity += code.count('if ')
            complexity += code.count('for ')
            complexity += code.count('while ')
            complexity += code.count('switch')
            complexity += code.count('catch')
        
        # Count nested structures
        complexity += code.count('{') // 2
        
        return complexity
    
    def _calculate_security_score(self, code: str, language: str) -> float:
        """Calculate security score based on security best practices"""
        score = 1.0
        
        # Check for unsafe patterns
        unsafe_patterns = {
            'python': [
                (r'eval\s*\(', 0.3),
                (r'exec\s*\(', 0.3),
                (r'__import__', 0.2),
                (r'pickle\.loads', 0.2),
            ],
            'cpp': [
                (r'strcpy\s*\(', 0.3),
                (r'strcat\s*\(', 0.3),
                (r'gets\s*\(', 0.4),
                (r'sprintf\s*\(', 0.2),
            ],
            'java': [
                (r'Runtime\.exec', 0.3),
                (r'ProcessBuilder', 0.2),
            ]
        }
        
        patterns = unsafe_patterns.get(language, [])
        for pattern, penalty in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                score -= penalty
        
        # Reward secure patterns
        secure_patterns = {
            'python': [
                (r'parameterized|prepared|execute\(.*\?', 0.2),
                (r'escape\(|html\.escape', 0.2),
                (r'validate|sanitize', 0.1),
            ],
            'cpp': [
                (r'strncpy|strncat', 0.2),
                (r'snprintf', 0.2),
            ],
            'java': [
                (r'PreparedStatement', 0.2),
                (r'validate|sanitize', 0.1),
            ]
        }
        
        patterns = secure_patterns.get(language, [])
        for pattern, bonus in patterns:
            if re.search(pattern, code, re.IGNORECASE):
                score += bonus
        
        return max(0.0, min(1.0, score))
    
    def compare_quality(self, original: Dict, fixed: Dict) -> Dict:
        """Compare quality between original and fixed code"""
        return {
            'readability_improvement': fixed['readability_score'] - original['readability_score'],
            'maintainability_improvement': fixed['maintainability_score'] - original['maintainability_score'],
            'security_improvement': fixed['security_score'] - original['security_score'],
            'overall_improvement': fixed['overall_score'] - original['overall_score'],
            'complexity_change': fixed['complexity'] - original['complexity']
        }




