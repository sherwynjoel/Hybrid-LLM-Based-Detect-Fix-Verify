"""ChatGPT-4 cloud integration"""

from typing import Dict, Optional, List
import os
from openai import OpenAI

from src.utils.config import config
from src.llm_models.prompt_engine import PromptEngine


class ChatGPTCloud:
    """ChatGPT-4 cloud API integration"""
    
    def __init__(self):
        api_key = config.openai_api_key
        if not api_key:
            # Don't raise error, just mark as unavailable
            self.client = None
            self.model_name = config.chatgpt_model
            self.prompt_engine = PromptEngine()
            return
        
        self.client = OpenAI(api_key=api_key)
        self.model_name = config.chatgpt_model
        self.prompt_engine = PromptEngine()
    
    def generate_fix(self, code: str, vulnerability: Dict,
                    language: str, context: Optional[str] = None) -> Dict:
        """Generate vulnerability fix using ChatGPT-4"""
        
        if self.client is None:
            return {
                'error': 'ChatGPT API key not configured. Set OPENAI_API_KEY environment variable.',
                'success': False
            }
        
        prompt = self.prompt_engine.generate_repair_prompt(
            code, vulnerability, language, context
        )
        
        system_prompt = self.prompt_engine.get_system_prompt(
            vulnerability.get('cwe', 'UNKNOWN')
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.config.get('llm_models', {}).get('chatgpt', {}).get('temperature', 0.3),
                max_tokens=config.config.get('llm_models', {}).get('chatgpt', {}).get('max_tokens', 2048),
                top_p=config.config.get('llm_models', {}).get('chatgpt', {}).get('top_p', 0.95)
            )
            
            generated_text = response.choices[0].message.content
            fixed_code = self._extract_code_block(generated_text, language)
            
            return {
                'fixed_code': fixed_code,
                'full_response': generated_text,
                'model': 'chatgpt-4',
                'success': True,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
        except Exception as e:
            return {
                'error': f"ChatGPT API error: {str(e)}",
                'success': False
            }
    
    def refine_fix(self, original_code: str, fixed_code: str,
                   feedback: List[str], language: str) -> Dict:
        """Refine existing fix based on feedback"""
        
        if self.client is None:
            return {
                'error': 'ChatGPT API key not configured. Set OPENAI_API_KEY environment variable.',
                'success': False
            }
        
        prompt = self.prompt_engine.generate_refinement_prompt(
            original_code, fixed_code, feedback, language
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are an expert security engineer refining code fixes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.config.get('llm_models', {}).get('chatgpt', {}).get('temperature', 0.3),
                max_tokens=config.config.get('llm_models', {}).get('chatgpt', {}).get('max_tokens', 2048)
            )
            
            generated_text = response.choices[0].message.content
            refined_code = self._extract_code_block(generated_text, language)
            
            return {
                'fixed_code': refined_code,
                'full_response': generated_text,
                'model': 'chatgpt-4',
                'success': True,
                'usage': {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            }
        except Exception as e:
            return {
                'error': f"ChatGPT API error: {str(e)}",
                'success': False
            }
    
    def generate_exploit(self, code: str, vulnerability: Dict, language: str) -> Dict:
        """Generate PoC exploit for verification"""
        
        if self.client is None:
            return {
                'error': 'ChatGPT API key not configured. Set OPENAI_API_KEY environment variable.',
                'success': False
            }
        
        prompt = self.prompt_engine.generate_exploit_prompt(code, vulnerability, language)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a security researcher creating safe PoC exploits for testing."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1024
            )
            
            generated_text = response.choices[0].message.content
            exploit_code = self._extract_code_block(generated_text, language)
            
            return {
                'exploit_code': exploit_code,
                'full_response': generated_text,
                'success': True
            }
        except Exception as e:
            return {
                'error': f"ChatGPT API error: {str(e)}",
                'success': False
            }
    
    def _extract_code_block(self, text: str, language: str) -> str:
        """Extract code block from LLM response"""
        import re
        
        # Look for code blocks with language specification
        code_block_pattern = f"```{language}\\n(.*?)```"
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        
        if matches:
            return matches[-1].strip()
        
        # Fallback: look for any code block
        code_block_pattern = "```\\n(.*?)```"
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        
        if matches:
            return matches[-1].strip()
        
        # If no code block found, try to extract after keywords
        lines = text.split('\n')
        code_started = False
        code_lines = []
        
        keywords = ['fixed code', 'code:', 'solution:', 'fix:']
        
        for line in lines:
            if any(keyword in line.lower() for keyword in keywords):
                code_started = True
                continue
            if code_started:
                if line.strip().startswith('```') or line.strip().startswith('explanation'):
                    break
                if line.strip():
                    code_lines.append(line)
        
        return '\n'.join(code_lines).strip()
    
    def is_available(self) -> bool:
        """Check if ChatGPT API is available"""
        return self.client is not None and bool(config.openai_api_key)

