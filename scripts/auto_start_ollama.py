"""Auto-start Ollama server if not running"""

import subprocess
import time
import requests
import os
import sys
from pathlib import Path

def check_ollama_running(port=11434):
    """Check if Ollama is running on given port"""
    try:
        response = requests.get(f"http://localhost:{port}/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(["ollama", "--version"], 
                              capture_output=True, 
                              timeout=5)
        return result.returncode == 0
    except:
        return False

def start_ollama_server():
    """Start Ollama server"""
    try:
        # Try to start Ollama in background (Windows)
        if sys.platform == "win32":
            subprocess.Popen(["ollama", "serve"], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:
            subprocess.Popen(["ollama", "serve"], 
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
        return True
    except Exception as e:
        print(f"Failed to start Ollama: {e}")
        return False

def check_codellama_model(port=11434):
    """Check if CodeLlama model is available"""
    try:
        response = requests.get(f"http://localhost:{port}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            for model in models:
                if 'codellama' in model.get('name', '').lower():
                    return True
        return False
    except:
        return False

def auto_setup_ollama():
    """Automatically setup and start Ollama if needed"""
    print("Checking Ollama setup...")
    
    # Check if Ollama is installed
    if not check_ollama_installed():
        print("[ERROR] Ollama is not installed!")
        print("   Please install from: https://ollama.ai/")
        return False
    
    print("[OK] Ollama is installed")
    
    # Check multiple ports
    ports_to_check = [11434, 11500]
    ollama_running = False
    working_port = None
    
    for port in ports_to_check:
        if check_ollama_running(port):
            print(f"[OK] Ollama server is running on port {port}")
            ollama_running = True
            working_port = port
            break
    
    if not ollama_running:
        print("[WARNING] Ollama server is not running. Starting...")
        if start_ollama_server():
            print("Waiting for server to start...")
            time.sleep(5)
            
            # Check again
            for port in ports_to_check:
                if check_ollama_running(port):
                    print(f"[OK] Ollama server started on port {port}")
                    ollama_running = True
                    working_port = port
                    break
            
            if not ollama_running:
                print("[ERROR] Failed to start Ollama server")
                print("   Please start manually: ollama serve")
                return False
        else:
            return False
    
    # Set environment variable for the working port
    if working_port:
        os.environ['OLLAMA_PORT'] = str(working_port)
        os.environ['OLLAMA_URL'] = f"http://localhost:{working_port}"
        print(f"[OK] Set OLLAMA_URL to http://localhost:{working_port}")
    
    # Check for CodeLlama model
    if check_codellama_model(working_port or 11434):
        print("[OK] CodeLlama model is available")
        return True
    else:
        print("[WARNING] CodeLlama model not found")
        print("   Downloading CodeLlama...")
        try:
            result = subprocess.run(["ollama", "pull", "codellama:13b"],
                                  timeout=600,  # 10 minutes timeout
                                  capture_output=True)
            if result.returncode == 0:
                print("[OK] CodeLlama model downloaded successfully")
                return True
            else:
                print("[ERROR] Failed to download CodeLlama model")
                print("   Run manually: ollama pull codellama:13b")
                return False
        except subprocess.TimeoutExpired:
            print("[WARNING] Download is taking longer than expected...")
            print("   Please wait or run manually: ollama pull codellama:13b")
            return False
        except Exception as e:
            print(f"[ERROR] Error downloading model: {e}")
            return False

if __name__ == "__main__":
    success = auto_setup_ollama()
    sys.exit(0 if success else 1)

