"""Multi-language code parsing utilities"""

import ast
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import re


class CodeParser:
    """Parser for multiple programming languages"""
    
    def __init__(self):
        self.supported_languages = ['python', 'cpp', 'java', 'c']
    
    def detect_language(self, file_path: str) -> Optional[str]:
        """Detect programming language from file extension"""
        ext = Path(file_path).suffix.lower()
        lang_map = {
            '.py': 'python',
            '.cpp': 'cpp',
            '.c': 'c',
            '.java': 'java',
            '.h': 'cpp',
            '.hpp': 'cpp'
        }
        return lang_map.get(ext)
    
    def parse_code(self, code: str, language: str) -> Dict:
        """Parse code and extract structural information"""
        if language == 'python':
            return self._parse_python(code)
        elif language in ['cpp', 'c']:
            return self._parse_cpp(code)
        elif language == 'java':
            return self._parse_java(code)
        else:
            return {'language': language, 'code': code, 'functions': []}
    
    def _parse_python(self, code: str) -> Dict:
        """Parse Python code using AST"""
        try:
            tree = ast.parse(code)
            functions = []
            classes = []
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        'name': node.name,
                        'line': node.lineno,
                        'args': [arg.arg for arg in node.args.args],
                        'code': ast.get_source_segment(code, node) or ''
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        'name': node.name,
                        'line': node.lineno
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    imports.append(ast.get_source_segment(code, node) or '')
            
            return {
                'language': 'python',
                'code': code,
                'functions': functions,
                'classes': classes,
                'imports': imports,
                'ast': tree
            }
        except SyntaxError as e:
            return {
                'language': 'python',
                'code': code,
                'error': str(e),
                'functions': []
            }
    
    def _parse_cpp(self, code: str) -> Dict:
        """Parse C/C++ code using regex patterns"""
        functions = []
        classes = []
        includes = []
        
        # Extract includes
        include_pattern = r'#include\s*[<"]([^>"]+)[>"]'
        includes = re.findall(include_pattern, code)
        
        # Extract function definitions
        function_pattern = r'(\w+\s+)*(\w+)\s*\([^)]*\)\s*\{'
        for match in re.finditer(function_pattern, code):
            func_name = match.group(2)
            line_num = code[:match.start()].count('\n') + 1
            functions.append({
                'name': func_name,
                'line': line_num,
                'code': self._extract_function_body(code, match.start())
            })
        
        # Extract class definitions
        class_pattern = r'class\s+(\w+)\s*\{'
        for match in re.finditer(class_pattern, code):
            class_name = match.group(1)
            line_num = code[:match.start()].count('\n') + 1
            classes.append({
                'name': class_name,
                'line': line_num
            })
        
        return {
            'language': 'cpp',
            'code': code,
            'functions': functions,
            'classes': classes,
            'includes': includes
        }
    
    def _parse_java(self, code: str) -> Dict:
        """Parse Java code using regex patterns"""
        functions = []
        classes = []
        imports = []
        
        # Extract imports
        import_pattern = r'import\s+([\w.]+);'
        imports = re.findall(import_pattern, code)
        
        # Extract method definitions
        method_pattern = r'(public|private|protected)?\s*(\w+\s+)*(\w+)\s*\([^)]*\)\s*\{'
        for match in re.finditer(method_pattern, code):
            method_name = match.group(3) if match.group(3) else 'unknown'
            line_num = code[:match.start()].count('\n') + 1
            functions.append({
                'name': method_name,
                'line': line_num,
                'code': self._extract_function_body(code, match.start())
            })
        
        # Extract class definitions
        class_pattern = r'(public\s+)?class\s+(\w+)\s*'
        for match in re.finditer(class_pattern, code):
            class_name = match.group(2)
            line_num = code[:match.start()].count('\n') + 1
            classes.append({
                'name': class_name,
                'line': line_num
            })
        
        return {
            'language': 'java',
            'code': code,
            'functions': functions,
            'classes': classes,
            'imports': imports
        }
    
    def _extract_function_body(self, code: str, start_pos: int) -> str:
        """Extract function body from start position"""
        brace_count = 0
        start_brace = code.find('{', start_pos)
        if start_brace == -1:
            return ''
        
        for i in range(start_brace, len(code)):
            if code[i] == '{':
                brace_count += 1
            elif code[i] == '}':
                brace_count -= 1
                if brace_count == 0:
                    return code[start_pos:i+1]
        return code[start_pos:]
    
    def extract_context(self, code: str, line_num: int, language: str, context_lines: int = 5) -> str:
        """Extract code context around a specific line"""
        lines = code.split('\n')
        start = max(0, line_num - context_lines - 1)
        end = min(len(lines), line_num + context_lines)
        return '\n'.join(lines[start:end])
    
    def get_function_at_line(self, parsed_code: Dict, line_num: int) -> Optional[Dict]:
        """Get function containing a specific line number"""
        for func in parsed_code.get('functions', []):
            func_line = func.get('line', 0)
            # Simple heuristic: function contains the line if it's within reasonable range
            if func_line <= line_num <= func_line + 50:
                return func
        return None

