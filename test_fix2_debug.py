#!/usr/bin/env python
"""Debug script to test FIX #2 functions locally."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

from config.rails.actions import _load_diagnostic_maps, _map_category_to_symptom_key, _extract_stf_by_skill_level

# Test 1
print('[TEST 1] Loading diagnostic maps...')
maps = _load_diagnostic_maps()
print(f'  Result: Loaded {len(maps)} symptom maps')
print()

# Test 2
print('[TEST 2] Map flipper -> symptom key...')
key = _map_category_to_symptom_key('flipper')
print(f'  Result: flipper maps to "{key}"')
print()

# Test 3
print('[TEST 3] Extract STF for beginner (right_flipper_dead)...')
if 'right_flipper_dead' in maps:
    rf_data = maps['right_flipper_dead']
    print(f'  right_flipper_dead found: {rf_data.get("title")}')
    steps = _extract_stf_by_skill_level(rf_data, 'beginner')
    print(f'  Got {len(steps)} steps:')
    for i, step in enumerate(steps):
        if len(step) > 80:
            print(f'    {step[:80]}...')
        else:
            print(f'    {step}')
else:
    print(f'  ERROR: right_flipper_dead not in maps')
    print(f'  Available: {list(maps.keys())}')
