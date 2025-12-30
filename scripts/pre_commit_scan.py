"""
Pre-commit hook script for Hybrid LLM Framework
Scans staged files before commit
"""

import sys
import subprocess
import tempfile
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.main import VulnerabilityRepairFramework


def get_staged_files():
    """Get list of staged files"""
    result = subprocess.run(
        ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACM'],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        return []
    
    files = result.stdout.strip().split('\n')
    return [f for f in files if f]  # Remove empty strings


def is_supported_file(file_path: str) -> tuple[bool, str]:
    """Check if file is supported and return language"""
    path = Path(file_path)
    ext = path.suffix.lower()
    
    language_map = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.h': 'cpp',
        '.hpp': 'cpp'
    }
    
    language = language_map.get(ext)
    return language is not None, language or ''


def scan_file(file_path: str, language: str) -> dict:
    """Scan a single file"""
    framework = VulnerabilityRepairFramework()
    
    try:
        result = framework.process_file(
            file_path,
            language=language,
            enable_refinement=False,  # Fast mode for pre-commit
            enable_verification=False
        )
        
        return {
            'file': file_path,
            'success': result.get('success', False),
            'vulnerabilities': result.get('vulnerabilities_found', 0),
            'results': result.get('results', [])
        }
    except Exception as e:
        return {
            'file': file_path,
            'success': False,
            'error': str(e),
            'vulnerabilities': 0
        }


def main():
    print("🔒 Running Hybrid LLM security scan on staged files...")
    
    staged_files = get_staged_files()
    
    if not staged_files:
        print("✅ No files to scan")
        sys.exit(0)
    
    # Filter supported files
    files_to_scan = []
    for file_path in staged_files:
        supported, language = is_supported_file(file_path)
        if supported:
            files_to_scan.append((file_path, language))
    
    if not files_to_scan:
        print("✅ No supported files to scan")
        sys.exit(0)
    
    print(f"Scanning {len(files_to_scan)} file(s)...")
    
    all_vulnerabilities = []
    critical_vulnerabilities = []
    
    for file_path, language in files_to_scan:
        result = scan_file(file_path, language)
        
        if result.get('vulnerabilities', 0) > 0:
            for vuln_result in result.get('results', []):
                vuln = vuln_result.get('vulnerability', {})
                severity = vuln.get('severity', 'MEDIUM')
                
                all_vulnerabilities.append({
                    'file': file_path,
                    'type': vuln.get('type', 'Unknown'),
                    'severity': severity,
                    'line': vuln.get('line', 0),
                    'message': vuln.get('message', '')
                })
                
                if severity == 'CRITICAL':
                    critical_vulnerabilities.append({
                        'file': file_path,
                        'type': vuln.get('type', 'Unknown'),
                        'line': vuln.get('line', 0),
                        'message': vuln.get('message', '')
                    })
    
    # Print results
    print("\n" + "="*60)
    print("Pre-Commit Security Scan Results")
    print("="*60)
    
    if critical_vulnerabilities:
        print(f"\n🔴 CRITICAL: {len(critical_vulnerabilities)} critical vulnerabilities found!")
        for vuln in critical_vulnerabilities:
            print(f"  {vuln['file']}:{vuln['line']} - {vuln['type']}: {vuln['message']}")
        print("\n❌ Commit blocked! Please fix critical vulnerabilities before committing.")
        sys.exit(1)
    
    if all_vulnerabilities:
        print(f"\n⚠️  Found {len(all_vulnerabilities)} vulnerabilities:")
        for vuln in all_vulnerabilities[:10]:  # Show first 10
            print(f"  {vuln['file']}:{vuln['line']} - {vuln['type']} ({vuln['severity']})")
        
        if len(all_vulnerabilities) > 10:
            print(f"  ... and {len(all_vulnerabilities) - 10} more")
        
        print("\n⚠️  Commit allowed but vulnerabilities detected.")
        print("Consider fixing vulnerabilities before committing.")
        sys.exit(0)
    
    print("\n✅ No vulnerabilities found! Commit allowed.")
    sys.exit(0)


if __name__ == '__main__':
    main()


