"""
Backend API server for IDE integrations
Provides REST API for VS Code, PyCharm, and IntelliJ plugins
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.main import VulnerabilityRepairFramework
from src.utils.config import config

app = Flask(__name__)
CORS(app)  # Enable CORS for IDE plugins

framework = VulnerabilityRepairFramework()

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'framework': 'Hybrid LLM Vulnerability Repair',
        'version': '1.0.0'
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Analyze code for vulnerabilities"""
    try:
        data = request.json
        code = data.get('code', '')
        language = data.get('language', 'python')
        privacy_first_mode = data.get('privacy_first_mode', True)
        
        if not code:
            return jsonify({'error': 'Code is required'}), 400
        
        # Set privacy-first mode in router
        framework.fix_generator.router.privacy_first_mode = privacy_first_mode
        
        # Create temporary file
        import tempfile
        import os
        
        suffix_map = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'cpp': '.cpp',
            'c': '.c'
        }
        
        suffix = suffix_map.get(language, '.py')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Process file
            result = framework.process_file(
                temp_file,
                language=language,
                enable_refinement=True,
                enable_verification=True
            )
            
            # Format vulnerabilities for IDE
            vulnerabilities = []
            if result.get('success') and result.get('results'):
                for r in result['results']:
                    vuln = r.get('vulnerability', {})
                    vulnerabilities.append({
                        'type': vuln.get('type', 'Unknown'),
                        'severity': vuln.get('severity', 'MEDIUM'),
                        'line': vuln.get('line', 0),
                        'message': vuln.get('message', ''),
                        'cwe': vuln.get('cwe', ''),
                        'code': vuln.get('code', ''),
                        'fix_available': bool(r.get('fixed_code'))
                    })
            
            return jsonify({
                'success': True,
                'vulnerabilities': vulnerabilities,
                'total': len(vulnerabilities),
                'summary': result.get('summary', {})
            })
        finally:
            # Clean up temp file
            if os.path.exists(temp_file):
                os.unlink(temp_file)
                
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/fix', methods=['POST'])
def fix():
    """Generate fix for vulnerability"""
    try:
        data = request.json
        code = data.get('code', '')
        vulnerability = data.get('vulnerability', {})
        language = data.get('language', 'python')
        
        if not code or not vulnerability:
            return jsonify({'error': 'Code and vulnerability are required'}), 400
        
        # Extract context
        context = framework.detector.extract_context(code, vulnerability)
        context_code = context.get('context', '')
        
        # Generate fix
        fix_result = framework.fix_generator.generate_fix(
            code, vulnerability, language, context_code
        )
        
        if not fix_result.get('success'):
            return jsonify({
                'success': False,
                'error': fix_result.get('error', 'Fix generation failed')
            }), 500
        
        return jsonify({
            'success': True,
            'fixed_code': fix_result.get('fixed_code', ''),
            'full_response': fix_result.get('full_response', ''),
            'model_used': fix_result.get('model_used', 'unknown'),
            'routing_decision': fix_result.get('routing_decision', {})
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/analyze-file', methods=['POST'])
def analyze_file():
    """Analyze file from path"""
    try:
        data = request.json
        file_path = data.get('file_path', '')
        
        if not file_path:
            return jsonify({'error': 'File path is required'}), 400
        
        if not Path(file_path).exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Process file
        result = framework.process_file(
            file_path,
            enable_refinement=True,
            enable_verification=True
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Get framework status"""
    try:
        codellama_available = framework.fix_generator.codellama.is_available()
        chatgpt_available = framework.fix_generator.chatgpt.is_available()
        
        return jsonify({
            'codellama_available': codellama_available,
            'chatgpt_available': chatgpt_available,
            'privacy_first_mode': framework.fix_generator.router.privacy_first_mode
        })
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("Starting IDE Integration API Server...")
    print("API available at: http://localhost:8501/api")
    print("Health check: http://localhost:8501/health")
    app.run(host='0.0.0.0', port=8501, debug=False)


