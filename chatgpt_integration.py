"""
Project Nautilus: ChatGPT Integration Wrapper

This module provides ChatGPT-compatible functions for running Nautilus
diagnostics while maintaining session state and returning structured responses.

Usage in ChatGPT:
  1. Copy this module's functions as ChatGPT function definitions
  2. Call nautilus_ask() in conversation
  3. Session state persists across turns
"""

import json
import time
from typing import Dict, Any, Tuple
from logic.manager import NautilusManager
from logic.discovery_script import DiscoveryScript
from guardrails.post_session_module import post_session_handler

# Global session manager (persists across function calls)
_nautilus_session = None
_discovery_script = None
_conversation_transcript = []


def initialize_session() -> Dict[str, Any]:
    """
    Initialize a new Nautilus session.
    Should be called at the start of conversation.
    
    Returns:
        {"status": "initialized", "message": "Ready for diagnosis"}
    """
    global _nautilus_session, _discovery_script, _conversation_transcript
    
    _nautilus_session = NautilusManager()
    _discovery_script = DiscoveryScript(_nautilus_session)
    _conversation_transcript = []
    
    return {
        "status": "initialized",
        "message": "Project Nautilus initialized. Please tell me about your machine and skill level.",
        "session_id": id(_nautilus_session)
    }


def nautilus_ask(user_message: str) -> Dict[str, Any]:
    """
    Main interaction endpoint for diagnostic conversation.
    
    Args:
        user_message: User's message/question/observation
        
    Returns:
        {"response": str, "status": str, "mode": str}
    """
    global _nautilus_session, _discovery_script, _conversation_transcript
    
    # Auto-initialize if needed
    if _nautilus_session is None:
        initialize_session()
    
    _conversation_transcript.append({
        "role": "user",
        "message": user_message,
        "timestamp": time.time()
    })
    
    # Use discovery script if machine not yet identified or playfield confirmation pending
    if (not _nautilus_session.session.skill_declared or
            _nautilus_session.session.awaiting_playfield_confirmation):
        response = _discovery_script.process_initial_response(user_message)
    else:
        response = _nautilus_session.ask(user_message)
    
    _conversation_transcript.append({
        "role": "assistant",
        "message": response,
        "timestamp": time.time()
    })
    
    # Strip debug tags before returning to Nautilus GPT
    clean_response = _strip_debug_tags(response)
    
    return {
        "response": clean_response,
        "status": "ok",
        "mode": _nautilus_session.session.mode
    }


def _strip_debug_tags(response: str) -> str:
    """
    Remove internal debug tags from manager output.
    Removes: [PD ...], [STRAIGHT ...], [TRUE ...], [FLUSH ...], [BRANCHES], [GATE BLOCKED]
    Keeps the actual diagnostic content.
    """
    lines = []
    for line in response.splitlines():
        # Skip lines that are purely debug tags
        if line.strip().startswith("[PD ") and "MODE]" in line:
            continue
        if line.strip().startswith("[STRAIGHT"):
            continue
        if line.strip().startswith("[TRUE"):
            continue
        if line.strip().startswith("[FLUSH"):
            continue
        if line.strip().startswith("[BRANCHES"):
            continue
        if line.strip().startswith("[GATE BLOCKED"):
            continue
        
        lines.append(line)
    
    # Join and clean up excess whitespace
    cleaned = "\n".join(lines).strip()
    return cleaned


def nautilus_end_session() -> Dict[str, Any]:
    """
    End session and generate post-session compliance report.
    
    Returns:
        {
            "report": {...},
            "verdict": "APPROVED_FOR_REPAIR|CONDITIONAL_APPROVAL|REQUIRES_MORE_EVIDENCE|COMPLIANCE_ISSUES",
            "recommendations": [list of recommendations],
            "transcript_saved": bool
        }
    """
    global _nautilus_session, _conversation_transcript
    
    if _nautilus_session is None:
        return {
            "status": "error",
            "message": "No active session to end"
        }
    
    # Generate post-session report
    report, report_string = post_session_handler(
        session_transcript=_conversation_transcript,
        manager_instance=_nautilus_session
    )
    
    result = {
        "status": "session_ended",
        "verdict": report["overall_verdict"],
        "compliance": {
            rule_id: check["status"] 
            for rule_id, check in report["compliance"].items()
        },
        "evidence_quality": report["evidence"]["quality_level"],
        "confidence_score": report["confidence"]["score"],
        "recommendations": report["recommendations_for_improvement"],
        "safety_summary": report["safety_summary"],
        "report_text": report_string
    }
    
    return result


def nautilus_get_session_state() -> Dict[str, Any]:
    """
    Get current session state without processing new input.
    Useful for checking status mid-conversation.
    
    Returns:
        Full session state snapshot
    """
    global _nautilus_session
    
    if _nautilus_session is None:
        return {"status": "error", "message": "No active session"}
    
    session = _nautilus_session.session
    
    return {
        "machine_title": session.machine_title,
        "manufacturer": session.manufacturer,
        "skill_level": session.skill_level,
        "mode": session.mode,
        "skill_declared": session.skill_declared,
        "current_symptom": session.current_symptom,
        "symptom_confidence": session.symptom_confidence,
        "evidence_collected": [
            {
                "type": e["type"],
                "text": e["text"][:100] + "..." if len(e["text"]) > 100 else e["text"],
                "symptom": e["symptom"]
            }
            for e in session.evidence_collected
        ],
        "evidence_summary": session.get_evidence_summary(),
        "conversation_turns": len(_conversation_transcript)
    }


def nautilus_set_test_mode(mode: str) -> Dict[str, Any]:
    """
    Manually set the skill mode for testing (Beginner|Intermediate|Pro).
    Bypasses discovery for faster testing.
    
    Args:
        mode: "beginner" | "intermediate" | "pro"
        
    Returns:
        {"status": "mode_set", "mode": mode}
    """
    global _nautilus_session, _discovery_script
    
    if _nautilus_session is None:
        initialize_session()
    
    # Set test mode directly
    mode_lower = mode.lower()
    if mode_lower not in ["beginner", "intermediate", "pro"]:
        return {"status": "error", "message": f"Invalid mode: {mode}"}
    
    # Lock session with test values
    _nautilus_session.session.lock_session(
        machine_title="Test Machine",
        manufacturer="Test Manufacturer",
        skill_level=mode_lower,
        mode=mode_lower
    )
    _nautilus_session.session.awaiting_playfield_confirmation = False
    _nautilus_session.session.playfield_access_confirmed = True
    _discovery_script.awaiting_discovery = False
    
    # Add to transcript for reference
    _conversation_transcript.append({
        "role": "system",
        "content": f"[TEST MODE] Skill level set to: {mode_lower}"
    })
    
    return {
        "status": "mode_set",
        "mode": mode_lower,
        "message": f"Test mode activated: {mode_lower.upper()} skill level"
    }


def nautilus_reset() -> Dict[str, Any]:
    """
    Reset session completely (start fresh).
    
    Returns:
        {"status": "reset_complete"}
    """
    global _nautilus_session, _discovery_script, _conversation_transcript
    
    _nautilus_session = None
    _discovery_script = None
    _conversation_transcript = []
    
    return {
        "status": "reset_complete",
        "message": "Session reset. Ready for new diagnosis."
    }


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _categorize_response(response: str) -> str:
    """Categorize response type from response text."""
    response_lower = response.lower()
    
    if "safety" in response_lower or "high voltage" in response_lower:
        return "safety_warning"
    elif "clarif" in response_lower or "more information" in response_lower:
        return "clarify"
    elif "i don't have enough" in response_lower or "need at least" in response_lower:
        return "stop"
    elif "didn't recognize" in response_lower:
        return "unknown_symptom"
    else:
        return "diagnostic"


def _extract_safety_warnings(response: str) -> list:
    """Extract safety warnings from response."""
    warnings = []
    response_lower = response.lower()
    
    if "high voltage" in response_lower:
        warnings.append("HIGH_VOLTAGE_RISK")
    if "power" in response_lower and "off" in response_lower:
        warnings.append("POWER_OFF_REQUIRED")
    if "solenoid" in response_lower:
        warnings.append("SOLENOID_WORK")
    if "dmd" in response_lower:
        warnings.append("DMD_HIGH_VOLTAGE")
    
    return warnings


# ============================================================================
# CHATGPT FUNCTION DEFINITIONS
# ============================================================================

CHATGPT_FUNCTIONS = [
    {
        "name": "initialize_nautilus_session",
        "description": "Initialize a new Project Nautilus diagnostic session",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "nautilus_ask",
        "description": "Send a message to Project Nautilus and get diagnostic response",
        "parameters": {
            "type": "object",
            "properties": {
                "user_message": {
                    "type": "string",
                    "description": "Your question or statement about the pinball machine"
                }
            },
            "required": ["user_message"]
        }
    },
    {
        "name": "nautilus_get_session_state",
        "description": "Get current session state (machine, symptom, evidence, confidence)",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "nautilus_set_test_mode",
        "description": "Set skill level directly for testing (bypasses discovery)",
        "parameters": {
            "type": "object",
            "properties": {
                "mode": {
                    "type": "string",
                    "enum": ["beginner", "intermediate", "pro"],
                    "description": "Skill level to test"
                }
            },
            "required": ["mode"]
        }
    },
    {
        "name": "nautilus_end_session",
        "description": "End session and generate compliance report",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "nautilus_reset",
        "description": "Reset session completely",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]


if __name__ == "__main__":
    print("\n" + "="*70)
    print("PROJECT NAUTILUS: CHATGPT INTEGRATION MODULE")
    print("="*70)
    print("\nAvailable functions for ChatGPT:")
    for func in CHATGPT_FUNCTIONS:
        print(f"  - {func['name']}")
    print("\nCopy CHATGPT_FUNCTIONS to your ChatGPT custom instructions.")
    print("\nQuick test:")
    initialize_session()
    result = nautilus_ask("I have a Williams Medieval Madness and I'm intermediate skill")
    print(f"\nResponse: {result['response']}")
    print(f"Status: Session locked={result['session_locked']}")
