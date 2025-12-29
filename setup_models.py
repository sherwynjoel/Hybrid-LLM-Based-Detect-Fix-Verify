"""Script to help set up LLM models for the framework"""

import os
import subprocess
import sys

print("=" * 60)
print("LLM Model Setup Guide")
print("=" * 60)
print()

# Check CodeLlama (Ollama)
print("[1] Checking CodeLlama 13B (Local)...")
try:
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5)
    if 'codellama' in result.stdout.lower():
        print("   [OK] CodeLlama found via Ollama")
        codellama_available = True
    else:
        print("   [FAIL] CodeLlama not found")
        print("   To install:")
        print("   1. Install Ollama from https://ollama.ai")
        print("   2. Run: ollama pull codellama:13b")
        codellama_available = False
except FileNotFoundError:
    print("   [FAIL] Ollama not installed")
    print("   Install from: https://ollama.ai")
    codellama_available = False
except Exception as e:
    print(f"   [WARNING] Error checking Ollama: {e}")
    codellama_available = False

print()

# Check ChatGPT API Key
print("[2] Checking ChatGPT-4 (Cloud)...")
api_key = os.getenv('OPENAI_API_KEY')
if api_key:
    print("   [OK] OpenAI API key found")
    print(f"   Key starts with: {api_key[:10]}...")
    chatgpt_available = True
else:
    print("   [FAIL] OpenAI API key not found")
    print("   To set up:")
    print("   1. Get API key from https://platform.openai.com/api-keys")
    print("   2. Set environment variable:")
    print("      Windows PowerShell: $env:OPENAI_API_KEY='your-key-here'")
    print("      Windows CMD: set OPENAI_API_KEY=your-key-here")
    print("      Or add to config.yaml")
    chatgpt_available = False

print()

# Summary
print("=" * 60)
print("SETUP SUMMARY")
print("=" * 60)
print(f"CodeLlama 13B (Local): {'[OK] Ready' if codellama_available else '[FAIL] Not Configured'}")
print(f"ChatGPT-4 (Cloud): {'[OK] Ready' if chatgpt_available else '[FAIL] Not Configured'}")
print()

if not codellama_available and not chatgpt_available:
    print("[WARNING] No models are configured!")
    print("   The framework needs at least one model to work.")
    print("   You can:")
    print("   1. Set up CodeLlama (free, local): .\\setup_codellama.ps1")
    print("   2. Set up ChatGPT-4 (requires API key): .\\setup_chatgpt.ps1")
    print("   3. Or both for hybrid routing")
elif codellama_available or chatgpt_available:
    print("[OK] At least one model is ready. Framework can work!")
    if codellama_available and chatgpt_available:
        print("[OK] Both models ready - full hybrid mode available!")

print()
print("=" * 60)

