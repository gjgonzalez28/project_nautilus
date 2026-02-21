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

---

# How to Run

Prerequisites
- Python 3.11+ (virtual environment recommended)
- `pyyaml` installed in the environment

Quick setup
```powershell
# from project root
python -m venv venv
.\venv\Scripts\Activate.ps1   # PowerShell
# or: .\venv\Scripts\activate   # cmd
python -m pip install --upgrade pip
python -m pip install pyyaml
```

Run the full interactive app
```powershell
# Run from the project root directory
python main.py
```

Run individual modules (package-safe)
```powershell
# Discovery script quick test
python -m logic.discovery_script

# Manager smoke test
python -m logic.manager
```

Notes
- The code expects the `logic` directory to be a package (it contains `__init__.py`).
- If you modify YAML files in `rules/`, the manager will use the `global` rules and the selected mode rules for safety logic. Mode files currently contain `safety_logic` with `interrupt_triggers` and `warning_message`.

Troubleshooting
- If you see `ModuleNotFoundError` for `logic` or `nautilus_core`, ensure you run commands from the project root so the project directory is on `PYTHONPATH`.
- To run modules as scripts, the test blocks include a `sys.path` fallback to append the project root automatically.
