#!/usr/bin/env python
"""
Project Nautilus: Session Inspector

View the state of any session from logs.
Shows all variables, evidence, state changes in a readable format.

Usage:
    python tools/inspect_session.py --trace-id conv_abc123
    python tools/inspect_session.py --latest
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import argparse

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


def load_logs(log_dir="logs"):
    """Load all logs from directory."""
    log_path = Path(log_dir)
    logs = []
    
    if not log_path.exists():
        print(f"Log directory {log_dir} not found")
        return logs
    
    for log_file in sorted(log_path.glob("*.log"), reverse=True):
        with open(log_file) as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue  # Skip malformed lines
    
    return logs


def filter_by_trace_id(logs, trace_id):
    """Filter logs by trace ID."""
    return [log for log in logs if log.get("trace_id") == trace_id]


def get_latest_trace_id(logs):
    """Get the most recent trace ID."""
    if not logs:
        return None
    
    trace_ids = {}
    for log in logs:
        trace_id = log.get("trace_id")
        if trace_id:
            if trace_id not in trace_ids:
                trace_ids[trace_id] = log.get("timestamp")
    
    if not trace_ids:
        return None
    
    return max(trace_ids.items(), key=lambda x: x[1])[0]


def format_trace(logs):
    """Format trace logs for human reading."""
    if not logs:
        print("No logs found for this trace.")
        return
    
    # Group by type
    state_changes = [l for l in logs if l.get("event") == "state_change"]
    flow_transitions = [l for l in logs if l.get("event") == "flow_transition"]
    gates = [l for l in logs if l.get("event") == "gate_evaluation"]
    intents = [l for l in logs if l.get("event") == "intent_recognition"]
    
    trace_id = logs[0].get("trace_id", "unknown")
    print("\n" + "=" * 80)
    print(f"TRACE: {trace_id}")
    print("=" * 80)
    
    # Summary
    print(f"\nTurns: {max([l.get('turn_number') or 0 for l in logs])}")
    print(f"Total events: {len(logs)}")
    print(f"State changes: {len(state_changes)}")
    print(f"Flow transitions: {len(flow_transitions)}")
    print(f"Gate evaluations: {len(gates)}")
    print(f"Intent recognitions: {len(intents)}")
    
    # State changes
    if state_changes:
        print("\n" + "-" * 80)
        print("STATE CHANGES:")
        print("-" * 80)
        for log in state_changes:
            data = log.get("data", {})
            var = data.get("variable")
            old = data.get("old_value")
            new = data.get("new_value")
            reason = data.get("reason")
            
            print(f"  Turn {log.get('turn_number')}: {var}")
            print(f"    {old} → {new}")
            if reason:
                print(f"    Reason: {reason}")
    
    # Flow transitions
    if flow_transitions:
        print("\n" + "-" * 80)
        print("FLOW TRANSITIONS:")
        print("-" * 80)
        for log in flow_transitions:
            data = log.get("data", {})
            from_flow = data.get("from_flow")
            to_flow = data.get("to_flow")
            reason = data.get("reason", "")
            
            print(f"  {from_flow} → {to_flow}")
            if reason:
                print(f"    {reason}")
    
    # Gates
    if gates:
        print("\n" + "-" * 80)
        print("GATE EVALUATIONS:")
        print("-" * 80)
        for log in gates:
            data = log.get("data", {})
            gate = data.get("gate")
            passed = "PASS" if data.get("passed") else "FAIL"
            condition = data.get("condition", "")
            
            print(f"  [{passed}] {gate}")
            if condition:
                print(f"    Condition: {condition}")
    
    # Intents
    if intents:
        print("\n" + "-" * 80)
        print("INTENT RECOGNITIONS:")
        print("-" * 80)
        for log in intents:
            data = log.get("data", {})
            user_text = data.get("user_text")
            intent = data.get("matched_intent")
            confidence = data.get("confidence")
            
            print(f"  Turn {log.get('turn_number')}: {intent} ({confidence:.2%})")
            print(f"    User: {user_text[:60]}...")
    
    print("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Inspect Project Nautilus session state")
    parser.add_argument("--trace-id", help="Trace ID to inspect")
    parser.add_argument("--latest", action="store_true", help="Inspect latest trace")
    parser.add_argument("--log-dir", default="logs", help="Log directory")
    
    args = parser.parse_args()
    
    # Load logs
    logs = load_logs(args.log_dir)
    if not logs:
        print("No logs found.")
        return 1
    
    # Determine which trace to show
    trace_id = args.trace_id
    if args.latest and not trace_id:
        trace_id = get_latest_trace_id(logs)
    
    if not trace_id:
        print("No trace found. Use --trace-id or --latest")
        return 1
    
    # Filter and display
    trace_logs = filter_by_trace_id(logs, trace_id)
    format_trace(trace_logs)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
