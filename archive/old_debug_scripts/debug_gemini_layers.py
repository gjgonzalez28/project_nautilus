#!/usr/bin/env python3
"""
Comprehensive Gemini API Debugging Script
Tests each layer of the stack to find where the timeout occurs.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load env vars
load_dotenv()

print("=" * 70)
print("GEMINI API DEBUGGING - LAYER BY LAYER")
print("=" * 70)

# ============================================================================
# Layer 1: Test Google GenAI SDK directly
# ============================================================================

print("\n[Layer 1] Testing google-genai SDK directly...")
print("-" * 70)

try:
    import google.generativeai as genai
    
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set in .env")
    
    genai.configure(api_key=api_key)
    print(f"✅ google-genai SDK imported and configured")
    
    # Test model availability
    try:
        model = genai.GenerativeModel('gemini-2.5-pro')
        print(f"✅ Model 'gemini-2.5-pro' loaded")
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        sys.exit(1)
    
    # Test synchronous call
    print("\nTesting synchronous API call (5 second timeout)...")
    response = asyncio.run(asyncio.wait_for(
        asyncio.to_thread(
            lambda: model.generate_content("Hello, test message")
        ),
        timeout=5.0
    ))
    print(f"✅ Synchronous call succeeded")
    print(f"   Response: {response.text[:100]}...")
    
except ImportError:
    print("❌ google-genai not installed: pip install google-generativeai")
    sys.exit(1)
except asyncio.TimeoutError:
    print("❌ TIMEOUT on synchronous call (>5 seconds)")
    print("   This suggests API is slow or unreachable")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# Layer 2: Test langchain-google-genai
# ============================================================================

print("\n[Layer 2] Testing langchain-google-genai...")
print("-" * 70)

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    print(f"✅ langchain-google-genai imported")
    
    # Initialize model
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            api_key=os.getenv('GEMINI_API_KEY'),
            temperature=0.7
        )
        print(f"✅ ChatGoogleGenerativeAI model initialized")
    except Exception as e:
        print(f"❌ Failed to initialize ChatGoogleGenerativeAI: {e}")
        sys.exit(1)
    
    # Test synchronous invoke
    print("\nTesting synchronous invoke (5 second timeout)...")
    result = asyncio.run(asyncio.wait_for(
        asyncio.to_thread(
            lambda: llm.invoke("Hello from langchain")
        ),
        timeout=5.0
    ))
    print(f"✅ Synchronous invoke succeeded")
    print(f"   Response: {str(result.content)[:100]}...")
    
except ImportError as e:
    print(f"❌ langchain-google-genai not installed: {e}")
    print("   pip install langchain-google-genai")
    sys.exit(1)
except asyncio.TimeoutError:
    print("❌ TIMEOUT on langchain invoke (>5 seconds)")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# Layer 3: Test async invoke
# ============================================================================

print("\n[Layer 3] Testing async invoke...")
print("-" * 70)

async def test_async_invoke():
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-pro",
            api_key=os.getenv('GEMINI_API_KEY'),
            temperature=0.7
        )
        
        print("Testing async ainvoke (10 second timeout)...")
        result = await asyncio.wait_for(
            llm.ainvoke("Async test message"),
            timeout=10.0
        )
        print(f"✅ Async ainvoke succeeded")
        print(f"   Response: {str(result.content)[:100]}...")
        
    except asyncio.TimeoutError:
        print(f"❌ TIMEOUT on async ainvoke (>10 seconds)")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_async_invoke())

# ============================================================================
# Layer 4: Test NeMo Guardrails integration
# ============================================================================

print("\n[Layer 4] Testing NeMo Guardrails...")
print("-" * 70)

async def test_nemo():
    try:
        from nemoguardrails import LLMRails, RailsConfig
        
        print("Loading NeMo config...")
        config = RailsConfig.from_path('./config/rails')
        print(f"✅ Config loaded")
        
        print("Initializing LLMRails...")
        rails = LLMRails(config)
        print(f"✅ LLMRails initialized")
        
        print("Testing generate_async (15 second timeout)...")
        response = await asyncio.wait_for(
            rails.generate_async(
                messages=[{"role": "user", "content": "Simple test"}]
            ),
            timeout=15.0
        )
        print(f"✅ NeMo generate_async succeeded")
        print(f"   Response: {response}...")
        
    except asyncio.TimeoutError:
        print(f"❌ TIMEOUT on NeMo generate_async (>15 seconds)")
        print("\n   This is the ACTUAL ISSUE!")
        print("   The problem is in the NeMo + Gemini integration")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

asyncio.run(test_nemo())

# ============================================================================
# Summary
# ============================================================================

print("\n" + "=" * 70)
print("DEBUGGING SUMMARY")
print("=" * 70)
print("""
If Layer 1-3 work but Layer 4 times out:
→ Problem is in NeMo's LLMRails.generate_async()
→ Check: config/rails/config.yml for issues
→ Check: Colang flow syntax errors

If Layer 2-3 fail:
→ Problem is in langchain-google-genai integration
→ Check: pip show langchain-google-genai langchain-core
→ Try: Reinstall recent version

If Layer 1 fails:
→ API key is invalid or API is down
→ Check: Google Cloud credentials
→ Try: Test in https://aistudio.google.com

Next: Check the logs in /logs/nautilus-*.log
""")
