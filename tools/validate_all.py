#!/usr/bin/env python
"""
Project Nautilus: Master Validator

Runs all validation checks before deployment.
Exit code 0 = all valid, non-zero = failures

Usage:
    python tools/validate_all.py
"""

import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from logging.logger import setup_logging, get_logger

logger = get_logger(__name__)


def validate_yaml_files():
    """Validate all YAML files can be parsed."""
    import yaml
    
    print("\n[VALIDATE] YAML Files...")
    rules_dir = PROJECT_ROOT / "rules"
    errors = []
    
    for yaml_file in rules_dir.glob("*.yaml"):
        try:
            with open(yaml_file) as f:
                yaml.safe_load(f)
            print(f"  ✓ {yaml_file.name}")
        except Exception as e:
            errors.append(f"{yaml_file.name}: {str(e)}")
            print(f"  ✗ {yaml_file.name}: {str(e)}")
    
    return len(errors) == 0, errors


def validate_json_files():
    """Validate all JSON files can be parsed."""
    import json
    
    print("\n[VALIDATE] JSON Files...")
    data_dir = PROJECT_ROOT / "data"
    errors = []
    
    for json_file in data_dir.glob("*.json"):
        try:
            with open(json_file) as f:
                json.load(f)
            print(f"  ✓ {json_file.name}")
        except Exception as e:
            errors.append(f"{json_file.name}: {str(e)}")
            print(f"  ✗ {json_file.name}: {str(e)}")
    
    return len(errors) == 0, errors


def validate_python_imports():
    """Validate all Python modules can be imported."""
    print("\n[VALIDATE] Python Imports...")
    modules_to_test = [
        "logic.manager",
        "logic.discovery_script",
        "logic.nautilus_core",
        "chatgpt_integration",
        "logging.logger"
    ]
    
    errors = []
    for module in modules_to_test:
        try:
            __import__(module)
            print(f"  ✓ {module}")
        except Exception as e:
            errors.append(f"{module}: {str(e)}")
            print(f"  ✗ {module}: {str(e)}")
    
    return len(errors) == 0, errors


def validate_required_files():
    """Validate all required files exist."""
    print("\n[VALIDATE] Required Files...")
    required_files = [
        "README.md",
        "app.py",
        "main.py",
        "rules/global.yaml",
        "rules/beginner.yaml",
        "rules/intermediate.yaml",
        "rules/pro.yaml",
        "data/diagnostic_maps.yaml",
        "data/machine_library.json",
        "requirements.txt"
    ]
    
    errors = []
    for file_path in required_files:
        full_path = PROJECT_ROOT / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            errors.append(f"{file_path}: MISSING")
            print(f"  ✗ {file_path}: MISSING")
    
    return len(errors) == 0, errors


def main():
    """Run all validators."""
    setup_logging(log_dir=str(PROJECT_ROOT / "logs"))
    
    print("=" * 70)
    print("PROJECT NAUTILUS: MASTER VALIDATOR")
    print("=" * 70)
    
    all_pass = True
    all_errors = []
    
    # Run validators
    yaml_pass, yaml_errors = validate_yaml_files()
    all_pass = all_pass and yaml_pass
    all_errors.extend(yaml_errors)
    
    json_pass, json_errors = validate_json_files()
    all_pass = all_pass and json_pass
    all_errors.extend(json_errors)
    
    files_pass, file_errors = validate_required_files()
    all_pass = all_pass and files_pass
    all_errors.extend(file_errors)
    
    imports_pass, import_errors = validate_python_imports()
    all_pass = all_pass and imports_pass
    all_errors.extend(import_errors)
    
    # Summary
    print("\n" + "=" * 70)
    if all_pass:
        print("✓ ALL VALIDATIONS PASSED")
        print("=" * 70)
        return 0
    else:
        print("✗ VALIDATION FAILURES:")
        for error in all_errors:
            print(f"  - {error}")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
