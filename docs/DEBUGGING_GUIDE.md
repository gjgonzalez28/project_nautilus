# Project Nautilus: Debugging Guide

## Overview

This guide explains how to use the diagnostic tools when Nautilus isn't working as expected.

---

## Quick Start

### 1. Run Validators First

Before anything else, ensure all data files are valid:

```powershell
python tools/validate_all.py
```

This checks:
- YAML files parse correctly
- JSON files parse correctly
- Required files exist
- Python modules can be imported

If validation fails, fix the errors before proceeding.

### 2. Run Tests

```powershell
# All tests
pytest tests/ -v

# Just unit tests (fast)
pytest tests/test_unit/ -v

# Just integration tests
pytest tests/test_integration/ -v
```

---

## Debugging a Broken Conversation

### Step 1: Enable Logging

The logging system is built-in, but ensure it's configured:

```python
from logging.logger import setup_logging, get_logger

# In your code
setup_logging(log_dir="logs", log_level="DEBUG")
logger = get_logger(__name__)
```

All events are logged to `logs/nautilus-YYYY-MM-DD.log` as JSON.

### Step 2: Run the Conversation

Start Flask or main.py and interact with Nautilus. Every message is logged.

### Step 3: Inspect the Session

After the conversation, inspect what happened:

```powershell
# Show latest conversation
python tools/inspect_session.py --latest

# Show specific conversation
python tools/inspect_session.py --trace-id conv_abc123def456
```

This shows:
- All state changes
- Flow transitions
- Gate evaluations
- Intent recognitions

---

## Understanding Log Events

### State Change Events

```json
{
  "event": "state_change",
  "component": "session_state",
  "data": {
    "variable": "current_symptom",
    "old_value": null,
    "new_value": "left_flipper_dead",
    "reason": "user said flipper not working"
  }
}
```

**What it means:** A variable in NeMo was updated. Track these to see if state persists correctly.

### Flow Transition Events

```json
{
  "event": "flow_transition",
  "component": "nemo_router",
  "data": {
    "from_flow": "discovery_gate",
    "to_flow": "playfield_gate",
    "reason": "user identified machine",
    "condition": "skill_declared == true"
  }
}
```

**What it means:** NeMo moved from one flow to another. Check the condition to see if routing logic is correct.

### Gate Evaluation Events

```json
{
  "event": "gate_evaluation",
  "component": "nemo_gates",
  "data": {
    "gate": "confidence_gate",
    "condition": "confidence >= 0.65",
    "passed": true,
    "details": {"current_confidence": 0.75}
  }
}
```

**What it means:** A gate (safety, confidence, etc.) was evaluated. If `passed: false`, flow was blocked.

---

## Common Issues & Solutions

### Issue: Symptom Gets Lost

**Symptom:** User says "left flipper is dead", system asks "what's broken?" again later.

**Debug:**
1. Run `inspect_session.py --latest`
2. Look for `event: state_change` with `variable: current_symptom`
3. Check if it changes from "left_flipper_dead" to `null`
4. Look at the `reason` field to see what caused the change

**Fix:** NeMo must not reset `$symptom` once set. Check Colang flow logic.

---

### Issue: System Asks Same Question Twice

**Symptom:** System asks "Do you know how to remove the glass?" then asks it again.

**Debug:**
1. Run `inspect_session.py --latest`
2. Look for `event: flow_transition`
3. Check if same flow runs twice
4. Look at `condition` to see why it re-entered

**Fix:** Flow logic is looping. Check Colang transition conditions.

---

### Issue: Confidence Gates Not Working

**Symptom:** Even with low evidence, system provides diagnosis.

**Debug:**
```powershell
# Run safety tests
pytest tests/test_safety/ -v
```

Look for `event: gate_evaluation` with `gate: confidence_gate`. Check if `passed` is correct.

---

## VS Code Debugging

### Set Breakpoints

1. Open `logic/manager.py` or any Python file
2. Click left margin to set breakpoint (red dot)
3. Press F5 to start debugger
4. Step through code with F10 (step) or F11 (step into)
5. Hover over variables to inspect values

### Debug with Configuration

Use pre-configured launch configs in `.vscode/launch.json`:

- **Python: Flask App** - Debug Flask server
- **Python: Current File** - Debug any file
- **Python: Run Tests** - Debug tests
- **Python: Interactive CLI** - Debug main.py

---

## Performance Profiling

Check if anything is slow:

```python
import time

start = time.time()
# ... do something ...
elapsed = (time.time() - start) * 1000
logger.log_python_boundary_call(
    function_name="extract_symptom",
    args={"text": user_input},
    result=symptom_id,
    execution_time_ms=elapsed
)
```

Then inspect logs for `execution_time_ms` values.

---

## Writing Tests

When you fix a bug, write a test to prevent regression:

```python
# tests/test_unit/test_symptom_persistence.py
import pytest

@pytest.mark.unit
def test_symptom_persists_across_turns():
    """
    Test: User says symptom once, it should persist
    """
    # Setup
    session = mock_nemo_session()
    
    # User says problem
    session["current_symptom"] = "left_flipper_dead"
    
    # User provides evidence
    session["evidence"] = [{"type": "observed", "text": "no linkage"}]
    
    # Symptom should NOT change
    assert session["current_symptom"] == "left_flipper_dead"
```

Run: `pytest tests/test_unit/test_symptom_persistence.py -v`

---

## Submitting Logs for Help

If you need help debugging:

1. Run the failing conversation
2. Get the trace ID from `inspect_session.py --latest`
3. Export logs: `python tools/inspect_session.py --trace-id conv_xxx > trace_export.txt`
4. Share the trace file

---

## Logging Levels

Control how much is logged:

```python
# In your code
setup_logging(log_level="DEBUG")  # Verbose, everything logged
setup_logging(log_level="INFO")   # Normal, key events
setup_logging(log_level="WARNING") # Only warnings/errors
```

**DEBUG** is slower but shows everything. Use for troubleshooting.
**INFO** is normal production level.

---

## Next Steps

Once you understand how to debug:

1. Write tests for your fixes
2. Run all validators before deploying
3. Keep logs for 7 days (auto-rotate)
4. Monitor Render logs in production
