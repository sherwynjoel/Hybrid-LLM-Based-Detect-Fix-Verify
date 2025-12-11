"""LLM-based fix generation"""

from typing import Dict, Optional, List
import time

from src.llm_models.codellama_local import CodeLlamaLocal
from src.llm_models.chatgpt_cloud import ChatGPTCloud
from src.llm_router.router import LLMRouter
from src.utils.config import config


class FixGenerator:
    """Generate vulnerability fixes using LLMs"""
    
    def __init__(self):
        self.router = LLMRouter()
        self.codellama = CodeLlamaLocal()
        self.chatgpt = ChatGPTCloud()
    
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
        
        return result
    
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

