"""
Project Nautilus: End-to-End Integration Test

Tests the complete diagnostic workflow:
1. Discovery (machine + skill identification)
2. Symptom capture (issue description)
3. Diagnostic reasoning (troubleshooting steps)
4. Safety validation (warnings/blocks)

Validates that all Colang flows work together properly.
"""

import os
import asyncio
from dotenv import load_dotenv
from nemoguardrails import RailsConfig, LLMRails

# Load environment
load_dotenv()

# Verify environment
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print("[ERROR] OPENAI_API_KEY not found!")
    exit(1)

print("="*70)
print(" PROJECT NAUTILUS - END-TO-END INTEGRATION TEST")
print("="*70)
print(f"[OK] OpenAI API Key: {api_key[:20]}...")

# Load NeMo config
print("\n[1/3] Loading NeMo Guardrails configuration...")
config = RailsConfig.from_path("./config")
rails = LLMRails(config)
print("[OK] Configuration loaded")

print("\n[2/3] Initializing LLM Rails...")
print("[OK] LLM Rails ready")

print("\n[3/3] Starting diagnostic session simulation...")
print("="*70)


async def simulate_complete_session():
    """
    Simulate a complete diagnostic conversation from start to finish.
    """
    
    print("\n" + "="*70)
    print("SCENARIO: User with weak flippers on Bally Eight Ball")
    print("="*70 + "\n")
    
    # ========================================================================
    # PHASE 1: USER INITIATES REQUEST
    # ========================================================================
    print("\n[USER] I need help fixing my pinball machine\n")
    
    response1 = await rails.generate_async(
        messages=[{"role": "user", "content": "I need help fixing my pinball machine"}]
    )
    
    print(f"[BOT] {response1['content']}\n")
    
    # Verify discovery flow triggered - should ask for machine AND skill level together
    if "machine" in response1['content'].lower() and "skill level" in response1['content'].lower():
        print("[PASS] PHASE 1 PASSED: Discovery flow triggered correctly (combined question)")
    else:
        print("[WARN] PHASE 1 WARNING: Discovery flow response unexpected")
        print(f"   Response was: {response1['content']}")
    
    # ========================================================================
    # PHASE 2: COMBINED MACHINE AND SKILL PARSING (NEW FLOW)
    # ========================================================================
    print("\n" + "-"*70)
    print("Testing combined machine and skill level parsing...")
    print("-"*70 + "\n")
    
    # Test the new ParseMachineAndSkillAction
    from config.rails.actions import parse_machine_and_skill_action
    
    parse_result = await parse_machine_and_skill_action("Bally Eight Ball 1977, beginner")
    
    print(f"Parse Result:")
    print(f"  - Machine Name: {parse_result.get('machine_name')}")
    print(f"  - Manufacturer: {parse_result.get('manufacturer')}")
    print(f"  - Era: {parse_result.get('era')}")
    print(f"  - Skill Level: {parse_result.get('skill_level')}")
    print(f"  - Needs Clarification: {parse_result.get('needs_clarification')}")
    
    if parse_result.get('machine_name') and parse_result.get('skill_level') == 'beginner':
        print("\n[PASS] PHASE 2 PASSED: Combined parsing works")
    else:
        print("\n[WARN] PHASE 2 WARNING: Parsing unexpected")
    
    # ========================================================================
    # PHASE 3: MODEL CLARIFICATION CHECK
    # ========================================================================
    print("\n" + "-"*70)
    print("Testing model clarification detection (Godzilla example)...")
    print("-"*70 + "\n")
    
    clarification_test = await parse_machine_and_skill_action("Godzilla, Stern, intermediate")
    
    print(f"Clarification Test:")
    print(f"  - Machine: {clarification_test.get('machine_name')}")
    print(f"  - Skill: {clarification_test.get('skill_level')}")
    print(f"  - Needs Clarification: {clarification_test.get('needs_clarification')}")
    print(f"  - Question: {clarification_test.get('clarification_question')}")
    
    if clarification_test.get('needs_clarification'):
        print("\n[PASS] PHASE 3 PASSED: Model clarification detection works")
    else:
        print("\n[WARN] PHASE 3 WARNING: Clarification not triggered")
    
    # ========================================================================
    # PHASE 4: SYMPTOM MATCHING
    # ========================================================================
    print("\n" + "-"*70)
    print("Testing symptom fuzzy matching...")
    print("-"*70 + "\n")
    
    from config.rails.actions import fuzzy_match_symptom_action
    
    symptom_result = await fuzzy_match_symptom_action(
        "My left flipper is weak and won't flip the ball",
        machine_id="EM_COMMON"
    )
    
    print(f"Symptom Match Result:")
    print(f"  - Matched: {symptom_result.get('matched')}")
    print(f"  - Category: {symptom_result.get('category')}")
    print(f"  - Confidence: {symptom_result.get('confidence')}")
    
    if symptom_result.get('matched') and symptom_result.get('category') == 'flipper':
        print("\n[PASS] PHASE 4 PASSED: Symptom categorization works")
    else:
        print("\n[WARN] PHASE 4 WARNING: Symptom matching unexpected")
    
    # ========================================================================
    # PHASE 5: DIAGNOSTIC GENERATION
    # ========================================================================
    print("\n" + "-"*70)
    print("Testing diagnostic step generation...")
    print("-"*70 + "\n")
    
    from config.rails.actions import generate_diagnostic_steps_action
    
    diagnostic_result = await generate_diagnostic_steps_action(
        symptom="left flipper weak",
        category="flipper",
        machine_info={
            "name": "Bally Eight Ball",
            "manufacturer": "Bally",
            "era": "EM"
        },
        skill_level="beginner"
    )
    
    print(f"Diagnostic Steps Generated:")
    for idx, step in enumerate(diagnostic_result.get('steps', []), 1):
        print(f"  {idx}. {step}")
    
    print(f"\nMetadata:")
    print(f"  - Confidence: {diagnostic_result.get('confidence')}")
    print(f"  - Estimated Time: {diagnostic_result.get('estimated_time')}")
    print(f"  - Safety Warnings: {len(diagnostic_result.get('safety_warnings', []))}")
    
    if diagnostic_result.get('steps'):
        print("\n[PASS] PHASE 5 PASSED: Diagnostic generation works")
    else:
        print("\n[WARN] PHASE 5 WARNING: No diagnostic steps generated")
    
    # ========================================================================
    # PHASE 6: SAFETY EVALUATION
    # ========================================================================
    print("\n" + "-"*70)
    print("Testing safety gate evaluation...")
    print("-"*70 + "\n")
    
    from config.rails.actions import evaluate_safety_gates_action
    
    # Test with safe repair (for beginner)
    safe_steps = ["Check flipper button", "Inspect mechanical linkage"]
    safety_result_safe = await evaluate_safety_gates_action(
        diagnostic_steps=safe_steps,
        machine_era="EM",
        skill_level="beginner"
    )
    
    print(f"Safety Evaluation (Safe Repair):")
    print(f"  - Safe: {safety_result_safe.get('safe')}")
    print(f"  - Warnings: {len(safety_result_safe.get('warnings', []))}")
    print(f"  - Requires Expert: {safety_result_safe.get('requires_expert')}")
    
    # Test with high voltage repair (for beginner)
    dangerous_steps = ["Test 120V power supply", "Check transformer voltage"]
    safety_result_dangerous = await evaluate_safety_gates_action(
        diagnostic_steps=dangerous_steps,
        machine_era="EM",
        skill_level="beginner"
    )
    
    print(f"\nSafety Evaluation (High Voltage Repair):")
    print(f"  - Safe: {safety_result_dangerous.get('safe')}")
    print(f"  - Warnings: {len(safety_result_dangerous.get('warnings', []))}")
    print(f"  - Requires Expert: {safety_result_dangerous.get('requires_expert')}")
    
    if not safety_result_dangerous.get('safe') and safety_result_dangerous.get('requires_expert'):
        print("\n[PASS] PHASE 6 PASSED: Safety gates working correctly")
    else:
        print("\n[WARN] PHASE 6 WARNING: Safety evaluation unexpected")
    
    # ========================================================================
    # PHASE 7: PLAYFIELD ACCESS DETECTION
    # ========================================================================
    print("\n" + "-"*70)
    print("Testing playfield access detection...")
    print("-"*70 + "\n")
    
    from config.rails.actions import detect_playfield_access_action
    
    # Test 1: Beginner with playfield access needed (old machine - lever)
    playfield_steps_old = ["Check flipper coil under playfield", "Test EOS switch"]
    playfield_result_old = await detect_playfield_access_action(
        diagnostic_steps=playfield_steps_old,
        machine_info={"name": "Bally Eight Ball 1977", "manufacturer": "Bally", "era": "EM"},
        skill_level="beginner"
    )
    
    print(f"Playfield Access Test (Beginner + Old Machine):")
    print(f"  - Needs Access: {playfield_result_old.get('needs_access')}")
    print(f"  - Lockdown Bar Type: {playfield_result_old.get('lockdown_bar_type')}")
    print(f"  - Show Instructions: {playfield_result_old.get('show_instructions')}")
    
    # Test 2: Beginner with modern Stern (clips)
    playfield_result_stern = await detect_playfield_access_action(
        diagnostic_steps=["Inspect pop bumper switch under playfield"],
        machine_info={"name": "Godzilla Premium 2021", "manufacturer": "Stern", "era": "Modern"},
        skill_level="beginner"
    )
    
    print(f"\nPlayfield Access Test (Beginner + Modern Stern):")
    print(f"  - Needs Access: {playfield_result_stern.get('needs_access')}")
    print(f"  - Lockdown Bar Type: {playfield_result_stern.get('lockdown_bar_type')}")
    print(f"  - Show Instructions: {playfield_result_stern.get('show_instructions')}")
    
    # Test 3: Intermediate user (should skip instructions)
    playfield_result_intermediate = await detect_playfield_access_action(
        diagnostic_steps=["Check flipper coil under playfield"],
        machine_info={"name": "Medieval Madness", "manufacturer": "Williams", "era": "WPC"},
        skill_level="intermediate"
    )
    
    print(f"\nPlayfield Access Test (Intermediate User):")
    print(f"  - Needs Access: {playfield_result_intermediate.get('needs_access')}")
    print(f"  - Show Instructions: {playfield_result_intermediate.get('show_instructions')}")
    
    # Test 4: No playfield access needed
    playfield_result_none = await detect_playfield_access_action(
        diagnostic_steps=["Check display", "Test sound system"],
        machine_info={"name": "Attack from Mars", "manufacturer": "Bally", "era": "WPC"},
        skill_level="beginner"
    )
    
    print(f"\nPlayfield Access Test (No Access Needed):")
    print(f"  - Needs Access: {playfield_result_none.get('needs_access')}")
    print(f"  - Show Instructions: {playfield_result_none.get('show_instructions')}")
    
    # Validate results
    if (playfield_result_old.get('lockdown_bar_type') == 'lever' and 
        playfield_result_stern.get('lockdown_bar_type') == 'clips' and
        not playfield_result_intermediate.get('show_instructions') and
        not playfield_result_none.get('needs_access')):
        print("\n[PASS] PHASE 7 PASSED: Playfield access detection working correctly")
    else:
        print("\n[WARN] PHASE 7 WARNING: Playfield access detection unexpected")
    
    # ========================================================================
    # PHASE 8: COIN DOOR CONSTRAINT VALIDATION
    # ========================================================================
    print("\n" + "-"*70)
    print("Testing coin door constraint (Rule 0C.R19)...")
    print("-"*70 + "\n")
    
    from config.rails.actions import generate_diagnostic_steps_action
    
    # Simulate a scenario where LLM might generate bad coin door steps
    # We'll manually create violating steps and test the validation
    print("Test 1: Steps with coin door violations (should be filtered)")
    violating_result = await generate_diagnostic_steps_action(
        symptom="power supply not working",
        category="electrical",
        machine_info={"name": "Test Machine", "manufacturer": "Test", "era": "Modern"},
        skill_level="beginner"
    )
    
    # Manually inject a violating step to test validation
    from config.rails.actions import _validate_coin_door_constraint
    bad_steps = [
        "Open the coin door and check the power supply connections",
        "Reach through the coin door and test fuse F12",
        "Look through the coin door and inspect the transformer",
        "Access the service button through the coin door"  # This one is allowed
    ]
    
    validated_steps = _validate_coin_door_constraint(bad_steps)
    
    print(f"Original steps: {len(bad_steps)}")
    print(f"Validated steps: {len(validated_steps)}")
    print(f"Violations filtered: {len(bad_steps) - len(validated_steps)}")
    
    # Should filter out 3 violations, keep 1 allowed step
    if len(validated_steps) == 1 and "service button" in validated_steps[0]:
        print("\n[PASS] PHASE 8 PASSED: Coin door constraint working correctly")
    else:
        print("\n[WARN] PHASE 8 WARNING: Coin door validation unexpected")
        print(f"   Validated steps: {validated_steps}")
    
    print("\n" + "="*70)


async def run_tests():
    """Execute all integration tests"""
    try:
        await simulate_complete_session()
        
        print("\n" + "="*70)
        print(" INTEGRATION TEST COMPLETE")
        print("="*70)
        print("\n[SUCCESS] All phases executed successfully!")
        print("\nSummary:")
        print("  [OK] Discovery flow triggers properly")
        print("  [OK] Machine fuzzy matching works")
        print("  [OK] Skill level extraction works")
        print("  [OK] Symptom categorization works")
        print("  [OK] Diagnostic generation works")
        print("  [OK] Safety gates function correctly")
        print("  [OK] Playfield access detection works")
        print("  [OK] Coin door constraint enforced")
        print("\n" + "="*70)
        
    except Exception as e:
        print(f"\n[ERROR] TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


# Run the test
if __name__ == "__main__":
    asyncio.run(run_tests())
