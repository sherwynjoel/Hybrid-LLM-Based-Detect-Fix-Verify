"""Easy one-click Ollama starter for the framework"""

import subprocess
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from scripts.auto_start_ollama import auto_setup_ollama

if __name__ == "__main__":
    print("=" * 50)
    print("Easy Ollama Setup for Hybrid LLM Framework")
    print("=" * 50)
    print()
    
    success = auto_setup_ollama()
    
    print()
    if success:
        print("=" * 50)
        print("[SUCCESS] Local LLM is ready to use!")
        print("=" * 50)
        print()
        print("You can now:")
        print("  1. Refresh your web UI page")
        print("  2. CodeLlama should show as 'Available'")
        print()
        print("Keep this window open to keep Ollama running.")
        print("Press Ctrl+C to stop.")
    else:
        print("=" * 50)
        print("[ERROR] Setup incomplete")
        print("=" * 50)
        print()
        print("Please:")
        print("  1. Install Ollama: https://ollama.ai/")
        print("  2. Run: ollama pull codellama:13b")
        print("  3. Run: ollama serve")
    
    # Keep running if successful
    if success:
        try:
            input("\nPress Enter to exit (this will stop Ollama)...")
        except KeyboardInterrupt:
            print("\nStopping...")

