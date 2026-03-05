# Project Nautilus: Diagnostic Toolkit Summary

**Created:** February 23, 2026  
**Status:** Ready for use

---

## What's Been Set Up

### 1. Structured Logging Infrastructure ✅

**Location:** `logging/logger.py`

Provides:
- JSON-formatted logs for all events
- Trace ID correlation (follow a single conversation through all logs)
- Built-in log event types: state changes, flow transitions, gate evaluations, intent recognition, LLM calls

**Usage:**
```python
from logging.logger import get_logger, setup_logging

setup_logging(log_dir="logs", log_level="DEBUG")
logger = get_logger(__name__)

logger.log_state_change("symptom", None, "left_flipper_dead", "user input")
logger.log_flow_transition("discovery", "symptoms", "user identified")
```

Logs written to: `logs/nautilus-YYYY-MM-DD.log`

---

### 2. VS Code Debugger Configuration ✅

**Location:** `.vscode/launch.json`, `.vscode/tasks.json`

Pre-configured debug profiles:
- **Python: Flask App** - Debug the web server
- **Python: Current File** - Debug any Python file
- **Python: Run Tests** - Debug pytest tests
- **Python: Interactive CLI** - Debug main.py

Quick tasks in VS Code task runner:
- Run Flask Server
- Run Tests (All / Unit / Integration)
- Validate All Data
- Inspect Session
- Replay Conversation

**How to use:**
1. Press `Ctrl+Shift+D` to open debugger
2. Select a profile and press F5
3. Click code margin to set breakpoints
4. F10 to step, F11 to step into, F6 to continue

---

### 3. Python Package Management ✅

**Files:**
- `requirements.txt` - Core dependencies
- `requirements-dev.txt` - Development-only (pytest, etc.)
- `.env.example` - Environment variables template

**Install:**
```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Packages added:**
- `nemo-guardrails` - NeMo/Colang engine
- `python-dotenv` - Environment variable loading
- `openai` - LLM API
- `pytest`, `pytest-cov` - Testing framework

---

### 4. Testing Framework ✅

**Location:** `tests/` directory

Structure:
```
tests/
  ├── conftest.py              # Pytest configuration & shared fixtures
  ├── test_unit/               # Unit tests (fast, isolated)
  ├── test_integration/        # Integration tests (full workflows)
  ├── test_safety/             # Safety constraint tests
  └── conversations/           # Golden test conversations (JSON)
```

**Example tests created:**
- `test_unit/test_yaml_loading.py` - Tests YAML files load correctly

**Run tests:**
```powershell
pytest tests/ -v                    # All tests
pytest tests/test_unit/ -v          # Just unit tests
pytest tests/test_safety/ -v        # Just safety tests
pytest tests/ --cov=logic --cov-report=html  # With coverage report
```

---

### 5. Diagnostic Tools (Validators & Inspectors) ✅

**Location:** `tools/` directory

**Baseline Validators (Complete Toolkit)**

**Tool 1: `validate_all.py`** - Master Validator
```powershell
python tools/validate_all.py
```
Checks:
- All YAML files parse (rules/*.yaml)
- All JSON files parse (data/*.json)
- Required files exist
- Python modules import correctly

**Tool 2: `validate_colang_flows.py`** - Colang Flow Validator ✅ NEW
```powershell
python tools/validate_colang_flows.py [--verbose]
```
Checks:
- All .co files syntax
- Flow definitions exist
- Action references valid
- config.yml flow references
- Emoji violations (DUTY #15)
- Unmatched parentheses

**Tool 3: `validate_machine_library.py`** - Machine Data Validator ✅ NEW
```powershell
python tools/validate_machine_library.py [--verbose]
```
Checks:
- machine_library.json structure
- Required fields (id, name, era, manufacturer)
- Duplicate IDs
- Valid era values
- Symptom data quality
- STF diagnosis sections

**Tool 4: `validate_diagnostic_maps.py`** - Diagnostic Maps Validator ✅ NEW
```powershell
python tools/validate_diagnostic_maps.py [--verbose]
```
Checks:
- diagnostic_maps.yaml structure
- Complete STF sections (STRAIGHT/TRUE/FLUSH)
- Check items (id, area, action)
- Branch definitions
- Data completeness

**Tool 5: `validate_config.py`** - NeMo Config Validator ✅ NEW
```powershell
python tools/validate_config.py [--verbose]
```
Checks:
- config.yml structure
- Model configuration (engine, model, api_key)
- Rails section (flows defined)
- Flow references exist
- Instructions section
- Environment variable usage

**Session Inspector**

**Tool 6: `inspect_session.py`** - Session Log Inspector
```powershell
python tools/inspect_session.py --latest              # Show latest conversation
python tools/inspect_session.py --trace-id conv_xxx   # Show specific conversation
```
Shows:
- All state changes in order
- Flow transitions
- Gate evaluations
- Intent recognitions

Helps debug: Why did the symptom disappear? Why didn't the gate work? What did the user say?

**Future Tools (Not Yet Built):**
- `replay_conversation.py` - Replay a conversation step-by-step
- `analyze_colang_flows.py` - Visualize flow graphs

---

### 6. Documentation ✅

**Location:** `docs/` directory

**File: `DEBUGGING_GUIDE.md`**
Explains:
- How to use all diagnostic tools
- How to understand log events
- Common issues & solutions
- How to write tests
- VS Code debugging tips

---

## What You Need to Do Now

### Step 1: Install Packages
```powershell
cd c:\Users\Gonzalez Family\Documents\project_nautilus
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Step 2: Copy .env File
```powershell
copy .env.example .env
# Edit .env and add your OpenAI API key
```

### Step 3: Run Validation
```powershell
python tools/validate_all.py
```
Should show all checks passing. If any fail, fix them before proceeding.

### Step 4: Run Tests
```powershell
pytest tests/ -v
```
Should see test_yaml_loading.py tests pass.

### Step 5: Try a Tool

Start Flask:
```powershell
python app.py
```

Have a conversation in the UI. Then inspect it:
```powershell
python tools/inspect_session.py --latest
```

You should see formatted output showing all events from the conversation.

---

## What's NOT Built Yet

These will be built once we have the NeMo architecture working:

- [ ] Complete validation tools (diagnostic maps, Colang flows)
- [ ] Conversation replay tool with breakpoints
- [ ] Flow graph visualization
- [ ] Integration tests (full conversation flows)
- [ ] Safety constraint tests
- [ ] Debug API endpoints (/debug/state, /debug/trace)
- [ ] Golden conversation corpus (test conversations)

---

## File Checklist

✅ `logging/logger.py` - Structured logging engine
✅ `logging/__init__.py` - Package initialization
✅ `.vscode/launch.json` - Debugger config
✅ `.vscode/tasks.json` - Quick tasks
✅ `requirements.txt` - Updated with all packages
✅ `requirements-dev.txt` - Dev packages
✅ `.env.example` - Environment template
✅ `tests/conftest.py` - Pytest configuration
✅ `tests/__init__.py` - Test package
✅ `tests/test_unit/__init__.py`
✅ `tests/test_integration/__init__.py`
✅ `tests/test_safety/__init__.py`
✅ `tests/test_unit/test_yaml_loading.py` - Example tests
✅ `tools/validate_all.py` - Master validator
✅ `tools/inspect_session.py` - Session inspector
✅ `docs/DEBUGGING_GUIDE.md` - Debugging documentation

**Total: 16 files created, 3 files updated**

---

## Next Phase

Once you confirm everything works:

1. Start building NeMo flows (`.co` files in `config/rails/`)
2. Add logging calls throughout NeMo flows
3. Write integration tests for full conversations
4. Build remaining diagnostic tools
5. Deploy and monitor

---

**You now have enterprise-grade diagnostic tools. No more flying blind.**
