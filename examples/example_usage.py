"""Example usage of the Hybrid LLM Vulnerability Repair Framework"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import VulnerabilityRepairFramework

# Example vulnerable Python code
vulnerable_code = """
import sqlite3

def get_user(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    # SQL Injection vulnerability
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()
"""

# Save to temporary file
import tempfile
import os
from pathlib import Path

# Create temp directory in project
temp_dir = Path(__file__).parent.parent / "temp"
temp_dir.mkdir(exist_ok=True)

temp_file = temp_dir / "test_vulnerable_code.py"
with open(temp_file, 'w', encoding='utf-8') as f:
    f.write(vulnerable_code)

print(f"Created test file: {temp_file}")

try:
    # Initialize framework
    framework = VulnerabilityRepairFramework()
    
    # Process the file
    print("Processing vulnerable code...")
    result = framework.process_file(
        str(temp_file),
        language='python',
        enable_refinement=True,
        enable_verification=True
    )
    
    # Display results
    if result.get('success'):
        print(f"\nVulnerabilities found: {result.get('vulnerabilities_found', 0)}")
        
        for i, repair_result in enumerate(result.get('results', []), 1):
            print(f"\n--- Vulnerability {i} ---")
            print(f"Type: {repair_result.get('vulnerability', {}).get('type', 'Unknown')}")
            print(f"CWE: {repair_result.get('vulnerability', {}).get('cwe', 'Unknown')}")
            print(f"Severity: {repair_result.get('vulnerability', {}).get('severity', 'Unknown')}")
            print(f"\nFixed Code:")
            print(repair_result.get('fixed_code', 'No fix generated'))
            print(f"\nMetrics:")
            metrics = repair_result.get('metrics', {})
            print(f"  Code Similarity: {metrics.get('code_similarity', 0):.2%}")
            print(f"  Fix Quality Score: {metrics.get('fix_quality_score', 0):.2f}")
            print(f"  Exploit Test Passed: {metrics.get('exploit_test_passed', False)}")
            print(f"  Static Analysis Passed: {metrics.get('static_analysis_passed', False)}")
            print(f"  Iterations: {repair_result.get('iterations', 1)}")
            print(f"  Processing Time: {repair_result.get('processing_time', 0):.2f}s")
        
        summary = result.get('summary', {})
        print(f"\n=== Summary ===")
        print(f"Success Rate: {summary.get('success_rate', 0):.2%}")
        print(f"Average Iterations: {summary.get('average_iterations', 0):.2f}")
        print(f"Total Processing Time: {summary.get('total_processing_time', 0):.2f}s")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")

finally:
    # Clean up
    try:
        if temp_file.exists():
            temp_file.unlink()
    except Exception as e:
        print(f"Warning: Could not delete temp file: {e}")

