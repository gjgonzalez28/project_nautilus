# Project Nautilus: Master Development Plan

**Version:** 1.0  
**Created:** February 23, 2026  
**Status:** ACTIVE DEVELOPMENT  
**Owner:** Gonzalez Family

---

## VISION

Build a pinball diagnostic assistant that:
- Guides hobbyists safely through troubleshooting
- Uses NeMo Guardrails as the conversation brain (deterministic, not ChatGPT guessing)
- Provides STF-based diagnostics (Straight/True/Flush progression)
- Supports beginner, intermediate, pro skill levels
- Works in any language (LLM handles translation)
- Identifies machines and problems via LLM/A2A (not hardcoded database)
- Never loses state, never loops infinitely, never violates safety rules

---

## SUCCESS CRITERIA

**For MVP (March 31, 2026):**
- ✅ User can describe their machine and problem
- ✅ System provides diagnostic steps without losing state
- ✅ No infinite loops (playfield question, symptom loss, etc.)
- ✅ Safety gates work (never suggest unsafe actions to beginners)
- ✅ Confidence gates work (ask for evidence when unsure)
- ✅ Can deploy to Render and access publicly
- ✅ Logs show exactly what happened in any conversation
- ✅ Can replay conversations to debug issues

**For Production (TBD):**
- Multi-language support verified
- Golden test suite passes (100 conversations work correctly)
- Performance acceptable (<2s response time)
- Monitoring/alerting set up on Render
- Google Sheets integration for trend analysis

---

## ARCHITECTURE DECISION: NeMo Brain

### Why NeMo (Not Pure Python)

**Python failed because:**
- SessionState dict loses state between RuleEngine turns
- ChatGPT + imperative Python = no guaranteed flow
- State management bug caused infinite loops

**NeMo solves this because:**
- Designed for multi-turn conversations with persistent state
- Variables ($machine_name, $symptom, etc.) don't get lost
- Flow transitions explicit, testable, deterministic
- Guards/gates block invalid paths programmatically
- Colang is a DSL built for conversation flows

**Architecture:**

```
NeMo (The Brain)
├─ Receives user input
├─ Recognizes intent
├─ Maintains state: $machine, $symptom, $confidence, $evidence
├─ Routes to correct flow (discovery → symptom → evidence → diagnosis)
├─ Calls Python utilities when needed
└─ Returns response

Python (The Toolbox)
├─ Load YAML rules
├─ Calculate confidence
├─ Call LLM for diagnosis
└─ Return results to NeMo
```

**Not doing:**
- Full machine library (A2A/LLM handles it)
- Hardcoded machine specs (LLM extracts from user description)
- Translation system (ChatGPT handles lang detection)

---

## DEVELOPMENT PHASES

### PHASE 1: Foundation & Verification (2-3 hours)

**Objectives:**
- Confirm diagnostic tools work
- Verify all data files are valid
- Prove testing framework runs
- Establish baseline logging

**Deliverables:**
1. Run `python tools/validate_all.py` → PASS ✅
2. Run `pytest tests/ -v` → All tests pass ✅
3. Create test log, inspect with `inspect_session.py` → Works ✅
4. All 3 completed without needing NeMo

**Success Criteria:**
- All validators pass
- Tests run and pass
- Logging works and is inspectable
- No NeMo errors (not needed yet)

**Dependencies:**
- Python 3.11+ installed
- pip install requirements.txt

**Risks:**
- Missing Python package → fix with pip
- YAML file syntax error → fix YAML

---

### PHASE 2: NeMo Setup & Hello World (1-2 hours)

**Objectives:**
- Install/configure NeMo properly
- Create simplest possible Colang flow
- Verify NeMo can execute flows
- Test logging captures NeMo events

**Deliverables:**
1. NeMo configuration directory structure
2. `config/rails/hello_world.co` - Minimal test flow
   ```
   define flow hello
     user say "Hello, what's your name?"
     user input message
     bot say "Your name is {message}"
   ```
3. Flask endpoint calls this flow
4. Make request, see response, check logs

**Success Criteria:**
- NeMo imports without error
- Hello world flow executes
- Response appears in Flask
- Event logged and visible with inspect_session.py

**Dependencies:**
- Phase 1 complete
- NeMo installed (pip install requirements.txt)

**Risks:**
- NeMo version incompatibility → test locally first
- Colang syntax error → consult NeMo docs
- LLM API issues → check OpenAI key in .env

---

### PHASE 3: Core NeMo Flows (4-6 hours)

**Objectives:**
- Build actual diagnostic flows
- Implement STF progression
- Add state persistence
- Instrument with logging

**Deliverables:**

1. **Discovery Flow** (`config/rails/discovery.co`)
   - User describes machine (natural language)
   - Extract: machine name, manufacturer, era
   - NeMo state: $machine_name, $manufacturer, $era
   - Proceed only when confident

2. **Playfield Gate Flow** (`config/rails/playfield.co`)
   - Ask: "Do you know how to remove glass and raise playfield?"
   - Handle: yes/no/clarification
   - If no: provide steps specific to manufacturer
   - NeMo state: $playfield_access_confirmed

3. **Symptom Extraction Flow** (`config/rails/symptom.co`)
   - Ask: "What's not working?"
   - User input: anything from "left flipper dead" to "all buttons stuck"
   - Call Python utility: fuzzy match to symptom_id
   - NeMo state: $current_symptom, $symptom_confidence

4. **Evidence Collection Flow** (`config/rails/evidence.co`)
   - Based on symptom, ask for evidence
   - Build evidence list one item at a time
   - Update confidence after each piece
   - NeMo state: $evidence_list, $confidence

5. **Diagnostic Output Flow** (`config/rails/diagnostics.co`)
   - Call Python utility: get diagnostic steps for symptom + confidence
   - Call LLM: generate explanation in user's skill level
   - Return STF steps (Straight, True, or True+Flush based on confidence)

6. **Safety Gates** (`config/rails/safety.co`)
   - Global safety rules from global.yaml
   - High voltage keywords → halt for beginners
   - Soldering/transformer work → halt for beginners
   - NeMo state: $safety_triggered

**Success Criteria:**
- All flows load without Colang syntax errors
- Can trace full conversation: machine → playfield → symptom → evidence → diagnosis
- State persists (symptom never disappears mid-flow)
- Logs show all transitions and state changes
- No infinite loops

**Dependencies:**
- Phase 2 complete
- diagnostic_maps.yaml loaded into Python utils
- LLM API working

**Risks:**
- Colang syntax complex → iterative debugging
- State not persisting → logging will reveal where
- LLM integration breaking → fallback to static responses

---

### PHASE 4: Testing & Integration (2-3 hours)

**Objectives:**
- Write integration tests
- Test with golden conversations
- Verify no state loss
- Verify gates work

**Deliverables:**

1. **Integration Tests** (`tests/test_integration/`)
   - Test: Happy path (machine → symptom → diagnosis)
   - Test: Typo recovery (misspelled machine name)
   - Test: Off-topic (user says something random, system redirects)
   - Test: Safety halt (beginner says soldering, system stops)
   - Test: Evidence gate (low confidence asked for evidence, high confidence proceeds)

2. **Golden Conversation Corpus** (`tests/conversations/`)
   - `happy_path.json` - Full successful diagnostic
   - `typo_recovery.json` - User misspells, recovers
   - `safety_halt.json` - Safety triggered, conversation ends
   - `evidence_gate.json` - Multiple evidence rounds before diagnostics

3. **Regression Test Suite** (`tests/test_integration/test_golden_conversations.py`)
   - For each golden conversation:
     - Replay it
     - Check: no infinite loops
     - Check: correct final diagnosis
     - Check: gates triggered at right time
     - Check: state never lost

**Success Criteria:**
- All integration tests pass
- No flakes (tests pass consistently)
- Golden conversation replay works
- Diagnostic tools capture every step
- Coverage: 90%+ of flow paths tested

**Dependencies:**
- Phase 3 complete
- Flows working end-to-end

**Risks:**
- Test data incomplete → build as you discover issues
- Flaky tests → improve test isolation

---

### PHASE 5: Deployment & Monitoring (TBD)

**Objectives:**
- Deploy to Render
- Set up monitoring
- Handle edge cases found in testing

**Deliverables:**
1. Render deployment working
2. Logs streaming to central location
3. Monitoring alerts set up
4. Rollback procedure documented

**Success Criteria:**
- Public URL working
- Conversations logged and inspectable
- Response times acceptable
- No crashes

---

## WHAT WE'RE NOT DOING (Scope Boundaries)

- ❌ Machine library (LLM/A2A provides this)
- ❌ Manual/schematic storage (users provide their own)
- ❌ Video tutorials (we guide to external resources)
- ❌ Real-time collab features (single-user conversations)
- ❌ Mobile app (web-only for MVP)
- ❌ Custom LLM fine-tuning (use base GPT-4)

---

## RISK MITIGATION

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| NeMo API changes | Low | High | Pin version, monitor releases |
| Infinite loops in Colang | Medium | High | Logging + inspect_session catches immediately |
| LLM latency too high | Low | Medium | Add caching, timeouts |
| State persistence fails | Low | High | Logging will show where, retest |
| Render deployment fails | Low | Medium | Keep local testing passing, rollback ready |

---

## TIMELINE ESTIMATES

| Phase | Scope | Est. Hours | Start | Target |
|-------|-------|-----------|-------|--------|
| 1 | Foundation | 2-3 | Feb 23 | Feb 23 |
| 2 | NeMo Setup | 1-2 | Feb 23 | Feb 24 |
| 3 | Core Flows | 4-6 | Feb 24 | Feb 25 |
| 4 | Testing | 2-3 | Feb 25 | Feb 26 |
| 5 | Deploy | TBD | Mar 1 | Mar 31 |

**Total (MVP): ~12-15 hours of focused work**

---

## SUCCESS = CONFIDENCE

When these are true, project is successful:

1. **You can describe a problem in your own words**, system understands it
2. **System never forgets what you symptoms, asks you again in same conversation**
3. **System provides safe guidance** (never suggests unsafe actions to beginners)
4. **You can debug any issue** by running `inspect_session.py` and seeing exact trace
5. **Tests pass consistently** (no flaky failures)
6. **You can deploy and users can access it** (Render URL works)

If any of these fail, project isn't done.

---

## FINAL NOTE

This plan is a commitment to doing it right. No band-aids, no corner-cutting, no guessing.

Every decision is documented here. Every phase is testable. Every risk is addressed.

If something breaks, we have tools to debug it. If something works, we have tests to prevent regression.

**The goal is a system you can trust.**
