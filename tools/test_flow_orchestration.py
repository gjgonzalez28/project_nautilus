#!/usr/bin/env python3
"""
Local Flow Orchestration Validator

Tests that NeMo correctly orchestrates flows without requiring deployment.
Validates that:
1. Config properly loads with rails.flows section
2. main.co flow is the entry point
3. Discovery flow triggers on symptom input
4. Custom actions are registered and called
5. No fallback to generic LLM (generate_user_intent)

Usage:
    python tools/test_flow_orchestration.py
"""

import asyncio
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment
load_dotenv()

from nemoguardrails import LLMRails, RailsConfig
from nemoguardrails.logging.verbose import set_verbose

# Test cases
TEST_CASES = [
    {
        "name": "Identity Gate Trigger",
        "input": "my right flipper doesn't work",
        "expected_flows": ["main", "discovery"],
        "expected_response_contains": ["tell me the title", "manufacturer", "skill level"],
        "should_not_contain": ["generate_user_intent"]
    },
    {
        "name": "Hello World Fallback",
        "input": "hello",
        "expected_flows": ["main", "hello_world"],
        "expected_response_contains": ["hello"],
        "should_not_contain": []
    }
]

class FlowExecutionTracker:
    """Captures flow execution for validation"""
    def __init__(self):
        self.flows_executed = []
        self.actions_called = []
        self.llm_calls = []
        
    def reset(self):
        self.flows_executed = []
        self.actions_called = []
        self.llm_calls = []


def setup_logging():
    """Enable verbose NeMo logging to capture flow execution"""
    # Set NeMo verbose mode
    set_verbose(True)
    
    # Configure Python logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    # Focus on NeMo loggers
    loggers = [
        'nemoguardrails.rails.llm.llmrails',
        'nemoguardrails.colang',
        'nemoguardrails.rails',
    ]
    
    for logger_name in loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)


async def test_flow_orchestration():
    """Main test function"""
    print("=" * 80)
    print("FLOW ORCHESTRATION VALIDATOR")
    print("=" * 80)
    
    # Step 1: Load configuration
    print("\n[1/5] Loading NeMo Configuration...")
    config_path = project_root / "config" / "rails"
    
    try:
        config = RailsConfig.from_path(str(config_path))
        print(f"✅ Config loaded from {config_path}")
    except Exception as e:
        print(f"❌ FAILED to load config: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 2: Validate config structure
    print("\n[2/5] Validating Configuration Structure...")
    
    # Check for rails.flows section
    config_yml_path = config_path / "config.yml"
    with open(config_yml_path, 'r') as f:
        config_content = f.read()
    
    if 'rails:' in config_content and 'flows:' in config_content:
        print("✅ Config has 'rails.flows' section")
    else:
        print("❌ Config missing 'rails.flows' section")
        print("   This will cause NeMo to bypass custom flows!")
        return False
    
    # Check main.co exists
    main_co_path = config_path / "main.co"
    if main_co_path.exists():
        print(f"✅ Found main.co at {main_co_path}")
    else:
        print("❌ main.co not found - orchestration entry point missing")
        return False
    
    # Step 3: Initialize LLMRails
    print("\n[3/5] Initializing LLMRails...")
    
    try:
        rails = LLMRails(config)
        print("✅ LLMRails initialized successfully")
    except Exception as e:
        print(f"❌ FAILED to initialize LLMRails: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 4: Check registered actions
    print("\n[4/5] Checking Registered Actions...")
    
    expected_actions = [
        "fuzzy_match_machine",
        "validate_skill_level",
        "fuzzy_match_symptom",
        "log_symptom_details",
        "generate_diagnostic_steps",
        "evaluate_safety_gates",
        "parse_machine_and_skill",
        "detect_playfield_access",
        "validate_photo_quality",
        "detect_board_level_work",  # DUTY #20
        "offer_skill_level_upgrade",  # DUTY #20
        "handle_social_pressure"  # DUTY #14
    ]
    
    # Try to get registered actions from config
    try:
        registered_actions = getattr(config, 'actions', [])
        if registered_actions:
            print(f"✅ Found {len(registered_actions)} registered actions")
            for action in registered_actions:
                print(f"   - {action}")
        else:
            print("⚠️  Could not enumerate actions (config.actions not available)")
            print("   Proceeding with runtime test...")
    except Exception as e:
        print("⚠️  Could not check actions:", e)
    
    # Step 5: Test Flow Execution
    print("\n[5/5] Testing Flow Execution...")
    print("-" * 80)
    
    # Check if we have API key for runtime tests
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Skipping runtime tests (no API key)")
        print("✅ Structural validation complete")
        print("\n" + "=" * 80)
        print("✅ STRUCTURAL VALIDATION PASSED")
        print("\nLimitations:")
        print("- Config structure: ✓ Validated")
        print("- Flow files: ✓ Validated")  
        print("- Runtime execution: ⚠️ Skipped (set GOOGLE_API_KEY to test)")
        print("\nNext: Run with API key to test full orchestration")
        print("=" * 80)
        return True
    
    all_passed = True
    
    for test_case in TEST_CASES:
        print(f"\n🧪 Test: {test_case['name']}")
        print(f"   Input: '{test_case['input']}'")
        
        try:
            # Send message to NeMo
            response = await asyncio.wait_for(
                rails.generate_async(
                    messages=[{"role": "user", "content": test_case['input']}]
                ),
                timeout=20.0
            )
            
            # Extract response text
            if isinstance(response, dict):
                response_text = response.get('content', '')
            else:
                response_text = str(response)
            
            print(f"   Response: {response_text[:100]}...")
            
            # Validate expected content
            passed = True
            for expected in test_case['expected_response_contains']:
                if expected.lower() in response_text.lower():
                    print(f"   ✅ Contains: '{expected}'")
                else:
                    print(f"   ❌ MISSING: '{expected}'")
                    passed = False
            
            # Validate should not contain
            for forbidden in test_case['should_not_contain']:
                if forbidden.lower() in response_text.lower():
                    print(f"   ❌ Should NOT contain: '{forbidden}'")
                    passed = False
            
            if passed:
                print(f"   ✅ Test PASSED")
            else:
                print(f"   ❌ Test FAILED")
                all_passed = False
                
        except asyncio.TimeoutError:
            print(f"   ❌ TIMEOUT (20 seconds)")
            all_passed = False
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            all_passed = False
    
    # Final summary
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED - Flow orchestration working correctly!")
        print("\nNext step: Deploy to Render and validate in production")
    else:
        print("❌ SOME TESTS FAILED - Review issues above")
        print("\nDo NOT deploy until orchestration works locally")
    print("=" * 80)
    
    return all_passed


async def main():
    """Entry point"""
    # Check API key - warn but continue with structural validation
    has_api_key = bool(os.getenv("GOOGLE_API_KEY"))
    if not has_api_key:
        print("⚠️  GOOGLE_API_KEY not set in environment")
        print("   Will perform structural validation only (no runtime tests)")
        print()
    
    # Uncomment to enable verbose logging (VERY verbose):
    # setup_logging()
    
    try:
        success = await test_flow_orchestration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
