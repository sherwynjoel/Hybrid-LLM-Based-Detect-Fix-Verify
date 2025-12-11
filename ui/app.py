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
            
            # Download fixed code
            st.download_button(
                label="📥 Download Fixed Code",
                data=fixed_code,
                file_name=f"fixed_vulnerability_{i}.{result.get('language', 'py')}",
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

