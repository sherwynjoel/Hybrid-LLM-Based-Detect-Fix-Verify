"""
Comprehensive unit test suite for the Hybrid LLM Vulnerability Repair Framework.

Run with:
    pytest tests/ -v
    pytest tests/ --cov=src --cov-report=term-missing
"""

import pytest
import sys
from pathlib import Path

# Ensure the project root is on sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

# ─── Fixtures ────────────────────────────────────────────────────────────────

SAMPLE_VULNERABLE_PYTHON = """
import sqlite3, subprocess, pickle, os, random
from flask import Flask, request
import hashlib

app = Flask(__name__)

def get_user(user_id):
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    return cursor.fetchone()

def ping_host(hostname):
    result = subprocess.call("ping -c 4 " + hostname, shell=True)
    return result

def read_file(filename):
    file_path = "/data/" + filename
    with open(file_path, 'r') as f:
        return f.read()

def load_data(data):
    return pickle.loads(data)

def connect_db():
    username = "admin"
    password = "password123"
    return None

def hash_pw(password):
    return hashlib.md5(password.encode()).hexdigest()

def gen_token():
    return str(random.randint(1000, 9999))
"""

SAMPLE_FIXED_SQL = """
import sqlite3

def get_user(user_id):
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE id = ?"
    cursor.execute(query, (user_id,))
    return cursor.fetchone()
"""

SAMPLE_FIXED_CMD = """
import subprocess, shlex

def ping_host(hostname):
    safe_host = shlex.quote(hostname)
    result = subprocess.call(["ping", "-c", "4", safe_host], shell=False)
    return result
"""

SAMPLE_FIXED_HASH = """
import hashlib

def hash_pw(password):
    return hashlib.sha256(password.encode()).hexdigest()
"""

SAMPLE_FIXED_RANDOM = """
import secrets

def gen_token():
    return str(secrets.randbelow(9000) + 1000)
"""

SAMPLE_FIXED_CREDS = """
import os

def connect_db():
    username = os.getenv("DB_USERNAME", "")
    password = os.getenv("DB_PASSWORD", "")
    return None
"""

SAMPLE_C_BUFFER = """
#include <string.h>
void copy_name(char* buf, const char* name) {
    strcpy(buf, name);
}
"""

SAMPLE_C_FIXED = """
#include <string.h>
void copy_name(char* buf, size_t buf_len, const char* name) {
    strncpy(buf, name, buf_len - 1);
    buf[buf_len - 1] = '\\0';
}
"""


# ─── Detection tests ──────────────────────────────────────────────────────────

class TestVulnerabilityDetector:

    @pytest.fixture(autouse=True)
    def setup(self):
        from src.detection.vulnerability_detector import VulnerabilityDetector
        self.detector = VulnerabilityDetector()

    def test_detects_sql_injection(self):
        vulns = self.detector.detect(SAMPLE_VULNERABLE_PYTHON, 'python')
        types = [v['type'] for v in vulns]
        assert any('SQL' in t for t in types), f"SQL Injection not found. Got: {types}"

    def test_detects_command_injection(self):
        vulns = self.detector.detect(SAMPLE_VULNERABLE_PYTHON, 'python')
        types = [v['type'] for v in vulns]
        assert any('Command' in t or 'Injection' in t for t in types), \
            f"Command Injection not found. Got: {types}"

    def test_detects_weak_crypto(self):
        vulns = self.detector.detect(SAMPLE_VULNERABLE_PYTHON, 'python')
        types = [v['type'] for v in vulns]
        assert any('Crypto' in t or 'crypto' in t.lower() for t in types), \
            f"Weak Cryptography not found. Got: {types}"

    def test_detects_hardcoded_credentials(self):
        vulns = self.detector.detect(SAMPLE_VULNERABLE_PYTHON, 'python')
        types = [v['type'] for v in vulns]
        assert any('Credential' in t for t in types), \
            f"Hardcoded Credentials not found. Got: {types}"

    def test_detects_insecure_random(self):
        vulns = self.detector.detect(SAMPLE_VULNERABLE_PYTHON, 'python')
        types = [v['type'] for v in vulns]
        assert any('Random' in t or 'random' in t.lower() for t in types), \
            f"Insecure Random not found. Got: {types}"

    def test_cwe_classification(self):
        vulns = self.detector.detect(SAMPLE_VULNERABLE_PYTHON, 'python')
        cwes = [v.get('cwe', '') for v in vulns]
        assert 'CWE-89' in cwes, f"CWE-89 (SQL Injection) not classified. Got CWEs: {cwes}"

    def test_clean_code_no_vulnerabilities(self):
        clean_code = 'def add(a, b):\n    return a + b\n'
        vulns = self.detector.detect(clean_code, 'python')
        assert len(vulns) == 0, f"Unexpected vulns in clean code: {vulns}"

    def test_extract_context(self):
        vuln = {'line': 5, 'type': 'test'}
        ctx = self.detector.extract_context(SAMPLE_VULNERABLE_PYTHON, vuln)
        assert 'context' in ctx
        assert isinstance(ctx['context'], str)
        assert len(ctx['context']) > 0

    def test_detect_returns_list(self):
        result = self.detector.detect(SAMPLE_VULNERABLE_PYTHON, 'python')
        assert isinstance(result, list)

    def test_each_vuln_has_required_keys(self):
        vulns = self.detector.detect(SAMPLE_VULNERABLE_PYTHON, 'python')
        required = {'type', 'severity', 'line', 'message', 'cwe'}
        for v in vulns:
            missing = required - set(v.keys())
            assert not missing, f"Vulnerability missing keys {missing}: {v}"


# ─── Router tests ─────────────────────────────────────────────────────────────

class TestLLMRouter:

    @pytest.fixture(autouse=True)
    def setup(self):
        from src.llm_router.router import LLMRouter
        self.router = LLMRouter()

    def test_sensitive_code_routes_local(self):
        sensitive = 'password = "super_secret_123"'
        vuln = {'severity': 'LOW', 'context': sensitive}
        decision = self.router.route(sensitive, vuln, 'python')
        assert decision == 'local', "Sensitive code must route to local"

    def test_normal_code_privacy_first_routes_cloud(self):
        self.router.privacy_first_mode = True
        code = 'def add(a, b): return a + b'
        vuln = {'severity': 'LOW', 'context': ''}
        decision = self.router.route(code, vuln, 'python')
        assert decision == 'cloud', "Normal code in privacy-first mode should go cloud"

    def test_critical_severity_routes_cloud(self):
        self.router.privacy_first_mode = True
        code = 'print("hello")'
        vuln = {'severity': 'CRITICAL', 'context': ''}
        decision = self.router.route(code, vuln, 'python')
        assert decision == 'cloud', "CRITICAL severity should route cloud"

    def test_privacy_detection_api_key(self):
        code = 'api_key = "sk_live_abc123xyz456"'
        vuln = {'context': code}
        assert self.router._requires_privacy(code, vuln) is True

    def test_privacy_detection_password(self):
        code = 'password = "hunter2"'
        vuln = {'context': ''}
        assert self.router._requires_privacy(code, vuln) is True

    def test_privacy_not_triggered_by_clean_code(self):
        code = 'x = 42\nprint(x)'
        vuln = {'context': ''}
        assert self.router._requires_privacy(code, vuln) is False

    def test_routing_decision_returns_dict(self):
        code = 'def foo(): pass'
        vuln = {'severity': 'LOW', 'context': ''}
        result = self.router.get_routing_decision(code, vuln, 'python')
        assert 'model' in result
        assert 'reasons' in result
        assert 'complexity_score' in result
        assert 'privacy_required' in result

    def test_complexity_calculation_python(self):
        code = 'def foo():\n    try:\n        pass\n    except:\n        pass\n' * 10
        vuln = {'context': ''}
        score = self.router._calculate_complexity(code, vuln, 'python')
        assert isinstance(score, int)
        assert score > 0

    def test_fallback_to_cloud_on_none_result(self):
        assert self.router.should_fallback_to_cloud(None) is True

    def test_no_fallback_on_good_result(self):
        result = {'quality_score': 0.9, 'verification_passed': True}
        assert self.router.should_fallback_to_cloud(result) is False


# ─── Fallback fix generator tests ────────────────────────────────────────────

class TestFallbackFixGenerator:

    @pytest.fixture(autouse=True)
    def setup(self):
        from src.repair.fallback_fix_generator import FallbackFixGenerator
        self.gen = FallbackFixGenerator()

    def test_sql_injection_fix(self):
        code = (
            "def get_user(uid):\n"
            "    query = \"SELECT * FROM users WHERE id = \" + uid\n"
            "    cursor.execute(query)\n"
        )
        vuln = {'type': 'SQL Injection', 'cwe': 'CWE-89', 'line': 2}
        fixed = self.gen.generate_fix(code, vuln, 'python')
        assert '?' in fixed, "Expected parameterized placeholder '?' in SQL fix"
        assert '+' not in fixed.split('query')[1].split('\n')[0], \
            "String concatenation should be removed from query line"

    def test_weak_crypto_fix(self):
        code = "import hashlib\ndef hash_pw(p):\n    return hashlib.md5(p.encode()).hexdigest()\n"
        vuln = {'type': 'Weak Cryptography', 'cwe': 'CWE-327', 'line': 3}
        fixed = self.gen.generate_fix(code, vuln, 'python')
        assert 'sha256' in fixed, "MD5 should be replaced with SHA-256"
        assert 'md5' not in fixed.lower(), "MD5 should not remain in fixed code"

    def test_insecure_random_fix(self):
        code = "import random\ntoken = random.randint(1000, 9999)\n"
        vuln = {'type': 'Insecure Random', 'cwe': 'CWE-338', 'line': 2}
        fixed = self.gen.generate_fix(code, vuln, 'python')
        assert 'secrets' in fixed, "Should replace random with secrets module"

    def test_hardcoded_credentials_fix(self):
        code = "import os\ndef conn():\n    password = \"mypassword\"\n"
        vuln = {'type': 'Hardcoded Credentials', 'cwe': 'CWE-798', 'line': 3}
        fixed = self.gen.generate_fix(code, vuln, 'python')
        assert 'os.getenv' in fixed or 'environ' in fixed, \
            "Password should come from environment variable"

    def test_unsupported_language_returns_original(self):
        code = "def foo(): pass"
        vuln = {'type': 'SQL Injection', 'cwe': 'CWE-89', 'line': 1}
        result = self.gen.generate_fix(code, vuln, 'cobol')
        assert result == code


# ─── Vulnerability tester tests ───────────────────────────────────────────────

class TestVulnerabilityTester:

    @pytest.fixture(autouse=True)
    def setup(self):
        from src.verification.vulnerability_tester import VulnerabilityTester
        from src.utils.config import config
        config.enable_exploit_verification = True
        self.tester = VulnerabilityTester()

    def test_sql_harness_detects_fixed_code(self):
        result = self.tester.test_vulnerability(
            SAMPLE_FIXED_SQL, '', 'python', is_fixed=True, cwe='CWE-89'
        )
        assert result['test_passed'] is True, \
            f"Fixed SQL code should pass. Output: {result.get('output', '')}"

    def test_md5_harness_flags_unfixed_code(self):
        code = "import hashlib\ndef h(p):\n    return hashlib.md5(p.encode()).hexdigest()\n"
        result = self.tester.test_vulnerability(
            code, '', 'python', is_fixed=True, cwe='CWE-327'
        )
        # Fixed=True but still using MD5 → should fail
        assert result['test_passed'] is False, \
            "Unfixed MD5 code should NOT pass the fixed-code check"

    def test_sha256_harness_passes_fixed_code(self):
        result = self.tester.test_vulnerability(
            SAMPLE_FIXED_HASH, '', 'python', is_fixed=True, cwe='CWE-327'
        )
        assert result['test_passed'] is True, \
            f"SHA-256 code should pass. Output: {result.get('output', '')}"

    def test_secrets_harness_passes_fixed_code(self):
        result = self.tester.test_vulnerability(
            SAMPLE_FIXED_RANDOM, '', 'python', is_fixed=True, cwe='CWE-338'
        )
        assert result['test_passed'] is True, \
            f"secrets.randbelow should pass. Output: {result.get('output', '')}"

    def test_hardcoded_creds_flagged(self):
        code = "def conn():\n    password = 'abc123'\n"
        result = self.tester.test_vulnerability(
            code, '', 'python', is_fixed=True, cwe='CWE-798'
        )
        assert result['test_passed'] is False, \
            "Code with hardcoded password should fail the fixed-code check"

    def test_env_var_creds_pass(self):
        result = self.tester.test_vulnerability(
            SAMPLE_FIXED_CREDS, '', 'python', is_fixed=True, cwe='CWE-798'
        )
        assert result['test_passed'] is True, \
            f"Env-var credentials should pass. Output: {result.get('output', '')}"

    def test_result_has_required_keys(self):
        result = self.tester.test_vulnerability(
            'x = 1', '', 'python', is_fixed=True, cwe='CWE-OTHER'
        )
        assert 'test_passed' in result
        assert 'vulnerable' in result
        assert 'output' in result

    def test_timeout_returns_failed(self, monkeypatch):
        import subprocess
        def mock_run(*args, **kwargs):
            raise subprocess.TimeoutExpired(cmd='python', timeout=1)
        monkeypatch.setattr(subprocess, 'run', mock_run)
        result = self.tester.test_vulnerability('x=1', '', 'python', cwe='CWE-GENERIC')
        assert result['test_passed'] is False
        assert 'Timeout' in result.get('error', '') or 'timed out' in result.get('output', '').lower()

    def test_verify_fix_returns_fix_successful_key(self):
        result = self.tester.verify_fix(
            SAMPLE_VULNERABLE_PYTHON, SAMPLE_FIXED_SQL,
            '', 'python', cwe='CWE-89'
        )
        assert 'fix_successful' in result
        assert 'original_test' in result
        assert 'fixed_test' in result


# ─── Metrics calculator tests ─────────────────────────────────────────────────

class TestMetricsCalculator:

    @pytest.fixture(autouse=True)
    def setup(self):
        from src.utils.metrics import MetricsCalculator, RepairMetrics
        self.calc = MetricsCalculator()
        self.RepairMetrics = RepairMetrics

    def test_similarity_identical(self):
        score = self.calc.calculate_code_similarity("abc", "abc")
        assert score == 1.0

    def test_similarity_different(self):
        score = self.calc.calculate_code_similarity("abc", "xyz")
        assert score < 0.5

    def test_similarity_between_zero_and_one(self):
        score = self.calc.calculate_code_similarity("hello world", "hello there")
        assert 0.0 <= score <= 1.0

    def test_fix_quality_all_passed(self):
        score = self.calc.calculate_fix_quality("a" * 100, "a" * 100, True, True)
        assert score > 0.9

    def test_fix_quality_all_failed(self):
        score = self.calc.calculate_fix_quality("a" * 100, "b" * 100, False, False)
        assert score < 0.5

    def _make_metric(self, exploit=True, static=True, iters=1, time=0.5):
        return self.RepairMetrics(
            vulnerability_id="v1",
            original_code="orig",
            fixed_code="fixed",
            fix_quality_score=0.8,
            code_similarity=0.9,
            exploit_test_passed=exploit,
            static_analysis_passed=static,
            iteration_count=iters,
            processing_time=time,
        )

    def test_accuracy_all_passed(self):
        metrics = [self._make_metric(True, True) for _ in range(5)]
        assert self.calc.calculate_accuracy(metrics) == 1.0

    def test_accuracy_none_passed(self):
        metrics = [self._make_metric(False, False) for _ in range(5)]
        assert self.calc.calculate_accuracy(metrics) == 0.0

    def test_accuracy_empty_list(self):
        assert self.calc.calculate_accuracy([]) == 0.0

    def test_avg_iterations(self):
        metrics = [self._make_metric(iters=i) for i in [1, 2, 3]]
        assert self.calc.calculate_average_iterations(metrics) == 2.0

    def test_avg_time(self):
        metrics = [self._make_metric(time=t) for t in [1.0, 2.0, 3.0]]
        assert abs(self.calc.calculate_average_time(metrics) - 2.0) < 0.001

    def test_generate_report_keys(self):
        metrics = [self._make_metric()]
        report = self.calc.generate_report(metrics)
        required = {'total_repairs', 'accuracy', 'precision', 'recall',
                    'f1_score', 'average_iterations', 'average_processing_time',
                    'successful_repairs', 'failed_repairs'}
        assert required.issubset(report.keys())

    def test_f1_zero_division(self):
        score = self.calc.calculate_f1_score(0.0, 0.0)
        assert score == 0.0


# ─── Main framework integration tests ─────────────────────────────────────────

class TestVulnerabilityRepairFramework:

    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        from src.main import VulnerabilityRepairFramework
        self.fw = VulnerabilityRepairFramework()
        self.tmp_path = tmp_path

    def _make_file(self, content: str, suffix: str = '.py') -> Path:
        p = self.tmp_path / f"test_code{suffix}"
        p.write_text(content, encoding='utf-8')
        return p

    def test_process_file_clean_code(self):
        fp = self._make_file("def add(a, b):\n    return a + b\n")
        result = self.fw.process_file(str(fp), language='python',
                                      enable_refinement=False, enable_verification=False)
        assert result['success'] is True
        assert result['vulnerabilities_found'] == 0

    def test_process_file_with_sql_injection(self):
        code = (
            "import sqlite3\n"
            "def q(uid):\n"
            "    query = \"SELECT * FROM users WHERE id = \" + uid\n"
            "    conn = sqlite3.connect(':memory:')\n"
            "    conn.cursor().execute(query)\n"
        )
        fp = self._make_file(code)
        result = self.fw.process_file(str(fp), language='python',
                                      enable_refinement=False, enable_verification=False)
        assert result['success'] is True
        assert result['vulnerabilities_found'] > 0

    def test_process_file_result_structure(self):
        fp = self._make_file(SAMPLE_VULNERABLE_PYTHON)
        result = self.fw.process_file(str(fp), language='python',
                                      enable_refinement=False, enable_verification=False)
        assert 'file_path' in result
        assert 'language' in result
        assert 'vulnerabilities_found' in result

    def test_process_file_missing_file(self):
        result = self.fw.process_file('/nonexistent/path/code.py', language='python')
        assert result['success'] is False
        assert 'error' in result

    def test_process_directory_empty(self):
        empty_dir = self.tmp_path / "empty"
        empty_dir.mkdir()
        result = self.fw.process_directory(str(empty_dir))
        assert result['success'] is True
        assert result.get('files_scanned', 0) == 0

    def test_process_directory_with_python_files(self):
        (self.tmp_path / "a.py").write_text("x = 1", encoding='utf-8')
        (self.tmp_path / "b.py").write_text("y = 2", encoding='utf-8')
        result = self.fw.process_directory(str(self.tmp_path),
                                           enable_refinement=False,
                                           enable_verification=False)
        assert result['success'] is True
        assert result['files_scanned'] >= 2

    def test_process_directory_result_structure(self):
        (self.tmp_path / "test.py").write_text("def f(): pass", encoding='utf-8')
        result = self.fw.process_directory(str(self.tmp_path),
                                           enable_refinement=False,
                                           enable_verification=False)
        required = {'success', 'directory', 'files_scanned',
                    'files_with_vulnerabilities', 'total_vulnerabilities',
                    'total_processing_time', 'directory_summary'}
        assert required.issubset(result.keys())

    def test_process_directory_not_a_directory(self):
        fp = self._make_file("x = 1")
        result = self.fw.process_directory(str(fp))
        assert result['success'] is False

    def test_generate_summary_all_succeeded(self):
        results = [
            {'success': True, 'processing_time': 1.0, 'iterations': 2,
             'metrics': {'exploit_test_passed': True, 'static_analysis_passed': True}}
            for _ in range(3)
        ]
        summary = self.fw._generate_summary(results)
        assert summary['success_rate'] == 1.0
        assert summary['exploit_verification_passed'] == 3

    def test_generate_summary_empty(self):
        summary = self.fw._generate_summary([])
        assert summary['total_vulnerabilities'] == 0
        assert summary['success_rate'] == 0


# ─── Config tests ─────────────────────────────────────────────────────────────

class TestConfig:

    def test_config_loads(self):
        from src.utils.config import config
        assert config is not None

    def test_config_has_defaults(self):
        from src.utils.config import config
        assert isinstance(config.max_iterations, int)
        assert config.max_iterations > 0
        assert isinstance(config.convergence_threshold, float)
        assert 0.0 < config.convergence_threshold <= 1.0

    def test_config_exploit_timeout_positive(self):
        from src.utils.config import config
        assert config.exploit_timeout > 0

    def test_config_complexity_threshold_positive(self):
        from src.utils.config import config
        assert config.complexity_threshold > 0
