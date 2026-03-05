"""
Test script to verify Discovery flow logic executes correctly.
This bypasses the Gemini API hang and tests the core Discovery functionality.
"""

import asyncio
import json
from pathlib import Path
from logic.discovery_helper import fuzzy_match_machine, validate_skill_level

def test_python_actions():
    """Test the Python helper functions directly."""
    print("=" * 60)
    print("Testing Python Helper Functions")
    print("=" * 60)
    
    # Test 1: Fuzzy match machine
    print("\n[Test 1] Fuzzy Match Machine")
    print("-" * 40)
    
    test_inputs = [
        "I have a Medieval Madness",
        "Medieval Madness machine",
        "MM pinball",
        "Medieval",
        "I don't know what machine I have"
    ]
    
    for user_input in test_inputs:
        result = fuzzy_match_machine(user_input, threshold=0.6)
        print(f"Input: '{user_input}'")
        print(f"  → Matched: {result['matched']}")
        if result['matched']:
            print(f"    Machine: {result.get('machine_id', 'N/A')}")
            print(f"    Manufacturer: {result.get('manufacturer', 'N/A')}")
            print(f"    Era: {result.get('era', 'N/A')}")
            print(f"    Confidence: {result.get('confidence', 0):.2f}")
        else:
            print(f"    Error: {result.get('error', 'No match')}")
        print()
    
    # Test 2: Validate skill level
    print("\n[Test 2] Validate Skill Level")
    print("-" * 40)
    
    skill_inputs = [
        "I'm a beginner",
        "I'm new to this",
        "I have some experience",
        "I'm an expert",
        "I'm very advanced",
        "I don't know anything about pinball"
    ]
    
    for user_input in skill_inputs:
        result = validate_skill_level(user_input)
        print(f"Input: '{user_input}'")
        print(f"  → Valid: {result['valid']}")
        print(f"    Level: {result.get('skill_level', 'N/A')}")
        print(f"    Confidence: {result.get('confidence', 0):.2f}")
        print()
    
    print("=" * 60)
    print("✅ All Python helper functions executed successfully")
    print("=" * 60)

if __name__ == "__main__":
    test_python_actions()
