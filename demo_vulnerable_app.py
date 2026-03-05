import os
import sqlite3
import subprocess

def login_user(username, password):
    # VULNERABILITY 1: Hardcoded Secret (Should trigger Local Model routing)
    # CWE-798: Use of Hard-coded Credentials
    admin_password = "SuperSecretAdminPassword123!"
    
    if password == admin_password:
        print("Admin access granted via backdoor")

    # VULNERABILITY 2: SQL Injection (Should be detected as High Severity)
    # CWE-89: Improper Neutralization of Special Elements in a SQL Command
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Direct concatenation of user input into query
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)
    user = cursor.fetchone()
    
    if user:
        return True
    return False

def check_server_status(ip_address):
    # VULNERABILITY 3: OS Command Injection (Critical Severity)
    # CWE-78: Improper Neutralization of Special Elements used in an OS Command
    # User input is passed directly to the shell
    command = "ping -c 1 " + ip_address
    os.system(command)

def get_profile(user_id):
    # VULNERABILITY 4: Insecure Deserialization (New Feature Test)
    # CWE-502: Deserialization of Untrusted Data
    import pickle
    data = request.args.get('data')
    user_obj = pickle.loads(data)
    return user_obj
