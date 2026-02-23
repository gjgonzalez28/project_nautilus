# Project Nautilus: System Architecture

**Version:** 2.0 (NeMo Guardrails)  
**Last Updated:** February 23, 2026  
**Status:** Foundation Phase (Pre-Implementation)

---

## 1. Executive Summary

Project Nautilus is a **deterministic diagnostic engine** for hardware troubleshooting, powered by:

- **NeMo Guardrails (Colang)** as the conversation orchestrator (deterministic state machine)
- **Python utilities** as the toolbox (fuzzy matching, API calls, data validation)
- **Structured JSON logging** for complete diagnostic visibility
- **YAML-based rules** for symptoms, evidence, and safety gates

**Key Innovation:** NeMo maintains conversation state (`$machine_name`, `$symptom`, `$confidence`, `$evidence`) across turns, eliminating the state-loss bugs that plagued the Python-only approach.

---

## 2. Architecture Model: Brain + Toolbox

```
┌─────────────────────────────────────┐
│  User Input (Text/Conversation)     │
└────────────────┬────────────────────┘
                 │
         ┌───────▼────────┐
         │  Flask Server  │ (http://localhost:5000)
         └────────┬───────┘
                  │
      ┌───────────▼──────────────┐
      │   NeMo Guardrails        │ ◄─── THE BRAIN
      │   (Colang Orchestrator)  │      - State machine
      │                          │      - Flow routing
      │  $machine_name           │      - Intent recognition
      │  $symptom               │      - Gate evaluation
      │  $confidence            │      - Response generation
      │  $evidence              │
      └───┬──────────────────────┘
          │
    ┌─────┼─────────────────────────────┐
    │     │                             │
    ▼     ▼                             ▼
┌────────────────┐         ┌──────────────────┐
│  Python Utils  │         │  ChatGPT API     │
│  (Toolbox)     │         │  (Diagnosis)     │
│                │         │                  │
│ • Fuzzy match  │         │ • Generate STF   │
│ • Rules load   │         │ • Explain steps  │
│ • Confidence   │         │ • Answer qs      │
│ • YAML parse   │         │                  │
│ • JSON valid   │         │                  │
└────┬───────────┘         └──────┬───────────┘
     │                            │
     └──────────────┬─────────────┘
                    │
        ┌───────────▼──────────┐
        │  StructuredLogger    │ (logs/)
        │  JSON Events         │
        │  (Trace Correlation) │
        └──────────────────────┘
```

---

## 3. Core Components

### 3.1 NeMo Guardrails (Colang) — The Brain

**Location:** `config/rails/`

Colang flows handle:
1. **Discovery Flow** (`discovery.co`) - Machine/skill identification
2. **Playfield Flow** (`playfield.co`) - Access confirmation
3. **Symptom Flow** (`symptom.co`) - Symptom extraction + fuzzy matching
4. **Evidence Flow** (`evidence.co`) - Evidence gathering per symptom
5. **Diagnostics Flow** (`diagnostics.co`) - STF diagnostic output
6. **Safety Flow** (`safety.co`) - Gate enforcement (0C.S1, 0C.R19, etc.)

**Why NeMo?**
- ✅ Deterministic state machine (no random behavior)
- ✅ Built-in memory (`$variables`) persists across turns
- ✅ Intent recognition without hallucination
- ✅ Flow routing based on conditions, not guesses
- ✅ Easy to test and debug (structured inputs/outputs)

### 3.2 Python Utilities — The Toolbox

**Location:** `logic/`

Stateless functions called by Colang flows:

```python
# discovery.py - Machine/skill matching
def find_machine(user_input: str) -> tuple[str, float]
def find_skill(user_input: str) -> tuple[str, float]

# symptom_matcher.py - Fuzzy matching (levenshtein/difflib)
def fuzzy_match_symptom(input_text: str, confidence_threshold: float = 0.75) 
    -> tuple[str, float]

# evidence_scorer.py - Calculate confidence
def calculate_symptom_confidence(evidence: list[str]) -> float
def calculate_diagnosis_confidence(stf: dict) -> float

# yaml_loader.py - Load rules
def load_rules(filename: str) -> dict
def load_diagnostic_maps() -> dict

# validators.py - Pre-flight checks
def validate_yaml_files() -> bool
def validate_json_files() -> bool
def validate_python_imports() -> bool
def validate_required_files() -> bool
```

**Why Python?**
- ✅ Fuzzy matching libraries (difflib, Levenshtein)
- ✅ YAML/JSON parsing (PyYAML, json)
- ✅ API calls (requests → ChatGPT)
- ✅ Data validation (type hints, assertions)
- ✅ Stateless = testable + deterministic

### 3.3 Structured Logging — The Diagnostic Recorder

**Location:** `logging/logger.py`

JSON event log with **trace IDs** for conversation correlation:

```json
{
  "timestamp": "2026-02-23T14:32:15.123456Z",
  "trace_id": "conv_abc123xyz789",
  "event_type": "state_change",
  "context": {
    "machine_name": "ThinkPad X1",
    "symptom": "Screen stays black",
    "confidence": 0.85,
    "evidence": ["Power LED off", "No fan noise"]
  },
  "message": "State machine advanced to symptom_evidence phase"
}
```

**Event Types:**
- `state_change` - Variable updated ($symptom, $confidence, etc.)
- `flow_transition` - Moved between Colang flows
- `gate_evaluation` - Safety rule checked (pass/fail)
- `intent_recognition` - User intent classified
- `python_boundary_call` - Called Python utility function
- `llm_call` - Called ChatGPT API

**Why JSON + Trace IDs?**
- ✅ Machine-readable (parse for debugging)
- ✅ Trace ID links all events from one conversation
- ✅ Timestamp enables timeline reconstruction
- ✅ Event types categorize for filtering

### 3.4 YAML Rules System

**Location:** `rules/`, `data/diagnostic_maps.yaml`

Four difficulty levels:

```
rules/
  ├── global.yaml           # All levels (safety gates, common skills)
  ├── beginner.yaml         # Level 1-2 (simple hardware checks)
  ├── intermediate.yaml     # Level 3-5 (BIOS, drivers)
  └── pro.yaml              # Level 6-10 (advanced: firmware, micro-code)

data/
  └── diagnostic_maps.yaml  # 19 symptoms, each with STF structure:
      └── Symptom:
          ├── evidence_checks: [...]
          ├── diagnostic_hypothesis: "..."
          ├── troubleshooting_steps: [...]
          └── safety_gates: ["0C.S1", ...]
```

---

## 4. Data Flow: Turn-by-Turn

```
┌─────────────────────────────────────┐
│ 1. User sends: "My screen is black" │
└────────────────┬────────────────────┘
                 │
         ┌───────▼──────────────┐
         │ Flask receives input │
         └────────┬─────────────┘
                  │
     ┌────────────▼────────────────┐
     │ NeMo Guardrails processes:  │
     │ 1. Parse text               │
     │ 2. Call intent recognizer   │
     │ 3. Evaluate flow conditions │
     │ 4. Route to symptom flow    │
     └──────┬─────────────────────┘
            │
    ┌───────▼────────────────────────┐
    │ Symptom Flow (Colang):         │
    │ 1. Extract symptom candidate   │
    │ 2. Call Python fuzzy_match()   │
    │    → "Screen stays black" (.92)│
    │ 3. Set $symptom = "Screen..." │
    │ 4. Set $confidence = 0.92      │
    │ 5. Ask: "Any LED indicators?"  │
    └──────┬──────────────────────────┘
           │
π──────────▼────────────────────────┐
    │ Evidence Flow (Colang):        │
    │ 1. Receive: "Power LED off"    │
    │ 2. Call Python score_evidence()│
    │    → $confidence = 0.95        │
    │ 3. Ask: "Any fan noise?"       │
    └──────┬───────────────────────────┘
           │
    ┌──────▼──────────────────────┐
    │ Gate Evaluation (Colang):    │
    │ Check: Is $confidence > 0.8? │
    │ Check: Is "Screen" safe?     │
    │ ✓ Pass → Continue            │
    │ ✗ Fail → Escalate            │
    └──────┬───────────────────────┘
           │
    ┌──────▼──────────────────────────┐
    │ Diagnostics Flow (Colang):      │
    │ 1. Call STF from diagnostic_maps│
    │ 2. Call ChatGPT API:            │
    │    "Generate repair steps for   │
    │     screen stays black with     │
    │     power LED off"              │
    │ 3. Receive response             │
    │ 4. Format with STF structure    │
    └──────┬──────────────────────────┘
           │
    ┌──────▼─────────────────────────────┐
    │ Logger (Parallel):                  │
    │ Log event_type=state_change         │
    │ Log event_type=flow_transition      │
    │ Log event_type=gate_evaluation      │
    │ Log event_type=llm_call             │
    │ All with same trace_id              │
    └──────┬──────────────────────────────┘
           │
    ┌──────▼────────────────────────┐
    │ Flask sends HTTP response:    │
    │ {                              │
    │   "response": "Power related...",
    │   "symptom": "Screen stays...",
    │   "confidence": 0.95,          │
    │   "steps": [...],              │
    │   "trace_id": "conv_abc123"    │
    │ }                              │
    └────────────────────────────────┘
```

---

## 5. File Structure & Responsibilities

```
project_nautilus/
│
├── 📁 config/                          # NeMo & runtime config
│   ├── config.yml                      # NeMo server settings
│   └── rails/                          # Colang flows (TBD)
│       ├── discovery.co                # Machine/skill ID (Phase 3)
│       ├── playfield.co                # Access gate (Phase 3)
│       ├── symptom.co                  # Symptom extraction (Phase 3)
│       ├── evidence.co                 # Evidence gathering (Phase 3)
│       ├── diagnostics.co              # STF output (Phase 3)
│       └── safety.co                   # Safety enforcement (Phase 3)
│
├── 📁 data/                            # Static data files
│   ├── diagnostic_maps.yaml            # 19 symptoms with STF
│   ├── machine_library.json            # A2A machine database
│   ├── manuals/                        # User manuals (future)
│   └── profiles/                       # User profiles (future)
│
├── 📁 logic/                           # Python utilities (toolbox)
│   ├── discovery_script.py             # Machine/skill matching
│   ├── manager.py                      # (DEPRECATED - being replaced)
│   ├── nautilus_core.py                # Core functions
│   ├── symptom_matcher.py              # Fuzzy matching (TBD)
│   ├── evidence_scorer.py              # Confidence calc (TBD)
│   ├── yaml_loader.py                  # Rules loader (TBD)
│   ├── validators.py                   # Pre-flight checks (TBD)
│   └── __pycache__/                    # Python cache (ignore)
│
├── 📁 logging/                         # Structured logging
│   ├── logger.py                       # StructuredLogger class
│   ├── __init__.py                     # Package init
│   └── (logs written to logs/ at runtime)
│
├── 📁 logs/                            # Runtime logs (empty at deploy)
│   └── (*.json files created by logger)
│
├── 📁 rules/                           # YAML difficulty levels
│   ├── global.yaml                     # All levels safety
│   ├── beginner.yaml                   # Level 1-2
│   ├── intermediate.yaml               # Level 3-5
│   └── pro.yaml                        # Level 6-10
│
├── 📁 guardrails/                      # Post-session helpers
│   └── post_session_module.py          # Safety review (Phase 4)
│
├── 📁 tests/                           # Test suite
│   ├── conftest.py                     # Pytest config & fixtures
│   ├── test_unit/                      # Unit tests
│   │   ├── test_yaml_loading.py
│   │   └── test_fuzzy_matching.py (TBD)
│   ├── test_integration/               # Integration tests
│   │   └── test_full_conversation.py (TBD)
│   └── test_safety/                    # Safety gate tests
│       └── test_gate_evaluation.py (TBD)
│
├── 📁 tools/                           # Development utilities
│   ├── validate_all.py                 # Pre-flight validator
│   └── inspect_session.py              # Log debugger
│
├── 📁 docs/                            # Documentation
│   ├── DEBUGGING_GUIDE.md              # How to debug
│   └── TOOLS_SUMMARY.md                # Tools reference
│
├── 📁 .vscode/                         # VS Code config
│   ├── launch.json                     # 5 debug profiles
│   └── tasks.json                      # 8 quick-run tasks
│
├── 📁 OLD_ARCHITECTURE.md              # Previous architecture (reference)
│
├── 🐍 app.py (TBD Phase 2)            # Flask entry point
├── 🐍 requirements.txt                 # Dependencies
├── 🐍 requirements-dev.txt             # Dev dependencies
├── .env.example                        # Environment template
├── .gitignore                          # Git ignore rules
├── README.md                           # Project overview
├── PROJECT_PLAN.md                     # 5-phase development plan
├── CURRENT_STATUS.md                   # Progress tracker
└── ARCHITECTURE.md                     # This file
```

---

## 6. Integration Points

### 6.1 Flask ↔ NeMo Guardrails

```python
# app.py (Phase 2)
from nemo_guardrails import LLMRails

@app.route('/diagnose', methods=['POST'])
def diagnose():
    user_input = request.json['message']
    conversation_id = request.json.get('trace_id', generate_trace_id())
    
    # Initialize NeMo session with trace_id context
    rails = LLMRails(
        config=NMConfig(...),
        context={'trace_id': conversation_id}
    )
    
    # Process through NeMo
    response, state = rails.generate(
        prompt=user_input,
        context_variables={'trace_id': conversation_id}
    )
    
    # Return with state context
    return {
        'response': response,
        'machine_name': state.get('$machine_name'),
        'symptom': state.get('$symptom'),
        'confidence': state.get('$confidence'),
        'trace_id': conversation_id
    }
```

**Flow:** HTTP request → Flask → NeMo instance → Python utils → ChatGPT → Response → Flask → HTTP response

### 6.2 NeMo ↔ Python Utilities (Colang Call)

```colang
# symptom.co
flow extract_symptom
    user_input = await get_user_message()
    
    # Call Python function
    result = await call_external_function(
        "fuzzy_match_symptom",
        user_input=user_input,
        threshold=0.75
    )
    
    symptom_name = result['symptom']
    confidence = result['confidence']
    
    $symptom = symptom_name
    $confidence = confidence
    
    await log_event(
        event_type="state_change",
        context={
            'symptom': symptom_name,
            'confidence': confidence
        }
    )
```

**Bridge:** Colang uses `call_external_function()` to invoke Python, gets result back, updates state.

### 6.3 Python ↔ ChatGPT API

```python
# logic/chatgpt_caller.py
import openai

def get_diagnostic_steps(symptom: str, evidence: list[str]) -> str:
    """Call ChatGPT for repair steps"""
    
    prompt = f"""
    Symptom: {symptom}
    Evidence: {', '.join(evidence)}
    
    Provide troubleshooting steps in STF format:
    - Situation: (describe problem)
    - Troubleshooting: (steps to diagnose)
    - Function: (expected outcome)
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
```

**Protocol:** Python calls OpenAI API → gets structured response → formats as STF → returns to Colang

---

## 7. State Machine: Conversation Flow

```
┌─────────────────────────────────────┐
│ [START] New Conversation            │
└────────┬────────────────────────────┘
         │
    ┌────▼──────────────────────┐
    │ DISCOVERY FLOW            │
    │ $machine_name = ?         │
    │ $skill_name = ?           │
    │ $playfield_ok = pending   │
    └────┬───────────────────────┘
         │
    ┌────▼──────────────────────┐
    │ PLAYFIELD FLOW            │
    │ User confirms access      │
    │ $playfield_ok = true      │
    └────┬───────────────────────┘
         │
    ┌────▼──────────────────────┐
    │ SYMPTOM FLOW              │
    │ $symptom = ?              │
    │ $confidence = initial     │
    └────┬───────────────────────┘
         │
    ┌────▼──────────────────────┐
    │ EVIDENCE FLOW             │
    │ Gather 2-3 evidence items │
    │ $confidence = refined     │
    │ $evidence = [...]         │
    └────┬───────────────────────┘
         │
    ┌────▼───────────────────────┐
    │ GATE EVALUATION            │
    │ Check: confidence > 0.80?  │
    │ Check: safety rules pass?  │
    └────┬──────────┬────────────┘
         │          │
    ✓ PASS       ✗ FAIL
         │          │
         │          └──────────────┐
         │                         │
    ┌────▼────────────────┐   ┌────▼──────────┐
    │ DIAGNOSTICS FLOW    │   │ ESCALATE FLOW │
    │ Generate STF:       │   │ Request human │
    │ • Situation         │   │ Override gate │
    │ • Troubleshooting   │   └────┬──────────┘
    │ • Function          │        │
    └────┬────────────────┘        │
         │◄───────────────────────┘
         │
    ┌────▼──────────────┐
    │ [END]              │
    │ Return diagnosis   │
    └────────────────────┘
```

---

## 8. Safety & Validation

### 8.1 Pre-Flight Validators (Phase 1)

```bash
python tools/validate_all.py
```

Checks:
- ✅ All YAML files parse correctly
- ✅ All JSON files parse correctly
- ✅ Python imports resolve
- ✅ Required data files exist
- ✅ NeMo configs valid

### 8.2 Safety Gates (Phase 3)

`safety.co` flow enforces rules:
- 0C.S1: Don't provide advice outside expertise
- 0C.R19: Confirm user understands risks
- 0C.XXX: (Additional gates per YAML rules)

### 8.3 Testing Strategy

**Unit Tests (Phase 1):**
```bash
pytest tests/test_unit/ -v
```
- YAML parsing
- JSON parsing
- Fuzzy matching accuracy
- Confidence calculations

**Integration Tests (Phase 4):**
```bash
pytest tests/test_integration/ -v
```
- Full conversation flows
- State persistence
- Gate enforcement
- Log correlation

**Safety Tests (Phase 4):**
```bash
pytest tests/test_safety/ -v
```
- Safety rules enforced
- No unsafe recommendations
- Evidence quality validated

---

## 9. Deployment Topology

### 9.1 Local Development

```
┌─────────────────────────────────────┐
│ VS Code                             │
│  ├── Flask debug server (port 5000) │
│  ├── NeMo server (port 8000)        │
│  └── Logs written to logs/          │
└─────────────────────────────────────┘
```

### 9.2 Testing (Render)

```
┌──────────────────────────────────────┐
│ Render                               │
│  ├── Flask app (https://url)         │
│  ├── NeMo Guardrails (embedded)      │
│  ├── Logs to /tmp/ (ephemeral)       │
│  └── Database: (future)              │
└──────────────────────────────────────┘
```

### 9.3 Production (Future)

```
┌──────────────────────────────────────┐
│ Target Platform (TBD)                │
│  ├── Load balancer                   │
│  ├── Flask replicas                  │
│  ├── NeMo Guardrails cluster         │
│  ├── PostgreSQL logs DB              │
│  └── Redis session cache (optional)  │
└──────────────────────────────────────┘
```

---

## 10. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Web Server** | Flask 2.3+ | HTTP API |
| **Conversation Engine** | NeMo Guardrails 0.11+ | State machine |
| **Conversation Language** | Colang | Flow definition |
| **LLM** | OpenAI GPT-4 | Diagnostics |
| **Rules Engine** | YAML + Python | Symptom/evidence config |
| **Fuzzy Matching** | difflib + Levenshtein | Symptom extraction |
| **Logging** | Python logging + JSON | Diagnostic recording |
| **Testing** | pytest + pytest-mock | Validation |
| **Environment** | Python 3.11+ | Language |
| **Version Control** | Git + GitHub | Collaboration |
| **IDE** | VS Code | Development |

---

## 11. Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **NeMo Guardrails, not pure Python** | State persists across turns; deterministic; built for conversations |
| **Colang for flows, Python for utilities** | Separation of concerns: orchestration vs. computation |
| **Structured JSON logging** | Machine-readable; traceable; auditable |
| **Trace IDs for correlation** | Reconstruct conversations; debug specific sessions |
| **YAML rules, not hardcoded** | Easy to modify difficulty levels, safety gates, symptoms |
| **ChatGPT for diagnostics** | LLM generates natural language steps; avoids hardcoding knowledge |
| **Fuzzy matching, not exact lookup** | Handles typos, synonyms; improves UX |
| **No machine library in code** | A2A/LLM handles it; reduces maintenance |

---

## 12. Known Limitations & Future Work

### Current Limitations
- No persistent session store (logs are ephemeral)
- No multi-language support yet (delegated to LLM)
- No offline mode (requires ChatGPT API)
- No analytics dashboard
- No user profiles (future)

### Future Enhancements (Post-MVP)
- Google Sheets integration (logging)
- Multi-language support (ChatGPT translate)
- Offline diagnostics (fallback rules)
- Analytics dashboard (Grafana)
- User profiles & history
- A2A machine library integration
- Mobile app/Progressive Web App

---

## 13. Glossary

| Term | Definition |
|------|-----------|
| **Colang** | NeMo's conversation language (defines flows) |
| **Flow** | Sequence of steps in Colang (e.g., discovery.co) |
| **Gate** | Safety rule that must pass before proceeding |
| **STF** | Situation-Troubleshooting-Function (diagnostic format) |
| **Trace ID** | Unique conversation identifier for log correlation |
| **$variable** | NeMo state variable (e.g., $symptom) |
| **Fuzzy Match** | Approximate string matching (handles typos) |
| **Confidence** | Probability that diagnosis is correct (0.0-1.0) |
| **Evidence** | Facts supporting a symptom diagnosis |
| **Playfield** | Domain the user is diagnosing (e.g., "Hardware") |

---

**For detailed implementation guides, see:**
- [PROJECT_PLAN.md](PROJECT_PLAN.md) — 5-phase development roadmap
- [CURRENT_STATUS.md](CURRENT_STATUS.md) — Progress tracker & blockers
- [docs/DEBUGGING_GUIDE.md](docs/DEBUGGING_GUIDE.md) — How to debug issues
- [docs/TOOLS_SUMMARY.md](docs/TOOLS_SUMMARY.md) — Developer tools reference
