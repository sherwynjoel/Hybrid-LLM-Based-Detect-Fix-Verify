"""CodeLlama 13B local integration"""

import subprocess
import json
from typing import Dict, Optional, List
import requests
import os

from src.utils.config import config
from src.llm_models.prompt_engine import PromptEngine


class CodeLlamaLocal:
    """Local CodeLlama 13B integration using Ollama or Transformers"""
    
    def __init__(self, use_ollama: bool = True):
        self.use_ollama = use_ollama
        self.model_name = config.codellama_model
        self.prompt_engine = PromptEngine()
        # Check for custom Ollama port (default is 11434, but can be 11500)
        default_port = os.getenv("OLLAMA_PORT", "11434")
        ollama_host = os.getenv("OLLAMA_HOST", f"http://localhost:{default_port}")
        self.ollama_url = os.getenv("OLLAMA_URL", ollama_host)
        
    def generate_fix(self, code: str, vulnerability: Dict, 
                     language: str, context: Optional[str] = None) -> Dict:
        """Generate vulnerability fix using local CodeLlama"""
        
        prompt = self.prompt_engine.generate_repair_prompt(
            code, vulnerability, language, context
        )
        
        if self.use_ollama:
            return self._generate_with_ollama(prompt, language)
        else:
            return self._generate_with_transformers(prompt, language)
    
    def refine_fix(self, original_code: str, fixed_code: str,
                   feedback: List[str], language: str) -> Dict:
        """Refine existing fix based on feedback"""
        
        prompt = self.prompt_engine.generate_refinement_prompt(
            original_code, fixed_code, feedback, language
        )
        
        if self.use_ollama:
            return self._generate_with_ollama(prompt, language)
        else:
            return self._generate_with_transformers(prompt, language)
    
    def _generate_with_ollama(self, prompt: str, language: str) -> Dict:
        """Generate using Ollama API"""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": config.config.get('llm_models', {}).get('codellama', {}).get('temperature', 0.2),
                        "top_p": config.config.get('llm_models', {}).get('codellama', {}).get('top_p', 0.95),
                        "num_predict": config.config.get('llm_models', {}).get('codellama', {}).get('max_tokens', 2048)
                    }
                },
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get('response', '')
                
                # Extract code block from response
                fixed_code = self._extract_code_block(generated_text, language)
                
                return {
                    'fixed_code': fixed_code,
                    'full_response': generated_text,
                    'model': 'codellama-local',
                    'success': True
                }
            else:
                return {
                    'error': f"Ollama API error: {response.status_code}",
                    'success': False
                }
        except requests.exceptions.RequestException as e:
            return {
                'error': f"Ollama connection error: {str(e)}",
                'success': False
            }
    
    def _generate_with_transformers(self, prompt: str, language: str) -> Dict:
        """Generate using Transformers library (fallback)"""
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            # Load model (this would be cached in production)
            model_name = "codellama/CodeLlama-13b-Instruct-hf"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                device_map="auto"
            )
            
            # Tokenize and generate
            inputs = tokenizer(prompt, return_tensors="pt")
            outputs = model.generate(
                inputs.input_ids,
                max_length=inputs.input_ids.shape[1] + config.config.get('llm_models', {}).get('codellama', {}).get('max_tokens', 2048),
                temperature=config.config.get('llm_models', {}).get('codellama', {}).get('temperature', 0.2),
                top_p=config.config.get('llm_models', {}).get('codellama', {}).get('top_p', 0.95),
                do_sample=True
            )
            
            generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
            fixed_code = self._extract_code_block(generated_text, language)
            
            return {
                'fixed_code': fixed_code,
                'full_response': generated_text,
                'model': 'codellama-transformers',
                'success': True
            }
        except ImportError:
            return {
                'error': "Transformers library not available. Install with: pip install transformers torch",
                'success': False
            }
        except Exception as e:
            return {
                'error': f"Transformers generation error: {str(e)}",
                'success': False
            }
    
    def _extract_code_block(self, text: str, language: str) -> str:
        """Extract code block from LLM response"""
        import re
        
        # Look for code blocks with language specification
        code_block_pattern = f"```{language}\\n(.*?)```"
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        
        if matches:
            return matches[-1].strip()  # Return last match
        
        # Fallback: look for any code block
        code_block_pattern = "```\\n(.*?)```"
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        
        if matches:
            return matches[-1].strip()
        
        # Try with different code block formats
        code_block_pattern = "```(.*?)```"
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        if matches:
            # Filter out markdown code blocks that are explanations
            for match in reversed(matches):
                code = match.strip()
                # Skip if it looks like explanation text
                if not (code.startswith('python') or code.startswith('```') or 
                        len(code.split('\n')) < 3 or 
                        any(word in code.lower()[:100] for word in ['explanation', 'summary', 'note'])):
                    return code
        
        # If no code block found, return text after "Fixed Code:" or similar
        lines = text.split('\n')
        code_started = False
        code_lines = []
        
        keywords = ['fixed code', 'code:', 'solution:', 'fix:', 'corrected code']
        
        for line in lines:
            if any(keyword in line.lower() for keyword in keywords):
                code_started = True
                continue
            if code_started:
                if line.strip().startswith('```') or 'explanation' in line.lower():
                    break
                if line.strip():
                    code_lines.append(line)
        
        extracted = '\n'.join(code_lines).strip()
        
        # If still empty, try to extract the first substantial code-like block
        if not extracted or len(extracted) < 10:
            # Look for lines that look like code (have indentation, keywords, etc.)
            code_keywords = ['def ', 'class ', 'import ', 'if ', 'for ', 'while ', 'return ', 
                           'function', 'void', 'int ', 'public ', 'private ']
            for i, line in enumerate(lines):
                if any(keyword in line for keyword in code_keywords):
                    # Extract from this line to end or next explanation
                    code_lines = []
                    for j in range(i, len(lines)):
                        if 'explanation' in lines[j].lower() or 'summary' in lines[j].lower():
                            break
                        code_lines.append(lines[j])
                    extracted = '\n'.join(code_lines).strip()
                    if len(extracted) > 20:
                        break
        
        return extracted
    
    def is_available(self) -> bool:
        """Check if CodeLlama is available"""
        if self.use_ollama:
            try:
                response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get('models', [])
                    model_names = [m.get('name', '') for m in models]
                    return any(self.model_name in name for name in model_names)
                return False
            except:
                return False
        else:
            # Check if transformers is available
            try:
                import transformers
                return True
            except ImportError:
                return False

