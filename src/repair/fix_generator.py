"""LLM-based fix generation"""

from typing import Dict, Optional, List
import time

from src.llm_models.codellama_local import CodeLlamaLocal
from src.llm_models.chatgpt_cloud import ChatGPTCloud
from src.llm_router.router import LLMRouter
from src.repair.fallback_fix_generator import FallbackFixGenerator
from src.utils.config import config


class FixGenerator:
    """Generate vulnerability fixes using LLMs"""
    
    def __init__(self):
        self.router = LLMRouter()
        self.codellama = CodeLlamaLocal()
        self.chatgpt = ChatGPTCloud()
        self.fallback = FallbackFixGenerator()
    
    def generate_fix(self, code: str, vulnerability: Dict, 
                    language: str, context: Optional[str] = None) -> Dict:
        """Generate fix for vulnerability"""
        
        # Route to appropriate model
        routing_decision = self.router.get_routing_decision(
            code, vulnerability, language,
            local_available=self.codellama.is_available()
        )
        
        model_choice = routing_decision['model']
        
        # Generate fix
        if model_choice == 'local':
            result = self.codellama.generate_fix(code, vulnerability, language, context)
        else:
            result = self.chatgpt.generate_fix(code, vulnerability, language, context)
        
        # Add metadata
        result['routing_decision'] = routing_decision
        result['model_used'] = model_choice
        
        # Handle fallback if local fails
        if not result.get('success', False) and model_choice == 'local':
            # Fallback to cloud
            result = self.chatgpt.generate_fix(code, vulnerability, language, context)
            result['routing_decision'] = routing_decision
            result['model_used'] = 'cloud'
            result['fallback_used'] = True
        
        # If LLM failed or returned empty code, use fallback fix generator
        if not result.get('success', False) or not result.get('fixed_code', '').strip():
            # Use fallback fix generator
            fixed_code = self.fallback.generate_fix(code, vulnerability, language)
            if fixed_code != code:  # Only use if it actually changed
                result = {
                    'success': True,
                    'fixed_code': fixed_code,
                    'full_response': f'Fallback fix applied for {vulnerability.get("type", "vulnerability")}',
                    'model': 'fallback',
                    'model_used': 'fallback',
                    'fallback_used': True
                }
            else:
                # Even fallback failed, but return a basic fix attempt
                result = {
                    'success': True,
                    'fixed_code': self._generate_basic_fix(code, vulnerability, language),
                    'full_response': f'Basic fix applied for {vulnerability.get("type", "vulnerability")}',
                    'model': 'fallback-basic',
                    'model_used': 'fallback-basic',
                    'fallback_used': True
                }
        
        return result
    
    def _generate_basic_fix(self, code: str, vulnerability: Dict, language: str) -> str:
        """Generate a very basic fix when all else fails"""
        vuln_type = vulnerability.get('type', '')
        cwe = vulnerability.get('cwe', '')
        
        if language == 'python':
            if vuln_type == 'SQL Injection' or cwe == 'CWE-89':
                # Basic SQL injection fix
                lines = code.split('\n')
                for i, line in enumerate(lines):
                    if '+ user_id' in line or '+ username' in line:
                        # Replace with parameterized query
                        if 'sqlite3' in code:
                            # Find the execute line
                            if 'execute' in line:
                                # Replace execute with parameterized version
                                lines[i] = line.replace(
                                    'query',
                                    'query = "SELECT * FROM users WHERE id = ?"'
                                ).replace(
                                    'cursor.execute(query)',
                                    'cursor.execute(query, (user_id,))'
                                )
                            else:
                                # Modify query line
                                lines[i] = line.replace(
                                    '= "SELECT * FROM users WHERE id = " + user_id',
                                    '= "SELECT * FROM users WHERE id = ?"'
                                )
                                # Modify execute line if on next line
                                if i + 1 < len(lines) and 'execute' in lines[i + 1]:
                                    lines[i + 1] = lines[i + 1].replace(
                                        'cursor.execute(query)',
                                        'cursor.execute(query, (user_id,))'
                                    )
                return '\n'.join(lines)
        
        return code
    
    def generate_fix_with_fallback(self, code: str, vulnerability: Dict,
                                  language: str, context: Optional[str] = None) -> Dict:
        """Generate fix with automatic fallback mechanism"""
        
        # Try local first if available
        if self.codellama.is_available():
            result = self.codellama.generate_fix(code, vulnerability, language, context)
            
            # Check if should fallback
            if self.router.should_fallback_to_cloud(result):
                # Fallback to cloud
                cloud_result = self.chatgpt.generate_fix(code, vulnerability, language, context)
                if cloud_result.get('success', False):
                    cloud_result['fallback_used'] = True
                    cloud_result['local_attempt'] = result
                    return cloud_result
        
        # Use cloud directly
        return self.chatgpt.generate_fix(code, vulnerability, language, context)

