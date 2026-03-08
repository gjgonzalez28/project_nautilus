#!/usr/bin/env python3
"""
Test NeMo Guardrails specifically to find the issue.
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

load_dotenv()

print("Testing NeMo Guardrails")
print("=" * 60)

try:
    from nemoguardrails import LLMRails, RailsConfig
    print("✅ nemoguardrails imported")
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

print("\nLoading config from ./config/rails...")
try:
    config = RailsConfig.from_path('./config/rails')
    print("✅ Config loaded successfully")
    print(f"   Dialog flows: {[f for f in dir(config) if 'flow' in f.lower()]}")
except Exception as e:
    print(f"❌ Config load failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nInitializing LLMRails...")
try:
    rails = LLMRails(config)
    print("✅ LLMRails initialized")
except Exception as e:
    print(f"❌ LLMRails init failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting NeMo generate() synchronously (30 second timeout)...")
print("This uses the hello_world flow as fallback...")
try:
    # Synchronous wrapper
    import nest_asyncio
    nest_asyncio.apply()  # Allow nested async
    
    response = asyncio.run(asyncio.wait_for(
        rails.generate_async(
            messages=[{"role": "user", "content": "Hello"}]
        ),
        timeout=30.0
    ))
    
    print(f"✅ SUCCESS!")
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    
except asyncio.TimeoutError:
    print(f"❌ TIMEOUT after 30 seconds")
    print("\nThis is the problem!")
    print("NeMo's generate_async() hangs even with a simple message")
    print("\nPossible causes:")
    print("1. Colang flow syntax error (check logs)")
    print("2. NeMo initialization issue with config")
    print("3. Flow orchestration bug in NeMo 0.20.0")
    sys.exit(1)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ NeMo is working with your flows!")
print("=" * 60)
