# Project Nautilus (Pinball Diagnostic Engine)

Project layout (created):

- `venv`          <-- Virtual environment (not created by this script)
- `config/`       <-- Main configuration
  - `rails/`      <-- Modular Colang (.co) files
- `actions/`      <-- Python custom actions
- `data/`         <-- Knowledge base (JSON/Markdown)
- `archive/`      <-- Old monolithic Spine files

Next steps:
- Lead developer: provide detailed `safety.co` Colang rules.
- Verify NeMo Guardrails availability inside the `venv`.
