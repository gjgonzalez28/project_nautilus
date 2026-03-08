#!/usr/bin/env python3
"""
Quick diagnostic: Test if Gemini API is even responding.
"""

import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

print("Gemini API Diagnostic")
print("=" * 60)
print(f"API Key present: {bool(api_key)}")
print(f"API Key prefix: {api_key[:20] if api_key else 'NONE'}...")

if not api_key:
    print("\n❌ ERROR: No API key found in .env")
    print("Set GEMINI_API_KEY in .env file")
    exit(1)

print(f"\nAttempting to configure google-genai...")

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    print("✅ Configuration successful")
except Exception as e:
    print(f"❌ Configuration failed: {e}")
    exit(1)

print(f"\nTesting list_models (this makes an API call)...")
print("This will tell us if the API is reachable...")

try:
    # This is a simple, fast API call to test connectivity
    models = genai.list_models()
    count = 0
    for model in models:
        count += 1
        if count >= 3:
            break
        print(f"  - {model.name}")
    print(f"✅ API is responding! Found {count}+ models")
except Exception as e:
    print(f"❌ API not responding: {e}")
    print("\nPossible causes:")
    print("1. Invalid API key")
    print("2. Gemini not enabled in Google Cloud project")
    print("3. API quota exceeded")
    print("4. Network/firewall blocking")
    exit(1)

print("\n" + "=" * 60)
print("Diagnostic: API connectivity is WORKING")
print("The timeout is likely in the langchain or NeMo layer")
print("=" * 60)
