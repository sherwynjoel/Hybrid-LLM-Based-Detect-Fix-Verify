#!/bin/bash
# Pre-commit hook for Hybrid LLM Framework

echo "🔒 Running Hybrid LLM security scan..."

# Get changed files
changed_files=$(git diff --cached --name-only --diff-filter=ACM | grep -E '\.(py|js|ts|java|cpp|c|h|hpp)$')

if [ -z "$changed_files" ]; then
    echo "✅ No supported files changed"
    exit 0
fi

# Run pre-commit scan
python scripts/pre_commit_scan.py

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo "❌ Security scan failed! Vulnerabilities found."
    echo "Please fix vulnerabilities before committing."
    echo ""
    echo "To bypass (not recommended): git commit --no-verify"
    exit 1
fi

echo "✅ Security scan passed!"
exit 0


