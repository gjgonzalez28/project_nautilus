"""
Project Nautilus: Structured JSON Logging

Provides centralized logging with trace ID correlation across all components.
Every log entry is JSON for easy parsing and analysis.

Usage:
    from app_logging.logger import get_logger
    logger = get_logger(__name__)
    
    logger.log_event("flow_transition", {
        "from_flow": "discovery_gate",
        "to_flow": "playfield_gate",
        "reason": "user_affirmed_machine_identification"
    })
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
import uuid


class NautilusJSONFormatter(logging.Formatter):
    """Format logs as structured JSON for parsing and analysis."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Convert log record to JSON."""
        log_object = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "trace_id": getattr(record, "trace_id", None),
            "turn_number": getattr(record, "turn_number", None),
            "component": getattr(record, "component", None),
            "event": getattr(record, "event", None),
            "data": getattr(record, "data", None),
        }
        
        # Remove None values to keep JSON clean
        log_object = {k: v for k, v in log_object.items() if v is not None}
        
        return json.dumps(log_object)


def setup_logging(log_dir: str = "logs", log_level: str = "INFO") -> None:
    """
    Configure centralized logging for the entire project.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
    """
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Create formatters
    json_formatter = NautilusJSONFormatter()
    
    # Create file handler (JSON logs)
    log_file = log_path / f"nautilus-{datetime.now().strftime('%Y-%m-%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(getattr(logging, log_level))
    file_handler.setFormatter(json_formatter)
    
    # Create console handler (pretty for humans)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    console_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)


class StructuredLogger:
    """Wrapper for structured logging with trace context."""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.trace_id = None
        self.turn_number = 0
    
    def set_trace_id(self, trace_id: Optional[str] = None) -> str:
        """Set or generate trace ID for correlation."""
        if trace_id is None:
            trace_id = f"conv_{uuid.uuid4().hex[:12]}"
        self.trace_id = trace_id
        return trace_id
    
    def increment_turn(self) -> None:
        """Increment turn counter."""
        self.turn_number += 1
    
    def log_event(
        self,
        event: str,
        data: Dict[str, Any],
        component: str = "",
        level: str = "INFO"
    ) -> None:
        """
        Log a structured event.
        
        Args:
            event: Event type (e.g., "flow_transition", "state_update")
            data: Event data (dict)
            component: Component that generated event
            level: Log level (DEBUG, INFO, WARNING, ERROR)
        """
        record = self.logger.makeRecord(
            name=self.logger.name,
            level=getattr(logging, level),
            fn="",
            lno=0,
            msg="",
            args=(),
            exc_info=None
        )
        
        # Attach structured data
        record.trace_id = self.trace_id
        record.turn_number = self.turn_number if self.turn_number > 0 else None
        record.component = component
        record.event = event
        record.data = data
        
        # Log at appropriate level
        self.logger.handle(record)
    
    def log_state_change(
        self,
        variable: str,
        old_value: Any,
        new_value: Any,
        reason: str = ""
    ) -> None:
        """Log a state variable change."""
        self.log_event(
            event="state_change",
            data={
                "variable": variable,
                "old_value": old_value,
                "new_value": new_value,
                "reason": reason
            },
            component="session_state"
        )
    
    def log_flow_transition(
        self,
        from_flow: str,
        to_flow: str,
        reason: str = "",
        condition: str = ""
    ) -> None:
        """Log a NeMo flow transition."""
        self.log_event(
            event="flow_transition",
            data={
                "from_flow": from_flow,
                "to_flow": to_flow,
                "reason": reason,
                "condition": condition
            },
            component="nemo_router"
        )
    
    def log_gate_evaluation(
        self,
        gate_name: str,
        condition: str,
        passed: bool,
        data: Dict[str, Any]
    ) -> None:
        """Log gate evaluation result."""
        self.log_event(
            event="gate_evaluation",
            data={
                "gate": gate_name,
                "condition": condition,
                "passed": passed,
                "details": data
            },
            component="nemo_gates"
        )
    
    def log_intent_recognition(
        self,
        user_text: str,
        matched_intent: str,
        confidence: float,
        alternatives: list = None
    ) -> None:
        """Log intent recognition result."""
        self.log_event(
            event="intent_recognition",
            data={
                "user_text": user_text[:100],  # Truncate for logs
                "matched_intent": matched_intent,
                "confidence": confidence,
                "alternatives": alternatives or []
            },
            component="nemo_intent_recognizer"
        )
    
    def log_python_boundary_call(
        self,
        function_name: str,
        args: Dict[str, Any],
        result: Any,
        execution_time_ms: float
    ) -> None:
        """Log NeMo → Python utility function call."""
        self.log_event(
            event="python_function_call",
            data={
                "function": function_name,
                "args": args,
                "result": result,
                "execution_time_ms": execution_time_ms
            },
            component="nemo_python_bridge"
        )
    
    def log_llm_call(
        self,
        prompt: str,
        response: str,
        model: str = "gpt-4",
        execution_time_ms: float = 0
    ) -> None:
        """Log LLM API call."""
        self.log_event(
            event="llm_call",
            data={
                "model": model,
                "prompt_length": len(prompt),
                "response_length": len(response),
                "execution_time_ms": execution_time_ms
            },
            component="llm_interface"
        )


def get_logger(name: str) -> StructuredLogger:
    """Get a structured logger instance."""
    return StructuredLogger(name)
