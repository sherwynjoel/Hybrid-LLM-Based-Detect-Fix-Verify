"""
Check CI scan results and determine if pipeline should pass/fail
"""

import json
import sys
from pathlib import Path


def check_results(report_path: str, fail_on_critical: bool = True, fail_on_high: bool = False) -> bool:
    """Check scan results and return True if should pass, False if should fail"""
    
    with open(report_path, 'r') as f:
        report = json.load(f)
    
    summary = report.get('summary', {})
    critical = summary.get('critical', 0)
    high = summary.get('high', 0)
    total = report.get('total_vulnerabilities', 0)
    
    print(f"\n🔒 Security Check Results:")
    print(f"  Critical: {critical}")
    print(f"  High: {high}")
    print(f"  Total: {total}")
    
    if fail_on_critical and critical > 0:
        print(f"\n❌ FAIL: {critical} critical vulnerabilities found!")
        print("Pipeline will fail. Please fix critical vulnerabilities before merging.")
        return False
    
    if fail_on_high and high > 0:
        print(f"\n❌ FAIL: {high} high severity vulnerabilities found!")
        print("Pipeline will fail. Please fix high severity vulnerabilities before merging.")
        return False
    
    if total > 0:
        print(f"\n⚠️  WARNING: {total} vulnerabilities found (non-blocking)")
        return True
    
    print(f"\n✅ PASS: No vulnerabilities found!")
    return True


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Check CI scan results')
    parser.add_argument('report', help='Path to security report JSON')
    parser.add_argument('--fail-on-critical', action='store_true', default=True,
                       help='Fail if critical vulnerabilities found')
    parser.add_argument('--fail-on-high', action='store_true',
                       help='Fail if high severity vulnerabilities found')
    
    args = parser.parse_args()
    
    if not Path(args.report).exists():
        print(f"Error: Report file {args.report} not found", file=sys.stderr)
        sys.exit(1)
    
    should_pass = check_results(args.report, args.fail_on_critical, args.fail_on_high)
    
    sys.exit(0 if should_pass else 1)


if __name__ == '__main__':
    main()

