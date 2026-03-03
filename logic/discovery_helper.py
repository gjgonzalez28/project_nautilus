"""
Project Nautilus: Discovery Helper

Fuzzy matching utilities for machine discovery.
Matches user input against machine_library.json to extract:
  - machine_name (user's description)
  - manufacturer (from library match)
  - era (from library match)
  - skill_level (beginner, intermediate, or pro)

Used by discovery.co Colang flow during Phase 3 machine identification.
"""

import json
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, Any, Optional
from app_logging.logger import StructuredLogger

logger = StructuredLogger(__name__)


def load_machine_library() -> list[Dict[str, Any]]:
    """Load machine_library.json from data directory."""
    library_path = Path(__file__).parent.parent / "data" / "machine_library.json"
    
    try:
        with open(library_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.log_event(
            event="machine_library_load_failed",
            data={"error": str(e)},
            component="discovery_helper"
        )
        return []


def fuzzy_match_machine(user_input: str, threshold: float = 0.6) -> Dict[str, Any]:
    """
    Fuzzy match user input against machine library.
    
    Args:
        user_input: User's description of the pinball machine
        threshold: Similarity score threshold (0.0-1.0), default 0.6
    
    Returns:
        Dict with:
          - matched: bool (True if match found above threshold)
          - machine_id: str (library ID, e.g., "EM_COMMON")
          - era: str (e.g., "EM", "Solid State Early")
          - manufacturer: str (e.g., "Bally")
          - confidence: float (similarity score 0.0-1.0)
          - error: str (if matched=False)
    """
    library = load_machine_library()
    
    if not library:
        return {
            "matched": False,
            "error": "Machine library not found"
        }
    
    user_input_lower = user_input.lower()
    best_match = None
    best_score = 0.0
    
    # Search by machine name and era keywords
    for machine in library:
        machine_name = machine.get("name", "").lower()
        machine_era = machine.get("era", "").lower()
        
        # Score: similarity to machine name
        name_score = SequenceMatcher(None, user_input_lower, machine_name).ratio()
        
        # Bonus if era keyword found in input
        era_score = 0.0
        if machine_era in user_input_lower:
            era_score = 0.3  # Bonus for era match
        
        total_score = (name_score * 0.7) + era_score
        
        if total_score > best_score:
            best_score = total_score
            best_match = machine
    
    if best_score >= threshold and best_match:
        result = {
            "matched": True,
            "machine_id": best_match.get("id"),
            "era": best_match.get("era"),
            "manufacturer": best_match.get("manufacturer"),
            "confidence": round(best_score, 2),
            "machine_name": user_input  # Keep user's original phrasing
        }
        
        logger.log_event(
            event="machine_matched",
            data={
                "user_input": user_input,
                "matched_machine": best_match.get("id"),
                "confidence": best_score
            },
            component="discovery_helper"
        )
        
        return result
    else:
        return {
            "matched": False,
            "user_input": user_input,
            "best_score": round(best_score, 2),
            "error": f"No machine match above {threshold} threshold"
        }


def validate_skill_level(user_input: str) -> Dict[str, Any]:
    """
    Validate and extract skill level from user input.
    
    Args:
        user_input: User's description (e.g., "I'm a beginner", "advanced user", "pro")
    
    Returns:
        Dict with:
          - valid: bool
          - skill_level: str ("beginner", "intermediate", or "pro")
          - confidence: float (0.0-1.0)
    """
    user_lower = user_input.lower()
    
    # Skill level keywords
    beginner_keywords = ["beginner", "new", "novice", "first time", "don't know", "learning"]
    intermediate_keywords = ["intermediate", "experienced", "handy", "comfortable", "basic knowledge"]
    pro_keywords = ["pro", "advanced", "expert", "professional", "experienced technician", "tech savvy"]
    
    skill_scores = {
        "beginner": 0.0,
        "intermediate": 0.0,
        "pro": 0.0
    }
    
    # Score each skill level based on keyword presence
    for keyword in beginner_keywords:
        if keyword in user_lower:
            skill_scores["beginner"] += 0.5
    
    for keyword in intermediate_keywords:
        if keyword in user_lower:
            skill_scores["intermediate"] += 0.5
    
    for keyword in pro_keywords:
        if keyword in user_lower:
            skill_scores["pro"] += 0.5
    
    # Find best match
    best_skill = max(skill_scores, key=skill_scores.get)
    confidence = skill_scores[best_skill]
    
    result = {
        "valid": confidence > 0.0,
        "skill_level": best_skill if confidence > 0.0 else None,
        "confidence": round(confidence, 2),
        "user_input": user_input
    }
    
    logger.log_event(
        event="skill_level_extracted",
        data={
            "skill_level": result.get("skill_level"),
            "confidence": result.get("confidence"),
            "user_input": user_input
        },
        component="discovery_helper"
    )
    
    return result
