# RESEARCH DOCUMENTATION INDEX

**Created:** February 24, 2026  
**Purpose:** Master index of all Phase 3 research and knowledge  
**For:** Next AI continuation session

---

## Quick Start - Read in This Order

If you're picking up Phase 3 work tomorrow, read these files in order:

### 1. **START HERE** (5 min read)
📄 **[RESEARCH_PHASE3_STRATEGY_MASTER.md](RESEARCH_PHASE3_STRATEGY_MASTER.md)**
- Gives complete Phase 3 overview
- Shows what's done (40%) vs what's left (60%)
- Lists specific tasks with time estimates
- Explains the Gemini API timeout blocker

### 2. Architecture Deep Dive (10 min)
📄 **[RESEARCH_NEMO_COLANG_INTEGRATION.md](RESEARCH_NEMO_COLANG_INTEGRATION.md)**
- How NeMo Guardrails + Colang work together
- What was fixed on Feb 24 (Colang 2.0 syntax)
- How @action decorators bridge Colang→Python
- Current status of all components

### 3. Specific Technical References (As Needed)

Each topic has deep-dive documentation:

📄 **[RESEARCH_STRUCTURED_LOGGER_API.md](RESEARCH_STRUCTURED_LOGGER_API.md)** - 10 min
- How to log events correctly (API signature)
- Common mistakes with keyword args
- Usage patterns and examples
- **READ THIS** before writing any new logging code

📄 **[RESEARCH_MACHINE_LIBRARY_FUZZY_MATCHING.md](RESEARCH_MACHINE_LIBRARY_FUZZY_MATCHING.md)** - 8 min
- Machine library structure and design
- How fuzzy matching algorithm works
- Why specific game titles don't match (intentional)
- How to improve matching (if needed)
- **READ THIS** if modifying discovery or symptom matching

### 4. Existing Documentation (Reference)
📄 **[COLANG_2_0_COMPLETE_SPECIFICATION.md](COLANG_2_0_COMPLETE_SPECIFICATION.md)**
- Full Colang 2.0 syntax reference
- All language constructs
- Grammar and semantics

📄 **[COLANG_2_0_SPECIFIC_PATTERNS.md](COLANG_2_0_SPECIFIC_PATTERNS.md)** ⭐ MOST USEFUL
- Real-world Colang patterns
- Copy-paste examples
- Solutions to specific problems
- **Refer to this instead of guessing syntax**

📄 **[COLANG_2_0_WORKING_EXAMPLES.md](COLANG_2_0_WORKING_EXAMPLES.md)**
- 20+ complete working examples
- Different flow types and structures
- Integration patterns

📄 **[COLANG_2_0_STANDARD_LIBRARY.md](COLANG_2_0_STANDARD_LIBRARY.md)**
- NeMo standard library flows
- Built-in actions
- Common utilities

📄 **[README_COLANG_DOCS.md](README_COLANG_DOCS.md)**
- Navigation guide for Colang docs

---

## What Was Done (Feb 24, 2026)

✅ **Colang 2.0 Syntax Fixed**
- discovery.co: Rewritten with correct syntax
- hello_world.co: Updated to Colang 2.0
- safety.co: Fixed placeholder syntax

✅ **Python Helpers Implemented**
- logic/discovery_helper.py: Fuzzy match + skill validation
- All functions tested and working

✅ **NeMo Integration Fixed**
- config/rails/actions.py: @action decorators added correctly
- StructuredLogger.log_event() calls fixed (data={} dict)
- NeMo configuration verified working

✅ **Documentation Created**
- This index
- Master strategy document
- 3 detailed research documents
- 500+ lines Colang reference docs

---

## What's Blocked (Feb 24, 2026)

⚠️ **Gemini API Timeout Issue**
- Discovery flow works BUT hangs when calling LLM
- NeMo loads, Python actions work, Colang is correct
- Issue is in the LLM integration layer
- See "[Gemini API Timeout](RESEARCH_PHASE3_STRATEGY_MASTER.md#known-issue-gemini-api-timeout)" in master document

**Impact:** Can't fully test discovery flow or any downstream flows  
**Resolution:** Debug or mock the LLM (see options in master document)

---

## What Remains (Phase 3)

5 flows not yet started:
1. **playfield.co** - 30 mins
2. **symptom.co** - 1 hour  
3. **evidence.co** - 1.5 hours
4. **diagnostics.co** - 2 hours
5. **safety.co** - 1.5 hours

**Prerequisite:** Resolve Gemini timeout (varies, 15 mins to 2 hours depending on cause)

**Total Remaining:** 8-10 hours after LLM fix

---

## Key Files Modified/Created

### Flows (Colang)
- `config/rails/discovery.co` - ✅ Complete, tested
- `config/rails/hello_world.co` - ✅ Fixed syntax
- `config/rails/safety.co` - ✅ Fixed syntax
- `config/rails/playfield.co` - ⏳ Not started
- `config/rails/symptom.co` - ⏳ Not started
- `config/rails/evidence.co` - ⏳ Not started
- `config/rails/diagnostics.co` - ⏳ Not started

### Python Helpers
- `logic/discovery_helper.py` - ✅ Complete (fuzzy match, skill validate)
- `logic/symptom_matcher.py` - ⏳ Not started
- `logic/evidence_scorer.py` - ⏳ Not started
- `logic/diagnostic_generator.py` - ⏳ Not started

### Config & Integration
- `config/rails/actions.py` - ✅ Fixed (@action decorators)
- `config/rails/config.yml` - ✅ Updated (discovery flow)

### Testing
- `test_python_actions.py` - ✅ Helper functions
- `test_discovery_direct.py` - ⚠️ Hangs on LLM call
- `test_simple_greeting.py` - ⚠️ Hangs on LLM call

---

## Critical Rules to Follow

### Rule 1: Comprehensive Research (NO Piecemeal)
Before implementing anything:
1. Read ALL related research docs
2. Understand complete architecture
3. Document your understanding
4. THEN code

### Rule 2: Documentation for Every Change
When you research a component:
1. Create RESEARCH_[COMPONENT].md file
2. Future AI reads it, not the code
3. Saves time on re-explaining

### Rule 3: Colang Syntax Reference First
Never guess at Colang syntax:
1. Check COLANG_2_0_SPECIFIC_PATTERNS.md first
2. Copy patterns exactly
3. Only refer to COMPLETE_SPECIFICATION if pattern not found

### Rule 4: StructuredLogger Usage
All logging must use this pattern:
```python
logger.log_event(
    event="event_name",
    data={...},  # ALL data in dict, not kwargs
    component="module_name"
)
```

---

## Code Archaeology - How to Find Things

**Question: How do I log correctly?**  
→ Read `RESEARCH_STRUCTURED_LOGGER_API.md`

**Question: How do I make a Colang flow?**  
→ Read `COLANG_2_0_SPECIFIC_PATTERNS.md` → Pattern #X

**Question: How does fuzzy matching work?**  
→ Read `RESEARCH_MACHINE_LIBRARY_FUZZY_MATCHING.md`

**Question: Where's the Gemini timeout?**  
→ See `RESEARCH_PHASE3_STRATEGY_MASTER.md` → "Known Issue"

**Question: What's the complete architecture?**  
→ Read `RESEARCH_NEMO_COLANG_INTEGRATION.md` + master document

**Question: How do I check if something works?**  
→ Look at test files in project root (`test_*.py`)

---

## Environment & Setup

**Python Version:** 3.13.7  
**Virtual Environment:** `venv/` (already configured)  
**Package Manager:** pip (use with `./venv/Scripts/pip.exe`)

**Key Packages:**
- nemoguardrails==0.20.0
- google-genai==1.64.0  
- langchain-google-genai==4.2.1
- flask==2.3.3
- pyyaml==6.0.1

**Running the Server:**
```bash
cd c:\Users\Gonzalez Family\Documents\project_nautilus
./venv/Scripts/python.exe app.py
```

**Testing Python Helpers:**
```bash
./venv/Scripts/python.exe test_python_actions.py
```

**Logging Location:**
```
logs/nautilus-YYYY-MM-DD.log (JSON formatted, one entry per line)
```

---

## API Endpoints

### Health Check
```
GET http://localhost:5000/health
Response: {status: "available", nemo_status: "loaded"|"failed"}
```

### Main Diagnostic Endpoint
```
POST http://localhost:5000/diagnose
Body: {"message": "user input", "trace_id": "optional_session_id"}
Response: {"response": "bot message", "trace_id": "id", "turn": 1}
```

### Inspect Session State
```
GET http://localhost:5000/inspect_session?trace_id=xyz
Response: Current state variables {machine_name, skill_level, ...}
```

---

## What TomJust Needs (User's Context)

- Architecture is complete
- Core discovery flow is built
- Python helpers work standalone
- NeMo + Colang integration fixed
- Gemini API timeout is the blocker

**When Gemini is fixed:**
- Can test discovery flow fully
- Can implement 5 remaining flows
- Estimated 8-10 hours to complete Phase 3

**When Phase 3 is done:**
- Can move to Phase 4 (persistence layer)
- All 6 flows working end-to-end
- Complete diagnostic conversation ready

---

## Quick Glossary

**Colang 2.0** - Conversation language, DSL for NeMo Guardrails  
**NeMo Guardrails** - LLM orchestration framework  
**@action** - Decorator that registers Python functions for Colang  
**flow** - Named conversation sequence in Colang  
**$variable** - State variable in Colang  
**await** - Waits for flow or action to complete, captures return value  
**bot say** - Send message to user  
**user said something** - Capture next user input  
**when/or when/else** - Conditional branching in Colang  

---

## Contacts & References

**GitHub:** nvidia/NeMo-Guardrails ([docs](https://github.com/NVIDIA/NeMo-Guardrails))  
**Colang Spec:** In `COLANG_2_0_COMPLETE_SPECIFICATION.md`  
**Project Owner:** @gonzalez (TomJust on GitHub)  

---

**Last Updated:** February 24, 2026, 7:30 PM  
**Next AI Session:** [Date TBD]  
**Status:** Ready to continue Phase 3 after Gemini fix

