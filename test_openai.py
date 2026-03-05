"""Test OpenAI integration with NeMo Guardrails"""
import os
import asyncio
from dotenv import load_dotenv
from nemoguardrails import RailsConfig, LLMRails

# Load environment variables
load_dotenv()

# Verify API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
print(f"API Key loaded: {api_key[:20]}..." if api_key else "API Key NOT found!")

# Load NeMo config
config = RailsConfig.from_path("./config")
print("NeMo config loaded successfully")

# Create rails instance
rails = LLMRails(config)
print("LLM Rails instance created")

# Test query
async def test():
    result = await rails.generate_async(messages=[
        {"role": "user", "content": "Hello, my flippers are weak"}
    ])
    return result

# Run test
result = asyncio.run(test())
print("\n" + "="*60)
print("SUCCESS! OpenAI Response:")
print("="*60)
print(result["content"])
print("="*60)
