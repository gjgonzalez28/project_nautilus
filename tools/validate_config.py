#!/usr/bin/env python
"""
Project Nautilus: Config Validator

Validates config.yml NeMo Guardrails configuration structure.

Usage:
    python tools/validate_config.py
    python tools/validate_config.py --verbose
"""

import sys
import yaml
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def find_colang_flows():
    """Find all available .co flow files"""
    rails_dir = PROJECT_ROOT / "config" / "rails"
    if not rails_dir.exists():
        return set()
    
    flows = set()
    for co_file in rails_dir.glob("*.co"):
        # Read file and extract flow names
        try:
            with open(co_file, 'r', encoding='utf-8') as f:
                import re
                content = f.read()
                # Find "flow <name>" definitions
                flow_matches = re.findall(r'^\s*flow\s+(\w+)', content, re.MULTILINE)
                flows.update(flow_matches)
        except:
            pass
    
    return flows


def validate_config():
    """Validate NeMo config.yml structure"""
    config_file = PROJECT_ROOT / "config" / "config.yml"
    
    if not config_file.exists():
        return False, ["config.yml not found"]
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return False, [f"YAML parse error: {str(e)}"]
    
    if not isinstance(config, dict):
        return False, ["Root element must be a dictionary"]
    
    errors = []
    warnings = []
    
    # Check required top-level keys
    if 'colang_version' not in config:
        warnings.append("Missing 'colang_version' - NeMo may use defaults")
    elif config['colang_version'] not in ['1.0', '2.0', '2.x']:
        warnings.append(f"Unusual colang_version: '{config['colang_version']}'")
    
    # Check models configuration
    if 'models' not in config:
        errors.append("Missing 'models' section - LLM configuration required")
    else:
        models = config['models']
        if not isinstance(models, list):
            errors.append("'models' must be a list")
        else:
            for i, model in enumerate(models):
                context = f"Model {i+1}"
                
                if not isinstance(model, dict):
                    errors.append(f"{context}: Must be a dictionary")
                    continue
                
                if 'type' not in model:
                    warnings.append(f"{context}: Missing 'type' field")
                if 'engine' not in model:
                    errors.append(f"{context}: Missing 'engine' field")
                if 'model' not in model:
                    errors.append(f"{context}: Missing 'model' field")
                
                # Check for API key configuration
                if 'api_key' in model:
                    api_key = model['api_key']
                    # Check if using environment variable syntax
                    if isinstance(api_key, str) and not api_key.startswith('${'):
                        warnings.append(f"{context}: API key should use environment variable syntax: ${{ENV_VAR}}")
    
    # Check rails configuration (critical for flows)
    if 'rails' not in config:
        errors.append("Missing 'rails' section - No flows will be loaded")
    else:
        rails = config['rails']
        if not isinstance(rails, dict):
            errors.append("'rails' must be a dictionary")
        else:
            if 'flows' not in rails:
                errors.append("Missing 'rails.flows' - No entry flows defined")
            else:
                flows_config = rails['flows']
                if not isinstance(flows_config, list):
                    errors.append("'rails.flows' must be a list")
                else:
                    # Check if referenced flows exist
                    available_flows = find_colang_flows()
                    for flow_name in flows_config:
                        if flow_name not in available_flows:
                            warnings.append(f"Flow '{flow_name}' referenced in config but not found in .co files")
    
    # Check instructions (optional but recommended)
    if 'instructions' not in config:
        warnings.append("No 'instructions' section - LLM will have no custom guidance")
    else:
        instructions = config['instructions']
        if not isinstance(instructions, list):
            warnings.append("'instructions' should be a list")
    
    return True, errors, warnings


def main():
    """Run config validation"""
    verbose = '--verbose' in sys.argv
    
    print("=" * 70)
    print("PROJECT NAUTILUS: CONFIG VALIDATOR")
    print("=" * 70)
    
    success, *details = validate_config()
    
    if not success:
        errors = details[0]
        print("\n✗ VALIDATION FAILED")
        for error in errors:
            print(f"  - {error}")
        print("=" * 70)
        return 1
    
    errors, warnings = details
    
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
