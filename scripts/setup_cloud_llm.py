"""Setup script for Cloud LLM (ChatGPT-4)"""

import os
import sys

def check_openai_key():
    """Check if OPENAI_API_KEY is set"""
    api_key = os.getenv('OPENAI_API_KEY', '')
    if api_key:
        # Mask the key for display
        masked = api_key[:8] + '...' + api_key[-4:] if len(api_key) > 12 else '***'
        return True, masked
    return False, None

def test_connection():
    """Test OpenAI API connection"""
    try:
        from src.llm_models.chatgpt_cloud import ChatGPTCloud
        chatgpt = ChatGPTCloud()
        return chatgpt.is_available()
    except Exception as e:
        print(f"Error testing connection: {e}")
        return False

def setup_cloud_llm():
    """Setup and verify Cloud LLM"""
    print("=" * 60)
    print("Cloud LLM (ChatGPT-4) Setup")
    print("=" * 60)
    print()
    
    # Check if API key is set
    has_key, masked_key = check_openai_key()
    
    if has_key:
        print(f"[OK] OPENAI_API_KEY is set: {masked_key}")
        print()
        print("Testing connection...")
        if test_connection():
            print("[SUCCESS] ChatGPT-4 is available and working!")
            print()
            print("You can now use ChatGPT-4 in the framework.")
            return True
        else:
            print("[ERROR] API key is set but connection failed")
            print()
            print("Possible issues:")
            print("  1. API key is invalid or expired")
            print("  2. No internet connection")
            print("  3. OpenAI API is down")
            print()
            print("Get a new API key from: https://platform.openai.com/api-keys")
            return False
    else:
        print("[ERROR] OPENAI_API_KEY is not set")
        print()
        print("To set up ChatGPT-4:")
        print()
        print("1. Get your API key:")
        print("   https://platform.openai.com/api-keys")
        print()
        print("2. Set environment variable:")
        print()
        print("   PowerShell:")
        print("   $env:OPENAI_API_KEY = 'your-api-key-here'")
        print()
        print("   Command Prompt:")
        print("   set OPENAI_API_KEY=your-api-key-here")
        print()
        print("   Linux/Mac:")
        print("   export OPENAI_API_KEY='your-api-key-here'")
        print()
        print("3. Make it permanent (Windows):")
        print("   - System Properties -> Environment Variables")
        print("   - Add OPENAI_API_KEY to User variables")
        print()
        print("4. Restart Streamlit server")
        print()
        return False

if __name__ == "__main__":
    success = setup_cloud_llm()
    sys.exit(0 if success else 1)


