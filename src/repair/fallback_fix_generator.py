"""Fallback fix generator for when LLM fails"""

from typing import Dict, Optional
import re


class FallbackFixGenerator:
    """Generate basic fixes when LLM fails"""
    
    def generate_fix(self, code: str, vulnerability: Dict, language: str) -> str:
        """Generate a basic fix for the vulnerability"""
        
        vuln_type = vulnerability.get('type', '')
        cwe = vulnerability.get('cwe', '')
        line_num = vulnerability.get('line', 0)
        
        if language == 'python':
            return self._fix_python(code, vuln_type, cwe, line_num)
        elif language in ['cpp', 'c']:
            return self._fix_cpp(code, vuln_type, cwe, line_num)
        elif language == 'java':
            return self._fix_java(code, vuln_type, cwe, line_num)
        
        return code  # Return original if no fix available
    
    def _fix_python(self, code: str, vuln_type: str, cwe: str, line_num: int) -> str:
        """Generate fix for Python code"""
        lines = code.split('\n')
        
        if vuln_type == 'SQL Injection' or cwe == 'CWE-89':
            # Fix SQL Injection - handle the specific case from single_vulnerability.py
            fixed_code = code
            
            # Pattern 1: "SELECT * FROM users WHERE id = " + user_id
            pattern1 = r'query\s*=\s*["\']([^"\']*)\s*\+\s*(\w+)'
            match = re.search(pattern1, code)
            if match:
                query_start = match.group(1)
                var_name = match.group(2)
                # Replace with parameterized query
                fixed_code = re.sub(
                    pattern1,
                    f'query = "{query_start}?"',
                    fixed_code
                )
                # Fix the execute line
                fixed_code = re.sub(
                    r'cursor\.execute\s*\(query\s*\)',
                    f'cursor.execute(query, ({var_name},))',
                    fixed_code
                )
                return fixed_code
            
            # Pattern 2: Direct execute with concatenation
            pattern2 = r'cursor\.execute\s*\(([^)]*)\s*\+\s*(\w+)\s*\)'
            match = re.search(pattern2, code)
            if match:
                query_part = match.group(1).strip('"\'')
                var_name = match.group(2)
                fixed_code = re.sub(
                    pattern2,
                    f'cursor.execute("{query_part}?", ({var_name},))',
                    fixed_code
                )
                return fixed_code
            
            # Pattern 3: Line-by-line fix for the specific format
            # Handle: query = "SELECT * FROM users WHERE id = " + user_id
            #         cursor.execute(query)
            for i, line in enumerate(lines):
                # Check if this line has string concatenation with a variable
                # Pattern: query = "SELECT ... " + variable
                pattern = r'query\s*=\s*["\']([^"\']+)\s*["\']\s*\+\s*(\w+)'
                match = re.search(pattern, line)
                if match:
                    query_base = match.group(1).rstrip()
                    var_name = match.group(2)
                    # Preserve indentation
                    indent = len(line) - len(line.lstrip())
                    indent_str = ' ' * indent
                    # Replace the query line - ensure space before ?
                    if not query_base.endswith(' '):
                        query_base += ' '
                    lines[i] = f'{indent_str}query = "{query_base}?"'
                    
                    # Fix execute line (check next few lines)
                    for j in range(i + 1, min(i + 3, len(lines))):
                        if 'cursor.execute' in lines[j] and 'query' in lines[j]:
                            # Replace execute with parameterized version
                            exec_indent = len(lines[j]) - len(lines[j].lstrip())
                            exec_indent_str = ' ' * exec_indent
                            lines[j] = f'{exec_indent_str}cursor.execute(query, ({var_name},))'
                            return '\n'.join(lines)
                
                # Also handle direct execute with concatenation
                if 'cursor.execute' in line and '+' in line:
                    var_match = re.search(r'\+ (\w+)', line)
                    if var_match:
                        var_name = var_match.group(1)
                        query_match = re.search(r'["\']([^"\']*)\s*\+\s*' + var_name, line)
                        if query_match:
                            query_base = query_match.group(1).rstrip()
                            indent = len(line) - len(line.lstrip())
                            indent_str = ' ' * indent
                            lines[i] = f'{indent_str}cursor.execute("{query_base}?", ({var_name},))'
                            return '\n'.join(lines)
            
            return '\n'.join(lines)
        
        elif vuln_type == 'Command Injection' or cwe == 'CWE-78':
            # Fix Command Injection
            for i, line in enumerate(lines):
                if i + 1 == line_num or 'subprocess' in line or 'os.system' in line:
                    # Replace with safe subprocess call
                    if 'os.system' in line:
                        lines[i] = re.sub(
                            r'os\.system\s*\(([^)]+)\)',
                            r'subprocess.run(\1, shell=False, check=True)',
                            line
                        )
                    elif 'subprocess.call' in line and 'shell=True' in line:
                        lines[i] = re.sub(
                            r'shell\s*=\s*True',
                            'shell=False',
                            line
                        )
            return '\n'.join(lines)
        
        elif vuln_type == 'Path Traversal' or cwe == 'CWE-22':
            # Fix Path Traversal
            for i, line in enumerate(lines):
                if i + 1 == line_num or 'open(' in line:
                    # Add path validation
                    if '+ filename' in line or '+ file_path' in line:
                        # Extract variable
                        var_match = re.search(r'\+ (\w+)', line)
                        if var_match:
                            var_name = var_match.group(1)
                            # Add before the line
                            lines.insert(i, f"    # Validate and sanitize path")
                            lines.insert(i + 1, f"    import os")
                            lines.insert(i + 2, f"    safe_path = os.path.basename({var_name})")
                            lines[i + 3] = re.sub(
                                r'\+ ' + var_name,
                                '+ safe_path',
                                lines[i + 3]
                            )
            return '\n'.join(lines)
        
        elif vuln_type == 'Hardcoded Credentials':
            # Fix Hardcoded Credentials
            for i, line in enumerate(lines):
                if i + 1 == line_num or 'password =' in line or 'api_key =' in line:
                    # Replace with environment variable
                    if 'password =' in line:
                        lines[i] = re.sub(
                            r'password\s*=\s*["\']([^"\']+)["\']',
                            r'password = os.getenv("PASSWORD", "")',
                            line
                        )
                        if 'import os' not in code:
                            lines.insert(0, 'import os')
            return '\n'.join(lines)
        
        elif vuln_type == 'Weak Cryptography' or 'md5' in code.lower():
            # Fix Weak Cryptography
            for i, line in enumerate(lines):
                if 'hashlib.md5' in line:
                    lines[i] = line.replace('hashlib.md5', 'hashlib.sha256')
            return '\n'.join(lines)
        
        elif vuln_type == 'Insecure Random':
            # Fix Insecure Random
            for i, line in enumerate(lines):
                if 'random.randint' in line or 'random.random' in line:
                    lines[i] = line.replace('random.', 'secrets.')
                    if 'import secrets' not in code:
                        # Add import
                        import_line = -1
                        for j, l in enumerate(lines):
                            if l.startswith('import ') or l.startswith('from '):
                                import_line = j
                        if import_line >= 0:
                            lines.insert(import_line + 1, 'import secrets')
            return '\n'.join(lines)
        
        return code
    
    def _fix_cpp(self, code: str, vuln_type: str, cwe: str, line_num: int) -> str:
        """Generate fix for C/C++ code"""
        # Basic C/C++ fixes would go here
        return code
    
    def _fix_java(self, code: str, vuln_type: str, cwe: str, line_num: int) -> str:
        """Generate fix for Java code"""
        # Basic Java fixes would go here
        return code

