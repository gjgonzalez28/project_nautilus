# Copilot Instructions - Project Nautilus

Project Nautilus is a pinball technician AI system built for safe, structured, multi-turn diagnostics.

## Session startup: Read project context in order

When starting a fresh coding session, read these files in order to understand current project state:

1. `.github/copilot-instructions.md` (this file) - Assistant rules and architecture boundaries
2. `docs/PROJECT_BRIEF.md` - Project overview, goals, and design principles
3. `docs/CURRENT_TASK.md` - **Current active work and blockers** (primary source for what to work on)
4. `docs/NEMO_DUTIES.md` - NeMo behavior specification (when working on conversation flows or rules)
5. `docs/SKILL_LEVEL_SYSTEM.md` - Skill level design reference (when working on mode-specific behavior)

Additional context:
- `docs/CURRENT_TASK.md` is the authoritative source for current work status and priorities
- `ARCHITECTURE.md` provides deep system design context when needed
- `archive/docs_legacy/` contains historical documentation; treat as reference only, not primary guidance

## Project purpose
- Build a reliable pinball repair assistant with three end-user modes: beginner, intermediate, and pro.
- Prioritize safety, machine identification, evidence gathering, and controlled diagnostics.
- Preserve architectural clarity, testability, and maintainability.

## Architecture boundaries
- The app owns session persistence and long-term state.
- NeMo Guardrails owns conversation orchestration, flow control, and guardrails.
- YAML files are the source of truth for rules, mode behavior, and safety requirements.
- Python utilities handle stateless computation, validation, parsing, and helper logic.
- LLM output must not replace hard safety rules or core orchestration logic.

## Non-negotiable rules
- Do not rewrite architecture without explicit approval.
- Do not invent missing requirements.
- Do not move safety-critical logic out of YAML rules unless explicitly instructed.
- Do not make broad changes across unrelated files.
- Do not edit files outside the approved task scope.
- Do not guess when uncertain; identify the uncertainty and propose a way to verify it.

## Required working style
- Start each new task by reading:
  1. `docs/CURRENT_TASK.md`
  2. `docs/PROJECT_BRIEF.md`
  3. Any files explicitly named in the task
- For rule behavior, read the relevant YAML files directly and use exact wording where required.
- Before changing code, restate:
  - the problem,
  - suspected cause,
  - files to edit,
  - tests to run,
  - definition of done.
- Make the smallest safe change that solves the confirmed problem.
- Prefer root-cause fixes over patches.
- Keep responses step-by-step and plain language.

## Testing discipline
- Never claim something is fixed without naming the exact test or validation step.
- When changing orchestration, session handling, YAML loading, or actions, identify the integration risk.
- If a change affects multiple layers, explain why each file must change before editing.

## Source of truth order
1. Current task file
2. YAML rules and code
3. Architecture docs
4. Older session notes

## Important project files
- `docs/CURRENT_TASK.md`
- `docs/PROJECT_BRIEF.md`
- `docs/NEMO_DUTIES.md`
- `docs/SKILL_LEVEL_SYSTEM.md`
- `docs/DEBUGGING_GUIDE.md`
- `docs/TOOLS_SUMMARY.md`
- `ARCHITECTURE.md`
- `rules/global.yaml`
- `rules/beginner.yaml`
- `rules/intermediate.yaml`
- `rules/pro.yaml`
