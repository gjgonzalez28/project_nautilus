#!/usr/bin/env python3
"""
Direct test of Discovery flow without Flask.
This isolates whether the issue is Flask, NeMo, or the Gemini API.
"""

import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from nemoguardrails import LLMRails, RailsConfig

async def test_discovery():
    """Test the discovery flow directly."""
    try:
        print("Loading NeMo configuration...")
        config = RailsConfig.from_path('./config/rails')
        
        print("Initializing LLMRails...")
        rails = LLMRails(config)
        print("✅ NeMo loaded successfully")
        
        # Test message
        test_message = "I have a Medieval Madness and I'm a beginner"
        print(f"\nTesting with message: '{test_message}'")
        
        # Generate response with timeout
        print("Sending to NeMo (with 10 second timeout)...")
        try:
            response = await asyncio.wait_for(
                rails.generate_async(
                    messages=[{"role": "user", "content": test_message}]
                ),
                timeout=10.0
            )
            print(f"\n✅ Response received:")
            print(f"Type: {type(response)}")
            if isinstance(response, dict):
                print(f"Content: {response.get('content', 'NO CONTENT')}")
            else:
                print(f"Response: {response}")
        except asyncio.TimeoutError:
            print("❌ TIMEOUT: LLM call took longer than 10 seconds")
            print("   This suggests the Gemini API is slow or hanging")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_discovery())
