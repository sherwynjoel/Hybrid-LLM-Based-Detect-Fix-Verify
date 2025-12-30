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
        self.privacy_first_mode = True  # Default: Privacy-first mode enabled
    
    def route(self, code: str, vulnerability: Dict, language: str) -> str:
        """
        Route to appropriate LLM model
        
        Privacy-First Mode (privacy_first_mode=True):
        - Sensitive code (passwords, secrets, credentials) → Local LLM (privacy)
        - Normal code → Cloud LLM (better accuracy)
        - Complex code → Cloud LLM (if not sensitive)
        
        Efficiency Mode (privacy_first_mode=False):
        - Sensitive code → Local LLM (always, for security)
        - Simple code → Local LLM (efficiency)
        - Complex/High severity → Cloud LLM (accuracy)
        
        Returns: 'local' or 'cloud'
        """
        # PRIORITY 1: Check privacy/security requirements FIRST
        # Sensitive code MUST stay local for privacy and security (always)
        if self._requires_privacy(code, vulnerability):
            return 'local'
        
        # If privacy-first mode is disabled, use efficiency-based routing
        if not self.privacy_first_mode:
            # Efficiency Mode: Default to local for efficiency
            complexity_score = self._calculate_complexity(code, vulnerability, language)
            if complexity_score > config.complexity_threshold:
                return 'cloud'
            
            severity = vulnerability.get('severity', 'MEDIUM').upper()
            if severity in ['CRITICAL', 'HIGH']:
                return 'cloud'
            
            # Default to local for efficiency
            return 'local'
        
        # Privacy-First Mode: Default to cloud for better accuracy
        # Check complexity - complex code benefits from cloud LLM
        complexity_score = self._calculate_complexity(code, vulnerability, language)
        if complexity_score > config.complexity_threshold:
            return 'cloud'
        
        # High severity vulnerabilities benefit from cloud accuracy
        severity = vulnerability.get('severity', 'MEDIUM').upper()
        if severity in ['CRITICAL', 'HIGH']:
            return 'cloud'
        
        # DEFAULT: Normal code goes to cloud for better accuracy
        # (Only sensitive code goes to local)
        return 'cloud'
    
    def _requires_privacy(self, code: str, vulnerability: Dict) -> bool:
        """
        Check if code contains sensitive information requiring local processing
        
        Detects:
        - Passwords, secrets, API keys, tokens
        - Security codes, encryption keys
        - Credentials, authentication data
        - Personal identifiable information (PII)
        - Financial information
        """
        code_lower = code.lower()
        full_code = code  # Search in full code, not just lowercased
        
        # Check privacy keywords in code
        for keyword in self.privacy_keywords:
            if keyword.lower() in code_lower:
                return True
        
        # Enhanced sensitive pattern detection
        sensitive_patterns = [
            # Passwords and credentials
            r'password\s*[:=]\s*["\'][^"\']+["\']',
            r'passwd\s*[:=]\s*["\'][^"\']+["\']',
            r'pwd\s*[:=]\s*["\'][^"\']+["\']',
            r'credential\s*[:=]\s*["\'][^"\']+["\']',
            r'auth\s*[:=]\s*["\'][^"\']+["\']',
            
            # API keys and tokens
            r'api[_-]?key\s*[:=]\s*["\'][^"\']+["\']',
            r'apikey\s*[:=]\s*["\'][^"\']+["\']',
            r'token\s*[:=]\s*["\'][^"\']+["\']',
            r'access[_-]?token\s*[:=]\s*["\'][^"\']+["\']',
            r'bearer[_-]?token\s*[:=]\s*["\'][^"\']+["\']',
            
            # Secrets and keys
            r'secret\s*[:=]\s*["\'][^"\']+["\']',
            r'secret[_-]?key\s*[:=]\s*["\'][^"\']+["\']',
            r'private[_-]?key\s*[:=]\s*["\'][^"\']+["\']',
            r'encryption[_-]?key\s*[:=]\s*["\'][^"\']+["\']',
            r'decryption[_-]?key\s*[:=]\s*["\'][^"\']+["\']',
            
            # Security codes
            r'security[_-]?code\s*[:=]\s*["\'][^"\']+["\']',
            r'pin\s*[:=]\s*["\'][^"\']+["\']',
            r'passcode\s*[:=]\s*["\'][^"\']+["\']',
            
            # Database credentials
            r'db[_-]?password\s*[:=]\s*["\'][^"\']+["\']',
            r'database[_-]?password\s*[:=]\s*["\'][^"\']+["\']',
            r'connection[_-]?string\s*[:=]\s*["\'][^"\']+["\']',
            
            # OAuth and authentication
            r'oauth[_-]?secret\s*[:=]\s*["\'][^"\']+["\']',
            r'client[_-]?secret\s*[:=]\s*["\'][^"\']+["\']',
            r'jwt[_-]?secret\s*[:=]\s*["\'][^"\']+["\']',
        ]
        
        # Check patterns in code
        for pattern in sensitive_patterns:
            if re.search(pattern, full_code, re.IGNORECASE):
                return True
        
        # Check in vulnerability context
        context = vulnerability.get('context', '')
        if context:
            for pattern in sensitive_patterns:
                if re.search(pattern, context, re.IGNORECASE):
                    return True
        
        # Check for hardcoded sensitive values (long strings that look like keys)
        # Look for patterns like: key = "sk_live_..." or password = "Abc123..."
        hardcoded_patterns = [
            r'["\'](sk_[a-zA-Z0-9_]{20,})["\']',  # Stripe-like keys
            r'["\'](pk_[a-zA-Z0-9_]{20,})["\']',  # Public keys
            r'["\']([a-zA-Z0-9+/]{40,}={0,2})["\']',  # Base64-like secrets
        ]
        
        for pattern in hardcoded_patterns:
            if re.search(pattern, full_code):
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
            reasons.append("🔒 Privacy-sensitive code detected - routing to Local LLM for security")
        
        if not self.privacy_first_mode:
            reasons.append("⚡ Efficiency Mode: Using default routing strategy")
        
        complexity = self._calculate_complexity(code, vulnerability, language)
        if complexity > config.complexity_threshold:
            if self.privacy_first_mode:
                reasons.append(f"High complexity ({complexity}) - routing to Cloud LLM for better accuracy")
            else:
                reasons.append(f"High complexity ({complexity}) - routing to Cloud LLM")
        
        severity = vulnerability.get('severity', 'MEDIUM')
        if severity in ['CRITICAL', 'HIGH']:
            if self.privacy_first_mode:
                reasons.append(f"High severity vulnerability ({severity}) - routing to Cloud LLM for better accuracy")
            else:
                reasons.append(f"High severity vulnerability ({severity}) - routing to Cloud LLM")
        
        if not self._requires_privacy(code, vulnerability):
            if self.privacy_first_mode and decision == 'cloud':
                reasons.append("Normal code - routing to Cloud LLM for optimal accuracy")
            elif not self.privacy_first_mode and decision == 'local':
                reasons.append("Simple code - routing to Local LLM for efficiency")
        
        if not local_available:
            if self._requires_privacy(code, vulnerability):
                reasons.append("⚠️ WARNING: Local model not available but sensitive code detected!")
            else:
                decision = 'cloud'
                reasons.append("Local model not available - using Cloud LLM")
        
        return {
            'model': decision,
            'reasons': reasons,
            'complexity_score': complexity,
            'privacy_required': self._requires_privacy(code, vulnerability)
        }



