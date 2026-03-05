#!/usr/bin/env python3
"""
Test langchain-google-genai specifically.
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("Testing langchain-google-genai")
print("=" * 60)

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print("✅ langchain_google_genai imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

try:
    print("\nInitializing ChatGoogleGenerativeAI...")
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro",
        api_key=os.getenv('GEMINI_API_KEY'),
        temperature=0.7
    )
    print("✅ Model initialized")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting simple invoke (synchronous)...")
print("(With 30 second timeout)")

try:
    # Simple synchronous call
    response = llm.invoke("Say hello and nothing else")
    print(f"✅ SUCCESS!")
    print(f"Response: {response.content}")
except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ langchain-google-genai is working!")
print("=" * 60)
