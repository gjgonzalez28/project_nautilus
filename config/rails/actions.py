"""
Project Nautilus: NeMo Guardrails Python Actions

Custom Python functions that Colang flows can call.
These bridge NeMo (conversation logic) with Python utilities (fuzzy matching, API calls, etc).

Usage:
In Colang flow, call custom actions like:
  result = await fuzzy_match_symptom(user_input)
  
These functions are auto-discovered by NeMo and made available to Colang.
"""

from typing import Optional, Dict, Any
import sys
import os
import json
from pathlib import Path
from nemoguardrails.actions import action
from openai import AsyncOpenAI
import yaml

# Add project root to path so we can import our modules
# __file__ = config/rails/actions.py, so project root is parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from app_logging.logger import StructuredLogger
from logic.discovery_helper import fuzzy_match_machine as fuzzy_machine_helper
from logic.discovery_helper import validate_skill_level as validate_skill_helper

logger = StructuredLogger(__name__)


# ============================================================================
# Lazy OpenAI Client Initialization
# ============================================================================

def _get_openai_client() -> AsyncOpenAI:
    """
    Get or create AsyncOpenAI client lazily.
    
    This function initializes the OpenAI client only when it's actually needed,
    rather than at module import time. This allows actions.py to import
    successfully even if OPENAI_API_KEY is not yet set.
    
    Returns:
        AsyncOpenAI instance
    
    Raises:
        ValueError if OPENAI_API_KEY is not set
    """
    if not hasattr(_get_openai_client, '_client'):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable not set. "
                "Set it before calling diagnostic actions."
            )
        _get_openai_client._client = AsyncOpenAI(api_key=api_key)
    return _get_openai_client._client


# ============================================================================
# Phase 2: Placeholder Actions (to be expanded in Phase 3)
# ============================================================================

async def initialize_session(user_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Initialize a diagnostic session.
    
    Args:
        user_id: Optional user identifier
    
    Returns:
        Session state dict with initial values
    """
    session_state = {
        "user_id": user_id,
        "machine_name": None,
        "skill_name": None,
        "symptom": None,
        "confidence": 0.0,
        "evidence": [],
        "playfield_confirmed": False,
        "turn": 0
    }
    
    logger.log_event(
        event="session_initialized",
        data=session_state,
        component="actions"
    )
    
    return session_state


# ============================================================================
# Phase 3: Discovery Flow Actions (NeMo @action decorated)
# ============================================================================

@action(name="FuzzyMatchMachineAction")
async def fuzzy_match_machine_action(user_input: str, threshold: float = 0.6) -> Dict[str, Any]:
    """
    Fuzzy match user input against machine library.
    
    Args:
        user_input: User's description of the pinball machine
        threshold: Similarity score threshold (default 0.6)
    
    Returns:
        Dict with matched machine info or error details
    """
    result = fuzzy_machine_helper(user_input, threshold)
    
    logger.log_event(
        event="fuzzy_match_machine_called",
        data={
            "user_input": user_input,
            "matched": result.get("matched"),
            "confidence": result.get("confidence")
        },
        component="actions"
    )
    
    return result


@action(name="ValidateSkillLevelAction")
async def validate_skill_level_action(user_input: str) -> Dict[str, Any]:
    """
    Validate and extract skill level from user input.
    
    Args:
        user_input: User's description of their skill level
    
    Returns:
        Dict with validated skill level
    """
    result = validate_skill_helper(user_input)
    
    logger.log_event(
        event="validate_skill_level_called",
        data={
            "user_input": user_input,
            "valid": result.get("valid"),
            "skill_level": result.get("skill_level"),
            "confidence": result.get("confidence")
        },
        component="actions"
    )
    
    return result


# ============================================================================
# Phase 3: Additional Fuzzy Matching (to be implemented)
# ============================================================================

@action(name="FuzzyMatchSymptomAction")
async def fuzzy_match_symptom_action(symptom_input: str, machine_id: Optional[str] = None, threshold: float = 0.65) -> Dict[str, Any]:
    """
    Fuzzy match user symptom to known issues in machine library.
    
    Args:
        symptom_input: User's description of the problem
        machine_id: Optional machine ID to narrow down symptom database
        threshold: Similarity score threshold (default 0.65)
    
    Returns:
        Dict with matched symptom info or error details
    """
    # Symptom categories and keywords
    symptom_categories = {
        "flipper": ["flipper", "flip", "bat", "weak", "stuck", "won't flip", "dead flipper"],
        "bumper": ["bumper", "pop bumper", "thumper", "jet bumper", "not firing", "dead bumper"],
        "lights": ["light", "lights", "bulb", "illumination", "dim", "flickering", "not lighting"],
        "coil": ["coil", "solenoid", "not firing", "weak", "stuck"],
        "switch": ["switch", "rollover", "target", "not registering", "stuck switch"],
        "sound": ["sound", "audio", "music", "bell", "chime", "no sound", "distorted"],
        "power": ["power", "won't start", "dead", "no power", "fuse", "transformer"],
        "display": ["display", "score", "dmd", "backglass", "not showing"],
        "motor": ["motor", "spinning", "vibration", "shaker", "not running"],
        "playfield": ["playfield", "glass", "ball", "stuck ball", "drain"]
    }
    
    symptom_lower = symptom_input.lower()
    best_category = "unknown"
    best_score = 0.0
    
    # Match against categories
    for category, keywords in symptom_categories.items():
        for keyword in keywords:
            if keyword in symptom_lower:
                score = len(keyword) / len(symptom_lower)  # Longer matches = higher score
                if score > best_score:
                    best_score = score
                    best_category = category
    
    matched = best_score >= threshold
    
    result = {
        "matched": matched,
        "category": best_category if matched else "unknown",
        "confidence": round(best_score, 2),
        "symptom_input": symptom_input
    }
    
    logger.log_event(
        event="fuzzy_match_symptom_called",
        data={
            "symptom_input": symptom_input,
            "machine_id": machine_id,
            "matched": result.get("matched"),
            "category": result.get("category"),
            "confidence": result.get("confidence")
        },
        component="actions"
    )
    
    return result


@action(name="LogSymptomDetailsAction")
async def log_symptom_details_action(symptom: str, category: Optional[str], details: Dict[str, Any]) -> Dict[str, Any]:
    """
    Log captured symptom details for diagnostic reasoning.
    
    Args:
        symptom: User's symptom description
        category: Matched category (if any)
        details: Additional details dict
    
    Returns:
        Confirmation dict
    """
    logger.log_event(
        event="symptom_details_logged",
        data={
            "symptom": symptom,
            "category": category,
            "details": details
        },
        component="actions"
    )
    
    return {
        "logged": True,
        "symptom": symptom,
        "category": category
    }


# ============================================================================
# Phase 3: Diagnostic Data Loading (NeMo guides LLM with real data)
# ============================================================================

def _load_diagnostic_maps() -> Dict[str, Any]:
    """
    Load diagnostic_maps.yaml from data directory.
    
    Returns:
        Dict with all symptom maps keyed by symptom name
    """
    diagnostic_maps_path = PROJECT_ROOT / "data" / "diagnostic_maps.yaml"
    
    try:
        with open(diagnostic_maps_path, 'r') as f:
            data = yaml.safe_load(f)
        return data.get("symptom_maps", {})
    except Exception as e:
        logger.log_event(
            event="diagnostic_maps_load_failed",
            data={"error": str(e), "path": str(diagnostic_maps_path)},
            component="actions"
        )
        return {}


def _map_category_to_symptom_key(category: str) -> str:
    """
    Map fuzzy symptom category to diagnostic_maps.yaml keys.
    
    Args:
        category: From FuzzyMatchSymptomAction (e.g., "flipper", "bumper")
    
    Returns:
        Symptom key from diagnostic_maps (e.g., "left_flipper_dead")
    """
    # Common mappings from fuzzy categories to diagnostic map keys
    category_mappings = {
        "flipper": "left_flipper_dead",  # Will be determined by context
        "bumper": "bumpers_not_working",
        "lights": "lights_not_working",
        "coil": "solenoid_not_firing",
        "switch": "switch_not_registering",
        "sound": "sound_not_working",
        "power": "power_supply_issue",
        "display": "display_not_showing",
        "motor": "motor_not_running",
        "playfield": "playfield_issue",
        "slingshot": "slingshots_not_firing"
    }
    
    return category_mappings.get(category, "unknown_issue")


def _extract_stf_by_skill_level(symptom_data: Dict[str, Any], skill_level: str) -> list[str]:
    """
    Extract STF checks from diagnostic map, filtered by skill level.
    
    Args:
        symptom_data: Dict from diagnostic_maps.yaml with 'stf' key
        skill_level: "beginner", "intermediate", or "pro"
    
    Returns:
        List of formatted diagnostic steps
    """
    if "stf" not in symptom_data:
        return []
    
    stf = symptom_data["stf"]
    steps = []
    
    # Beginner: Only STRAIGHT (physical) checks
    if skill_level == "beginner":
        if "straight" in stf and "checks" in stf["straight"]:
            steps.append("=== PHYSICAL/MECHANICAL CHECKS (Start Here) ===")
            for check in stf["straight"]["checks"]:
                step_text = f"Step {check.get('id', 'S?')}: {check.get('area', 'Check')}"
                step_text += f" - {check.get('action', 'Perform check')}"
                steps.append(step_text)
    
    # Intermediate: STRAIGHT + TRUE (physical + validation)
    elif skill_level == "intermediate":
        if "straight" in stf and "checks" in stf["straight"]:
            steps.append("=== PHYSICAL/MECHANICAL CHECKS ===")
            for check in stf["straight"]["checks"]:
                step_text = f"Step {check.get('id', 'S?')}: {check.get('area', 'Check')}"
                step_text += f" - {check.get('action', 'Perform check')}"
                steps.append(step_text)
        
        if "true" in stf and "checks" in stf["true"]:
            steps.append("\n=== VALIDATION/MEASUREMENT CHECKS ===")
            for check in stf["true"]["checks"]:
                step_text = f"Step {check.get('id', 'T?')}: {check.get('area', 'Check')}"
                step_text += f" - {check.get('action', 'Perform check')}"
                steps.append(step_text)
    
    # Pro: STRAIGHT + TRUE + FLUSH (physical + validation + repair)
    elif skill_level == "pro":
        if "straight" in stf and "checks" in stf["straight"]:
            steps.append("=== PHYSICAL/MECHANICAL CHECKS ===")
            for check in stf["straight"]["checks"]:
                step_text = f"Step {check.get('id', 'S?')}: {check.get('area', 'Check')}"
                step_text += f" - {check.get('action', 'Perform check')}"
                steps.append(step_text)
        
        if "true" in stf and "checks" in stf["true"]:
            steps.append("\n=== VALIDATION/MEASUREMENT CHECKS ===")
            for check in stf["true"]["checks"]:
                step_text = f"Step {check.get('id', 'T?')}: {check.get('area', 'Check')}"
                step_text += f" - {check.get('action', 'Perform check')}"
                steps.append(step_text)
        
        if "flush" in stf and "checks" in stf["flush"]:
            steps.append("\n=== COMPONENT REPAIR/REPLACEMENT ===")
            for check in stf["flush"]["checks"]:
                step_text = f"Step {check.get('id', 'F?')}: {check.get('area', 'Check')}"
                step_text += f" - {check.get('action', 'Perform check')}"
                steps.append(step_text)
    
    return steps


def _get_diagnostic_steps_from_data(
    symptom: str,
    category: str,
    skill_level: str
) -> Dict[str, Any]:
    """
    Get diagnostic steps from diagnostic_maps.yaml instead of LLM.
    This is the DATA-DRIVEN approach where NeMo controls the LLM.
    
    Args:
        symptom: User's symptom description
        category: Matched category (flipper, bumper, etc.)
        skill_level: User skill level (beginner, intermediate, pro)
    
    Returns:
        Dict with steps, confidence, and metadata
    """
    # Load diagnostic maps
    diagnostic_maps = _load_diagnostic_maps()
    
    if not diagnostic_maps:
        logger.log_event(
            event="diagnostic_maps_empty",
            data={"symptom": symptom, "category": category},
            component="actions"
        )
        return {
            "steps": ["ERROR: Diagnostic database not loaded. Please try again."],
            "confidence": 0.0,
            "safety_warnings": [],
            "estimated_time": "Unknown",
            "needs_manual": False,
            "source": "error"
        }
    
    # Map category to symptom key
    symptom_key = _map_category_to_symptom_key(category)
    
    # Look up the symptom in diagnostic maps
    if symptom_key not in diagnostic_maps:
        logger.log_event(
            event="symptom_not_in_maps",
            data={"context": symptom_key, "available_keys": list(diagnostic_maps.keys())},
            component="actions"
        )
        return {
            "steps": [f"I don't have diagnostic steps for '{symptom_key}' in the database yet. Please describe the issue in more detail."],
            "confidence": 0.3,
            "safety_warnings": [],
            "estimated_time": "Unknown",
            "needs_manual": False,
            "source": "not_found"
        }
    
    symptom_data = diagnostic_maps[symptom_key]
    
    # Extract title
    title = symptom_data.get("title", symptom_key)
    
    # Extract STF steps filtered by skill level
    steps = _extract_stf_by_skill_level(symptom_data, skill_level)
    
    if not steps:
        steps = ["No diagnostic steps available for this issue."]
    
    # Add title at the beginning
    steps.insert(0, f"TROUBLESHOOTING: {title}")
    
    # Extract safety warnings if any
    safety_warnings = []
    overview = symptom_data.get("overview", "")
    if "high voltage" in overview.lower():
        safety_warnings.append("This may involve high voltage - disconnect power before testing")
    if "electrical" in overview.lower():
        safety_warnings.append("Electrical safety precautions required")
    
    if not safety_warnings:
        safety_warnings = ["Follow all safety guidelines"]
    
    # Estimate time based on number of steps
    num_steps = len([s for s in steps if s.startswith("Step")])
    estimated_time = f"{max(num_steps * 3, 10)}-{num_steps * 5 + 10} minutes"
    
    # Check if steps will need manual/photo (if they mention specific locations)
    steps_text = ' '.join(steps).lower()
    needs_manual = bool(any(pattern in steps_text for pattern in ["fuse", "connector", "test point", "pin", "component", "board"]))
    
    result = {
        "steps": steps,
        "confidence": 0.95,  # High confidence - using structured data
        "safety_warnings": safety_warnings,
        "estimated_time": estimated_time,
        "needs_manual": needs_manual,
        "source": "diagnostic_maps"  # Track that this came from data, not LLM
    }
    
    logger.log_event(
        event="diagnostic_steps_from_data",
        data={
            "symptom": symptom,
            "category": category,
            "skill_level": skill_level,
            "steps_count": len(result["steps"]),
            "source": "diagnostic_maps"
        },
        component="actions"
    )
    
    return result


async def _call_llm_for_diagnostic_steps(
    machine_info: Dict[str, Any],
    symptom: str,
    category: str,
    skill_level: str
) -> str:
    """
    DEPRECATED: This function is kept for backwards compatibility.
    
    NOTE: New approach uses _get_diagnostic_steps_from_data() instead.
    The LLM should be used to FORMAT and EXPLAIN the steps, not INVENT them.
    
    This function is no longer called by GenerateDiagnosticStepsAction.
    """
    machine_name = machine_info.get("name", "Unknown machine")
    manufacturer = machine_info.get("manufacturer", "Unknown")
    era = machine_info.get("era", "Unknown")
    
    # Placeholder - not used anymore
    return "ERROR: LLM generation deprecated. Use diagnostic_maps instead."


@action(name="GenerateDiagnosticStepsAction")
async def generate_diagnostic_steps_action(
    symptom: str,
    category: str,
    machine_info: Dict[str, Any],
    skill_level: str,
    additional_details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate diagnostic troubleshooting steps from diagnostic_maps.yaml.
    
    NEW APPROACH: Data-driven instead of LLM-driven.
    NeMo loads the actual STF structures and controls what the user sees.
    LLM can be used later for formatting/explanation if needed.
    
    Args:
        symptom: The issue description
        category: Symptom category (flipper, bumper, etc.)
        machine_info: Machine details (name, era, manufacturer)
        skill_level: User's skill level (beginner, intermediate, pro)
        additional_details: Optional extra symptom context
    
    Returns:
        Dict with diagnostic steps, confidence, and specificity flag
    """
    try:
        # Get diagnostic steps from data, not LLM
        result = _get_diagnostic_steps_from_data(
            symptom=symptom,
            category=category,
            skill_level=skill_level
        )
        
        # Validate coin door constraint (Rule 0C.R19)
        result["steps"] = _validate_coin_door_constraint(result["steps"])
        
        # Detect if steps require specific technical details
        needs_manual = _check_if_steps_need_manual(result["steps"])
        result["needs_manual"] = needs_manual
        
        logger.log_event(
            event="diagnostic_steps_generated",
            data={
                "symptom": symptom,
                "category": category,
                "skill_level": skill_level,
                "steps_count": len(result["steps"]),
                "needs_manual": result["needs_manual"],
                "source": result.get("source", "unknown")
            },
            component="actions"
        )
        
        return result
        
    except Exception as e:
        logger.log_event(
            event="diagnostic_generation_failed",
            data={
                "error": str(e),
                "symptom": symptom,
                "category": category
            },
            component="actions"
        )
        # Fallback response
        return {
            "steps": [
                "ERROR: Unable to generate diagnostic steps.",
                "Step 1: Disconnect power.",
                "Step 2: Visually inspect the affected area.",
                "Step 3: Check for obvious mechanical damage or loose connections.",
                "Step 4: If no obvious issue found, contact a service professional."
            ],
            "confidence": 0.3,
            "safety_warnings": ["Disconnect power before testing"],
            "estimated_time": "15-30 minutes",
            "needs_manual": False,
            "error": str(e),
            "source": "fallback"
        }


def _check_if_steps_need_manual(steps: list[str]) -> bool:
    """
    Detect if diagnostic steps require specific technical details
    that would benefit from a manual or photo.
    
    Returns True if steps mention:
    - Specific fuse numbers (F1, F114, etc.)
    - Connector IDs (J5, CN12, etc.)
    - Test points (TP2, TP14, etc.)
    - Part numbers or component IDs
    - Specific voltage values at specific locations
    - Board-specific pinouts
    
    Returns False for general steps like:
    - "Check the power supply"
    - "Inspect coil for damage"
    - "Test switch continuity"
    """
    # Keywords that indicate board-specific details
    specific_keywords = [
        r'\bF\d+\b',        # Fuse numbers: F1, F114
        r'\bJ\d+\b',        # Connectors: J5, J12
        r'\bCN\d+\b',       # Connectors: CN1, CN12
        r'\bTP\d+\b',       # Test points: TP2, TP14
        r'\bC\d+\b',        # Capacitors: C14, C23
        r'\bR\d+\b',        # Resistors: R12, R45
        r'\bU\d+\b',        # ICs: U8, U12
        r'\bQ\d+\b',        # Transistors: Q3, Q7
        r'\bD\d+\b',        # Diodes: D1, D5
        r'\bpin \d+\b',     # Pin numbers
        r'part number',
        r'component [A-Z]+\d+',
        r'at connector',
        r'test point',
    ]
    
    import re
    
    # Check all steps for specific technical references
    steps_text = ' '.join(steps).lower()
    
    for pattern in specific_keywords:
        if re.search(pattern, steps_text, re.IGNORECASE):
            return True
    
    return False


def _validate_coin_door_constraint(steps: list[str]) -> list[str]:
    """
    Validate and filter diagnostic steps to enforce Rule 0C.R19 (Coin Door Hard-Gate).
    
    This prevents Nautilus from generating steps that access components through the coin door.
    Only allowed coin door activities: interlock switch, service buttons, volume button, 
    lockdown bar release.
    
    Args:
        steps: List of diagnostic step strings
    
    Returns:
        Validated list of steps with coin door violations removed/flagged
    """
    import re
    
    # Keywords that indicate coin door access
    coin_door_keywords = [
        r'coin door',
        r'coin-door',
        r'through.*door',
        r'via.*coin',
        r'reach.*door'
    ]
    
    # Prohibited items to access via coin door
    prohibited_items = [
        'fuse', 'connector', 'wire', 'wiring', 'board', 'power supply',
        'transformer', 'coil', 'switch', 'relay', 'component', 'test point'
    ]
    
    # Allowed coin door activities (don't flag these)
    allowed_activities = [
        'interlock', 'service button', 'volume button', 'lockdown bar'
    ]
    
    validated_steps = []
    violations_found = []
    
    for step in steps:
        step_lower = step.lower()
        is_violation = False
        
        # Check if step mentions coin door
        mentions_coin_door = any(re.search(pattern, step_lower) for pattern in coin_door_keywords)
        
        if mentions_coin_door:
            # Check if it's an allowed activity
            is_allowed = any(allowed in step_lower for allowed in allowed_activities)
            
            if not is_allowed:
                # Check if it mentions prohibited items
                mentions_prohibited = any(item in step_lower for item in prohibited_items)
                
                if mentions_prohibited:
                    is_violation = True
                    violations_found.append(step)
                    logger.log_event(
                        event="coin_door_violation_detected",
                        data={"step": step},
                        component="actions"
                    )
        
        # Only include steps that don't violate coin door rule
        if not is_violation:
            validated_steps.append(step)
    
    if violations_found:
        logger.log_event(
            event="coin_door_violations_filtered",
            data={"count": len(violations_found), "violations": violations_found},
            component="actions"
        )
    
    return validated_steps


# ============================================================================
# Phase 3: Safety Validation Actions
# ============================================================================

@action(name="EvaluateSafetyGatesAction")
async def evaluate_safety_gates_action(
    diagnostic_steps: list[str],
    machine_era: str,
    skill_level: str
) -> Dict[str, Any]:
    """
    Evaluate if diagnostic steps pass safety validations.
    
    Args:
        diagnostic_steps: List of diagnostic steps
        machine_era: Era of machine (EM, Solid State, etc.)
        skill_level: User's skill level
    
    Returns:
        Dict with safety evaluation results
    """
    # Check for high voltage keywords
    high_voltage_keywords = ["voltage", "power supply", "transformer", "120v", "240v", "mains"]
    contains_high_voltage = any(
        any(keyword in step.lower() for keyword in high_voltage_keywords)
        for step in diagnostic_steps
    )
    
    result = {
        "safe": True,
        "warnings": [],
        "requires_expert": False
    }
    
    # Add warnings for high voltage work
    if contains_high_voltage:
        result["warnings"].append("This repair involves high voltage - disconnect power before proceeding")
        
        if skill_level == "beginner":
            result["requires_expert"] = True
            result["safe"] = False
            result["warnings"].append("HIGH VOLTAGE WORK: Recommend consulting a professional for this repair")
    
    logger.log_event(
        event="safety_gates_evaluated",
        data={
            "safe": result["safe"],
            "warning_count": len(result["warnings"]),
            "requires_expert": result["requires_expert"]
        },
        component="actions"
    )
    
    return result


# ============================================================================
# Phase 1.5: Combined Machine and Skill Parsing
# ============================================================================

@action(name="ParseMachineAndSkillAction")
async def parse_machine_and_skill_action(user_input: str) -> Dict[str, Any]:
    """
    Parse machine name, manufacturer, model, and skill level from a single user response.
    Also detect if model clarification is needed (Premium vs LE vs Pro, etc.)
    
    Args:
        user_input: User's combined response with machine and skill info
    
    Returns:
        Dict with parsed machine_name, manufacturer, era, skill_level, 
        needs_clarification flag, and clarification_question if needed
    """
    user_lower = user_input.lower()
    
    # Extract skill level
    skill_level = None
    if "beginner" in user_lower or "new" in user_lower or "first time" in user_lower:
        skill_level = "beginner"
    elif "intermediate" in user_lower or "some experience" in user_lower:
        skill_level = "intermediate"
    elif "advanced" in user_lower or "pro" in user_lower or "expert" in user_lower or "professional" in user_lower:
        skill_level = "pro"
    
    # For now, use simplified machine extraction (will be replaced with LLM)
    # Extract machine name from input
    machine_name = user_input
    if skill_level:
        # Remove skill level from machine name
        skill_keywords = ["beginner", "intermediate", "advanced", "pro", "expert", "professional", "new", "first time", "some experience"]
        for keyword in skill_keywords:
            machine_name = machine_name.replace(keyword, "").replace(keyword.title(), "")
        machine_name = machine_name.strip().strip(",").strip()
    
    # Check if clarification needed for common multi-version titles
    needs_clarification = False
    clarification_question = ""
    
    multi_version_machines = {
        "godzilla": "I see there are Premium, LE, and Pro versions of Godzilla. Which one do you have?",
        "medieval madness": "Is this the original Medieval Madness or the remake?",
        "monster bash": "Is this the original Monster Bash or the remake?",
        "dialed in": "Is this the standard or Limited Edition version?",
        "iron maiden": "Which Iron Maiden version do you have? (Pro, Premium, or LE)",
        "rush": "Which Rush version do you have? (Pro, Premium, or LE)",
        "led zeppelin": "Which Led Zeppelin version do you have? (Pro, Premium, or LE)",
    }
    
    machine_lower = machine_name.lower()
    for machine_key, question in multi_version_machines.items():
        if machine_key in machine_lower and not any(v in machine_lower for v in ["premium", "le", "pro ", " pro", "limited"]):
            needs_clarification = True
            clarification_question = question
            break
    
    # Placeholder for manufacturer/era (will use LLM in future)
    manufacturer = "Unknown"
    era = "Modern"
    
    result = {
        "machine_name": machine_name,
        "manufacturer": manufacturer,
        "era": era,
        "skill_level": skill_level,
        "needs_clarification": needs_clarification,
        "clarification_question": clarification_question
    }
    
    logger.log_event(
        event="machine_and_skill_parsed",
        data={
            "machine": machine_name,
            "skill_level": skill_level,
            "needs_clarification": needs_clarification
        },
        component="actions"
    )
    
    return result


# ============================================================================
# Playfield Access Detection
# ============================================================================

@action(name="DetectPlayfieldAccessAction")
async def detect_playfield_access_action(
    diagnostic_steps: list[str],
    machine_info: Dict[str, Any],
    skill_level: str
) -> Dict[str, Any]:
    """
    Detect if diagnostic steps require playfield access and determine lockdown bar type.
    Only relevant for beginners who may need guidance.
    
    Args:
        diagnostic_steps: List of diagnostic steps
        machine_info: Machine details (name, manufacturer, era)
        skill_level: User's skill level
    
    Returns:
        Dict with needs_access flag, lockdown_bar_type, and instructions
    """
    # Only check for beginners - intermediates and pros know how to access playfield
    if skill_level != "beginner":
        return {
            "needs_access": False,
            "lockdown_bar_type": None,
            "show_instructions": False
        }
    
    # Check if steps require physical access under playfield
    playfield_keywords = [
        "playfield", "coil", "switch", "flipper", "bumper", "slingshot",
        "under the playfield", "raise the playfield", "pop bumper",
        "drop target", "kicker", "magnet", "diverter", "trough"
    ]
    
    steps_text = ' '.join(diagnostic_steps).lower()
    needs_access = any(keyword in steps_text for keyword in playfield_keywords)
    
    if not needs_access:
        return {
            "needs_access": False,
            "lockdown_bar_type": None,
            "show_instructions": False
        }
    
    # Determine lockdown bar type based on manufacturer and era
    manufacturer = machine_info.get("manufacturer", "").lower()
    era = machine_info.get("era", "").lower()
    machine_name = machine_info.get("name", "").lower()
    
    # Modern Stern (2000s+) typically use clips
    if "stern" in manufacturer:
        # Check if it's a modern Stern (post-2000)
        if any(year in machine_name for year in ["20", "202"]) or "modern" in era:
            lockdown_bar_type = "clips"
        else:
            lockdown_bar_type = "lever"
    # Older machines use lever
    else:
        lockdown_bar_type = "lever"
    
    result = {
        "needs_access": True,
        "lockdown_bar_type": lockdown_bar_type,
        "show_instructions": True
    }
    
    logger.log_event(
        event="playfield_access_detected",
        data={
            "needs_access": needs_access,
            "lockdown_bar_type": lockdown_bar_type,
            "skill_level": skill_level
        },
        component="actions"
    )
    
    return result


# ============================================================================
# Deprecated/Stub Actions
# ============================================================================
# These functions will be filled in during Phase 3:
#
# async def calculate_confidence(evidence: list[str]) -> float:
#     """Calculate symptom diagnosis confidence"""
#     pass
# ============================================================================


# ============================================================================
# Phase 3: LLM Integration (to be implemented)
# ============================================================================
# These functions will call ChatGPT for diagnostics:
#
# async def generate_diagnostic_steps(symptom: str, evidence: list[str]) -> str:
#     """Call ChatGPT to generate STF diagnostic steps"""
#     pass
#
# async def evaluate_safety_gates(diagnostic_result: Dict) -> Dict[str, bool]:
#     """Check if diagnostic result passes safety rules"""
#     pass
# ============================================================================
