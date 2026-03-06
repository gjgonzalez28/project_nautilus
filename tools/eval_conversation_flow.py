#!/usr/bin/env python3
"""
Project Nautilus: Multi-turn Conversation Evaluator

Purpose:
- Validate turn-by-turn continuity for the live /diagnose API.
- Detect identity-gate loops (Turn 2+ repeating discovery prompt).
- Track checkpoints across runs for regression visibility.

Usage:
    python tools/eval_conversation_flow.py
    python tools/eval_conversation_flow.py --base-url https://project-nautilus-pz7n.onrender.com
    python tools/eval_conversation_flow.py --dry-run
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib import error, request


@dataclass
class TurnExpectation:
    turn: int
    user_message: str
    expect_any: List[str]
    expect_not_any: List[str]
    checkpoint_id: str
    checkpoint_desc: str


@dataclass
class Scenario:
    id: str
    name: str
    turns: List[TurnExpectation]


SCENARIOS: List[Scenario] = [
    Scenario(
        id="identity_to_symptom_progression",
        name="Identity Gate should not repeat on turn 2",
        turns=[
            TurnExpectation(
                turn=1,
                user_message="my right flipper doesnt work",
                expect_any=[
                    "title of your machine",
                    "manufacturer",
                    "skill level",
                ],
                expect_not_any=[],
                checkpoint_id="CP-01",
                checkpoint_desc="Turn 1 triggers identity gate prompt",
            ),
            TurnExpectation(
                turn=2,
                user_message="its an attack from mars by williams and im a beginner",
                expect_any=[
                    "what issue are you experiencing",
                    "got it - sounds like",
                    "let me gather",
                    "thanks! i have enough information",
                ],
                expect_not_any=[
                    "title of your machine",
                    "manufacturer and model if appropriate",
                ],
                checkpoint_id="CP-02",
                checkpoint_desc="Turn 2 advances beyond identity gate",
            ),
            TurnExpectation(
                turn=3,
                user_message="left flipper is weak and slow",
                expect_any=[
                    "let me analyze",
                    "diagnostic",
                    "estimated time",
                    "would you like me to walk through",
                    "what issue are you experiencing",
                ],
                expect_not_any=[
                    "title of your machine",
                    "manufacturer and model if appropriate",
                ],
                checkpoint_id="CP-03",
                checkpoint_desc="Turn 3 remains out of identity loop",
            ),
        ],
    ),
    Scenario(
        id="typo_recovery",
        name="Typo input should still avoid identity loop after turn 1",
        turns=[
            TurnExpectation(
                turn=1,
                user_message="i need help with my pinball amchine",
                expect_any=["title of your machine", "skill level"],
                expect_not_any=[],
                checkpoint_id="CP-04",
                checkpoint_desc="Turn 1 identity gate appears for typo scenario",
            ),
            TurnExpectation(
                turn=2,
                user_message="attack from mars williams beginner",
                expect_any=[
                    "what issue are you experiencing",
                    "got it - sounds like",
                    "let me gather",
                    "thanks! i have enough information",
                ],
                expect_not_any=["title of your machine", "manufacturer and model if appropriate"],
                checkpoint_id="CP-05",
                checkpoint_desc="Turn 2 typo scenario progresses past identity",
            ),
        ],
    ),
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _git_commit() -> str:
    try:
        out = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], stderr=subprocess.DEVNULL)
        return out.decode("utf-8").strip()
    except Exception:
        return "unknown"


def _contains_any(text: str, phrases: List[str]) -> Optional[str]:
    text_l = text.lower()
    for phrase in phrases:
        if phrase.lower() in text_l:
            return phrase
    return None


def _post_diagnose(base_url: str, message: str, trace_id: Optional[str], timeout: int) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"message": message}
    if trace_id:
        payload["trace_id"] = trace_id

    req = request.Request(
        url=f"{base_url.rstrip('/')}/diagnose",
        method="POST",
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload).encode("utf-8"),
    )

    try:
        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body)
            return {
                "ok": True,
                "status": resp.getcode(),
                "data": data,
            }
    except error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        parsed: Any
        try:
            parsed = json.loads(body) if body else {}
        except Exception:
            parsed = {"raw": body}
        return {
            "ok": False,
            "status": e.code,
            "error": parsed,
        }
    except Exception as e:
        return {
            "ok": False,
            "status": None,
            "error": {"message": str(e)},
        }


def evaluate_scenario(base_url: str, timeout: int, scenario: Scenario, dry_run: bool = False) -> Dict[str, Any]:
    trace_id: Optional[str] = None
    turn_results: List[Dict[str, Any]] = []
    checkpoints: List[Dict[str, Any]] = []

    for turn_cfg in scenario.turns:
        if dry_run:
            response_text = "[DRY RUN] plumbing check"
            api_result = {"ok": True, "status": 200, "data": {"response": response_text, "trace_id": "dry-run-trace"}}
        else:
            api_result = _post_diagnose(base_url, turn_cfg.user_message, trace_id, timeout)

        passed = True
        fail_reasons: List[str] = []
        matched_expected: Optional[str] = None

        if api_result["ok"]:
            data = api_result.get("data", {})
            response_text = str(data.get("response", ""))
            trace_id = data.get("trace_id", trace_id)

            if not dry_run:
                if turn_cfg.expect_any:
                    matched_expected = _contains_any(response_text, turn_cfg.expect_any)
                    if not matched_expected:
                        passed = False
                        fail_reasons.append("expected_text_missing")

                if turn_cfg.expect_not_any:
                    forbidden_hit = _contains_any(response_text, turn_cfg.expect_not_any)
                    if forbidden_hit:
                        passed = False
                        fail_reasons.append(f"forbidden_text_found:{forbidden_hit}")
        else:
            response_text = json.dumps(api_result.get("error", {}), ensure_ascii=False)
            passed = False
            fail_reasons.append("api_error")

        checkpoint = {
            "checkpoint_id": turn_cfg.checkpoint_id,
            "description": turn_cfg.checkpoint_desc,
            "turn": turn_cfg.turn,
            "passed": passed,
            "reasons": fail_reasons,
            "matched_expected": matched_expected,
        }

        turn_results.append(
            {
                "turn": turn_cfg.turn,
                "user_message": turn_cfg.user_message,
                "api_ok": api_result["ok"],
                "status": api_result["status"],
                "trace_id": trace_id,
                "response": response_text,
                "checkpoint": checkpoint,
            }
        )
        checkpoints.append(checkpoint)

    passed_all = all(c["passed"] for c in checkpoints)

    return {
        "scenario_id": scenario.id,
        "scenario_name": scenario.name,
        "passed": passed_all,
        "final_trace_id": trace_id,
        "checkpoints": checkpoints,
        "turn_results": turn_results,
    }


def save_artifacts(save_dir: Path, payload: Dict[str, Any]) -> Dict[str, str]:
    save_dir.mkdir(parents=True, exist_ok=True)

    latest_file = save_dir / "eval_results_latest.json"
    history_file = save_dir / "eval_history.jsonl"
    checkpoints_file = save_dir / "eval_checkpoints_latest.json"

    latest_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    history_file.parent.mkdir(parents=True, exist_ok=True)
    with history_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    checkpoint_summary = {
        "run_id": payload.get("run_id"),
        "timestamp": payload.get("timestamp"),
        "checkpoints": [
            cp
            for scenario in payload.get("scenarios", [])
            for cp in scenario.get("checkpoints", [])
        ],
    }
    checkpoints_file.write_text(json.dumps(checkpoint_summary, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "latest": str(latest_file),
        "history": str(history_file),
        "checkpoints": str(checkpoints_file),
    }


def print_summary(result: Dict[str, Any]) -> None:
    print("=" * 88)
    print("PROJECT NAUTILUS - MULTI-TURN EVAL")
    print("=" * 88)
    print(f"Run ID:    {result['run_id']}")
    print(f"Commit:    {result['commit']}")
    print(f"Base URL:  {result['base_url']}")
    if result.get("dry_run"):
        print("Mode:      DRY RUN (checkpoint matching skipped)")
    print(f"Timestamp: {result['timestamp']}")
    print("-" * 88)

    total_cp = 0
    passed_cp = 0

    for scenario in result["scenarios"]:
        status = "PASS" if scenario["passed"] else "FAIL"
        print(f"[{status}] {scenario['scenario_name']} ({scenario['scenario_id']})")
        print(f"       Trace ID: {scenario.get('final_trace_id')}")

        for cp in scenario["checkpoints"]:
            total_cp += 1
            if cp["passed"]:
                passed_cp += 1
                print(f"       ✅ {cp['checkpoint_id']} T{cp['turn']}: {cp['description']}")
            else:
                print(f"       ❌ {cp['checkpoint_id']} T{cp['turn']}: {cp['description']} -> {', '.join(cp['reasons'])}")

    print("-" * 88)
    print(f"Checkpoint pass rate: {passed_cp}/{total_cp}")
    print(f"Overall: {'PASS' if result['passed'] else 'FAIL'}")
    print("=" * 88)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate multi-turn conversation continuity for Nautilus.")
    parser.add_argument("--base-url", default="http://localhost:5000", help="Base API URL (default: http://localhost:5000)")
    parser.add_argument("--timeout", type=int, default=45, help="HTTP timeout in seconds")
    parser.add_argument("--save-dir", default="logs", help="Directory for eval artifacts")
    parser.add_argument("--dry-run", action="store_true", help="Do not call API; simulate responses")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    run_id = f"eval-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6]}"

    scenario_results = [
        evaluate_scenario(args.base_url, args.timeout, scenario, dry_run=args.dry_run)
        for scenario in SCENARIOS
    ]

    passed = all(s["passed"] for s in scenario_results)

    result_payload = {
        "run_id": run_id,
        "timestamp": _now_iso(),
        "commit": _git_commit(),
        "base_url": args.base_url,
        "dry_run": args.dry_run,
        "passed": passed,
        "scenarios": scenario_results,
    }

    artifact_paths = save_artifacts(Path(args.save_dir), result_payload)
    result_payload["artifacts"] = artifact_paths

    print_summary(result_payload)
    print(f"Artifacts: {artifact_paths}")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
