# CURRENT TASK

Last updated: 2026-03-08
Status: ACTIVE
Priority: High

## Current objective
Fix the multi-turn conversation failure in Project Nautilus so turn 2 and later continue the same diagnostic session instead of looping back to the identity gate.

## Problem summary
Observed behavior:
- Turn 1 works.
- Turn 2+ regresses or loops back to the identity gate.
- Production testing on Render shows the session is not continuing correctly.
- The likely issue is broken session persistence or incorrect NeMo conversation state handling across HTTP requests.

## Why this matters
This bug blocks the core product goal because Nautilus must function as a reliable multi-turn diagnostic assistant. If state does not persist, NeMo cannot safely orchestrate symptom gathering, evidence gathering, or mode-aware diagnostics.

## Current hypothesis
Most likely root causes:
- A new NeMo or LLMRails instance is being created per request without restoring prior session state.
- Conversation history, event history, or state variables are not being persisted outside the request lifecycle.
- The app may be using single-turn request patterns where multi-turn session patterns are required.
- Render deployment may be exposing the issue more clearly because runtime state is ephemeral.

## Scope for this task
Allowed focus:
- Session persistence
- Request/response flow
- NeMo state restoration
- Trace ID / conversation ID handling
- Integration between Flask and NeMo

Do not focus on:
- New features
- UI improvements
- Manual OCR
- New rule design
- Non-blocking refactors
- Broad architecture redesign unless explicitly approved

## Files likely relevant
Read these first:
- `app.py`
- `ARCHITECTURE.md`
- `docs/PROJECT_BRIEF.md`
- `config/config.yml`
- `config/rails/` relevant flow files
- `actions.py` or equivalent NeMo action registration file
- Any session/state helper file
- Any Render-specific startup or deployment config

Read if needed:
- `rules/global.yaml`
- `rules/beginner.yaml`
- `rules/intermediate.yaml`
- `rules/pro.yaml`

## Files not to edit unless clearly necessary
- Rule files unrelated to the session bug
- Large documentation files
- Mode behavior files not directly involved in session persistence
- Styling, UI, or unrelated utilities

## Required working method
Before making any change:
1. Restate the bug in plain English.
2. Identify the exact suspected break point.
3. Name the files you plan to inspect.
4. Explain how you will prove the root cause.
5. Name the test or validation command to run after the change.

During implementation:
1. Make the smallest possible safe change.
2. Keep architecture boundaries intact.
3. Do not invent new flows or redesign rules unless approved.
4. Prefer proving the bug with logs/tests before patching.

After implementation:
1. Explain exactly what changed.
2. Explain why the change should fix turn 2+ behavior.
3. Run or name the validation steps.
4. State any remaining uncertainty.

## Definition of done
This task is done only if:
- Turn 1 works.
- Turn 2 continues the same session.
- Turn 3 also continues correctly.
- The conversation does not loop back to the identity gate unless intentionally reset.
- Session identity is traceable with a consistent conversation or trace ID.
- Logs show evidence that prior session state was loaded before processing the next turn.
- The fix works locally first.
- If tested on Render, behavior matches local expectations.

## Validation steps
Use the smallest relevant validation first.

Potential checks:
- Start the app locally.
- Run the conversation flow evaluator.
- Use the same trace/session ID across multiple turns.
- Inspect logs for state load, state update, and state reuse.
- Confirm whether symptom, mode, or machine data survives into turn 2.

## Suggested logging checkpoints
Add or verify logs for:
- Request received
- Trace ID or conversation ID received/generated
- Session state loaded
- Current flow before NeMo call
- Action call inputs/outputs
- State after NeMo call
- Session state saved
- Response returned

## Known constraints
- The user prefers step-by-step guidance and relies heavily on AI assistance.
- Avoid broad rewrites.
- Keep changes understandable and testable.
- The project uses NeMo Guardrails, YAML rules, Python utilities, and structured logging.
- The app should remain aligned with the documented architecture unless a deviation is explicitly approved.

## Notes for the coding assistant
Do not solve this by making random changes across multiple files.
Do not assume NeMo automatically provides durable session persistence across HTTP requests.
Do not declare success without proving multi-turn continuity.
Do not get distracted by unrelated improvements.

## Session notes
- Previous architecture review suggested that app-level persistence should own durable conversation state.
- The likely long-term direction is to separate:
  - NeMo orchestration
  - app/session persistence
  - rule storage
  - long-term logs/history

## If blocked
If the root cause is still unclear after inspection:
1. Stop changing code.
2. Summarize the evidence gathered.
3. Name the exact unanswered question.
4. Propose one narrow next diagnostic step.
