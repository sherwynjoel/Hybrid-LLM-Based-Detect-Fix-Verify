"""
Generate CI summary from security report
"""

import json
import sys
from pathlib import Path


def generate_summary(report_path: str):
    """Generate markdown summary for CI"""
    
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    summary = report.get('summary', {})
    total = report.get('total_vulnerabilities', 0)
    critical = summary.get('critical', 0)
    high = summary.get('high', 0)
    medium = summary.get('medium', 0)
    low = summary.get('low', 0)
    
    print("## 🔒 Security Scan Results\n")
    print(f"**Files Scanned:** {report.get('files_scanned', 0)}")
    print(f"**Files with Vulnerabilities:** {report.get('files_with_vulnerabilities', 0)}")
    print(f"**Total Vulnerabilities:** {total}\n")
    
    print("### Severity Breakdown")
    print(f"- 🔴 **Critical:** {critical}")
    print(f"- 🟠 **High:** {high}")
    print(f"- 🟡 **Medium:** {medium}")
    print(f"- 🟢 **Low:** {low}\n")
    
    if critical > 0:
        print("⚠️ **Critical vulnerabilities found! Merge blocked.**\n")
    elif total > 0:
        print("⚠️ Vulnerabilities found but not blocking.\n")
    else:
        print("✅ **No vulnerabilities found!**\n")
    
    # Show top vulnerabilities
    vulnerabilities = report.get('vulnerabilities', [])
    if vulnerabilities:
        print("### Top Vulnerabilities")
        for vuln in vulnerabilities[:5]:
            print(f"- `{vuln['file']}:{vuln['line']}` - {vuln['type']} ({vuln['severity']})")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python generate_ci_summary.py <report.json>")
        sys.exit(1)
    
    generate_summary(sys.argv[1])






