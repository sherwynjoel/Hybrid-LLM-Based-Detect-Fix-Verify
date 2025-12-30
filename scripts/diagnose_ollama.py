"""Diagnose Ollama and CodeLlama setup"""

import requests
import subprocess
import sys
import os

def check_ollama_process():
    """Check if Ollama process is running"""
    try:
        if sys.platform == "win32":
            result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq ollama.exe"],
                                   capture_output=True, text=True)
            if "ollama.exe" in result.stdout:
                return True
        else:
            result = subprocess.run(["pgrep", "-f", "ollama"],
                                   capture_output=True)
            return result.returncode == 0
    except:
        pass
    return False

def check_ollama_server(port):
    """Check if Ollama server is responding on given port"""
    try:
        response = requests.get(f"http://localhost:{port}/api/tags", timeout=2)
        if response.status_code == 200:
            return True, response.json()
        return False, None
    except:
        return False, None

def check_codellama_model(data):
    """Check if CodeLlama model is in the response"""
    if not data:
        return False, None
    models = data.get('models', [])
    for model in models:
        name = model.get('name', '').lower()
        if 'codellama' in name:
            return True, model.get('name')
    return False, None

def diagnose():
    """Run full diagnosis"""
    print("=" * 60)
    print("Ollama & CodeLlama Diagnosis")
    print("=" * 60)
    print()
    
    # Check 1: Ollama process
    print("[1] Checking Ollama process...")
    if check_ollama_process():
        print("    [OK] Ollama process is running")
    else:
        print("    [ERROR] Ollama process not found")
        print("    Solution: Run 'ollama serve' in a terminal")
        return False
    print()
    
    # Check 2: Ollama server on port 11434
    print("[2] Checking Ollama server on port 11434...")
    running, data = check_ollama_server(11434)
    if running:
        print("    [OK] Ollama server is responding on port 11434")
        has_model, model_name = check_codellama_model(data)
        if has_model:
            print(f"    [OK] CodeLlama model found: {model_name}")
            print()
            print("=" * 60)
            print("[SUCCESS] Everything is working!")
            print("=" * 60)
            print()
            print("If web UI still shows 'Not Available', try:")
            print("  1. Refresh the web UI page")
            print("  2. Restart the Streamlit server")
            return True
        else:
            print("    [ERROR] CodeLlama model not found")
            print("    Solution: Run 'ollama pull codellama:13b'")
    else:
        print("    [ERROR] Ollama server not responding on port 11434")
    print()
    
    # Check 3: Ollama server on port 11500
    print("[3] Checking Ollama server on port 11500...")
    running, data = check_ollama_server(11500)
    if running:
        print("    [OK] Ollama server is responding on port 11500")
        has_model, model_name = check_codellama_model(data)
        if has_model:
            print(f"    [OK] CodeLlama model found: {model_name}")
            print()
            print("=" * 60)
            print("[SUCCESS] Everything is working on port 11500!")
            print("=" * 60)
            print()
            print("Set environment variable:")
            print("  $env:OLLAMA_PORT = '11500'")
            print("  $env:OLLAMA_URL = 'http://localhost:11500'")
            print()
            print("Then restart Streamlit server")
            return True
        else:
            print("    [ERROR] CodeLlama model not found")
    else:
        print("    [INFO] Ollama server not running on port 11500")
    print()
    
    # Summary
    print("=" * 60)
    print("[DIAGNOSIS SUMMARY]")
    print("=" * 60)
    print()
    print("Issues found:")
    print("  1. Ollama server is not responding on any port")
    print()
    print("Solutions:")
    print("  1. Start Ollama server:")
    print("     - Open a new terminal")
    print("     - Run: ollama serve")
    print("     - Keep that terminal window open")
    print()
    print("  2. Download CodeLlama model (if needed):")
    print("     - Run: ollama pull codellama:13b")
    print()
    print("  3. After starting, refresh the web UI page")
    print()
    
    return False

if __name__ == "__main__":
    success = diagnose()
    sys.exit(0 if success else 1)


