"""Intelligent router for selecting between local and cloud LLMs"""

from typing import Dict, List, Optional
import re

from src.utils.config import config
from src.utils.code_parser import CodeParser


class LLMRouter:
    """Intelligent router for LLM selection"""
    
    def __init__(self):
        self.parser = CodeParser()
        self.privacy_keywords = config.config.get('router', {}).get('privacy_keywords', [])
    
    def route(self, code: str, vulnerability: Dict, language: str) -> str:
        """
        Route to appropriate LLM model
        Returns: 'local' or 'cloud'
        """
        # Check privacy requirements
        if self._requires_privacy(code, vulnerability):
            return 'local'
        
        # Check complexity
        complexity_score = self._calculate_complexity(code, vulnerability, language)
        if complexity_score > config.complexity_threshold:
            return 'cloud'
        
        # Check vulnerability severity
        severity = vulnerability.get('severity', 'MEDIUM').upper()
        if severity in ['CRITICAL', 'HIGH']:
            return 'cloud'
        
        # Default to local for efficiency
        return 'local'
    
    def _requires_privacy(self, code: str, vulnerability: Dict) -> bool:
        """Check if code contains sensitive information requiring local processing"""
        code_lower = code.lower()
        
        for keyword in self.privacy_keywords:
            if keyword.lower() in code_lower:
                return True
        
        # Check for API keys, tokens, credentials in context
        context = vulnerability.get('context', '')
        sensitive_patterns = [
            r'api[_-]?key\s*[:=]\s*["\'][^"\']+["\']',
            r'token\s*[:=]\s*["\'][^"\']+["\']',
            r'password\s*[:=]\s*["\'][^"\']+["\']',
            r'secret\s*[:=]\s*["\'][^"\']+["\']',
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, context, re.IGNORECASE):
                return True
        
        return False
    
    def _calculate_complexity(self, code: str, vulnerability: Dict, language: str) -> int:
        """Calculate code complexity score"""
        complexity = 0
        
        # Base complexity from code size
        complexity += len(code.split('\n')) * 0.5
        
        # Add complexity for nested structures
        if language == 'python':
            complexity += code.count('def ') * 5
            complexity += code.count('class ') * 10
            complexity += code.count('try:') * 3
            complexity += code.count('except') * 3
        elif language in ['cpp', 'c', 'java']:
            complexity += code.count('{') * 2
            complexity += code.count('}') * 2
            complexity += code.count('if') * 2
            complexity += code.count('for') * 2
            complexity += code.count('while') * 2
        
        # Add complexity based on vulnerability context size
        context = vulnerability.get('context', '')
        complexity += len(context.split('\n')) * 2
        
        # Add complexity for multiple vulnerabilities in same file
        # (This would be passed as parameter in real implementation)
        
        return int(complexity)
    
    def should_fallback_to_cloud(self, local_result: Optional[Dict], 
                                 max_retries: int = 2) -> bool:
        """Determine if should fallback to cloud after local failure"""
        if local_result is None:
            return True
        
        # Check if local model produced low-quality result
        if 'quality_score' in local_result:
            if local_result['quality_score'] < config.local_threshold:
                return True
        
        # Check if fix failed verification
        if 'verification_passed' in local_result:
            if not local_result['verification_passed']:
                return True
        
        return False
    
    def get_routing_decision(self, code: str, vulnerability: Dict, 
                           language: str, local_available: bool = True) -> Dict:
        """Get detailed routing decision"""
        decision = self.route(code, vulnerability, language)
        
        reasons = []
        
        if self._requires_privacy(code, vulnerability):
            reasons.append("Privacy-sensitive code detected")
        
        complexity = self._calculate_complexity(code, vulnerability, language)
        if complexity > config.complexity_threshold:
            reasons.append(f"High complexity ({complexity})")
        
        severity = vulnerability.get('severity', 'MEDIUM')
        if severity in ['CRITICAL', 'HIGH']:
            reasons.append(f"High severity vulnerability ({severity})")
        
        if not local_available:
            decision = 'cloud'
            reasons.append("Local model not available")
        
        return {
            'model': decision,
            'reasons': reasons,
            'complexity_score': complexity,
            'privacy_required': self._requires_privacy(code, vulnerability)
        }



