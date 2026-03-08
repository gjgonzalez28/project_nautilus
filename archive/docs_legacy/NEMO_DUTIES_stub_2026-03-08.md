# NEMO DUTIES - Project Nautilus

Last updated: 2026-03-08
Status: Active specification
Purpose: Exact behavioral specification for NeMo Guardrails duties and response requirements.

## How to use this file
- Use this file when implementing or validating NeMo behavior.
- For rule-sensitive behavior, compare this file against the YAML source files.
- If this file conflicts with the YAML rule files, the YAML files are the final source of truth.
- Do not mix temporary bug notes into this file.
- Do not use this file as the current-task tracker.

## Source-of-truth order
1. Relevant YAML rule file
2. This file
3. Older handoff notes or session notes

## Duty status labels
- Documented = specified here but not yet confirmed in code
- Partial = some implementation exists but needs verification
- Implemented = working behavior exists in code and still needs regression testing
- Violated = code currently contradicts the rule

---

## Duty 1 - Identity Gate
Status: Documented
Mode: All

### Trigger
User asks any question about their machine before required identity details are gathered.

### Required response
Exact text:
```text
Great, I can help with that. Please tell me the title and manufacturer of your game, the model if appropriate, and your skill level.
```
