# PROJECT NAUTILUS: CHATGPT TEST SCENARIOS
**Created:** February 19, 2026  
**Purpose:** Systematically test PD Pro across all three skill modes

---

## HOW TO USE IN CHATGPT

### **Setup Instructions**
1. Go to [ChatGPT](https://chatgpt.com)
2. Start a new conversation
3. Create a **Custom GPT** or use in regular chat with function calling enabled
4. Add functions from `chatgpt_integration.py` → `CHATGPT_FUNCTIONS`
5. Copy/paste the key instruction below

### **Key ChatGPT Instruction**
```
You are testing Project Nautilus (PD Pro), a pinball diagnostic system.
Use these functions to run test scenarios:
- initialize_nautilus_session(): Start new session
- nautilus_ask(user_message): Send message to Nautilus
- nautilus_set_test_mode(mode): Force beginner/intermediate/pro
- nautilus_get_session_state(): Check current state
- nautilus_end_session(): Generate compliance report
- nautilus_reset(): Start fresh

Run scenarios, check responses, note rule adjustments needed.
```

---

## TEST SCENARIO PACK 1: ELECTRICAL ISSUES

### **Scenario 1.1: Left Flipper Dead (All Modes)**
Testing: Symptom matching, confidence progression, mode-specific gating

**BEGINNER:**
```
Mode: beginner
Turn 1: "My left flipper isn't working at all. What do I check?"
       → Expected: Generic guidance, 32% confidence
Turn 2: "I tested the solenoid coil with my multimeter"
       → Expected: Evidence collected, confidence ~40%
Turn 3: "Should I replace the solenoid?"
       → Expected: CLARIFY action (needs 65% for beginner)
Turn 4: "The manual says coil should read 50 ohms but mine reads open"
       → Expected: Evidence added, confidence higher but still ~50-60%
```

**INTERMEDIATE:**
```
Mode: intermediate
[Same turns as beginner]
Turn 3: "Should I replace the solenoid?"
       → Expected: CLARIFY or STOP (needs 75% for intermediate - higher bar)
```

**PRO:**
```
Mode: pro
[Same turns as beginner]
Turn 3: "Should I replace the solenoid?"
       → Expected: DIAGNOSTIC (no gating, shows all details)
```

**What to Check:**
- [ ] Beginner threshold (65%) vs Intermediate (75%) working correctly
- [ ] Pro mode shows details without asking for confirmation
- [ ] Confidence score incrementing as evidence added
- [ ] Evidence "Observed" type detected properly

---

### **Scenario 1.2: High Voltage Safety (All Modes)**
Testing: Safety interrupt triggering, power-off warnings

**ALL MODES:**
```
Turn 1: "Solenoids aren't firing. What should I test?"
       → Expected: Includes safety warning about power-off
Turn 2: "I measured the solenoid voltage at 50V"
       → Expected: Safety interrupt message triggers, suggests turning power off first
```

**What to Check:**
- [ ] Safety warning triggers for "solenoid" keyword
- [ ] "Power off" language included in response
- [ ] Warning doesn't block diagnostic path unnecessarily

---

## TEST SCENARIO PACK 2: MECHANICAL ISSUES

### **Scenario 2.1: Bumpers Not Firing**
Testing: Symptom matching on less-obvious symptoms

**ALL MODES:**
```
Turn 1: "Bumpers aren't working. What could be wrong?"
       → Expected: Should match "bumpers_not_working" symptom
Turn 2: "I see the mechanical bumper moves when I press it by hand"
       → Expected: Observation captured
Turn 3: "Should I replace the coil?"
       → Beginner: CLARIFY | Intermediate: CLARIFY or CLARIFY | Pro: DIAGNOSTIC
```

**What to Check:**
- [ ] Symptom matching works for "bumpers"
- [ ] Physical observation counts as evidence (might not match keywords)
- [ ] Confidence increases appropriately

---

### **Scenario 2.2: Drop Targets Stuck**
Testing: Multi-step troubleshooting

**INTERMEDIATE:**
```
Turn 1: "Drop target is stuck in the down position. What do I do?"
       → Expected: Symptom matched, guidance on mechanical or solenoid issue
Turn 2: "I tried moving it by hand and it's stuck tight"
       → Expected: Evidence of physical obstruction
Turn 3: "Tried applying slight pressure but it won't move"
       → Expected: More evidence
Turn 4: "How do I fix it?"
       → Check confidence level and gate decision
```

**What to Check:**
- [ ] "Stuck" keyword triggers drop_target symptom or similar
- [ ] Physical evidence being captured
- [ ] Progression through evidence collection before recommending repair

---

## TEST SCENARIO PACK 3: DISPLAY ISSUES

### **Scenario 3.1: Backglass DMD Not Working**
Testing: Display-specific rules, electrical nature

**PRO:**
```
Turn 1: "DMD display is completely dark. No image at all."
       → Expected: Safety warning about DMD power, guidance on testing
Turn 2: "Checked the display ribbon cable, looks loose"
       → Expected: Physical evidence + electrical issue start
Turn 3: "Should I reseat the connector?"
       → Expected: Full diagnostic without gating (Pro mode)
```

**What to Check:**
- [ ] DMD triggers high-voltage safety warning
- [ ] Display-specific diagnostics shown
- [ ] Progression through checks (connector before replacement)

---

## TEST SCENARIO PACK 4: VAGUE/AMBIGUOUS INPUTS

### **Scenario 4.1: Unclear Problem Description**
Testing: Confidence gates protecting against bad recommendations

**BEGINNER:**
```
Turn 1: "Something's weird with my machine"
       → Expected: LOW confidence, asks for clarification
Turn 2: "I think some game mode isn't working?"
       → Expected: Still low confidence, more specific prompts
Turn 3: "Maybe the flippers are slow?"
       → Expected: Symptom detection on "flippers"/"slow", but confidence still building
Turn 4: "Should I fix it?"
       → Expected: STOP action (confidence <30%)
```

**What to Check:**
- [ ] Vague inputs don't trigger confident recommendations
- [ ] System asks for specific measurements before proceeding
- [ ] STOP gate activates when confidence critically low

---

### **Scenario 4.2: Expert User with Minimal Language**
Testing: Can detailed expert descriptions maintain confidence?

**PRO:**
```
Turn 1: "1k5 resistor blown on the power supply board, Q3 collector circuit"
       → Expected: Recognized as expert language, confidence should be high
Turn 2: "Need to order replacement 1k5 film resistor, 1/4W"
       → Expected: Professional language recognized, full diagnostic
```

**What to Check:**
- [ ] Expert technical language is recognized (even without "I measured")
- [ ] Confidence doesn't tank for technical input
- [ ] Pro mode trusts expert judgment

---

## RULES ADJUSTMENT CHECKLIST

After running scenarios, note issues:

### **Evidence Recognition**
- [ ] Keywords missing? (e.g., "checked", "looked at", "found")
- [ ] Should detect units? ("0V", "50 ohms", "open circuit")
- [ ] Physical observations being missed? ("stuck", "cracked", "loose")

### **Symptom Matching**
- [ ] Any symptom words not matching? (e.g., "slow" → "weak"?)
- [ ] Partial matches needed? (e.g., "bumper" including "bumpers"?)
- [ ] Case sensitivity issues?

### **Gate Thresholds**
- [ ] Beginner 65% too high/low? (Should allow safe guesses?)
- [ ] Intermediate 75% too strict? (Real techs get frustrated?)
- [ ] Pro truly needs no gating? (Any risky recommendations?)

### **Safety Warnings**
- [ ] Triggering too often? (Users ignore if too frequent)
- [ ] Not triggering enough? (Critical safety issue)
- [ ] Blocking diagnostics inappropriately?

### **Confidence Calculation**
- [ ] 40/40/20 weights balanced? (Too much weight on symptom? Evidence?)
- [ ] Saturation at 3 items correct? (Should accept more evidence?)
- [ ] Manual evidence (6 pts) vs Observed (10 pts) realistic?

---

## SAMPLE ISSUES TO DOCUMENT

Create a table if you find problems:

| Mode | Scenario | Issue | Suggested Fix |
|------|----------|-------|---------------|
| BEGINNER | Flipper scenario | Asks for clarification at 55% when user has good evidence | Adjust beginner threshold to 60%? |
| INTERMEDIATE | Vague input | Never reaches STOP gate, keeps asking | Lower confidence threshold for STOP gate? |
| PRO | Display issue | Mentions solenoid work but no power-off warning | Add display safety keywords to global rules |

---

## SUCCESS CRITERIA

System is ready to deploy when:
- [ ] All Beginner scenarios complete without needing higher confidence than 65%
- [ ] All Intermediate scenarios use 75% threshold as intended
- [ ] All Pro scenarios show detailed guidance without gates
- [ ] No false positives for safety warnings
- [ ] Clear evidence progression in each scenario
- [ ] No rules need adjustment (or document minimal changes)

---

## NOTES FOR THIS SESSION

**Start here:** Run Scenario 1.1 (Left Flipper) in all three modes first.  
**Then:** Run Scenario 4.1 (Vague input) to test confidence gating.  
**Finally:** Try scenarios that involve your own real pinball machines if possible.

**Save results:** After each mode test, note any rules adjustments needed in the "Issues" table above.

---

## QUICK REFERENCE: FUNCTION USAGE

```python
# In ChatGPT, use these exact function calls:

nautilus_reset()  # Fresh start
initialize_session()
nautilus_set_test_mode("beginner")  # or "intermediate", "pro"
nautilus_ask("Your message here")
nautilus_get_session_state()  # Check current state without new input
nautilus_end_session()  # Generate compliance report
```

---

## WHEN TO STOP TESTING

You can move to production when:
1. All three modes behave as expected
2. Confidence gates aren't blocking legitimate repairs
3. Safety warnings aren't too noisy or too quiet
4. Evidence collection captures the types of language real techs use
5. You're satisfied with rule adjustments (document any changes)

**Current status:** System feature-complete, ready for real-world testing via ChatGPT.
