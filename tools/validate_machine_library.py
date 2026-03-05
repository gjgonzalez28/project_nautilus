#!/usr/bin/env python
"""
Project Nautilus: Machine Library Validator

Validates machine_library.json structure and data quality.

Usage:
    python tools/validate_machine_library.py
    python tools/validate_machine_library.py --verbose
"""

import sys
import json
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def validate_machine_library():
    """Validate machine library structure and content"""
    library_file = PROJECT_ROOT / "data" / "machine_library.json"
    
    if not library_file.exists():
        return False, ["machine_library.json not found"]
    
    try:
        with open(library_file, 'r', encoding='utf-8') as f:
            machines = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"JSON parse error: {str(e)}"]
    
    if not isinstance(machines, list):
        return False, ["Root element must be an array"]
    
    errors = []
    warnings = []
    
    required_fields = ['id', 'name', 'era', 'manufacturer']
    valid_eras = ['EM', 'Solid State Early', 'Solid State Mid', 'Solid State Modern', 'DMD', 'LCD']
    
    machine_ids = set()
    
    for i, machine in enumerate(machines):
        machine_context = f"Machine {i+1}"
        
        # Check required fields
        for field in required_fields:
            if field not in machine:
                errors.append(f"{machine_context}: Missing required field '{field}'")
        
        # Check for duplicate IDs
        if 'id' in machine:
            machine_id = machine['id']
            machine_context = f"Machine '{machine_id}'"
            
            if machine_id in machine_ids:
                errors.append(f"{machine_context}: Duplicate ID '{machine_id}'")
            machine_ids.add(machine_id)
        
        # Validate era
        if 'era' in machine and machine['era'] not in valid_eras:
            warnings.append(f"{machine_context}: Unknown era '{machine['era']}' (expected one of: {', '.join(valid_eras)})")
        
        # Validate symptoms array
        if 'symptoms' in machine:
            if not isinstance(machine['symptoms'], list):
                errors.append(f"{machine_context}: 'symptoms' must be an array")
            else:
                for j, symptom in enumerate(machine['symptoms']):
                    symptom_context = f"{machine_context}, Symptom {j+1}"
                    
                    if not isinstance(symptom, dict):
                        errors.append(f"{symptom_context}: Must be an object")
                        continue
                    
                    # Check symptom fields
                    if 'symptom' not in symptom:
                        errors.append(f"{symptom_context}: Missing 'symptom' field")
                    
                    if 'diagnosis' not in symptom:
                        warnings.append(f"{symptom_context}: Missing 'diagnosis' field")
                    
                    # Check diagnosis contains STF keywords
                    if 'diagnosis' in symptom:
                        diag = symptom['diagnosis'].upper()
                        has_straight = 'STRAIGHT:' in diag
                        has_true = 'TRUE:' in diag
                        has_flush = 'FLUSH:' in diag
                        
                        if not (has_straight and has_true and has_flush):
                            warnings.append(f"{symptom_context}: Diagnosis should contain STRAIGHT/TRUE/FLUSH sections")
        else:
            warnings.append(f"{machine_context}: No 'symptoms' array defined")
    
    return len(errors) == 0, errors, warnings, len(machines), len(machine_ids)


def main():
    """Run machine library validation"""
    verbose = '--verbose' in sys.argv
    
    print("=" * 70)
    print("PROJECT NAUTILUS: MACHINE LIBRARY VALIDATOR")
    print("=" * 70)
    
    success, *details = validate_machine_library()
    
    if not success:
        errors = details[0]
        print("\n✗ VALIDATION FAILED")
        for error in errors:
            print(f"  - {error}")
        print("=" * 70)
        return 1
    
    errors, warnings, machine_count, unique_ids = details
    
    print(f"\n[INFO] Found {machine_count} machines with {unique_ids} unique IDs")
    
    if errors:
        print("\n✗ CRITICAL ERRORS:")
        for error in errors:
            print(f"  - {error}")
    
    if warnings:
        print(f"\n⚠ WARNINGS ({len(warnings)} total):")
        if verbose:
            for warning in warnings:
                print(f"  - {warning}")
        else:
            for warning in warnings[:5]:
                print(f"  - {warning}")
            if len(warnings) > 5:
                print(f"  ... and {len(warnings) - 5} more (use --verbose to see all)")
    
    print("\n" + "=" * 70)
    if not errors:
        if warnings:
            print("✓ STRUCTURE VALID (with warnings)")
        else:
            print("✓ ALL VALIDATIONS PASSED")
        print("=" * 70)
        return 0
    else:
        print(f"✗ {len(errors)} CRITICAL ERRORS FOUND")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
