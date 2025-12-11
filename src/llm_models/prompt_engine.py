"""Context-aware prompt generation for LLMs"""

from typing import Dict, List, Optional


class PromptEngine:
    """Generate context-aware prompts for vulnerability repair"""
    
    def __init__(self):
        self.system_prompts = self._load_system_prompts()
    
    def generate_repair_prompt(self, code: str, vulnerability: Dict, 
                              language: str, context: Optional[str] = None) -> str:
        """Generate prompt for vulnerability repair"""
        
        cwe = vulnerability.get('cwe', 'UNKNOWN')
        severity = vulnerability.get('severity', 'MEDIUM')
        line_num = vulnerability.get('line', 0)
        message = vulnerability.get('message', '')
        
        prompt = f"""You are an expert security engineer tasked with fixing a {severity} severity vulnerability in {language} code.

Vulnerability Details:
- CWE ID: {cwe}
- Severity: {severity}
- Location: Line {line_num}
- Description: {message}

Vulnerable Code:
```{language}
{code}
```

"""
        
        if context:
            prompt += f"""Code Context:
```{language}
{context}
```

"""
        
        prompt += """Your task:
1. Identify the root cause of the vulnerability
2. Generate a secure fix that:
   - Eliminates the vulnerability completely
   - Maintains code functionality
   - Follows security best practices
   - Preserves code readability and maintainability
3. Provide the complete fixed code block
4. Explain the security improvement

Please provide:
1. Fixed code (complete function/block)
2. Brief explanation of the fix
3. Security best practices applied

Fixed Code:
```{language}
"""
        
        return prompt
    
    def generate_refinement_prompt(self, original_code: str, fixed_code: str,
                                  feedback: List[str], language: str) -> str:
        """Generate prompt for iterative refinement"""
        
        feedback_text = '\n'.join([f"- {f}" for f in feedback])
        
        prompt = f"""You previously generated a fix for a vulnerability, but the fix needs refinement based on the following feedback:

Feedback:
{feedback_text}

Original Vulnerable Code:
```{language}
{original_code}
```

Previous Fix Attempt:
```{language}
{fixed_code}
```

Please refine the fix to address all feedback points while maintaining security and functionality.

Refined Fixed Code:
```{language}
"""
        
        return prompt
    
    def generate_exploit_prompt(self, code: str, vulnerability: Dict, 
                               language: str) -> str:
        """Generate prompt for exploit generation (for verification)"""
        
        cwe = vulnerability.get('cwe', 'UNKNOWN')
        message = vulnerability.get('message', '')
        
        prompt = f"""You are a security researcher creating a Proof-of-Concept (PoC) exploit for testing vulnerability fixes.

Vulnerability Details:
- CWE ID: {cwe}
- Description: {message}

Vulnerable Code:
```{language}
{code}
```

Generate a safe PoC exploit that:
1. Demonstrates the vulnerability exists
2. Can be safely executed in a test environment
3. Clearly shows the security issue
4. Does not cause harm to systems

Provide the exploit code and explanation.

Exploit Code:
```{language}
"""
        
        return prompt
    
    def _load_system_prompts(self) -> Dict:
        """Load system prompts for different CWE categories"""
        return {
            'CWE-79': 'You are fixing an XSS (Cross-Site Scripting) vulnerability. Ensure all user input is properly sanitized and escaped.',
            'CWE-89': 'You are fixing an SQL Injection vulnerability. Use parameterized queries or prepared statements.',
            'CWE-78': 'You are fixing a Command Injection vulnerability. Validate and sanitize all user inputs before executing commands.',
            'CWE-22': 'You are fixing a Path Traversal vulnerability. Validate and sanitize file paths, use safe path operations.',
            'CWE-119': 'You are fixing a Buffer Overflow vulnerability. Use safe string functions and proper bounds checking.',
            'CWE-20': 'You are fixing an Input Validation vulnerability. Implement comprehensive input validation and sanitization.',
        }
    
    def get_system_prompt(self, cwe: str) -> str:
        """Get system prompt for specific CWE"""
        return self.system_prompts.get(cwe, 'You are fixing a security vulnerability. Apply security best practices.')

