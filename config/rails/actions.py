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

# Add project root to path so we can import our modules
PROJECT_ROOT = Path(__file__).resolve().parents[1]
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
# Phase 3: Diagnostic Reasoning Actions
# ============================================================================

async def _call_llm_for_diagnostic_steps(
    machine_info: Dict[str, Any],
    symptom: str,
    category: str,
    skill_level: str
) -> str:
    """
    Call gpt-5.2 LLM to generate diagnostic steps.
    
    Args:
        machine_info: Dict with machine name, era, manufacturer
        symptom: The reported symptom/issue
        category: Symptom category (flipper, bumper, etc.)
        skill_level: User's skill level (beginner, intermediate, pro)
    
    Returns:
        String with diagnostic steps from LLM
    """
    machine_name = machine_info.get("name", "Unknown machine")
    manufacturer = machine_info.get("manufacturer", "Unknown")
    era = machine_info.get("era", "Unknown")
    
    prompt = f"""You are a pinball machine diagnostic expert.
    
MACHINE INFO:
- Name: {machine_name}
- Manufacturer: {manufacturer}
- Era: {era}

USER'S SKILL LEVEL: {skill_level}

REPORTED SYMPTOM: {symptom}
CATEGORY: {category}

Generate diagnostic troubleshooting steps for this user. Follow these rules:

1. Tailor the complexity to the user's skill level:
   - Beginner: Simple, safe checks first (visual inspection, basic testing)
   - Intermediate: More technical checks (continuity testing, component measurement)
   - Pro: Advanced diagnostics (board-level testing, part replacement)

2. Rule 0C.R19 - COIN DOOR CONSTRAINT:
   Never suggest accessing components through the coin door.
   Only safe coin door access: interlock switch, service buttons, volume, lockdown bar.
   For ALL other work: must remove glass and raise playfield.

3. Always start with safety warnings if testing will involve power or high voltage.

4. Format output as numbered steps (Step 1:, Step 2:, etc.)

5. Include estimated time and tools/equipment needed.

Generate the diagnostic steps now:"""

    try:
        openai_client = _get_openai_client()
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a pinball machine diagnostic expert helping users troubleshoot their machines. You prioritize safety and follow all diagnostic rules."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.1,  # Keep focused on facts
            max_tokens=1000
        )
        
        steps_text = response.choices[0].message.content
        return steps_text
        
    except Exception as e:
        logger.log_event(
            event="llm_diagnostic_call_failed",
            data={
                "error": str(e),
                "machine": machine_name,
                "symptom": symptom
            },
            component="actions"
        )
        # Return fallback steps if LLM fails
        return "Step 1: Disconnect power.\nStep 2: Visually inspect the affected area.\nStep 3: Check for obvious mechanical damage or loose connections."


@action(name="GenerateDiagnosticStepsAction")
async def generate_diagnostic_steps_action(
    symptom: str,
    category: str,
    machine_info: Dict[str, Any],
    skill_level: str,
    additional_details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate diagnostic troubleshooting steps using LLM.
    
    Args:
        symptom: The issue description
        category: Symptom category (flipper, bumper, etc.)
        machine_info: Machine details (name, era, manufacturer)
        skill_level: User's skill level (beginner, intermediate, pro)
        additional_details: Optional extra symptom context
    
    Returns:
        Dict with diagnostic steps, confidence, and specificity flag
    """
    # Call LLM to generate diagnostic steps
    try:
        llm_response = await _call_llm_for_diagnostic_steps(
            machine_info=machine_info,
            symptom=symptom,
            category=category,
            skill_level=skill_level
        )
        
        # Parse LLM response into steps list
        # Split by "Step N:" pattern
        raw_steps = llm_response.split("\n")
        steps = [step.strip() for step in raw_steps if step.strip() and ("step" in step.lower() or step.startswith("•") or step.startswith("-"))]
        
        # If no steps found, fallback to splitting by newline
        if not steps:
            steps = [step.strip() for step in raw_steps if step.strip()]
        
        # Validate coin door constraint (Rule 0C.R19)
        steps = _validate_coin_door_constraint(steps)
        
        # Detect if steps require specific technical details
        needs_manual = _check_if_steps_need_manual(steps)
        
        # Extract safety warnings from LLM response
        safety_warnings = []
        if "disconnect" in llm_response.lower() or "power" in llm_response.lower():
            safety_warnings.append("Disconnect power before testing")
        if "high voltage" in llm_response.lower():
            safety_warnings.append("This machine contains high voltage components")
        if not safety_warnings:
            safety_warnings = ["Follow all safety guidelines"]
        
        # Estimate time based on number of steps
        estimated_time = f"{min(len(steps) * 5, 45)}-{min(len(steps) * 5 + 15, 60)} minutes"
        
        result = {
            "steps": steps,
            "confidence": 0.85,  # Higher confidence with real LLM
            "safety_warnings": safety_warnings,
            "estimated_time": estimated_time,
            "needs_manual": needs_manual,
            "raw_response": llm_response  # Include raw for debugging
        }
        
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
        result = {
            "steps": [
                "Step 1: Disconnect power.",
                "Step 2: Visually inspect the affected area.",
                "Step 3: Check for obvious mechanical damage or loose connections.",
                "Step 4: If no obvious issue found, contact a service professional."
            ],
            "confidence": 0.5,
            "safety_warnings": ["Disconnect power before testing"],
            "estimated_time": "15-30 minutes",
            "needs_manual": False,
            "error": str(e)
        }
    
    logger.log_event(
        event="diagnostic_steps_generated",
        data={
            "symptom": symptom,
            "category": category,
            "skill_level": skill_level,
            "steps_count": len(result["steps"]),
            "needs_manual": result["needs_manual"]
        },
        component="actions"
    )
    
    return result


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
