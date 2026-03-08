"""Test Discovery Flow End-to-End"""
import os
import asyncio
from dotenv import load_dotenv
from nemoguardrails import RailsConfig, LLMRails

# Load environment variables
load_dotenv()

# Verify API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("ERROR: OPENAI_API_KEY not found in environment")
    exit(1)

print(f"✓ API Key loaded: {api_key[:20]}...")

# Load NeMo config
config = RailsConfig.from_path("./config")
print("✓ NeMo config loaded")

# Create rails instance
rails = LLMRails(config)
print("✓ LLM Rails instance created\n")

print("="*60)
print("DISCOVERY FLOW TEST - Simulating User Conversation")
print("="*60)

# Test conversation
async def test_discovery():
    """Simulate discovery flow trigger"""
    
    # User initiates - this should trigger the discovery flow
    print("\nUSER: I need help fixing my pinball machine\n")
    response1 = await rails.generate_async(
        messages=[{"role": "user", "content": "I need help fixing my pinball machine"}]
    )
    print(f"BOT: {response1['content']}\n")
    
    print("="*60)
    print("If you see the discovery greeting above, the flow is working!")
    print("="*60)

# Run test
try:
    asyncio.run(test_discovery())
    print("\n✓ TEST PASSED: Discovery flow executed successfully")
except Exception as e:
    print(f"\n✗ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
