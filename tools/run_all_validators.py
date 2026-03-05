#!/usr/bin/env python
"""
Project Nautilus: Run All Validators

Runs all validation tools and provides a comprehensive baseline report.

Usage:
    python tools/run_all_validators.py [--verbose]
"""

import sys
import subprocess
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def run_validator(script_name, description, verbose=False):
    """Run a validator script and return results"""
    print(f"\n{'=' * 70}")
    print(f"RUNNING: {description}")
    print('=' * 70)
    
    script_path = PROJECT_ROOT / "tools" / script_name
    if not script_path.exists():
        print(f"✗ Validator not found: {script_name}")
        return False
    
    args = ["python", str(script_path)]
    if verbose:
        args.append("--verbose")
    
    try:
        result = subprocess.run(args, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"✗ Error running {script_name}: {str(e)}")
        return False


def main():
    """Run all validators"""
    verbose = '--verbose' in sys.argv
    
    print("=" * 70)
    print("PROJECT NAUTILUS: COMPREHENSIVE VALIDATION SUITE")
    print("=" * 70)
    print("\nRunning all baseline validators...\n")
    
    validators = [
        ("validate_all.py", "YAML/JSON/Python/Files Validator"),
        ("validate_colang_flows.py", "Colang Flows Validator"),
        ("validate_config.py", "NeMo Config Validator"),
        ("validate_machine_library.py", "Machine Library Validator"),
        ("validate_diagnostic_maps.py", "Diagnostic Maps Validator"),
    ]
    
    results = {}
    
    for script_name, description in validators:
        success = run_validator(script_name, description, verbose)
        results[description] = success
    
    # Summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for description, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status} - {description}")
    
    print("\n" + "=" * 70)
    if passed == total:
        print(f"✓ ALL {total} VALIDATORS PASSED")
        print("=" * 70)
        print("\n🎉 Baseline established - All project files validated!")
        return 0
    else:
        print(f"⚠ {passed}/{total} VALIDATORS PASSED")
        print("=" * 70)
        print(f"\n⚠ {total - passed} validators found issues - review output above")
        return 1


if __name__ == "__main__":
    sys.exit(main())
