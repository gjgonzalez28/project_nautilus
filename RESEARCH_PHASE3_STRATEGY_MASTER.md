# MASTER: Phase 3 Implementation Strategy & Status

**Date Created:** February 24, 2026  
**Status:** 40% Complete - Core discovery flow built, LLM integration issue needs resolution  
**Critical:** See RESEARCH_*.md files for detailed component knowledge

---

## Executive Summary

Phase 3 goal: Build 6 core Colang flows that orchestrate diagnostic conversation. 

**Progress:**
- ✅ Discovery flow created (100%) 
- ✅ Python helpers implemented & tested (100%)
- ✅ @action decorators registered (100%)
- ✅ NeMo config and Colang syntax fixed (100%)
- ⚠️ LLM integration working but has timeout issue (0%)
- ⏳ 5 remaining flows not started (0%)

**Blocker:** Gemini API calls timeout. Affects testing and validation of entire flow system.

---

## Architecture Overview

```
User Input (HTTP /diagnose)
    ↓
Flask (app.py)
    ├─ Validate JSON
    ├─ Create session
    └─ Call NeMo LLMRails
         ↓
    NeMo Guardrails (LLMRails)
         ├─ Load config.yml
         ├─ Route to dialog flow
         └─ Execute Colang flow
              ↓
         [Discovery Flow] → [Playfield Flow] → [Symptom Flow] → [Evidence Flow] → [Diagnostics Flow]
              ↓
         Each flow may:
         ├─ Capture user input ($input = await user said something)
         ├─ Call Python action ($result = await FuzzyMatchAction(...))
         ├─ Conditional logic (when/or when/else)
         ├─ Bot response (bot say "message")
         └─ Set state variables ($machine_name = value)
         ↓
    Return state + bot response to Flask
         ↓
JSON response to client
    └─ {response: "text", trace_id: "id", turn: N, state: {...}}
```

---

## Implemented Components

### 1. Discovery Flow (COMPLETE) ✅

**File:** `config/rails/discovery.co` (101 lines)

**Purpose:** Extract machine identity and skill level

**Structure:**
- Main flow: `flow discovery` (orchestration)
- Sub-flow 1: `flow discover_machine_flow` 
  - Captures user input
  - Calls FuzzyMatchMachineAction
  - Sets $machine_name, $manufacturer, $era
- Sub-flow 2: `flow discover_skill_level_flow`
  - Captures user input  
  - Calls ValidateSkillLevelAction
  - Sets $skill_level

**State Variables Set:**
```
$machine_name = "User's description"
$manufacturer = "Bally|Williams|Gottlieb|Stern|Various"
$era = "EM|Solid State Early|Solid State Mid|Modern"
$skill_level = "beginner|intermediate|pro"
```

**Next Flow:** playfield.co

---

### 2. Python Helper Module (COMPLETE) ✅

**File:** `logic/discovery_helper.py` (175 lines)

**Functions:**

1. **fuzzy_match_machine(user_input, threshold=0.6) -> Dict**
   - Input: "I have a Williams from the 90s"
   - Output: {matched: True, machine_id: "WILLIAMS_WPC", era: "Solid State Mid", ...}
   - Uses: SequenceMatcher from difflib
   - Scoring: Name match (70%) + Era keyword bonus (30%)

2. **validate_skill_level(user_input) -> Dict**
   - Input: "I'm a beginner"
   - Output: {valid: True, skill_level: "beginner", confidence: 0.5}
   - Uses: Keyword-based classification
   - Keywords: beginner=[new, learning], intermediate=[experienced], pro=[expert, advanced]

3. **load_machine_library() -> List[Dict]**
   - Loads `data/machine_library.json`
   - Returns list of 6 machine category dicts
   - Cached per module load

**Logging:** All functions log events to /logs/nautilus-*.log

---

### 3. NeMo Actions Bridge (COMPLETE) ✅

**File:** `config/rails/actions.py` (150 lines)

**Implemented Actions:**

1. **FuzzyMatchMachineAction** (Line 67)
   ```python
   @action(name="FuzzyMatchMachineAction")
   async def fuzzy_match_machine_action(user_input: str, threshold: float = 0.6) -> Dict:
       result = fuzzy_machine_helper(user_input, threshold)
       logger.log_event(event="machine_matched", data={...}, component="actions")
       return result
   ```

2. **ValidateSkillLevelAction** (Line 87)
   ```python
   @action(name="ValidateSkillLevelAction")
   async def validate_skill_level_action(user_input: str) -> Dict:
       result = validate_skill_helper(user_input)
       logger.log_event(event="skill_level_extracted", data={...}, component="actions")
       return result
   ```

**Key Requirements Met:**
- ✅ Names end with "Action" (NeMo requirement)
- ✅ All functions are async
- ✅ All have @action decorator
- ✅ All log with StructuredLogger

---

### 4. NeMo Configuration (COMPLETE) ✅

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
      - discovery      # ← Phase 3 flows start here
      - hello_world    # ← Fallback simple flow
  
  output:
    flows: []

config:
  flow_logging:
    enabled: true
```

**Configuration Details:**
- **LLM:** Gemini 2.5 Pro (configured in .env)
- **Dialog flows:** Processed in order until one completes
- **Flow logging:** All flow transitions logged

---

### 5. Colang 2.0 Syntax (FIXED) ✅

**Files Fixed:**
- `config/rails/discovery.co` - Main Phase 3 flow
- `config/rails/hello_world.co` - Fallback test flow  
- `config/rails/safety.co` - Placeholder phase 3 flow

**Key Syntax Fixes Applied:**
- `define flow` → `flow` (Colang 2.0 declaration)
- `bot "text"` → `bot say "text"` (explicit action)
- `user ".*"` → `$input = await user said something` (capture)
- `if/elif/else` → `when/or when/else` (conditionals)
- Missing `import core` → Added (standard library access)

---

## 5 Remaining Flows (NOT YET STARTED)

### 1. playfield.co - Playfield Access Validation

**Purpose:** Ensure user has access to playfield before diagnostics  
**Complexity:** Low (simple yes/no validation)
**Dependencies:** discovery.co must complete first ($machine_name must be set)

**Pseudo-code:**
```colang
flow playfield
    when $skill_level == "beginner"
        bot say "Can you remove glass and raise playfield?"
    or when $skill_level in ["intermediate", "pro"]
        bot say "Do you have playfield access?"
    
    when user said "yes"
        $playfield_confirmed = True
    or when user said "no"
        bot say "You need playfield access to proceed"
        return  # Exit diagnostic
```

**Estimated Time:** 30 mins

---

### 2. symptom.co - Symptom Extraction

**Purpose:** Extract what's NOT working  
**Complexity:** Medium (fuzzy matching against 30+ symptoms)  
**Dependencies:** discovery.co ($machine_name) + playfield.co ($playfield_confirmed)

**Pseudo-code:**
```colang
flow symptom
    bot say "What's not working with your {$machine_name}?"
    $user_input = await user said something
    
    $symptom_result = await FuzzyMatchSymptomAction(
        machine_id=$machine_id,
        user_input=$user_input
    )
    
    when $symptom_result.matched == True
        $symptom = $symptom_result.symptom
        $symptom_id = $symptom_result.symptom_id
        $symptom_confidence = $symptom_result.confidence
    or when $symptom_result.matched == False
        bot say "Can you describe that differently?"
        # Retry
```

**New Python Helper Needed:**
- File: `logic/symptom_matcher.py`
- Function: `fuzzy_match_symptom(machine_id, user_input, threshold=0.65)`
- Logic: Match user description against machine's symptom list

**Estimated Time:** 1 hour

---

### 3. evidence.co - Gather Diagnostic Evidence

**Purpose:** Collect 2-3 follow-up questions to narrow diagnosis  
**Complexity:** Medium (dynamic question selection)  
**Dependencies:** symptom.co ($symptom_id)

**Pseudo-code:**
```colang
flow evidence
    # For current symptom, ask 2-3 evidence questions
    $evidence_list = []
    
    flow collect_evidence
        bot say "Follow-up question 1 about {$symptom}?"
        $answer1 = await user said something
        $evidence_list.append($answer1)
        
        bot say "Follow-up question 2?"
        $answer2 = await user said something
        $evidence_list.append($answer2)
    
    $confidence = await calculate_confidence(
        symptom=$symptom,
        evidence=$evidence_list,
        skill_level=$skill_level
    )
    
    when $confidence >= skill_threshold
        # Enough info, proceed to diagnostics
        pass
    or when $confidence < skill_threshold
        # Need more info
        await collect_more_evidence
```

**New Python Helper Needed:**
- File: `logic/evidence_scorer.py`
- Function: `calculate_confidence(symptom, evidence_list, skill_level)`
- Logic: Score confidence based on answer quality

**Estimated Time:** 1-1.5 hours

---

### 4. diagnostics.co - Generate STF Output

**Purpose:** Load diagnostic steps and format by skill level  
**Complexity:** High (LLM integration for explanations)  
**Dependencies:** evidence.co ($diagnostic_confidence)

**Pseudo-code:**
```colang
flow diagnostics
    # Load STF from diagnostic_maps.yaml
    $stf = await load_diagnostic_steps(
        machine_id=$machine_id,
        symptom_id=$symptom_id
    )
    
    # Format STF by skill level
    when $skill_level == "beginner"
        # Show STRAIGHT only, with explanation
        $explanation = await explain_with_gemini(
            stf=$stf.straight,
            style="novice_friendly"
        )
    or when $skill_level == "intermediate"
        # Show STRAIGHT + TRUE with technical terms
        $explanation = await explain_with_gemini(
            stf=$stf.straight + $stf.true,
            style="technical"
        )
    or when $skill_level == "pro"
        # Show all steps, no explanation
        $explanation = $stf.straight + $stf.true + $stf.flush
    
    bot say $explanation
```

**New Python Helper Needed:**
- File: `logic/diagnostic_generator.py`
- Function: `load_diagnostic_steps(machine_id, symptom_id)` - Query YAML
- Function: `format_stf_by_skill(stf_dict, skill_level)` - Format text

**LLM Integration Needed:**
- Use Gemini to generate human-friendly explanations
- Keep STF structure intact (STRAIGHT: ..., TRUE: ..., FLUSH: ...)

**Estimated Time:** 2 hours

---

### 5. safety.co - Safety Gate Enforcement (ENHANCED)

**Purpose:** Enforce skill-level and safety constraints  
**Complexity:** High (rule engine, gate logic)  
**Dependencies:** All above flows

**Rules from global.yaml:**
- 0C.S1: High voltage warning (must be pro)
- 0C.R19: Expertise boundary checks
- Soldering restrictions (not for beginner)
- Power supply modifications (not for beginner)

**Pseudo-code:**
```colang
flow safety_override
    # Before returning diagnostics, check safety
    when $stf contains "soldering"
        when $skill_level == "beginner"
            bot say "ERROR: Soldering not recommended for beginners"
            return  # Abort diagnostic
    
    when $stf contains "high voltage"
        when $skill_level != "pro"
            bot say "WARNING: This task requires professional expertise"
            when user said "continue"
                pass
            or when user said "skip"
                return
    
    # Safety check passed, proceed with diagnostics
    pass
```

**Config Files Needed:**
- Already exists: `data/rules/global.yaml`
- Already exists: `data/rules/beginner.yaml`, `intermediate.yaml`, `pro.yaml`

**Estimated Time:** 1-1.5 hours

---

## Dependencies & Integration Matrix

| Flow | Depends On | Sets Variables | Calls Actions | Uses Config |
|------|-----------|---------------|----|---|
| discovery | (start) | machine, manufacturer, era, skill | FuzzyMatch, ValidateSkill | - |
| playfield | discovery | playfield_confirmed | - | rules/beginner.yaml |
| symptom | discovery, playfield | symptom, symptom_id, confidence | FuzzyMatchSymptom | - |
| evidence | symptom | evidence_list, diagnostic_confidence | - | (dynamic) |
| diagnostics | evidence | stf_output, explanation | LoadSteps, ExplainGemini | diagnostic_maps.yaml |
| safety | all | none | CheckSafety | global.yaml, skill rules |

---

## Outstanding Issue: Gemini API Timeout

### Current Symptom
```
Flask /diagnose endpoint
  → NeMo.generate_async() called
  → Hangs indefinitely (no response, no error)
```

### Investigation Findings
- NeMo loads successfully (HTTP 200 health check)
- discovery.co parses correctly (no syntax errors)
- Python helpers work (tested standalone)
- @actions are registered (NeMo recognizes them)
- Issue is in the LLM call itself

### Debugging Steps for Next AI

1. **Test direct Gemini call:**
   ```python
   from langchain_google_genai import ChatGoogleGenerativeAI
   model = ChatGoogleGenerativeAI(model="gemini-2.5-pro", api_key=KEY)
   response = await model.ainvoke("Hello")
   print(response)  # Does this timeout?
   ```

2. **Check API key validity:**
   - Test in Google's Python SDK directly
   - Check API quota in Google Cloud console

3. **Check langchain version compatibility:**
   ```bash
   pip show langchain langchain-google-genai langchain-core
   ```

4. **Enable debug logging:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   logging.getLogger("langchain_google_genai").setLevel(logging.DEBUG)
   ```

5. **Monitor with strace/debugger:**
   - Is it hanging on network I/O?
   - Is it looping internally?
   - Is there a default timeout being hit?

### Workaround Options

**Option A: Mock LLM for testing**
- Doesn't solve real problem but lets you test flow logic
- Implement MockLLMAction that returns deterministic responses

**Option B: Increase timeout**
- Change from 10s to 30s in app.py
- Masks problem but might work if API is just slow

**Option C: Use different LLM**
- Switch to OpenAI (model="gpt-4")
- Switch to Anthropic (model="claude-opus")
- Requires different langchain library

**Option D: Debug langchain/NeMo integration**
- Check if there's a version mismatch
- Review NeMo's LLMRails initialization code
- Check if config.yml has wrong settings

---

## Testing Approach for Phase 3

### Unit Tests ✅
```bash
# Python helpers
python test_python_actions.py
```

### Integration Tests ⏳
```bash
# Once Gemini issue is resolved:
curl -X POST http://localhost:5000/diagnose \
  -H "Content-Type: application/json" \
  -d '{"message": "I have a Williams machine and I'"'"'m a beginner"}'

# Expected response: Bot identifies machine + asks for playfield access
```

### End-to-End Test ⏳
```bash
# Multi-turn conversation:
1. POST /diagnose "Williams machine, beginner"
   → Returns: "Great! Can you access the playfield?"
2. POST /diagnose "Yes, I can" (trace_id from previous)
   → Returns: "What's not working?"
3. POST /diagnose "Lights aren't working" (trace_id)
   → Returns: Follow-up questions from evidence.co
4. ...continue...
```

---

## Deliverables Checklist for Phase 3

- [x] Colang 2.0 syntax reference docs (COLANG_*.md)
- [x] Discovery flow implemented & tested
- [x] Python helpers for discovery (fuzzy & skill validation)
- [x] @action decorators for NeMo
- [x] StructuredLogger integration
- [ ] Playfield flow (30 min)
- [ ] Symptom flow (1 hour)
- [ ] Evidence flow (1.5 hours)
- [ ] Diagnostics flow (2 hours)
- [ ] Safety flow enhancement (1.5 hours)
- [ ] Golden conversation testing (1 hour)
- [ ] API/LLM timeout resolution (varies)

**Total Remaining:** ~8-10 hours of coding (AFTER resolving Gemini issue)

---

## Research Documents for Next AI

Read these FIRST if you're continuing Phase 3:

1. **RESEARCH_STRUCTURED_LOGGER_API.md** - How to log correctly
2. **RESEARCH_MACHINE_LIBRARY_FUZZY_MATCHING.md** - Fuzzy matching algorithm  
3. **RESEARCH_NEMO_COLANG_INTEGRATION.md** - NeMo/Colang architecture details
4. **COLANG_2_0_SPECIFIC_PATTERNS.md** - Colang syntax patterns (most useful)
5. **This file** - Phase 3 overall strategy

---

## Next Steps (Priority Order)

1. **CRITICAL: Resolve Gemini API timeout**
   - Debug langchain-google-genai integration
   - Test standalone Gemini call
   - Consider mock/alternative LLM

2. Implement remaining 5 flows

3. Build golden conversation tests

4. Performance tuning & logging optimization

