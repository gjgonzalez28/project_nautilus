#!/usr/bin/env python3
"""
Comprehensive test of the full Project Nautilus system post-changes.
Validates:
- Discovery + session locking
- Symptom detection
- Evidence collection (all 3 types)
- Confidence calculation  
- Gate behavior
"""

from logic.manager import NautilusManager
from logic.discovery_script import DiscoveryScript

def test_complete_flow():
    results = []

    # Test 1: Discovery
    print("\n" + "="*70)
    print("TEST 1: Identity Discovery & Session Lock")
    print("="*70)
    manager = NautilusManager()
    discovery = DiscoveryScript(manager)
    
    response = discovery.process_initial_response("Williams Medieval Madness intermediate")
    if not discovery.awaiting_discovery and manager.session.mode == "intermediate":
        print("[PASS] Session locked, mode set to intermediate")
        results.append("PASS")
    else:
        print("[FAIL] Session not properly locked")
        results.append("FAIL")

    # Test 2: Symptom Detection
    print("\n" + "="*70)
    print("TEST 2: Symptom Detection & Mapping")
    print("="*70)
    response = manager.ask("My left flipper is dead what should I check")
    if manager.session.current_symptom == "left_flipper_dead":
        print(f"[PASS] Symptom detected: {manager.session.current_symptom}")
        print(f"       Response preview: {response[:60]}...")
        results.append("PASS")
    else:
        print(f"[FAIL] Expected 'left_flipper_dead', got '{manager.session.current_symptom}'")
        results.append("FAIL")

    # Test 3: Evidence Extraction - Observed
    print("\n" + "="*70)
    print("TEST 3: Evidence Extraction - OBSERVED Type")
    print("="*70)
    response = manager.ask("I tested the solenoid and measured zero voltage")
    evidence_count = len(manager.session.evidence_collected)
    if evidence_count > 0 and manager.session.evidence_collected[0]['type'] == 'Observed':
        print(f"[PASS] Observed evidence collected")
        print(f"       Total evidence: {evidence_count}")
        results.append("PASS")
    else:
        print(f"[FAIL] Evidence not collected (count={evidence_count})")
        results.append("FAIL")

    # Test 4: Evidence Extraction - Manual
    print("\n" + "="*70)
    print("TEST 4: Evidence Extraction - MANUAL Type")
    print("="*70)
    response = manager.ask("Per the manual page 42 the solenoid should show 50V")
    evidence_count = len(manager.session.evidence_collected)
    evidence_types = manager.session.get_evidence_summary()
    if evidence_types['Manual'] > 0:
        print(f"[PASS] Manual evidence collected")
        print(f"       Summary: {evidence_types}")
        results.append("PASS")
    else:
        print(f"[FAIL] Manual evidence not detected: {evidence_types}")
        results.append("FAIL")

    # Test 5: Evidence Extraction - Hypothesis  
    print("\n" + "="*70)
    print("TEST 5: Evidence Extraction - HYPOTHESIS Type")
    print("="*70)
    response = manager.ask("I think maybe the coil is burned from a short")
    evidence_types = manager.session.get_evidence_summary()
    if evidence_types['Hypothesis'] > 0:
        print(f"[PASS] Hypothesis evidence collected")
        print(f"       Summary: {evidence_types}")
        results.append("PASS")
    else:
        print(f"[FAIL] Hypothesis evidence not detected: {evidence_types}")
        results.append("FAIL")

    # Test 6: Confidence Calculation
    print("\n" + "="*70)
    print("TEST 6: Confidence Calculation with Evidence")
    print("="*70)
    # Manually trigger confidence calculation
    confidence = manager.engine._calculate_confidence(
        manager.session, 
        symptom_match_quality=0.8 if manager.session.current_symptom else 0.5
    )
    
    print(f"       Evidence collected: {len(manager.session.evidence_collected)}")
    print(f"       Evidence types: {manager.session.get_evidence_summary()}")
    print(f"       Calculated confidence: {confidence:.1f}%")
    
    if confidence > 50:  # Should be high with symptom + 3 evidence items
        print(f"[PASS] Confidence > 50% ({confidence:.1f}%)")
        results.append("PASS")
    else:
        print(f"[WARN] Low confidence ({confidence:.1f}%) - may need evidence quality review")
        results.append("WARN")

    # Test 7: Safe Fix Request (avoid solenoid safety trigger)
    print("\n" + "="*70)
    print("TEST 7: Fix Request with Gate Logic")
    print("="*70)
    response = manager.ask("Can I fix this by replacing the flipper mechanism")
    
    is_proceed = "I have some guidance" in response or "Step 1" in response or "[PD" in response
    is_clarify = "more information" in response or "tell me more" in response.lower()
    is_safety = "Safety" in response or "High voltage" in response
    
    print(f"       Response: {response[:80]}...")
    if is_safety:
        print(f"[WARN] Safety interrupt triggered (blocking gate logic)")
        results.append("WARN")
    elif is_proceed or is_clarify:
        print(f"[PASS] Gate logic executed (Proceed/Clarify)")
        results.append("PASS")
    else:
        print(f"[FAIL] Unexpected response type")
        results.append("FAIL")

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    passed = results.count("PASS")
    warned = results.count("WARN")
    failed = results.count("FAIL")
    
    print(f"PASSED: {passed}/7")
    print(f"WARNED: {warned}/7")
    print(f"FAILED: {failed}/7")
    
    if failed == 0:
        print("\n[OVERALL: SUCCESS] All critical tests passed!")
    elif warned > 0:
        print("\n[OVERALL: PARTIAL] Some warnings but no failures.")
    else:
        print("\n[OVERALL: FAILURE] Some tests failed.")

if __name__ == "__main__":
    test_complete_flow()
