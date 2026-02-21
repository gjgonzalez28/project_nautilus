"""
Project Nautilus: NeMo Guardrails Post-Session Evaluation Module

This module integrates with NeMo Guardrails to:
1. Review entire session transcript after diagnosis completes
2. Evaluate compliance with safety rules (0C.S1, 0C.R19, etc.)
3. Assess evidence quality and diagnostic confidence
4. Generate compliance report and recommendations

Usage:
    from guardrails.post_session_module import SessionEvaluator
    
    evaluator = SessionEvaluator()
    report = evaluator.evaluate_session(
        session_transcript=[...],
        session_state=manager.session,
        diagnostic_result_message=...
    )
"""

import json
from typing import Dict, List, Any, Tuple
from datetime import datetime


class SessionEvaluator:
    """
    Evaluates a completed diagnostic session for safety compliance,
    evidence quality, and recommendation confidence.
    """
    
    def __init__(self):
        """Initialize evaluator with compliance rules."""
        self.compliance_rules = {
            "0C.S1": {
                "name": "High-Voltage Safety",
                "trigger_keywords": ["high voltage", "dmd", "solenoid", "50v"],
                "required_warning": True,
                "severity": "critical"
            },
            "0C.R19": {
                "name": "Coin Door Access Restriction",
                "trigger_keywords": ["coin door", "coin mechanism"],
                "required_restriction": True,
                "severity": "high"
            },
            "0C.R2": {
                "name": "First-Response Gate",
                "required_condition": "Session must start with machine/manufacturer/skill declaration",
                "severity": "critical"
            },
            "0C.R13": {
                "name": "Manual Integrity",
                "required_condition": "Manual links should be provided for flush recommendations",
                "severity": "medium"
            }
        }
        
        self.evidence_quality_weights = {
            "Observed": 10,
            "Manual": 6,
            "Hypothesis": 2
        }
    
    def evaluate_session(
        self,
        session_transcript: List[Dict[str, str]],
        session_state: Any,
        diagnostic_result_message: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluate a complete session for compliance and quality.
        
        Args:
            session_transcript: List of {"role": "user|assistant", "content": "..."} turns
            session_state: SessionState object from manager
            diagnostic_result_message: Final recommendation from system
            
        Returns:
            Comprehensive evaluation report
        """
        
        # Run compliance checks
        compliance_checks = self._check_compliance(session_transcript, session_state)
        
        # Assess evidence quality
        evidence_assessment = self._assess_evidence(session_state)
        
        # Evaluate recommendation confidence
        confidence_assessment = self._assess_confidence(session_state, diagnostic_result_message)
        
        # Generate safety mitigation summary
        safety_summary = self._generate_safety_summary(session_transcript, session_state)
        
        # Compile full report
        report = {
            "session_timestamp": datetime.now().isoformat(),
            "session_summary": {
                "machine": session_state.machine_title,
                "manufacturer": session_state.manufacturer,
                "skill_level": session_state.skill_level,
                "mode": session_state.mode,
                "total_turns": len(session_transcript),
                "current_symptom": session_state.current_symptom
            },
            "compliance": compliance_checks,
            "evidence": evidence_assessment,
            "confidence": confidence_assessment,
            "safety_summary": safety_summary,
            "overall_verdict": self._determine_verdict(
                compliance_checks,
                evidence_assessment,
                confidence_assessment
            ),
            "recommendations_for_improvement": self._generate_recommendations(
                compliance_checks,
                evidence_assessment,
                confidence_assessment
            )
        }
        
        return report
    
    def _check_compliance(
        self,
        transcript: List[Dict[str, str]],
        session_state: Any
    ) -> Dict[str, Any]:
        """Check compliance with all safety and operational rules."""
        checks = {}
        transcript_text = "\n".join([turn.get("content", "") for turn in transcript])
        
        for rule_id, rule_spec in self.compliance_rules.items():
            check_result = {
                "rule_id": rule_id,
                "name": rule_spec.get("name"),
                "severity": rule_spec.get("severity"),
                "status": "PASS",
                "details": ""
            }
            
            # Rule 0C.S1: High-voltage safety
            if rule_id == "0C.S1":
                hv_triggered = any(
                    kw in transcript_text.lower() 
                    for kw in rule_spec["trigger_keywords"]
                )
                hv_warned = "Safety" in transcript_text or "High voltage" in transcript_text
                
                if hv_triggered and not hv_warned:
                    check_result["status"] = "FAIL"
                    check_result["details"] = "High-voltage content mentioned but no safety warning issued"
                elif hv_triggered and hv_warned:
                    check_result["status"] = "PASS"
                    check_result["details"] = "Safety warning properly issued for HV content"
                else:
                    check_result["status"] = "N/A"
                    check_result["details"] = "No HV-related content in session"
            
            # Rule 0C.R19: Coin door restriction
            elif rule_id == "0C.R19":
                coin_door_mentioned = any(
                    kw in transcript_text.lower()
                    for kw in rule_spec["trigger_keywords"]
                )
                coin_door_restricted = "coin door" not in transcript_text.lower() or \
                    "restricted" in transcript_text.lower()
                
                if coin_door_mentioned and not coin_door_restricted:
                    check_result["status"] = "FAIL"
                    check_result["details"] = "Coin door mentioned without access restriction"
                else:
                    check_result["status"] = "PASS"
                    check_result["details"] = "Coin door access properly restricted or not applicable"
            
            # Rule 0C.R2: First-response gate
            elif rule_id == "0C.R2":
                if session_state.skill_declared and session_state.machine_title:
                    check_result["status"] = "PASS"
                    check_result["details"] = "Session properly locked with machine/skill declaration"
                else:
                    check_result["status"] = "FAIL"
                    check_result["details"] = "Session incomplete - missing machine or skill declaration"
            
            # Rule 0C.R13: Manual integrity
            elif rule_id == "0C.R13":
                manual_provided = "manual" in transcript_text.lower() or "pdf" in transcript_text.lower()
                check_result["status"] = "PASS" if manual_provided else "WARN"
                check_result["details"] = "Manual reference" if manual_provided else "No manual provided (Flush recommendations may lack support)"
            
            checks[rule_id] = check_result
        
        return checks
    
    def _assess_evidence(self, session_state: Any) -> Dict[str, Any]:
        """Assess quality and coverage of evidence collected."""
        evidence_summary = session_state.get_evidence_summary()
        total_evidence = len(session_state.evidence_collected)
        
        # Calculate evidence quality score
        quality_score = (
            evidence_summary.get("Observed", 0) * self.evidence_quality_weights["Observed"] +
            evidence_summary.get("Manual", 0) * self.evidence_quality_weights["Manual"] +
            evidence_summary.get("Hypothesis", 0) * self.evidence_quality_weights["Hypothesis"]
        ) / 40.0 * 100  # Normalize to 0-100
        
        # Quality interpretation
        if quality_score >= 80:
            quality_level = "EXCELLENT"
        elif quality_score >= 60:
            quality_level = "GOOD"
        elif quality_score >= 40:
            quality_level = "FAIR"
        else:
            quality_level = "POOR"
        
        return {
            "total_pieces": total_evidence,
            "distribution": evidence_summary,
            "quality_score": round(quality_score, 1),
            "quality_level": quality_level,
            "assessment": {
                "Observed": "Strongest evidence type" if evidence_summary.get("Observed", 0) > 0 else "Not provided",
                "Manual": "Reference documentation" if evidence_summary.get("Manual", 0) > 0 else "Not referenced",
                "Hypothesis": "Technician interpretation" if evidence_summary.get("Hypothesis", 0) > 0 else "Not stated"
            }
        }
    
    def _assess_confidence(
        self,
        session_state: Any,
        diagnostic_result: str = ""
    ) -> Dict[str, Any]:
        """Assess confidence level in the diagnostic result."""
        confidence_score = session_state.symptom_confidence
        
        # Determine confidence level
        if confidence_score >= 75:
            confidence_level = "HIGH"
            verdict = "Proceed with recommended repair"
        elif confidence_score >= 50:
            confidence_level = "MODERATE"
            verdict = "More evidence recommended before proceeding"
        else:
            confidence_level = "LOW"
            verdict = "Clarification needed; inconclusive diagnosis"
        
        return {
            "score": round(confidence_score, 1),
            "level": confidence_level,
            "recommendation": verdict,
            "threshold_beginner": 65,
            "threshold_intermediate": 75,
            "threshold_pro": "N/A (unlimited)"
        }
    
    def _generate_safety_summary(
        self,
        transcript: List[Dict[str, str]],
        session_state: Any
    ) -> Dict[str, Any]:
        """Generate summary of safety-critical interactions."""
        transcript_text = "\n".join([turn.get("content", "") for turn in transcript])
        
        safety_triggers = {
            "high_voltage": "high voltage" in transcript_text.lower() or "dmd" in transcript_text.lower(),
            "solenoid": "solenoid" in transcript_text.lower(),
            "power_supply": "power" in transcript_text.lower(),
            "electrical_work": any(kw in transcript_text.lower() for kw in ["continuity", "ohm", "voltage", "meter"])
        }
        
        triggered_count = sum(1 for v in safety_triggers.values() if v)
        
        return {
            "triggers_present": safety_triggers,
            "trigger_count": triggered_count,
            "risk_level": "HIGH" if triggered_count >= 2 else "MEDIUM" if triggered_count == 1 else "LOW",
            "required_precautions": self._get_precautions(safety_triggers)
        }
    
    def _get_precautions(self, triggers: Dict[str, bool]) -> List[str]:
        """Get list of required precautions based on detected safety triggers."""
        precautions = []
        
        if triggers.get("high_voltage") or triggers.get("solenoid"):
            precautions.append("CRITICAL: Verify power is OFF before proceeding with any electrical work")
        
        if triggers.get("electrical_work"):
            precautions.append("Use proper testing equipment (multimeter, continuity tester)")
            precautions.append("Follow manufacturer's electrical safety guidelines")
        
        if triggers.get("power_supply"):
            precautions.append("Ensure proper grounding and discharge procedures")
        
        if not precautions:
            precautions.append("Standard mechanical repair precautions apply")
        
        return precautions
    
    def _determine_verdict(
        self,
        compliance: Dict,
        evidence: Dict,
        confidence: Dict
    ) -> str:
        """Determine overall session verdict."""
        compliance_pass = all(
            check.get("status") in ["PASS", "N/A"] 
            for check in compliance.values()
        )
        
        evidence_adequate = evidence.get("quality_level") in ["GOOD", "EXCELLENT"]
        confidence_adequate = confidence.get("level") in ["HIGH", "MODERATE"]
        
        if compliance_pass and evidence_adequate and confidence_adequate:
            return "APPROVED_FOR_REPAIR"
        elif compliance_pass and evidence_adequate:
            return "CONDITIONAL_APPROVAL"
        elif compliance_pass:
            return "REQUIRES_MORE_EVIDENCE"
        else:
            return "COMPLIANCE_ISSUES_DETECTED"
    
    def _generate_recommendations(
        self,
        compliance: Dict,
        evidence: Dict,
        confidence: Dict
    ) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Compliance recommendations
        for rule_id, check in compliance.items():
            if check.get("status") == "FAIL":
                recommendations.append(f"ADDRESS: {check['name']} - {check['details']}")
        
        # Evidence recommendations
        if evidence.get("quality_level") == "POOR":
            recommendations.append("EVIDENCE: Collect more strong evidence (measurements, tests) before proceeding")
        
        if evidence["distribution"].get("Observed", 0) == 0:
            recommendations.append("EVIDENCE: Include physical measurements or test results (Observed evidence)")
        
        if evidence["distribution"].get("Manual", 0) == 0:
            recommendations.append("EVIDENCE: Reference manual or schematic to validate findings")
        
        # Confidence recommendations
        if confidence.get("level") == "LOW":
            recommendations.append(f"CONFIDENCE: Current score {confidence['score']:.0f}% is below threshold. Request clarification on symptoms.")
        
        if not recommendations:
            recommendations.append("Session meets all requirements for proceeding with recommended repairs.")
        
        return recommendations
    
    def generate_report_string(self, report: Dict[str, Any]) -> str:
        """Generate a human-readable report string."""
        lines = [
            "=" * 80,
            "PROJECT NAUTILUS: POST-SESSION EVALUATION REPORT",
            "=" * 80,
            f"\nSession Timestamp: {report['session_timestamp']}",
            f"Machine: {report['session_summary']['machine']} ({report['session_summary']['manufacturer']})",
            f"Mode: {report['session_summary']['mode']} | Skill: {report['session_summary']['skill_level']}",
            f"Symptom Diagnosed: {report['session_summary']['current_symptom']}",
            f"Total Conversation Turns: {report['session_summary']['total_turns']}",
            "\n" + "-" * 80,
            "COMPLIANCE REVIEW",
            "-" * 80
        ]
        
        for rule_id, check in report['compliance'].items():
            status_symbol = "[PASS]" if check['status'] == "PASS" else "[FAIL]" if check['status'] == "FAIL" else "[WARN]"
            lines.append(f"{status_symbol} {check['rule_id']} - {check['name']}")
            lines.append(f"           {check['details']}")
        
        lines.extend([
            "\n" + "-" * 80,
            "EVIDENCE ASSESSMENT",
            "-" * 80,
            f"Total Evidence Pieces: {report['evidence']['total_pieces']}",
            f"Quality Distribution:",
            f"  - Observed (strongest): {report['evidence']['distribution']['Observed']} pieces",
            f"  - Manual (medium): {report['evidence']['distribution']['Manual']} pieces",
            f"  - Hypothesis (weakest): {report['evidence']['distribution']['Hypothesis']} pieces",
            f"Quality Score: {report['evidence']['quality_score']:.1f}/100 ({report['evidence']['quality_level']})",
            "\n" + "-" * 80,
            "CONFIDENCE ASSESSMENT",
            "-" * 80,
            f"Diagnostic Confidence: {report['confidence']['score']:.1f}%",
            f"Confidence Level: {report['confidence']['level']}",
            f"Recommendation: {report['confidence']['recommendation']}",
            f"(Thresholds: Beginner={report['confidence']['threshold_beginner']}%, Intermediate={report['confidence']['threshold_intermediate']}%)",
            "\n" + "-" * 80,
            "SAFETY SUMMARY",
            "-" * 80,
            f"Risk Level: {report['safety_summary']['risk_level']}",
            f"Safety Triggers Detected:",
        ])
        
        for trigger, present in report['safety_summary']['triggers_present'].items():
            status = "[TRIGGERED]" if present else "[Not detected]"
            lines.append(f"  {status} {trigger}")
        
        lines.extend([
            "\nRequired Precautions:",
        ])
        
        for precaution in report['safety_summary']['required_precautions']:
            lines.append(f"  - {precaution}")
        
        lines.extend([
            "\n" + "-" * 80,
            "OVERALL VERDICT",
            "-" * 80,
            f"Status: {report['overall_verdict']}",
            "\nRecommendations:",
        ])
        
        for i, rec in enumerate(report['recommendations_for_improvement'], 1):
            lines.append(f"  {i}. {rec}")
        
        lines.append("\n" + "=" * 80)
        
        return "\n".join(lines)


def post_session_handler(
    session_transcript: List[Dict[str, str]],
    manager_instance: Any
) -> Tuple[Dict[str, Any], str]:
    """
    Convenience function for NeMo Guardrails integration.
    
    Args:
        session_transcript: Chat history
        manager_instance: NautilusManager instance
        
    Returns:
        (evaluation_report_dict, report_string)
    """
    evaluator = SessionEvaluator()
    report = evaluator.evaluate_session(
        session_transcript=session_transcript,
        session_state=manager_instance.session,
        diagnostic_result_message=""
    )
    report_string = evaluator.generate_report_string(report)
    
    return report, report_string


if __name__ == "__main__":
    # Example usage
    print("\nNeMo Guardrails Post-Session Module Loaded")
    print("Usage: from guardrails.post_session_module import post_session_handler")
    print("       report, report_string = post_session_handler(transcript, manager)")
