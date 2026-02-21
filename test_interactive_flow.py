#!/usr/bin/env python3
"""
Test the complete Project Nautilus interactive flow:
1. Identity discovery (machine + skill selection)
2. Symptom description
3. Evidence gathering
4. Confidence gates and output decision
"""

from logic.manager import NautilusManager
from logic.discovery_script import DiscoveryScript

def test_full_flow():
    print("\n" + "="*60)
    print("   NAUTILUS INTERACTIVE FLOW TEST")
    print("="*60)
    
    manager = NautilusManager()
    discovery = DiscoveryScript(manager)
    
    # Test Scenario 1: Discovery Phase - Machine identification
    print("\n--- PHASE 1: MACHINE DISCOVERY ---")
    user_input = "I'm working on a Williams Addams Family pinball machine"
    print(f"USER: {user_input}")
    response = discovery.process_initial_response(user_input)
    print(f"NAUTILUS: {response}\n")
    
    # Test Scenario 1b: Skill level
    user_input = "I'm intermediate skill level"
    print(f"USER: {user_input}")
    response = discovery.process_initial_response(user_input)
    print(f"NAUTILUS: {response}\n")
    
    # Check session is locked
    print(f"[SESSION LOCKED: {not discovery.awaiting_discovery}]")
    print(f"[STATE] Machine: {manager.session.machine_title}")
    print(f"[STATE] Mode: {manager.session.mode}\n")
    
    # Test Scenario 2: Symptom Description (no fix recommendation yet)
    print("--- PHASE 2: SYMPTOM DESCRIPTION ---")
    user_input = "Left flipper is not working. What do I check?"
    print(f"USER: {user_input}")
    response = manager.ask(user_input)
    print(f"NAUTILUS: {response}\n")
    print(f"[STATE] Current symptom: {manager.session.current_symptom}")
    print(f"[STATE] Evidence count: {len(manager.session.evidence_collected)}\n")
    
    # Test Scenario 3: Evidence Gathering (observed evidence)
    print("--- PHASE 3A: EVIDENCE - OBSERVED ---")
    user_input = "I measured the voltage at the solenoid and confirmed it shows 0V"
    print(f"USER: {user_input}")
    response = manager.ask(user_input)
    print(f"NAUTILUS: {response}\n")
    print(f"[STATE] Evidence count: {len(manager.session.evidence_collected)}")
    for i, evidence in enumerate(manager.session.evidence_collected, 1):
        print(f"  [{i}] Type: {evidence['type']}, Text: {evidence['text'][:50]}...\n")
    
    # Test Scenario 4: More Evidence (manual/documentation)
    print("--- PHASE 3B: EVIDENCE - MANUAL/DOCUMENTATION ---")
    user_input = "Per the manual, the solenoid should show 50V when powered"
    print(f"USER: {user_input}")
    response = manager.ask(user_input)
    print(f"NAUTILUS: {response}\n")
    print(f"[STATE] Evidence count: {len(manager.session.evidence_collected)}\n")
    
    # Test Scenario 5: Ask for fix recommendation (triggers gates)
    print("--- PHASE 4: REQUESTING FIX RECOMMENDATION (GATES) ---")
    user_input = "So should I replace the solenoid? How do I fix this?"
    print(f"USER: {user_input}")
    response = manager.ask(user_input)
    print(f"NAUTILUS: {response}\n")
    print(f"[STATE] Confidence score: {manager.session.symptom_confidence:.1f}%")
    print(f"[STATE] Evidence summary: {manager.session.get_evidence_summary()}\n")
    
    # Test Scenario 6: Unknown symptom fallback
    print("--- PHASE 5: UNKNOWN SYMPTOM HANDLING ---")
    user_input = "What about the frammistan oscillator?"
    print(f"USER: {user_input}")
    response = manager.ask(user_input)
    print(f"NAUTILUS: {response}\n")
    
    print("="*60)
    print("   FLOW TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    test_full_flow()
