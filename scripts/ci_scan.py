"""
CI/CD Security Scan Script
Scans codebase for vulnerabilities and generates report
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import VulnerabilityRepairFramework
from src.utils.config import config


def scan_directory(directory: Path, language: str = None, output: str = None) -> Dict:
    """Scan directory for vulnerabilities"""
    
    framework = VulnerabilityRepairFramework()
    results = []
    total_vulnerabilities = 0
    
    # Find files to scan
    extensions = {
        'python': ['.py'],
        'javascript': ['.js'],
        'typescript': ['.ts'],
        'java': ['.java'],
        'cpp': ['.cpp', '.c', '.h', '.hpp'],
        'c': ['.c', '.h']
    }
    
    if language:
        file_extensions = extensions.get(language, [])
    else:
        # Scan all supported languages
        file_extensions = []
        for ext_list in extensions.values():
            file_extensions.extend(ext_list)
    
    files_scanned = 0
    files_with_vulns = 0
    
    for ext in file_extensions:
        for file_path in directory.rglob(f'*{ext}'):
            # Skip certain directories
            if any(skip in str(file_path) for skip in ['node_modules', '.git', '__pycache__', 'venv', '.venv']):
                continue
            
            try:
                # Detect language from extension
                if not language:
                    if ext in ['.py']:
                        file_language = 'python'
                    elif ext in ['.js']:
                        file_language = 'javascript'
                    elif ext in ['.ts']:
                        file_language = 'typescript'
                    elif ext in ['.java']:
                        file_language = 'java'
                    elif ext in ['.cpp', '.hpp', '.h']:
                        file_language = 'cpp'
                    elif ext in ['.c']:
                        file_language = 'c'
                    else:
                        continue
                else:
                    file_language = language
                
                # Process file
                result = framework.process_file(
                    str(file_path),
                    language=file_language,
                    enable_refinement=False,  # Faster for CI
                    enable_verification=False  # Faster for CI
                )
                
                files_scanned += 1
                
                if result.get('success') and result.get('vulnerabilities_found', 0) > 0:
                    files_with_vulns += 1
                    total_vulnerabilities += result.get('vulnerabilities_found', 0)
                    
                    # Format for CI report
                    for vuln_result in result.get('results', []):
                        vuln = vuln_result.get('vulnerability', {})
                        results.append({
                            'file': str(file_path.relative_to(directory)),
                            'type': vuln.get('type', 'Unknown'),
                            'severity': vuln.get('severity', 'MEDIUM'),
                            'line': vuln.get('line', 0),
                            'message': vuln.get('message', ''),
                            'cwe': vuln.get('cwe', ''),
                            'code': vuln.get('code', ''),
                            'fix_available': bool(vuln_result.get('fixed_code'))
                        })
            
            except Exception as e:
                print(f"Error scanning {file_path}: {e}", file=sys.stderr)
                continue
    
    # Generate summary
    critical = sum(1 for r in results if r['severity'] == 'CRITICAL')
    high = sum(1 for r in results if r['severity'] == 'HIGH')
    medium = sum(1 for r in results if r['severity'] == 'MEDIUM')
    low = sum(1 for r in results if r['severity'] == 'LOW')
    
    report = {
        'timestamp': time.time(),
        'files_scanned': files_scanned,
        'files_with_vulnerabilities': files_with_vulns,
        'total_vulnerabilities': total_vulnerabilities,
        'vulnerabilities': results,
        'summary': {
            'critical': critical,
            'high': high,
            'medium': medium,
            'low': low
        },
        'scan_success': True
    }
    
    # Write report
    if output:
        with open(output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"Report saved to {output}")
    
    return report


def main():
    parser = argparse.ArgumentParser(description='CI/CD Security Scan')
    parser.add_argument('--path', '-p', default='.', help='Path to scan')
    parser.add_argument('--language', '-l', help='Language to scan (python, java, etc.)')
    parser.add_argument('--output', '-o', default='security-report.json', help='Output file')
    parser.add_argument('--format', '-f', default='json', choices=['json'], help='Output format')
    parser.add_argument('--fail-on-critical', action='store_true', help='Exit with error if critical vulnerabilities found')
    
    args = parser.parse_args()
    
    scan_path = Path(args.path).resolve()
    if not scan_path.exists():
        print(f"Error: Path {scan_path} does not exist", file=sys.stderr)
        sys.exit(1)
    
    print(f"Scanning {scan_path}...")
    report = scan_directory(scan_path, args.language, args.output)
    
    # Print summary
    print("\n" + "="*60)
    print("Security Scan Summary")
    print("="*60)
    print(f"Files Scanned: {report['files_scanned']}")
    print(f"Files with Vulnerabilities: {report['files_with_vulnerabilities']}")
    print(f"Total Vulnerabilities: {report['total_vulnerabilities']}")
    print(f"\nSeverity Breakdown:")
    print(f"  Critical: {report['summary']['critical']}")
    print(f"  High: {report['summary']['high']}")
    print(f"  Medium: {report['summary']['medium']}")
    print(f"  Low: {report['summary']['low']}")
    print("="*60)
    
    # Exit with error if critical vulnerabilities found
    if args.fail_on_critical and report['summary']['critical'] > 0:
        print("\n❌ Critical vulnerabilities found! Exiting with error code.")
        sys.exit(1)
    
    if report['total_vulnerabilities'] > 0:
        print(f"\n⚠️  {report['total_vulnerabilities']} vulnerabilities found.")
        sys.exit(1)
    else:
        print("\n✅ No vulnerabilities found!")
        sys.exit(0)


if __name__ == '__main__':
    main()


