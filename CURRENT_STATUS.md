# Project Nautilus: Current Status

**Last Updated:** February 23, 2026, 14:00 UTC  
**Phase:** PRE-PHASE 1 (Foundation setup)  
**Overall Progress:** 25% (diagnostic tools built, not yet tested)

---

## WHAT'S DONE ✅

### Diagnostic Infrastructure
- [x] Structured logging system (`logging/logger.py`)
- [x] VS Code debugger config (`.vscode/launch.json`, `.tasks.json`)
- [x] Requirements files updated (`requirements.txt`, `requirements-dev.txt`)
- [x] Environment template (`.env.example`)
- [x] Pytest configuration (`tests/conftest.py`)
- [x] Test directory structure created
- [x] Master validator (`tools/validate_all.py`)
- [x] Session inspector (`tools/inspect_session.py`)
- [x] Example unit tests (`tests/test_unit/test_yaml_loading.py`)
- [x] Debugging guide (`docs/DEBUGGING_GUIDE.md`)
- [x] Tools summary (`docs/TOOLS_SUMMARY.md`)
- [x] This plan (`PROJECT_PLAN.md`)

**Total files created:** 19  
**Total files modified:** 3

### Existing (from previous work)
- [x] Flask app structure (`app.py`)
- [x] YAML rules (global, beginner, intermediate, pro)
- [x] Diagnostic maps (`data/diagnostic_maps.yaml`)
- [x] Discovery script (`logic/discovery_script.py`)
- [x] Manager/RuleEngine (`logic/manager.py`) - **broken state management, being replaced**
- [x] HTML/CSS chat UI (`index.html`)

---

## WHAT'S PENDING 🟡

### PHASE 1: Foundation Verification (TODO)
- [ ] Install packages via `pip install -r requirements.txt`
- [ ] Install dev packages via `pip install -r requirements-dev.txt`
- [ ] Copy `.env.example` to `.env` and add OpenAI key
- [ ] Run `python tools/validate_all.py` → verify all checks pass
- [ ] Run `pytest tests/ -v` → verify tests run and pass
- [ ] Create manual test log entry and inspect with `inspect_session.py`
- **Blocker:** User must complete these steps before proceeding

### PHASE 2: NeMo Setup (TODO)
- [ ] Verify NeMo Guardrails installs correctly
- [ ] Create NeMo config directory structure
- [ ] Write minimal "hello world" Colang flow
- [ ] Create Flask endpoint that calls NeMo flow
- [ ] Test: Make request to endpoint, get response
- [ ] Verify logs capture NeMo events

### PHASE 3-5: Core Development (TODO)
- [ ] Discovery flow (machine/skill extraction)
- [ ] Playfield confirmation flow
- [ ] Symptom extraction flow
- [ ] Evidence collection flow
- [ ] Diagnostic output flow
- [ ] Safety gates implementation
- [ ] Integration tests
- [ ] Golden conversation corpus
- [ ] Deployment to Render

---

## WHAT'S BROKEN 🔴

### Current Issues (Being Fixed)
1. **State loss bug** in `logic/manager.py`
   - Problem: SessionState dict doesn't persist across turns
   - Cause: Python dict + manual state management
   - Status: **Will be replaced by NeMo** (not patched)
   - Impact: Symptom disappears mid-conversation, infinite loops

2. **Current app.py uses broken manager**
   - Problem: `chatgpt_integration.py` calls `NautilusManager.ask()` which has state issues
   - Status: Both files will be decommissioned when NeMo replaces them
   - Impact: App currently doesn't work end-to-end

3. **No NeMo flows exist yet**
   - Problem: `config/rails/` only has `safety.co` skeleton
   - Status: Building in Phase 2-3
   - Impact: Can't test full diagnostic flow yet

---

## DEPENDENCIES

### External
- [x] Python 3.11+ (assumed installed)
- [x] VS Code (assumed installed)
- [x] Git (assumed installed)
- [ ] pip packages (needs `pip install -r requirements.txt`)
- [ ] OpenAI API key (user must add to `.env`)

### Internal
- [x] YAML rules files (exist, validated)
- [x] Diagnostic maps (exist, validated)
- [ ] NeMo/Colang (installed but not configured)
- [ ] Flask (installed, minimal setup exists)

---

## BLOCKERS

**None currently.** Ready to proceed to Phase 1.

---

## NEXT IMMEDIATE ACTIONS

**For User:**
1. Copy `.env.example` to `.env`
2. Edit `.env`, add your OpenAI API key
3. Run these commands:
   ```powershell
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   python tools/validate_all.py
   pytest tests/ -v
   ```
4. Report results (pass/fail on each)

**For AI (after user confirms Phase 1 complete):**
1. Create NeMo config structure
2. Write hello world flow
3. Integrate Flask + NeMo
4. Move to Phase 2

---

## DECISION LOG

| Date | Decision | Rationale | Status |
|------|----------|-----------|--------|
| Feb 23 | Use NeMo as brain | Python state management failed | DECIDED |
| Feb 23 | Build diagnostic tools first | Can't debug what you can't see | IN PROGRESS |
| Feb 23 | No hardcoded machine library | LLM/A2A handles it better | DECIDED |
| Feb 23 | Phase-based development | Reduces risk of building wrong thing | PLANNED |

---

## TEAM NOTES

### What Changed Since Last Session
- **Ditched Python-only architecture** - Too fragile for state management
- **Adopted NeMo fully** - Proper tool for conversation flows
- **Built diagnostic infrastructure first** - No more flying blind
- **Explicit phases** - Clear milestones, testable at each step

### Key Insight
The broken state management wasn't a bug—it was the inevitable result of choosing Python dicts over a conversation engine designed for this. NeMo fixes the root cause, not the symptom.

### Confidence Level
**HIGH** - Architecture is sound, diagnostic tools are in place, path forward is clear.

---

## METRICS TO TRACK

- [ ] Phase 1: All validators pass
- [ ] Phase 2: NeMo hello world works
- [ ] Phase 3: Full conversation end-to-end
- [ ] Phase 4: 100% golden test pass
- [ ] Phase 5: Public URL accessible

---

## COMMUNICATION

This document gets updated:
- After each phase completes
- When blockers arise
- When decisions change
- Before/after major work sessions

Commit to git with: `git add CURRENT_STATUS.md && git commit -m "Update status after Phase X"`

---

**Last verified working:** Diagnostic tools created but not yet tested  
**Last verified broken:** app.py (depends on broken manager.py)  
**Status confidence:** Phase 1 should be straightforward, Phase 2-3 have some unknowns with NeMo integration
