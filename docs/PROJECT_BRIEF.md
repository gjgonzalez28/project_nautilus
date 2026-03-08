# PROJECT BRIEF - Project Nautilus

Last updated: 2026-03-08
Status: Active foundation / debugging phase

## What this project is
Project Nautilus is a pinball technician AI system designed to guide users through safe, structured, multi-turn troubleshooting conversations.

Its purpose is to help end users diagnose pinball machine problems while respecting safety gates, machine differences, evidence quality, and skill level.

## End goal
Build a reliable, monetizable pinball technician assistant that can eventually support app, website, or chatbot deployment.

The system must:
- maintain conversation continuity across turns
- identify the machine before deep diagnostics
- enforce safety rules consistently
- adapt guidance to user skill level
- avoid unsafe or unsupported guesses
- remain testable, explainable, and maintainable

## User modes
The system supports three user-facing modes:
- Beginner
- Intermediate
- Pro

These modes should change how guidance is presented, how much detail is given, and what actions are considered appropriate.

Modes should not create three completely separate diagnostic engines unless explicitly approved. Shared logic should remain centralized where possible.

## High-level architecture
Current intended architecture:
- App layer handles HTTP requests, session persistence, and deployment concerns.
- NeMo Guardrails handles conversation orchestration, guardrails, flow routing, and stateful dialogue behavior.
- YAML rules define safety constraints, mode behavior, and policy requirements.
- Python utilities handle stateless helper logic such as validation, parsing, fuzzy matching, and scoring.
- Logging captures structured traceable events for debugging and validation.
- LLM output is used for explanation and language generation, not as the sole authority for safety-critical logic.

## Important architectural boundaries
Non-negotiable boundaries unless explicitly approved:
- Do not let LLM prompts replace hard safety rules.
- Do not move core rule logic out of YAML without approval.
- Do not treat NeMo as the only durable memory layer for web requests.
- Do not rely on undocumented assumptions about multi-turn persistence.
- Do not mix temporary task notes into permanent project instructions.

## Current phase
The project is still in a foundational phase.
The immediate priority is reliability, not feature expansion.

Current focus areas:
- multi-turn conversation continuity
- state persistence across requests
- NeMo orchestration correctness
- clean boundaries between orchestration, state, rules, and utilities
- debug visibility through logs and tests

## Current blocker
Primary blocker:
- Turn 1 works, but turn 2 and later may loop, reset, or fall back to the identity gate instead of continuing the same session.

This is currently more important than adding new features.

## Design principles
The system should be:
- safe before helpful
- deterministic where possible
- evidence-driven
- mode-aware
- testable in small pieces
- easy to debug with logs
- maintainable over time

## How work should be approached
When working on this project:
- prefer root-cause analysis over patching
- make the smallest safe change that solves the confirmed problem
- keep architecture boundaries intact
- validate changes with logs or tests
- avoid broad rewrites unless explicitly requested
- keep explanations step-by-step and clear

## Source-of-truth files
Most important files for understanding the project:
- `.github/copilot-instructions.md`
- `docs/CURRENT_TASK.md`
- `ARCHITECTURE.md`
- `docs/NEMO_DUTIES.md`
- `rules/global.yaml`
- `rules/beginner.yaml`
- `rules/intermediate.yaml`
- `rules/pro.yaml`

## What this project is not
This is not a freeform chatbot that improvises repairs.
This is not a system that should guess machine-specific details without evidence.
This is not a project where AI should rewrite major architecture on its own.
This is not a good place for broad refactoring during active debugging unless approved.

## Short summary for AI assistants
Project Nautilus is a safety-first, multi-turn pinball technician system.
Preserve architecture clarity, protect the rule system, focus on reliability, and solve one scoped problem at a time.
