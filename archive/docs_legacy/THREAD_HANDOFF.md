# Project Nautilus: Thread Handoff & Assistant Rules

**Last Updated:** March 4, 2026  
**Status:** ACTIVE - READ THIS FIRST IN EVERY SESSION

---

## PART 1: MANDATORY ASSISTANT RULES

### Core Principles

1. **Act as a Professional Developer, Architect, and Engineer**
   - Approach all work with professional-grade standards
   - Consider long-term maintainability and scalability
   - Follow established software engineering best practices

2. **99% Certainty Rule**
   - Be 99% certain that what you're doing is correct before implementing
   - If uncertain, ask questions first
   - Don't guess or assume - verify with the user

3. **No Cutting Corners**
   - Implement complete, production-quality solutions
   - Don't skip steps or take shortcuts
   - If time/complexity is an issue, discuss trade-offs explicitly

4. **Don't Make Things Up Without Permission**
   - Don't invent features, patterns, or changes on your own
   - Stay within the scope of defined requirements
   - When suggesting improvements, clearly mark them as suggestions

5. **NEVER Rewrite or Change Architecture Without Explicit Permission**
   - The existing architecture (PROJECT_PLAN.md, ARCHITECTURE.md) is king
   - Follow the documented phases and structure
   - If you see architectural issues, flag them for discussion - don't "fix" them
   - Changes to core design require user approval

6. **NO SUMMARIZATIONS - READ LINE-BY-LINE FOR RULES & CRITICAL DOCS** ⚠️ CRITICAL
   - When reading rule files (global.yaml, beginner.yaml, intermediate.yaml, pro.yaml): **READ EVERY LINE**
   - When understanding requirements: **NO quick summaries, READ ACTUAL CONTENT**
   - When implementing from NeMo rules: **REFER BACK TO EXACT LINES**, not paraphrases
   - This prevents misunderstandings, misimplementations, and missed edge cases
   - Applies to: YAML rules, ARCHITECTURE.md, PROJECT_PLAN.md, SYSTEM_INSTRUCTIONS.md
   - When you reference a rule, cite the exact line/field, not your interpretation

### Working Protocol

- **When uncertain:** Ask questions before proceeding
- **Before major changes:** Get explicit confirmation
- **When suggesting improvements:** Clearly separate suggestions from requirements
- **During implementation:** Follow the documented plan exactly
- **If plan seems wrong:** Discuss, don't deviate

---

## PART 2: WORKFLOW GUIDELINES

### Response Style
- Always provide step-by-step instructions, assuming no prior knowledge
- Avoid assumptions; clarify every step and option
- Use plain language and avoid jargon unless requested
- Explain actions before making changes

### Workflow Preferences
- Prioritize automation and low-friction solutions, but allow for manual review when needed
- **Pause before making code changes unless explicitly approved**
- Offer both automated and manual options
- Document all changes and provide clear instructions for review

### Planning Philosophy
- **Approach like a cabinet maker:** Review the entire job, study all plans and elevations, visualize the finished product BEFORE starting
- Ensure every step is planned and fits into the overall workflow
- **Never skip details or move forward without understanding the full scope**
- Prioritize methodical, start-to-finish execution with clear checkpoints

### Troubleshooting
- If a process is complex or error-prone, break it into small, actionable steps
- If the user expresses frustration, slow down and offer alternatives
- Always offer to summarize goals, next steps, and rules for handoff

### Communication
- Confirm user intent before proceeding with major changes
- Ask for explicit approval before implementing new features or workflows
- Offer to create or update documentation files for rules, goals, and preferences

---

## PART 3: PROJECT ARCHITECTURE (Key Reference)

**Project Type:** Deterministic diagnostic engine for hardware troubleshooting  
**Core Stack:** NeMo Guardrails (Colang) + Python utilities + YAML rules + Flask

### System Components

#### Brain: NeMo Guardrails (Colang)
- **Location:** `config/rails/*.co` files
- **Purpose:** Conversation orchestrator, state machine, flow routing
- **State Variables:** `$machine_name`, `$manufacturer`, `$era`, `$skill_level`, `$symptom`, `$confidence`, `$evidence`
- **Key Flows:** discovery.co, playfield.co, symptom.co, evidence.co, diagnostic.co, safety.co
- **Files Used:** hello_world.co → defines `flow main` (entry point)

#### Toolbox: Python Utilities
- **Location:** `logic/` directory
- **Purpose:** Fuzzy matching, YAML parsing, API calls, validation
- **Key Functions:** FuzzyMatchMachineAction, ValidateSkillLevelAction, FuzzyMatchSymptomAction, GenerateDiagnosticStepsAction

#### Rules Engine: YAML Files
- **Location:** `rules/` and `data/` directories
- **Files:**
  - `global.yaml` - Universal rules (STF philosophy, identity gate, session opening, disclaimers)
  - `beginner.yaml` - Skill level 1-2 (playfield access gate, safety interrupts, output states)
  - `intermediate.yaml` - Skill level 3-5 (baseline assumptions, practical tone)
  - `pro.yaml` - Skill level 6-10 (technical tone, high detail) ⚠️ INCOMPLETE - missing disclaimer section
  - `diagnostic_maps.yaml` - Symptom STF structures (917 lines, 19+ symptoms)

#### Configuration
- **`config.yml`** - NeMo configuration (lists dialog flows) ⚠️ BUG: Lists `- hello_world` but should be `- main`
- **`config/rails/actions.py`** - Custom @action decorators for NeMo

---

## PART 4: PROJECT LAYOUT

```
project_nautilus/
├── app.py                          # Flask server entry point
├── config/
│   ├── config.yml                  # NeMo configuration
│   └── rails/
│       ├── *.co files              # Colang conversation flows
│       ├── config.yml              # Flow definitions
│       └── actions.py              # Custom @action decorators
├── logic/
│   ├── __init__.py
│   ├── discovery_helper.py         # Machine/skill matching
│   ├── guardrails.py               # NeMo initialization
│   ├── manager.py                  # Rule loading
│   └── nautilus_core.py            # Core engine
├── rules/
│   ├── global.yaml                 # Universal rules
│   ├── beginner.yaml               # Skill level 1-2
│   ├── intermediate.yaml           # Skill level 3-5
│   └── pro.yaml                    # Skill level 6-10
├── data/
│   ├── diagnostic_maps.yaml        # Symptom definitions
│   ├── machine_library.json        # Machine database
│   └── manuals/                    # PDF documentation
├── ARCHITECTURE.md                 # System design (675 lines)
├── PROJECT_PLAN.md                 # Development phases
├── AI_GROUND_RULES.md              # Mandatory assistant rules
├── assistant_guidelines.md         # Workflow preferences
└── THREAD_HANDOFF.md               # This file

```

---

## PART 5: RULES DOCUMENTS (What You Must Follow)

### Global Rules (universal, all skill levels)
**File:** `rules/global.yaml`

**Key Gates:**
- **0C.R19:** Coin door access ONLY for interlock, service buttons, lockdown bar release
- **0C.R20:** Power button locations - NEVER GUESS
- **0C.S1:** High-voltage warning for anything over 50V
- **0C.S2:** Always verify ground strap before board-level testing
- **0C.R13:** Mandate full PDF access, provide IPDB links
- **0C.R1:** No emojis, standard text only

**Identity Gate:** REQUIRED fields = machine_title, manufacturer, era, skill_level. If missing, STOP.

**Session Opening:** "Great, I can help with that." + request machine info

**Disclaimer:** Project Nautilus cannot supply/store/distribute manuals (copyright). Users must download from IPDB.org. Uploaded manuals are session-only and discarded.

### Beginner Rules (skill level 1-2)
**File:** `rules/beginner.yaml`

**Safety Interrupt Triggers:** "transformer", "high voltage", "wall outlet", "soldering"  
**Safety Warning:** "[PO GLOBAL]: Safety Interrupt (0C.S1). High voltage risk. As a beginner, please STOP and unplug the machine before proceeding."

**Playfield Access Question:** "Do you know how to remove the glass and raise the playfield?"

**action_safety_guard:** Do NOT recommend when electrical risk is non-trivial, physical damage likely, or evidence weak. CAN explain theory, state unlocking evidence, outline technician steps.

**location_gate:** Before giving specific connector/fuse/test-point IDs, ask for manual page OR board photo (max 4 lines, don't include specific locations in the request).

**version_confirmation:** Confirm machine title/era/board ID before relying on pinouts.

**social_pressure_resistance:** If user says "just give the answer", respond with why confidence isn't possible, minimum required info, prioritize accuracy and safety.

### Intermediate Rules (skill level 3-5)
**File:** `rules/intermediate.yaml`

**Same gates as beginner** but:
- Tone: "Practical and Direct" (not "Encouraging but Cautious")
- Detail level: "Medium-High" (not "Medium")
- Baseline assumption: "When users ask questions, assume they have already performed obvious basic checks unless they say otherwise"

### Pro Rules (skill level 6-10)
**File:** `rules/pro.yaml`

**Same gates as beginner/intermediate** but:
- Tone: "Technical"
- Detail level: "High"
- **⚠️ BUG:** Missing full disclaimer section (only has disclaimer_triggers, not actual text)
- **⚠️ BUG:** Missing output_states, action_safety_guard, location_gate, version_confirmation, social_pressure_resistance sections

---

## PART 6: HOW TO RUN THE PROJECT

### Prerequisites
```powershell
# Python 3.11+
python --version

# Check virtual environment(s)
.\venv\Scripts\Activate.ps1
pip list | findstr nemo  # Check NeMo Guardrails installed
```

### Start the Server
```powershell
# From project root
python app.py
# Server runs on http://localhost:5000
```

### Run Tests
```powershell
pytest tests/ -v                    # All tests
pytest tests/test_unit/ -v         # Unit tests only
pytest tests/test_integration/ -v  # Integration tests only
```

### Validate Rules
```powershell
python tools/validate_all.py       # Validate YAML/JSON files
python tools/inspect_session.py    # Inspect conversation state
python tools/replay_conversation.py # Replay a past session
```

---

## PART 7: CURRENT KNOWN ISSUES

### Critical Bugs
1. **config.yml Entry Point Mismatch**
   - `config.yml` lists flows `- hello_world` but `hello_world.co` defines `flow main`
   - NeMo cannot find `hello_world` flow, falls back to generic LLM
   - **Fix:** Change config.yml to `- main`

2. **Missing Flow Implementations**
   - Designed in PROJECT_PLAN.md but not implemented:
     - `playfield.co` (mandatory beginner safety gate)
     - `evidence.co` (confidence building before diagnosis)
   - Sequence is currently: discovery → symptom → diagnosis
   - Should be: discovery → playfield (beginner only) → symptom → evidence → diagnosis

3. **LLM Response Instead of Structured Diagnosis**
   - `GenerateDiagnosticStepsAction` calls LLM with generic prompt
   - Should instead query `diagnostic_maps.yaml` for STF structure
   - User gets entertainment trivia instead of troubleshooting steps

4. **pro.yaml Is Incomplete**
   - Missing: disclaimers section (has disclaimer_triggers but no content)
   - Missing: output_states, action_safety_guard, location_gate, version_confirmation, social_pressure_resistance

### Deployment Status
- ✅ Render.com deployment successful
- ✅ NeMo Guardrails loading
- ✅ All 8 custom actions registered
- ✅ OpenAI API accessible
- ❌ Conversation flow broken (config issue + missing flows)
- ❌ Diagnostic output wrong (LLM instead of maps)

---

## PART 8: HOW TO HAND OFF TO NEXT THREAD

Include in conversation summary:
1. What you've completed (✅)
2. What's blocking progress (❌)
3. Current focus/next steps
4. Any user decisions still pending

**Critical for next thread:**
- Reference this THREAD_HANDOFF.md file
- Read AI_GROUND_RULES.md rule #6 first (no summarizations)
- Verify you read YAML files line-by-line, not summaries
- Check ARCHITECTURE.md for system design context
- Confirm current known issues section above

---

**Remember:** Rule #6 is not optional. Read the YAML files line-by-line. Don't summarize. Cite exact fields when you reference rules.

