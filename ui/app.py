"""Streamlit web UI for Hybrid LLM Vulnerability Repair Framework"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import streamlit as st
import json
import time
import tempfile
import os

from src.main import VulnerabilityRepairFramework
from src.utils.config import config

# Page configuration
st.set_page_config(
    page_title="Hybrid LLM Vulnerability Repair Framework",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .code-block {
        background-color: #282c34;
        color: #abb2bf;
        padding: 1rem;
        border-radius: 0.5rem;
        overflow-x: auto;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'framework' not in st.session_state:
    st.session_state.framework = VulnerabilityRepairFramework()
if 'results' not in st.session_state:
    st.session_state.results = None
if 'processing' not in st.session_state:
    st.session_state.processing = False

def main():
    """Main UI function"""
    
    # Header
    st.markdown('<div class="main-header">🔒 Hybrid LLM Vulnerability Repair Framework</div>', 
                unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.subheader("LLM Settings")
        use_refinement = st.checkbox("Enable Multi-Iteration Refinement", value=True)
        use_verification = st.checkbox("Enable Exploit-Based Verification", value=True)
        
        st.subheader("Model Status")
        codellama_status = check_codellama_status()
        chatgpt_status = check_chatgpt_status()
        
        st.write(f"**CodeLlama 13B (Local):** {'✅ Available' if codellama_status else '❌ Not Available'}")
        st.write(f"**ChatGPT-4 (Cloud):** {'✅ Available' if chatgpt_status else '❌ Not Available'}")
        
        st.subheader("About")
        st.info("""
        This framework combines local (CodeLlama 13B) and cloud-based (ChatGPT-4) LLMs 
        for automated vulnerability detection, repair, and verification.
        """)
    
    # Main content area
    tab1, tab2, tab3 = st.tabs(["🔍 Code Analysis", "📊 Results & Metrics", "📚 Documentation"])
    
    with tab1:
        st.header("Upload or Paste Code")
        
        input_method = st.radio(
            "Select input method:",
            ["📝 Paste Code", "📁 Upload File"],
            horizontal=True
        )
        
        code_input = ""
        language = None
        
        if input_method == "📝 Paste Code":
            language = st.selectbox(
                "Programming Language",
                ["python", "cpp", "c", "java"],
                index=0
            )
            code_input = st.text_area(
                "Enter your code:",
                height=300,
                placeholder="Paste your code here...",
                help="Paste the code you want to analyze for vulnerabilities"
            )
        else:
            uploaded_file = st.file_uploader(
                "Choose a file",
                type=['py', 'cpp', 'c', 'java', 'txt'],
                help="Upload a source code file"
            )
            
            if uploaded_file:
                code_input = uploaded_file.read().decode('utf-8')
                file_ext = Path(uploaded_file.name).suffix
                lang_map = {'.py': 'python', '.cpp': 'cpp', '.c': 'c', '.java': 'java'}
                language = lang_map.get(file_ext, 'python')
                st.code(code_input, language=language)
        
        # Process button
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            process_button = st.button("🚀 Analyze & Repair", type="primary", use_container_width=True)
        with col2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_button:
            st.session_state.results = None
            st.rerun()
        
        if process_button and code_input:
            process_code(code_input, language, use_refinement, use_verification)
        elif process_button and not code_input:
            st.error("Please provide code to analyze")
    
    with tab2:
        display_results()
    
    with tab3:
        display_documentation()

def check_codellama_status():
    """Check if CodeLlama is available"""
    try:
        return st.session_state.framework.fix_generator.codellama.is_available()
    except Exception:
        return False

def check_chatgpt_status():
    """Check if ChatGPT is available"""
    try:
        return st.session_state.framework.fix_generator.chatgpt.is_available()
    except Exception:
        return False

def process_code(code: str, language: str, use_refinement: bool, use_verification: bool):
    """Process code for vulnerabilities"""
    
    st.session_state.processing = True
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix=f'.{language}', delete=False) as f:
        f.write(code)
        temp_file = f.name
    
    try:
        with st.spinner("🔍 Analyzing code for vulnerabilities..."):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Detection
            status_text.text("Step 1/4: Detecting vulnerabilities...")
            progress_bar.progress(25)
            time.sleep(0.5)
            
            # Process file
            result = st.session_state.framework.process_file(
                temp_file,
                language=language,
                enable_refinement=use_refinement,
                enable_verification=use_verification
            )
            
            progress_bar.progress(100)
            status_text.text("✅ Analysis complete!")
            time.sleep(0.5)
            
            st.session_state.results = result
            st.rerun()
    
    except Exception as e:
        st.error(f"Error processing code: {str(e)}")
        st.exception(e)
    finally:
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        st.session_state.processing = False

def get_vulnerability_explanation(vuln_type: str, cwe: str) -> str:
    """Get explanation of the vulnerability"""
    explanations = {
        'SQL Injection': 'SQL Injection occurs when user input is directly concatenated into SQL queries without proper sanitization. Attackers can inject malicious SQL code to manipulate database queries, potentially accessing, modifying, or deleting data.',
        'Command Injection': 'Command Injection happens when user input is passed to system commands without validation. Attackers can execute arbitrary commands on the server, leading to complete system compromise.',
        'Path Traversal': 'Path Traversal vulnerabilities allow attackers to access files outside the intended directory by manipulating file paths (e.g., using "../" sequences). This can lead to unauthorized file access.',
        'Insecure Deserialization': 'Insecure Deserialization occurs when untrusted data is deserialized without proper validation. This can lead to remote code execution, privilege escalation, or denial of service attacks.',
        'Hardcoded Credentials': 'Hardcoded credentials (passwords, API keys) in source code are a critical security risk. If the code is exposed, attackers can gain unauthorized access to systems and data.',
        'XSS': 'Cross-Site Scripting (XSS) allows attackers to inject malicious scripts into web pages viewed by other users. This can lead to session hijacking, defacement, or theft of sensitive information.',
        'Weak Cryptography': 'Using weak cryptographic algorithms (like MD5) makes it easier for attackers to break encryption or generate collisions, compromising data integrity and confidentiality.',
        'Information Disclosure': 'Information Disclosure occurs when sensitive information (API keys, secrets, internal paths) is exposed in error messages, logs, or code, helping attackers understand system internals.',
        'Insecure Random': 'Using insecure random number generators (like random.randint) for security-sensitive operations (tokens, passwords) makes them predictable and vulnerable to attacks.',
        'Missing Input Validation': 'Missing input validation allows attackers to provide unexpected or malicious input, leading to various security vulnerabilities including buffer overflows, injection attacks, and logic errors.',
        'Debug Mode in Production': 'Debug mode in production exposes sensitive information, detailed error messages, and debugging tools, making it easier for attackers to find and exploit vulnerabilities.'
    }
    
    return explanations.get(vuln_type, f'This is a {vuln_type} vulnerability (CWE: {cwe}). It represents a security weakness that could be exploited by attackers.')

def extract_fix_explanation(full_response: str) -> str:
    """Extract fix explanation from LLM response"""
    if not full_response:
        return ""
    
    lines = full_response.split('\n')
    explanation_lines = []
    in_explanation = False
    
    keywords = ['explanation', 'fix', 'solution', 'security improvement', 'what was fixed']
    
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in keywords) and ':' in line:
            in_explanation = True
            # Include the line with the keyword
            explanation_lines.append(line)
            continue
        
        if in_explanation:
            # Stop if we hit code blocks or new sections
            if line.strip().startswith('```') or any(word in line_lower for word in ['code:', 'fixed code:', 'summary:']):
                break
            if line.strip():
                explanation_lines.append(line)
    
    explanation = '\n'.join(explanation_lines).strip()
    
    # If no explanation found, try to get first paragraph
    if not explanation:
        paragraphs = full_response.split('\n\n')
        for para in paragraphs[:3]:
            if len(para) > 50 and not para.strip().startswith('```'):
                explanation = para
                break
    
    return explanation

def get_security_improvements(vuln_type: str, cwe: str) -> list:
    """Get list of security improvements applied"""
    improvements_map = {
        'SQL Injection': [
            'Used parameterized queries/prepared statements',
            'Input validation and sanitization',
            'Proper error handling without exposing database structure'
        ],
        'Command Injection': [
            'Input validation and sanitization',
            'Use of safe command execution methods',
            'Whitelist-based input validation'
        ],
        'Path Traversal': [
            'Path validation and sanitization',
            'Use of safe path operations',
            'Restricted file access to intended directories'
        ],
        'Insecure Deserialization': [
            'Input validation before deserialization',
            'Use of safe deserialization methods',
            'Restricted object types allowed'
        ],
        'Hardcoded Credentials': [
            'Removed hardcoded credentials',
            'Use of environment variables or secure configuration',
            'Proper credential management'
        ],
        'XSS': [
            'Input sanitization and escaping',
            'Content Security Policy (CSP) implementation',
            'Output encoding for user-generated content'
        ],
        'Weak Cryptography': [
            'Replaced with strong cryptographic algorithms (SHA-256, bcrypt)',
            'Proper key management',
            'Use of secure random number generators'
        ],
        'Information Disclosure': [
            'Removed sensitive information from code',
            'Secure error handling',
            'Proper logging without exposing secrets'
        ],
        'Insecure Random': [
            'Replaced with cryptographically secure random generators',
            'Use of secrets module (Python) or equivalent',
            'Proper random number generation for security contexts'
        ],
        'Missing Input Validation': [
            'Comprehensive input validation',
            'Type checking and range validation',
            'Sanitization of user inputs'
        ],
        'Debug Mode in Production': [
            'Disabled debug mode',
            'Removed debug statements',
            'Production-safe error handling'
        ]
    }
    
    return improvements_map.get(vuln_type, [
        'Applied security best practices',
        'Input validation and sanitization',
        'Proper error handling'
    ])

def generate_download_content(repair_result: dict, language: str, original_code: str) -> str:
    """Generate comprehensive download content with description"""
    
    vuln = repair_result.get('vulnerability', {})
    fixed_code = repair_result.get('fixed_code', '')
    full_response = repair_result.get('full_response', '')
    metrics = repair_result.get('metrics', {})
    validation = repair_result.get('validation', {})
    
    # Build comprehensive description
    content = []
    content.append("=" * 80)
    content.append("VULNERABILITY REPAIR REPORT")
    content.append("=" * 80)
    content.append("")
    
    # Vulnerability Information
    content.append("VULNERABILITY DETAILS:")
    content.append("-" * 80)
    content.append(f"Type: {vuln.get('type', 'Unknown')}")
    content.append(f"CWE ID: {vuln.get('cwe', 'Unknown')}")
    content.append(f"Severity: {vuln.get('severity', 'Unknown')}")
    content.append(f"Line Number: {vuln.get('line', 'Unknown')}")
    content.append(f"Description: {vuln.get('message', 'No description available')}")
    content.append("")
    
    # What is the Issue
    content.append("WHAT IS THE ISSUE:")
    content.append("-" * 80)
    issue_description = get_vulnerability_explanation(vuln.get('type', ''), vuln.get('cwe', ''))
    content.append(issue_description)
    content.append("")
    
    # Original Vulnerable Code
    if original_code:
        content.append("ORIGINAL VULNERABLE CODE:")
        content.append("-" * 80)
        # Extract the relevant function/block around the vulnerable line
        vulnerable_line = vuln.get('line', 0)
        if vulnerable_line > 0:
            lines = original_code.split('\n')
            start = max(0, vulnerable_line - 5)
            end = min(len(lines), vulnerable_line + 10)
            context_code = '\n'.join(lines[start:end])
            content.append(context_code)
        else:
            content.append(original_code)
        content.append("")
    
    # What Was Fixed
    content.append("WHAT WAS FIXED:")
    content.append("-" * 80)
    if fixed_code:
        fix_explanation = extract_fix_explanation(full_response)
        if fix_explanation:
            content.append(fix_explanation)
        else:
            content.append("The vulnerability was fixed by applying security best practices:")
            content.append(f"- Replaced vulnerable code with secure implementation")
            content.append(f"- Applied {vuln.get('type', 'security')} mitigation techniques")
        content.append("")
    else:
        content.append("WARNING: Fix generation failed or returned empty code.")
        content.append("The LLM may not have generated a proper fix. Please review the original code.")
        content.append("")
    
    # Fixed Code
    content.append("FIXED CODE:")
    content.append("-" * 80)
    if fixed_code:
        content.append(fixed_code)
    else:
        content.append("No fixed code available.")
        content.append("")
        content.append("Original code (for reference):")
        if original_code:
            content.append(original_code)
    content.append("")
    
    # Security Improvements
    content.append("SECURITY IMPROVEMENTS:")
    content.append("-" * 80)
    improvements = get_security_improvements(vuln.get('type', ''), vuln.get('cwe', ''))
    for improvement in improvements:
        content.append(f"- {improvement}")
    content.append("")
    
    # Metrics
    if metrics:
        content.append("QUALITY METRICS:")
        content.append("-" * 80)
        content.append(f"Code Similarity: {metrics.get('code_similarity', 0):.1%}")
        content.append(f"Fix Quality Score: {metrics.get('fix_quality_score', 0):.2f}")
        content.append(f"Exploit Test: {'PASSED' if metrics.get('exploit_test_passed', False) else 'FAILED'}")
        content.append(f"Static Analysis: {'PASSED' if metrics.get('static_analysis_passed', False) else 'FAILED'}")
        content.append("")
    
    # Processing Information
    content.append("PROCESSING INFORMATION:")
    content.append("-" * 80)
    content.append(f"Model Used: {repair_result.get('model_used', 'Unknown')}")
    content.append(f"Iterations: {repair_result.get('iterations', 1)}")
    content.append(f"Processing Time: {repair_result.get('processing_time', 0):.2f}s")
    content.append("")
    
    content.append("=" * 80)
    content.append("End of Report")
    content.append("=" * 80)
    
    return '\n'.join(content)

def display_results():
    """Display analysis results"""
    
    st.header("Analysis Results")
    
    if st.session_state.results is None:
        st.info("👆 Go to 'Code Analysis' tab to analyze code")
        return
    
    result = st.session_state.results
    
    if not result.get('success', False):
        st.error(f"Error: {result.get('error', 'Unknown error')}")
        return
    
    # Summary metrics
    summary = result.get('summary', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Vulnerabilities Found",
            summary.get('total_vulnerabilities', 0)
        )
    
    with col2:
        st.metric(
            "Successful Repairs",
            summary.get('successful_repairs', 0)
        )
    
    with col3:
        success_rate = summary.get('success_rate', 0)
        st.metric(
            "Success Rate",
            f"{success_rate:.1%}"
        )
    
    with col4:
        st.metric(
            "Avg Processing Time",
            f"{summary.get('average_processing_time', 0):.2f}s"
        )
    
    # Detailed results
    st.subheader("Detailed Results")
    
    results_list = result.get('results', [])
    
    if not results_list:
        st.success("✅ No vulnerabilities detected in the code!")
        return
    
    for i, repair_result in enumerate(results_list, 1):
        with st.expander(f"Vulnerability {i}: {repair_result.get('vulnerability', {}).get('type', 'Unknown')}", expanded=True):
            vuln = repair_result.get('vulnerability', {})
            
            # Vulnerability info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**CWE:** {vuln.get('cwe', 'Unknown')}")
            with col2:
                st.write(f"**Severity:** {vuln.get('severity', 'Unknown')}")
            with col3:
                st.write(f"**Line:** {vuln.get('line', 'Unknown')}")
            
            st.write(f"**Description:** {vuln.get('message', 'No description')}")
            
            # Fixed code
            fixed_code = repair_result.get('fixed_code', '')
            if fixed_code:
                st.subheader("🔧 Fixed Code")
                st.code(fixed_code, language=result.get('language', 'python'))
            else:
                st.warning("⚠️ Fix generation failed or returned empty code. The LLM may not have generated a proper fix. Please review the original code and try again.")
                st.subheader("📝 Original Code (for reference)")
                original_code = result.get('original_code', '')
                if original_code:
                    # Show context around the vulnerable line
                    vulnerable_line = vuln.get('line', 0)
                    if vulnerable_line > 0:
                        lines = original_code.split('\n')
                        start = max(0, vulnerable_line - 5)
                        end = min(len(lines), vulnerable_line + 10)
                        context_code = '\n'.join(lines[start:end])
                        st.code(context_code, language=result.get('language', 'python'))
                    else:
                        st.code(original_code, language=result.get('language', 'python'))
            
            # Metrics
            metrics = repair_result.get('metrics', {})
            if metrics:
                st.subheader("📊 Metrics")
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Code Similarity", f"{metrics.get('code_similarity', 0):.1%}")
                with col2:
                    st.metric("Fix Quality", f"{metrics.get('fix_quality_score', 0):.2f}")
                with col3:
                    exploit_status = "✅ Passed" if metrics.get('exploit_test_passed', False) else "❌ Failed"
                    st.write(f"**Exploit Test:** {exploit_status}")
                with col4:
                    static_status = "✅ Passed" if metrics.get('static_analysis_passed', False) else "❌ Failed"
                    st.write(f"**Static Analysis:** {static_status}")
            
            # Processing info
            st.write(f"**Iterations:** {repair_result.get('iterations', 1)}")
            st.write(f"**Processing Time:** {repair_result.get('processing_time', 0):.2f}s")
            st.write(f"**Model Used:** {repair_result.get('model_used', 'Unknown')}")
            
            # Download fixed code with description
            download_content = generate_download_content(
                repair_result, 
                result.get('language', 'python'),
                result.get('original_code', '')
            )
            
            st.download_button(
                label="📥 Download Fixed Code with Description",
                data=download_content,
                file_name=f"fixed_vulnerability_{i}_{vuln.get('type', 'unknown').replace(' ', '_')}.txt",
                mime="text/plain",
                key=f"download_{i}"
            )
    
    # Export results
    st.subheader("Export Results")
    results_json = json.dumps(result, indent=2)
    st.download_button(
        label="📥 Download Results (JSON)",
        data=results_json,
        file_name="vulnerability_repair_results.json",
        mime="application/json"
    )

def display_documentation():
    """Display documentation"""
    
    st.header("📚 Documentation")
    
    st.subheader("Overview")
    st.write("""
    The Hybrid LLM-Based Detect–Fix–Verify Framework combines local (CodeLlama 13B) 
    and cloud-based (ChatGPT-4) Large Language Models for automated vulnerability 
    detection, repair, and verification.
    """)
    
    st.subheader("Features")
    st.markdown("""
    - **Hybrid LLM Architecture**: Intelligent routing between local and cloud models
    - **Exploit-Based Verification**: PoC exploit generation and testing
    - **Multi-Iteration Refinement**: Adaptive feedback loops for quality improvement
    - **Multi-Language Support**: Python, C/C++, Java
    """)
    
    st.subheader("How It Works")
    st.markdown("""
    1. **Detection**: Static analysis tools detect vulnerabilities
    2. **Routing**: Intelligent selection between local (CodeLlama) and cloud (ChatGPT-4)
    3. **Repair**: LLM generates fixes with context-aware prompts
    4. **Refinement**: Multi-iteration improvement based on feedback
    5. **Verification**: Exploit-based testing validates fixes
    """)
    
    st.subheader("Supported Languages")
    st.write("- Python (.py)")
    st.write("- C/C++ (.cpp, .c)")
    st.write("- Java (.java)")
    
    st.subheader("Vulnerability Types")
    st.write("- SQL Injection (CWE-89)")
    st.write("- Cross-Site Scripting (CWE-79)")
    st.write("- Command Injection (CWE-78)")
    st.write("- Path Traversal (CWE-22)")
    st.write("- Buffer Overflow (CWE-119)")
    st.write("- Input Validation (CWE-20)")

if __name__ == "__main__":
    main()

