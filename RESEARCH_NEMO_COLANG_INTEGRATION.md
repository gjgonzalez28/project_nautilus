# Research: NeMo Guardrails + Colang 2.0 Integration - Complete Status

**Date Researched:** February 24, 2026  
**Status:** Partial - Core flows working, LLM integration has timeout issue  
**Files:** `config/rails/discovery.co`, `config/rails/actions.py`, `config/rails/config.yml`

---

## Current Integration Status

### ✅ WORKING
- [x] Colang 2.0 syntax in discovery.co (FIXED Feb 24)
- [x] Colang 2.0 syntax in hello_world.co (FIXED Feb 24)
- [x] Colang 2.0 syntax in safety.co (FIXED Feb 24)
- [x] @action decorators in actions.py (IMPLEMENTED)
- [x] NeMo configuration loads without parse errors (HTTP 200 health checks)
- [x] Flask server initializes successfully
- [x] Python helper functions execute without errors
- [x] StructuredLogger integration in actions.py

### ⚠️ PARTIAL
- [ ] Discovery flow executes through NeMo (hangs during LLM call)
- [ ] Gemini API integration (slow response times/timeouts)
- [ ] End-to-end flow testing (blocked by LLM timeout)

### ❌ KNOWN ISSUES
1. **Gemini API Timeouts:** Discovery flow test hangs at LLM call
2. **NeMo/Gemini Integration:** May have langchain-google-genai compatibility issues
3. **Test Message Completion:** Flask /diagnose endpoint times out waiting for response

---

## Colang 2.0 Syntax Fixes Applied

### Fix 1: discovery.co

**Before (Incorrect):**
```colang
define flow discovery  # WRONG: Old Colang 1.0 syntax
  bot "text"           # WRONG: Missing "say"
  elif condition       # WRONG: No elif in Colang 2.0
  await discover_*     # WRONG: Misplaced await
```

**After (Correct Colang 2.0):**
```colang
import core

flow discovery        # ✅ New syntax
    bot say "text"    # ✅ Has "say"
    when condition    # ✅ Use when/or when/else
        pass
    or when other_condition
        pass
    else
        pass
    
    await discover_machine_flow  # ✅ Proper await in flow
```

**Key Changes:**
- `define flow` → `flow` (simpler declaration)
- `bot "text"` → `bot say "text"` (explicit)
- `elif` → `or when` (Colang conditional style)
- `import core` at top (access standard library)

**Files Fixed:**
1. `config/rails/discovery.co` (101 lines, 3 sub-flows)
2. `config/rails/hello_world.co` (simpler test flow)
3. `config/rails/safety.co` (placeholder for Phase 3)

---

## @action Decorator Implementation

### Requirement: NeMo Action Naming Convention

**MUST END WITH "Action"** - This is how NeMo's auto-discovery works:

```python
# ❌ WRONG - NeMo won't find it
@action(name="fuzzy_match_machine")
async def fuzzy_match_machine_action(...):
    pass

# ✅ CORRECT - NeMo discovers and registers it
@action(name="FuzzyMatchMachineAction")
async def fuzzy_match_machine_action(...):
    pass
```

### Current Actions Implemented

**File:** `config/rails/actions.py`

1. **FuzzyMatchMachineAction** (Line ~67)
   ```python
   @action(name="FuzzyMatchMachineAction")
   async def fuzzy_match_machine_action(
       user_input: str, 
       threshold: float = 0.6
   ) -> Dict[str, Any]:
       """Fuzzy match user input against machine library"""
       result = fuzzy_machine_helper(user_input, threshold)
       logger.log_event(...)
       return result
   ```
   
   **Called From:** `config/rails/discovery.co` line 58
   ```colang
   $result = await FuzzyMatchMachineAction(user_input=$user_input)
   ```

2. **ValidateSkillLevelAction** (Line ~87)
   ```python
   @action(name="ValidateSkillLevelAction")
   async def validate_skill_level_action(user_input: str) -> Dict[str, Any]:
       """Validate and extract skill level from input"""
       result = validate_skill_helper(user_input)
       logger.log_event(...)
       return result
   ```
   
   **Called From:** `config/rails/discovery.co` line 79
   ```colang
   $result = await ValidateSkillLevelAction(user_input=$user_input)
   ```

### Action Invocation in Colang

```colang
# Syntax: $var = await ActionName(param1=value1, param2=value2)
$result = await FuzzyMatchMachineAction(user_input=$user_input, threshold=0.6)

# Access returned values with dot notation
when $result.matched == True
    $machine = $result.machine_id
```

---

## NeMo Configuration

**File:** `config/rails/config.yml`

```yaml
models:
  - type: main
    engine: google_genai
    model: gemini-2.5-pro

rails:
  input:
    flows: []
  
  dialog:
    flows:
      - discovery
      - hello_world    # Fallback simple flow
  
  output:
    flows: []

config:
  flow_logging:
    enabled: true
```

### Key Settings
- **LLM Model:** `gemini-2.5-pro` (paid tier, required for good performance)
- **Engine:** `google_genai` (langchain integration)
- **Dialog Flows:** [discovery, hello_world] (processed in order)
- **Flow Logging:** Enabled (tracks flow execution in logs)

### Environment Variables

**File:** `.env`
```
GEMINI_API_KEY=AIzaSyAjXUvQwIEhRADBInEvfy98Wli7vEFJq_k
GEMINI_MODEL=gemini-2.5-pro
NEMO_CONFIG_PATH=./config/rails
```

---

## Known Issue: Gemini API Timeouts

### Symptoms
1. Flask `/diagnose` endpoint hangs indefinitely
2. Direct test via `test_discovery_direct.py` hangs at LLM call
3. 10-second timeout triggers on async call
4. No error thrown, just silence

### Root Causes (Investigation)

**Possible causes:**
1. **Gemini API rate limiting** - Free tier may have limits
2. **API key issue** - Key might be shared/revoked (not recommended putting in repo)
3. **langchain-google-genai version mismatch** - May have dependency issues
4. **Network latency** - Gemini API server might be slow from current location
5. **NeMo/langchain compatibility** - Specific version combination issue

### Current Workaround

**Option A (Recommended): Use mock LLM**
Create mock action that returns deterministic responses:

```python
@action(name="MockLLMAction")
async def mock_llm(prompt: str) -> str:
    """Mock LLM for testing without real API calls"""
    return "Mock response - replace with real LLM when API works"
```

**Option B: Increase timeout**
In `app.py`, increase timeout:
```python
response = await asyncio.wait_for(
    nemo_rails.generate_async(...),
    timeout=30.0  # Increased from 10s
)
```

**Option C: Debug langchain integration**
Check if langchain-google-genai is properly installed:
```bash
pip show langchain-google-genai
```

If installed, verify initialization:
```python
from langchain_google_genai import ChatGoogleGenerativeAI
model = ChatGoogleGenerativeAI(model="gemini-2.5-pro", api_key="KEY")
response = await model.ainvoke("test")
```

---

## Discovery Flow Execution Path

### Flow Diagram

```
User Input (Flask /diagnose)
    ↓
NeMo.generate_async() 
    ↓
Load discovery.co flow
    ↓
flow discovery
    ├─ Bot greeting message
    ├─ await discover_machine_flow
    │  ├─ Ask "What machine..."
    │  ├─ $input = await user said something
    │  ├─ $result = await FuzzyMatchMachineAction(user_input=$input)
    │  └─ Set $machine_name, $manufacturer, $era
    │
    ├─ await discover_skill_level_flow
    │  ├─ Ask "What's your experience level..."
    │  ├─ $input = await user said something
    │  ├─ $result = await ValidateSkillLevelAction(user_input=$input)
    │  └─ Set $skill_level
    │
    └─ Bot final message with $machine_name
    ↓
Return to Flask
    ↓
Send JSON response to client
```

### State Variables Set During Discovery

These variables are available to subsequent flows:
- `$machine_name` - User's original description
- `$manufacturer` - From library match (e.g., "Williams")
- `$era` - From library match (e.g., "Solid State Mid")
- `$skill_level` - From validation (e.g., "beginner")

---

## What's Missing for Phase 3 Completion

### 5 Remaining Core Flows

1. **playfield.co** - Ask "Can you access playfield?"
   - Validate skill level prerequisites
   - Set $playfield_confirmed

2. **symptom.co** - Extract symptom/problem
   - Fuzzy match against symptom library
   - Set $symptom, $symptom_id

3. **evidence.co** - Gather supporting info
   - Ask 2-3 follow-up questions
   - Calculate $diagnostic_confidence

4. **diagnostics.co** - Generate recommendation
   - Load STF from diagnostic_maps.yaml
   - Call Gemini for explanation
   - Format by skill level

5. **safety.co** - Enforce safety gates (ENHANCED)
   - Check global.yaml + skill-level rules
   - Block unsafe recommendations

### Integration Requirements

- All flows must be listed in `config/rails/config.yml` dialog flows
- All flows must use correct Colang 2.0 syntax
- All flows must use @action decorators for Python calls
- All flows must set state variables for next flow
- All flows must log events with StructuredLogger

---

## Testing Strategy

### Unit Tests
✅ Python helper functions (discovery_helper.py)
✅ StructuredLogger API usage
✅ @action decorator registration

### Integration Tests
⚠️ Single flow execution (blocked by Gemini timeout)
⏳ Multi-flow execution (blocked by Gemini timeout)
⏳ End-to-end conversation (blocked by Gemini timeout)

### Resolution
Need to either:
1. Fix Gemini API integration (investigate timeout)
2. Implement mock LLM for testing
3. Use alternative LLM provider (OpenAI, etc.)

---

## Files That Mirror This Documentation

- `COLANG_2_0_COMPLETE_SPECIFICATION.md` - Full Colang syntax
- `COLANG_2_0_WORKING_EXAMPLES.md` - Real working examples
- `COLANG_2_0_SPECIFIC_PATTERNS.md` - Pattern reference (most useful)
- `RESEARCH_STRUCTURED_LOGGER_API.md` - Logger API details
- `RESEARCH_MACHINE_LIBRARY_FUZZY_MATCHING.md` - Fuzzy matching details

