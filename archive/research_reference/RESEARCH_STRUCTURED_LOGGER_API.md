# Research: StructuredLogger API - Complete Reference

**Date Researched:** February 24, 2026  
**Status:** Complete - All behaviors documented  
**File Location:** `app_logging/logger.py`

---

## Overview

`StructuredLogger` provides structured JSON logging with trace ID correlation across the Project Nautilus codebase. All log entries are JSON-formatted for easy parsing and analysis.

---

## Critical API Signature

### Method: `log_event()`

```python
def log_event(
    self,
    event: str,
    data: Dict[str, Any],
    component: str = "",
    level: str = "INFO"
) -> None:
```

**Parameters:**
- `event` (str, REQUIRED): Event type identifier (e.g., `"flow_transition"`, `"state_update"`, `"machine_matched"`)
- `data` (Dict[str, Any], REQUIRED): Event payload as dictionary. This is where ALL contextual data goes.
- `component` (str, optional, default=""): Component/module name that generated the event (e.g., `"discovery_helper"`, `"flask_api"`, `"nemo_init"`)
- `level` (str, optional, default="INFO"): Log level - one of `"DEBUG"`, `"INFO"`, `"WARNING"`, `"ERROR"`

---

## Common Mistakes & Corrections

### ❌ WRONG: Passing keyword arguments directly

```python
logger.log_event(
    event="skill_level_extracted",
    skill_level="beginner",          # ❌ WRONG
    confidence=0.95,                 # ❌ WRONG
    component="discovery_helper"
)
```

**Error:** `TypeError: log_event() got an unexpected keyword argument 'skill_level'`

### ✅ CORRECT: Wrap all data in `data` dict

```python
logger.log_event(
    event="skill_level_extracted",
    data={                           # ✅ CORRECT
        "skill_level": "beginner",
        "confidence": 0.95
    },
    component="discovery_helper"
)
```

---

## Usage Patterns

### Pattern 1: Simple Event Logging

```python
logger.log_event(
    event="machine_library_load_failed",
    data={"error": str(e)},
    component="discovery_helper"
)
```

### Pattern 2: Multi-field Event Logging

```python
logger.log_event(
    event="user_input_processed",
    data={
        "user_input": "Medieval Madness",
        "matched_machine": "WILLIAMS_WPC",
        "confidence": 0.87,
        "took_ms": 45
    },
    component="discovery_helper"
)
```

### Pattern 3: Error-level Logging

```python
logger.log_event(
    event="fuzzy_match_error",
    data={
        "reason": "Library file missing",
        "exception_type": "FileNotFoundError"
    },
    component="discovery_helper",
    level="ERROR"
)
```

### Pattern 4: Complex Nested Data

```python
logger.log_event(
    event="session_state_update",
    data={
        "session_id": "sess_abc123",
        "updates": {
            "machine_name": "Bally MPU",
            "skill_level": "intermediate"
        },
        "timestamp_ms": 1708874103456
    },
    component="flask_api"
)
```

---

## Trace ID Correlation

Every `StructuredLogger` instance has a unique `trace_id` that gets added to every log entry automatically. This enables tracing a single conversation/session through multiple components.

**Accessing the trace ID:**
```python
logger = StructuredLogger(__name__)
current_trace_id = logger.trace_id
```

**Setting a new trace ID:**
```python
new_trace_id = logger.set_trace_id()  # Generates new UUID
```

---

## JSON Output Format

Each log entry becomes a JSON object like:

```json
{
  "timestamp": "2026-02-24T19:49:31.540026Z",
  "level": "INFO",
  "logger": "logic.discovery_helper",
  "message": "",
  "trace_id": "abc-123-def-456",
  "component": "discovery_helper",
  "event": "skill_level_extracted",
  "data": {
    "skill_level": "beginner",
    "confidence": 0.5,
    "user_input": "I'm new to this"
  }
}
```

---

## Files Using StructuredLogger (in codebase)

1. **app.py** - Flask HTTP handlers
   - Uses: event logging for diagnose endpoint
   - Events: "user_message", "assistant_message"

2. **logic/discovery_helper.py** - Machine/skill matching
   - Uses: Result logging, error tracking
   - Events: "machine_matched", "skill_level_extracted", "library_load_failed"

3. **config/rails/actions.py** - NeMo action bridges
   - Uses: Action invocation logging
   - Events: "fuzzy_match_called", "validate_skill_called"

---

## Gotchas & Best Practices

### 1. Always Use `data={}` Dict
The `log_event()` signature expects `data` as a **named parameter containing a dict**. Keyword args beyond the signature are rejected.

### 2. Data Dict Can Be Empty
```python
logger.log_event(
    event="simple_event",
    data={},  # Empty dict is fine
    component="foo"
)
```

### 3. Nested Data is Supported
Store complex structures as nested dicts or lists inside `data`:
```python
logger.log_event(
    event="complex_event",
    data={
        "items": [1, 2, 3],
        "nested": {"key": "value"}
    },
    component="foo"
)
```

### 4. Always Specify `component`
While optional, always provide `component` for debugging:
```python
logger.log_event(event="x", data={}, component="my_module")  # ✅ GOOD
logger.log_event(event="x", data={})  # ⚠️ Missing component name
```

---

## Initialization

```python
from app_logging.logger import StructuredLogger

# Each module creates its own logger
logger = StructuredLogger(__name__)
```

---

## Next Steps for AI

When debugging logging issues:
1. Check if `log_event()` is using `data={}` dict or passing kwargs directly
2. Verify `component` is set (helps in log analysis)
3. Look for events in `/logs/nautilus-*.log` (newest file has latest entries)
4. Filter logs: `grep "error"` or `grep "COMPONENT_NAME"` for specific issues

