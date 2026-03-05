#!/usr/bin/env python
"""
Project Nautilus: Diagnostic Maps Validator

Validates diagnostic_maps.yaml structure and STF completeness.

Usage:
    python tools/validate_diagnostic_maps.py
    python tools/validate_diagnostic_maps.py --verbose
"""

import sys
import yaml
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def validate_diagnostic_maps():
    """Validate diagnostic maps structure and content"""
    maps_file = PROJECT_ROOT / "data" / "diagnostic_maps.yaml"
    
    if not maps_file.exists():
        return False, ["diagnostic_maps.yaml not found"]
    
    try:
        with open(maps_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return False, [f"YAML parse error: {str(e)}"]
    
    if not isinstance(data, dict):
        return False, ["Root element must be a dictionary"]
    
    if 'symptom_maps' not in data:
        return False, ["Missing 'symptom_maps' key"]
    
    symptom_maps = data['symptom_maps']
    if not isinstance(symptom_maps, dict):
        return False, ["'symptom_maps' must be a dictionary"]
    
    errors = []
    warnings = []
    
    symptom_count = len(symptom_maps)
    complete_stf_count = 0
    
    for symptom_key, symptom_data in symptom_maps.items():
        context = f"Symptom '{symptom_key}'"
        
        # Check required fields
        if not isinstance(symptom_data, dict):
            errors.append(f"{context}: Must be a dictionary")
            continue
        
        if 'title' not in symptom_data:
            warnings.append(f"{context}: Missing 'title' field")
        
        if 'stf' not in symptom_data:
            errors.append(f"{context}: Missing 'stf' (STRAIGHT/TRUE/FLUSH) structure")
            continue
        
        stf = symptom_data['stf']
        if not isinstance(stf, dict):
            errors.append(f"{context}: 'stf' must be a dictionary")
            continue
        
        # Validate STF sections
        has_straight = 'straight' in stf
        has_true = 'true' in stf
        has_flush = 'flush' in stf
        
        if not has_straight:
            errors.append(f"{context}: Missing 'straight' section in STF")
        if not has_true:
            errors.append(f"{context}: Missing 'true' section in STF")
        if not has_flush:
            errors.append(f"{context}: Missing 'flush' section in STF")
        
        if has_straight and has_true and has_flush:
            complete_stf_count += 1
        
        # Validate each STF section has 'checks' array
        for section_name in ['straight', 'true', 'flush']:
            if section_name in stf:
                section = stf[section_name]
                if not isinstance(section, dict):
                    errors.append(f"{context}: '{section_name}' section must be a dictionary")
                    continue
                
                if 'checks' not in section:
                    warnings.append(f"{context}: '{section_name}' section missing 'checks' array")
                    continue
                
                checks = section['checks']
                if not isinstance(checks, list):
                    errors.append(f"{context}: '{section_name}.checks' must be an array")
                    continue
                
                # Validate check items
                for i, check in enumerate(checks):
                    check_context = f"{context}, {section_name.upper()} check {i+1}"
                    
                    if not isinstance(check, dict):
                        errors.append(f"{check_context}: Must be a dictionary")
                        continue
                    
                    if 'id' not in check:
                        warnings.append(f"{check_context}: Missing 'id' field")
                    if 'area' not in check:
                        warnings.append(f"{check_context}: Missing 'area' field")
                    if 'action' not in check:
                        warnings.append(f"{check_context}: Missing 'action' field")
        
        # Check for branches (optional but good to have)
        if 'branches' in symptom_data:
            if not isinstance(symptom_data['branches'], list):
                warnings.append(f"{context}: 'branches' should be an array")
    
    return True, errors, warnings, symptom_count, complete_stf_count


def main():
    """Run diagnostic maps validation"""
    verbose = '--verbose' in sys.argv
    
    print("=" * 70)
    print("PROJECT NAUTILUS: DIAGNOSTIC MAPS VALIDATOR")
    print("=" * 70)
    
    success, *details = validate_diagnostic_maps()
    
    if not success:
        errors = details[0]
        print("\n✗ VALIDATION FAILED")
        for error in errors:
            print(f"  - {error}")
        print("=" * 70)
        return 1
    
    errors, warnings, symptom_count, complete_stf_count = details
    
    print(f"\n[INFO] Found {symptom_count} symptom maps")
    print(f"[INFO] {complete_stf_count}/{symptom_count} have complete STF structure")
    
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
