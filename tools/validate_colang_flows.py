#!/usr/bin/env python
"""
Project Nautilus: Colang Flow Validator

Validates Colang .co files for syntax errors and configuration issues.

Usage:
    python tools/validate_colang_flows.py
    python tools/validate_colang_flows.py --verbose
"""

import sys
import re
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def find_colang_files():
    """Find all .co files in config/rails/"""
    rails_dir = PROJECT_ROOT / "config" / "rails"
    if not rails_dir.exists():
        return []
    return list(rails_dir.glob("*.co"))


def find_registered_actions():
    """Find all registered @action functions in actions.py"""
    actions_file = PROJECT_ROOT / "config" / "rails" / "actions.py"
    if not actions_file.exists():
        return set()
    
    actions = set()
    with open(actions_file, 'r', encoding='utf-8') as f:
        content = f.read()
        # Find @action decorated functions
        pattern = r'@action\([^)]*name\s*=\s*["\']([^"\']+)["\']'
        matches = re.findall(pattern, content)
        actions.update(matches)
        
        # Also find class-based actions
        pattern = r'class\s+(\w+Action)\s*\('
        matches = re.findall(pattern, content)
        # Convert PascalCase to snake_case
        for match in matches:
            snake_case = re.sub(r'(?<!^)(?=[A-Z])', '_', match).lower()
            actions.add(snake_case)
    
    return actions


def validate_colang_file(filepath, registered_actions):
    """Validate a single Colang file"""
    errors = []
    warnings = []
    flows_found = []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check for flow definitions
    for i, line in enumerate(lines, 1):
        # Find flow definitions
        if re.match(r'^\s*flow\s+\w+', line):
            flow_name = re.search(r'flow\s+(\w+)', line).group(1)
            flows_found.append(flow_name)
        
        # Check for await statements with unknown actions
        await_match = re.search(r'await\s+(\w+)\s*\(', line)
        if await_match:
            action_name = await_match.group(1)
            # Skip common flow control keywords
            if action_name not in ['UtteranceBotAction', 'UtteranceUserAction'] and \
               not action_name.startswith('user_') and \
               action_name not in registered_actions:
                # Check if it might be a flow reference (would be in another .co file)
                if not action_name.islower() or '_' not in action_name:
                    warnings.append(f"Line {i}: Unknown action or flow '{action_name}'")
        
        # Check for common syntax issues
        if 'orbot say' in line.lower() or 'oruser said' in line.lower():
            errors.append(f"Line {i}: Possible typo - 'orbot' or 'oruser' instead of 'or bot'/'or user'")
        
        # Check for missing quotes in bot say statements
        if re.search(r'bot\s+say\s+[^"\']', line) and not re.search(r'bot\s+say\s+\$', line):
            warnings.append(f"Line {i}: 'bot say' statement may be missing quotes")
        
        # Check for emoji characters (DUTY #15 violation)
        if re.search(r'[\U0001F300-\U0001F9FF]|[\u2600-\u26FF]|[\u2700-\u27BF]', line):
            errors.append(f"Line {i}: Contains emoji character (violates DUTY #15)")
        
        # Check for unmatched parentheses
        if line.count('(') != line.count(')'):
            warnings.append(f"Line {i}: Unmatched parentheses")
        
        # Check for indentation issues (Colang uses indentation)
        if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            if not re.match(r'^\s*(flow|import|from)', line):
                if i > 1 and lines[i-2].strip().endswith(':'):
                    errors.append(f"Line {i}: Expected indentation after ':'")
    
    return {
        'errors': errors,
        'warnings': warnings,
        'flows': flows_found
    }


def check_config_yml():
    """Check config.yml for flow references"""
    config_file = PROJECT_ROOT / "config" / "config.yml"
    if not config_file.exists():
        return None, ["config.yml not found"]
    
    import yaml
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    flows_in_config = []
    errors = []
    
    # Check rails section
    if 'rails' in config and 'flows' in config['rails']:
        flows_in_config = config['rails']['flows']
    else:
        errors.append("No 'rails.flows' defined in config.yml")
    
    return flows_in_config, errors


def main():
    """Run Colang flow validation"""
    verbose = '--verbose' in sys.argv
    
    print("=" * 70)
    print("PROJECT NAUTILUS: COLANG FLOW VALIDATOR")
    print("=" * 70)
    
    # Find all .co files
    colang_files = find_colang_files()
    if not colang_files:
        print("\n✗ No Colang files found in config/rails/")
        return 1
    
    print(f"\nFound {len(colang_files)} Colang files:")
    for f in colang_files:
        print(f"  - {f.name}")
    
    # Find registered actions
    print("\n[CHECK] Registered Actions...")
    registered_actions = find_registered_actions()
    print(f"  Found {len(registered_actions)} registered actions")
    if verbose:
        for action in sorted(registered_actions):
            print(f"    - {action}")
    
    # Validate each file
    print("\n[VALIDATE] Colang Files...")
    all_flows = {}
    all_errors = []
    all_warnings = []
    
    for filepath in sorted(colang_files):
        result = validate_colang_file(filepath, registered_actions)
        all_flows[filepath.stem] = result['flows']
        
        if result['errors'] or result['warnings']:
            print(f"\n  {filepath.name}:")
            if result['flows']:
                print(f"    Flows: {', '.join(result['flows'])}")
            for error in result['errors']:
                print(f"    ✗ ERROR: {error}")
                all_errors.append(f"{filepath.name}: {error}")
            for warning in result['warnings']:
                print(f"    ⚠ WARNING: {warning}")
                all_warnings.append(f"{filepath.name}: {warning}")
        else:
            print(f"  ✓ {filepath.name}")
            if result['flows']:
                print(f"    Flows: {', '.join(result['flows'])}")
    
    # Check config.yml references
    print("\n[CHECK] config.yml Flow References...")
    config_flows, config_errors = check_config_yml()
    if config_errors:
        for error in config_errors:
            print(f"  ✗ {error}")
            all_errors.append(f"config.yml: {error}")
    elif config_flows:
        print(f"  Entry flows: {config_flows}")
        # Check if referenced flows exist
        all_flow_names = set()
        for flows in all_flows.values():
            all_flow_names.update(flows)
        
        for flow in config_flows:
            if flow not in all_flow_names:
                warning = f"Flow '{flow}' referenced in config but not found in .co files"
                print(f"  ⚠ WARNING: {warning}")
                all_warnings.append(warning)
            else:
                print(f"  ✓ Flow '{flow}' found")
    
    # Summary
    print("\n" + "=" * 70)
    if not all_errors:
        print("✓ NO CRITICAL ERRORS")
        if all_warnings:
            print(f"⚠ {len(all_warnings)} warnings (review recommended)")
        else:
            print("✓ ALL VALIDATIONS PASSED")
        print("=" * 70)
        return 0
    else:
        print(f"✗ {len(all_errors)} CRITICAL ERRORS FOUND:")
        for error in all_errors:
            print(f"  - {error}")
        if all_warnings:
            print(f"\n⚠ {len(all_warnings)} warnings:")
            for warning in all_warnings[:5]:  # Show first 5
                print(f"  - {warning}")
            if len(all_warnings) > 5:
                print(f"  ... and {len(all_warnings) - 5} more")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
