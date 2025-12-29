"""
Sample vulnerable code file for testing the Hybrid LLM Vulnerability Repair Framework
This file contains multiple common security vulnerabilities
"""

import os
import subprocess
import sqlite3
import pickle
from flask import Flask, request

app = Flask(__name__)

# ============================================
# VULNERABILITY 1: SQL Injection
# ============================================
def get_user_data(user_id):
    """SQL Injection vulnerability - user input directly in query"""
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # VULNERABLE: Direct string concatenation
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    return cursor.fetchone()

# ============================================
# VULNERABILITY 2: Command Injection
# ============================================
def ping_host(hostname):
    """Command Injection vulnerability - user input in system command"""
    # VULNERABLE: User input directly in subprocess call
    result = subprocess.call("ping -c 4 " + hostname, shell=True)
    return result

# ============================================
# VULNERABILITY 3: Path Traversal
# ============================================
def read_file(filename):
    """Path Traversal vulnerability - no path validation"""
    # VULNERABLE: No validation of file path
    file_path = "/data/" + filename
    with open(file_path, 'r') as f:
        return f.read()

# ============================================
# VULNERABILITY 4: Insecure Deserialization
# ============================================
def load_user_data(data):
    """Insecure Deserialization - unpickling untrusted data"""
    # VULNERABLE: Pickle can execute arbitrary code
    user_data = pickle.loads(data)
    return user_data

# ============================================
# VULNERABILITY 5: Hardcoded Credentials
# ============================================
def connect_to_database():
    """Hardcoded credentials vulnerability"""
    # VULNERABLE: Credentials in source code
    username = "admin"
    password = "password123"
    conn = sqlite3.connect(f'sqlite:///{username}:{password}@localhost/db')
    return conn

# ============================================
# VULNERABILITY 6: XSS (Cross-Site Scripting)
# ============================================
@app.route('/search')
def search():
    """XSS vulnerability - user input not sanitized"""
    query = request.args.get('q', '')
    # VULNERABLE: User input directly in HTML response
    return f"<h1>Search Results for: {query}</h1>"

# ============================================
# VULNERABILITY 7: Weak Cryptography
# ============================================
def hash_password(password):
    """Weak cryptography - using MD5"""
    import hashlib
    # VULNERABLE: MD5 is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()

# ============================================
# VULNERABILITY 8: Information Disclosure
# ============================================
def get_system_info():
    """Information disclosure - exposing sensitive system info"""
    # VULNERABLE: Exposing sensitive environment variables
    return {
        'os': os.environ.get('OS'),
        'path': os.environ.get('PATH'),
        'api_key': os.environ.get('SECRET_API_KEY')
    }

# ============================================
# VULNERABILITY 9: Insecure Random
# ============================================
def generate_token():
    """Insecure random number generation"""
    import random
    # VULNERABLE: Using predictable random for security token
    token = random.randint(1000, 9999)
    return str(token)

# ============================================
# VULNERABILITY 10: Missing Input Validation
# ============================================
def process_payment(amount):
    """Missing input validation"""
    # VULNERABLE: No validation of amount (could be negative)
    balance = 1000
    balance -= amount  # Could result in negative balance
    return balance

if __name__ == '__main__':
    app.run(debug=True)  # VULNERABLE: Debug mode enabled in production

