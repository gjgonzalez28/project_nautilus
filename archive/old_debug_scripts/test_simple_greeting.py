#!/usr/bin/env python3
"""
Direct test of NeMo with a simple greeting to check if Gemini API works at all.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from nemoguardrails import LLMRails, RailsConfig

async def test_simple_greeting():
    """Test with a very simple greeting first."""
    try:
        print("Loading NeMo configuration...")
        config = RailsConfig.from_path('./config/rails')
        
        print("Initializing LLMRails...")
        rails = LLMRails(config)
        print("✅ NeMo loaded successfully")
        
        # Test with simple message first
        test_message = "Hello"
        print(f"\nTesting with simple message: '{test_message}'")
        
        # Generate response with timeout
        print("Sending to NeMo (with 15 second timeout)...")
        try:
            response = await asyncio.wait_for(
                rails.generate_async(
                    messages=[{"role": "user", "content": test_message}]
                ),
                timeout=15.0
            )
            print(f"\n✅ Response received!")
            print(f"Type: {type(response)}")
            if isinstance(response, dict):
                print(f"Content: {response.get('content', 'NO CONTENT')}")
            else:
                print(f"Response: {response}")
        except asyncio.TimeoutError:
            print("❌ TIMEOUT: LLM call took longer than 15 seconds")
            print("   Gemini API might be slow, unreachable, or API key issues")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_greeting())
