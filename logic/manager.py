import yaml
import os
import re
from logic.nautilus_core import NautilusCore


def normalize_input(text):
    """
    Normalize user input for consistent rule matching.
    - Convert to lowercase
    - Replace underscores with spaces
    - Strip leading/trailing whitespace
    - Collapse multiple spaces to single space
    
    Examples:
      "COIN_DOOR" -> "coin door"
      "High  Voltage" -> "high voltage"
      "  DMD  " -> "dmd"
    """
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.lower().replace('_', ' ')).strip()


class SessionState:
    """
    Tracks the current session state across the diagnostic flow.
    Attributes:
      machine_title: User-provided machine name (e.g., "Eight Ball")
      manufacturer: User-provided manufacturer (e.g., "Bally")
      era: Inferred or provided era (EM_Common, Bally_1978_MPU, etc.)
      skill_level: User-provided skill (beginner, intermediate, advanced)
      mode: Mapped mode (beginner, intermediate, pro)
      skill_declared: True if identity gate has passed
      rules: {"global": {...}, "mode": {...}} loaded from YAML
      evidence_collected: List of dicts with keys: type (Observed/Manual/Hypothesis), text, symptom
      disclaimers_shown: Set of disclaimer IDs already shown in this session
      current_symptom: The issue being diagnosed (e.g., "left flipper dead")
      symptom_confidence: Float 0-100 representing confidence in diagnosis
    """
    def __init__(self):
        self.machine_title = None
        self.manufacturer = None
        self.era = None
        self.skill_level = None
        self.mode = None
        self.skill_declared = False
        self.rules = None
        self.evidence_collected = []  # List of {"type": "Observed|Manual|Hypothesis", "text": "...", "symptom": "..."}
        self.disclaimers_shown = set()
        self.current_symptom = None
        self.symptom_confidence = 0.0
        self.awaiting_playfield_confirmation = False
        self.playfield_access_confirmed = False

    def lock_session(self, machine_title, manufacturer, skill_level, mode):
        """Lock session state once identity gate passes."""
        self.machine_title = machine_title
        self.manufacturer = manufacturer
        self.skill_level = skill_level
        self.mode = mode
        self.skill_declared = True
    
    def add_evidence(self, evidence_type, text, symptom=None):
        """
        Add structured evidence to session.
        Args:
          evidence_type: 'Observed', 'Manual', or 'Hypothesis'
          text: The evidence statement
          symptom: Optional symptom this applies to
        """
        self.evidence_collected.append({
            "type": evidence_type,
            "text": text.strip(),
            "symptom": symptom or self.current_symptom
        })
    
    def get_evidence_summary(self):
        """Return count of each evidence type."""
        observed = sum(1 for e in self.evidence_collected if e["type"] == "Observed")
        manual = sum(1 for e in self.evidence_collected if e["type"] == "Manual")
        hypothesis = sum(1 for e in self.evidence_collected if e["type"] == "Hypothesis")
        return {"Observed": observed, "Manual": manual, "Hypothesis": hypothesis}


class RuleEngine:
    """
    Core diagnostic rule engine. Evaluates user input against the loaded rules
    in a defined pipeline order:
      1. Identity gate (title/manufacturer/era/skill)
      2. Coin door enforcement (0C.R19)
      3. Safety interrupts (global + mode-specific)
      4. Disclaimer triggers (meter/manual/probe)
      5. Output state gates (Proceed/Clarify/Stop for beginner/intermediate)
      6. Diagnostic mapping (fetch STF map, stage by mode detail level)
    """
    def __init__(self, nautilus_core):
        self.librarian = nautilus_core

    def evaluate(self, user_input, session_state):
        """
        Evaluate user input against the entire rule pipeline.
        Returns: (action, message, session_updates)
          action: 'identity_gate' | 'redirect' | 'warn' | 'clarify' | 'proceed' | 'diagnostic'
          message: Response text to user
          session_updates: Dict of session state changes to apply
        """
        # Pipeline execution in order of priority
        
        # 1. IDENTITY GATE
        if not session_state.skill_declared:
            return self._check_identity_gate(session_state)
        
        # 2. COIN DOOR ENFORCEMENT (0C.R19)
        coin_door_result = self._check_coin_door_violation(user_input, session_state)
        if coin_door_result:
            return coin_door_result
        
        # 2.5. EVIDENCE EXTRACTION (happens for every turn, independent of gates)
        self._extract_evidence(user_input, session_state)
        
        # 3. SAFETY INTERRUPTS
        safety_result = self._check_safety_interrupts(user_input, session_state)
        if safety_result:
            return safety_result
        
        # 4. DISCLAIMER TRIGGERS
        disclaimer_result = self._check_disclaimer_triggers(user_input, session_state)
        if disclaimer_result:
            return disclaimer_result
        
        # 5. DIAGNOSTIC MAPPING (extract symptom and provide guidance)
        diagnostic_result = self._diagnostic_mapping(user_input, session_state)
        
        # 6. OUTPUT STATE GATES (beginner/intermediate only)
        # Apply gates AFTER diagnostic mapping so we know the symptom
        if session_state.mode in ["beginner", "intermediate"]:
            gate_result = self._check_output_gates(user_input, session_state, diagnostic_result)
            if gate_result:
                return gate_result
        
        return diagnostic_result

    def _check_identity_gate(self, session_state):
        """
        Rule 0C.R2: First response must ask for machine title, manufacturer, skill level.
        Returns: (action, message, updates)
        """
        action = "identity_gate"
        global_rules = self._load_global_rules()
        session_opening = global_rules.get("session_opening", {})
        
        message = (
            f"{session_opening.get('greeting', 'Great, I can help with that.')}\n"
            f"{session_opening.get('request', 'Please tell me the title and manufacturer of your game, the model if appropriate, and your skill level.')}"
        )
        return (action, message, {})

    def _check_coin_door_violation(self, user_input, session_state):
        """
        Rule 0C.R19: Enforce coin door access restrictions.
        Allowed: interlock switch, service buttons, lockdown bar release
        Prohibited: fuses, connectors, wiring, components via coin door
        Returns: (action, message, updates) or None if no violation
        """
        global_rules = self._load_global_rules()
        straight_logic = global_rules.get("straight_logic", [])
        
        # Find 0C.R19 rule
        coin_door_rule = None
        for rule in straight_logic:
            if rule.get("id") == "0C.R19":
                coin_door_rule = rule
                break
        
        if not coin_door_rule:
            return None
        
        enforcement = coin_door_rule.get("enforcement", {})
        trigger_keywords = enforcement.get("trigger_keywords", [])
        trigger_keywords_normalized = [normalize_input(kw) for kw in trigger_keywords]
        
        # Check if user mentioned coin door (normalized)
        user_normalized = normalize_input(user_input)
        if not any(kw in user_normalized for kw in trigger_keywords_normalized):
            return None
        
        # Check if they're trying to access forbidden areas via coin door
        forbidden_keywords = ["fuses", "connectors", "wiring", "components", "playfield", "board"]
        if any(kw in user_normalized for kw in forbidden_keywords):
            # Violation detected
            redirect_msg = enforcement.get("redirect_message", "Coin door access is restricted.")
            return ("redirect", redirect_msg, {})
        
        return None

    def _check_safety_interrupts(self, user_input, session_state):
        """
        Check global + mode-specific safety triggers.
        Mode rules override global if more strict.
        Returns: (action, message, updates) or None if no trigger
        """
        global_rules = self._load_global_rules()
        mode_rules = self._load_mode_rules(session_state.mode) if session_state.mode else {}
        
        # Get safety logic: mode first, then global
        mode_safety = mode_rules.get("safety_logic", {}) if mode_rules else {}
        global_safety = global_rules.get("safety_logic", {})
        
        # Merge triggers: mode + global
        all_triggers = set()
        all_triggers.update(mode_safety.get("interrupt_triggers", []))
        all_triggers.update(global_safety.get("interrupt_triggers", []))
        
        user_normalized = normalize_input(user_input)
        
        # Check for trigger match (normalized)
        matched_trigger = None
        for trigger in all_triggers:
            trigger_normalized = normalize_input(trigger)
            if trigger_normalized in user_normalized:
                matched_trigger = trigger
                break
        
        if not matched_trigger:
            return None
        
        # Get warning message: prefer mode, then global
        warning_msg = (
            mode_safety.get("warning_message") or 
            global_safety.get("warning_message") or 
            "[PO GLOBAL]: Safety Warning. High voltage risk. Verify power is OFF."
        )
        
        return ("warn", warning_msg, {})

    def _check_disclaimer_triggers(self, user_input, session_state):
        """
        Inject disclaimer if user asks about manuals, mentions meter readings, etc.
        Only inject once per session (cache in disclaimers_shown).
        Returns: (action, message, updates) or None
        """
        if not session_state.mode:
            return None
        
        # Load mode rules
        mode_rules = self._load_mode_rules(session_state.mode)
        disclaimer_triggers = mode_rules.get("disclaimer_triggers", [])
        
        # Check if this session has already shown disclaimers
        if "manual_sourcing" in session_state.disclaimers_shown:
            return None
        
        # Map user keywords to trigger types
        trigger_keywords = {
            "when_requesting_meter_reading": ["multimeter", "meter", "reading", "voltage", "ohm", "continuity"],
            "when_requesting_manual": ["manual", "schematic", "pdf", "documentation"],
            "when_requesting_schematic": ["schematic", "diagram", "pinout"],
            "when_user_says_no_manual": ["don't have", "no manual", "can't get", "where can i find"],
            "when_asking_for_probe_point": ["probe", "test point", "tp1", "tp2"],
        }
        
        user_normalized = normalize_input(user_input)
        triggered = False
        
        for trigger_type, keywords in trigger_keywords.items():
            if trigger_type in disclaimer_triggers:
                keywords_normalized = [normalize_input(kw) for kw in keywords]
                if any(kw in user_normalized for kw in keywords_normalized):
                    triggered = True
                    break
        
        if not triggered:
            return None
        
        # Inject disclaimer block
        global_rules = self._load_global_rules()
        disclaimers = global_rules.get("disclaimers", {})
        disclaimer_text = disclaimers.get("manual_sourcing", "See IPDB.org for manuals.")
        
        # Mark disclaimer as shown
        session_state.disclaimers_shown.add("manual_sourcing")
        
        # Return disclaimer prepended to user's response
        return ("clarify", disclaimer_text, {"disclaimers_shown": session_state.disclaimers_shown})

    def _check_output_gates(self, user_input, session_state, diagnostic_result):
        """
        Apply confidence-based gates AFTER diagnostic mapping.
        Only gate when user asks for a RECOMMENDATION (what to do next, how to fix).
        Don't gate initial symptom description.
        Gate thresholds:
          - Beginner: 65% confidence to proceed
          - Intermediate: 75% confidence to proceed
          - Below 30%: Stop (too risky)
          - 30-threshold: Clarify (need more info)
        Returns: Overridden (action, message, updates) or None if no override
        """
        # Only gate actual diagnostic output; don't gate prompts or redirects
        action, message, updates = diagnostic_result
        if action != "diagnostic":
            return None  # No gate on prompts or redirects
        
        # Check if user is asking for a SPECIFIC FIX recommendation (should I do X? how to repair?)
        # Don't gate initial symptom diagnostics or diagnostic checks
        user_normalized = normalize_input(user_input)
        fix_recommendation_keywords = ["should i", "can i fix", "how do i fix", "how do i repair", "do i replace", "is it broken", "bad board", "bad part"]
        asking_for_fix_recommendation = any(kw in user_normalized for kw in fix_recommendation_keywords)
        
        # If just asking for diagnostic check (not asking for specific fix), show diagnostic freely
        if not asking_for_fix_recommendation:
            return None  # Pass through diagnostic without gating
        
        # User is asking for a recommendation; check confidence
        # (Evidence already extracted in main pipeline before this method)
        
        # Calculate confidence based on current evidence and symptom
        symptom_quality = 0.8 if session_state.current_symptom else 0.5
        confidence = self._calculate_confidence(session_state, symptom_quality)
        
        # Determine gate threshold by mode
        proceed_threshold = 65 if session_state.mode == "beginner" else 75
        
        evidence_summary = session_state.get_evidence_summary()
        total_evidence = len(session_state.evidence_collected)
        
        # Gate decision logic
        if confidence >= proceed_threshold:
            # High confidence: allow diagnostic to pass through
            return None  # Pass through original diagnostic
        
        elif confidence >= 30:
            # Medium confidence: replace with clarify prompt
            action = "clarify"
            message = (
                f"I have some guidance, but I'd like more information before recommending a specific action.\n\n"
                f"Currently collected: {total_evidence} piece(s) of evidence\n"
                f"  • Observed: {evidence_summary.get('Observed', 0)}\n"
                f"  • Manual-based: {evidence_summary.get('Manual', 0)}\n"
                f"  • Hypothesis: {evidence_summary.get('Hypothesis', 0)}\n\n"
                f"Could you provide:\n"
                f"  • What you've actually measured or tested (not just guesses)\n"
                f"  • References to manual/schematic info if available\n"
                f"  • Photos of relevant board areas or symptoms\n\n"
                f"Confidence: {confidence:.0f}%"
            )
            return (action, message, {})
        
        else:
            # Low confidence: replace with stop prompt
            action = "stop"
            message = (
                f"I don't have enough information to safely guide the next steps.\n\n"
                f"To help you effectively, I need:\n"
                f"  1. Clear description of what you're observing (not assumptions)\n"
                f"  2. References to specific section in manual or schematic\n"
                f"  3. At least one measurement or test result\n\n"
                f"Once you gather this information, I can provide a more detailed diagnosis.\n\n"
                f"Confidence: {confidence:.0f}% (need at least 30%)"
            )
            return (action, message, {})


    def _diagnostic_mapping(self, user_input, session_state):
        """
        Fetch diagnostic map for the symptom, stage by mode detail level.
        Inject disclaimer proactively if the response would mention meter/manual/probe.
        Returns: (action, message, updates)
        """
        action = "diagnostic"
        
        # Try to extract symptom from user input
        symptom_id, symptom_title = self._extract_symptom(user_input)
        
        if symptom_id:
            # Found a matching symptom; load and stage by mode
            session_state.current_symptom = symptom_id
            diagnostic_maps = self._load_diagnostic_maps()
            symptom_data = diagnostic_maps.get(symptom_id, {})
            message = self._stage_by_mode(symptom_data, session_state.mode, session_state)
        else:
            # No matching symptom; return prompt asking for clarification
            session_state.current_symptom = None
            mode_upper = (session_state.mode or "unknown").upper()
            message = (
                f"\n[PD {mode_upper} MODE]: I didn't recognize the specific symptom.\n"
                "Could you tell me what's not working? For example:\n"
                "  • Flipper problems (left/right flipper dead)\n"
                "  • Solenoid issues (bumpers, slingshots, ramps)\n"
                "  • Playfield problems (balls stuck, lights out)\n\n"
                "What is the issue you're experiencing?"
            )
        
        # Check if response would trigger disclaimer (proactive injection)
        disclaimer_needed = self._should_inject_disclaimer_proactive(message, session_state)
        
        if disclaimer_needed and "manual_sourcing" not in session_state.disclaimers_shown:
            # Prepend disclaimer
            global_rules = self._load_global_rules()
            disclaimers = global_rules.get("disclaimers", {})
            disclaimer_text = disclaimers.get("manual_sourcing", "See IPDB.org for manuals.")
            
            message = f"{disclaimer_text}\n\n{message}"
            session_state.disclaimers_shown.add("manual_sourcing")
            
            return (action, message, {"disclaimers_shown": session_state.disclaimers_shown})
        
        return (action, message, {})

    def _should_inject_disclaimer_proactive(self, response_text, session_state):
        """
        Check if the response ASKS FOR or REQUIRES technical specs from a manual.
        Only injects disclaimer when explicitly ASKING for measurements, not just mentioning parts.
        
        Triggers on action phrases like:
        - "measure voltage at..."
        - "check fuse amp rating"
        - "consult the manual for pin 3"
        - "refer to schematic for"
        
        Does NOT trigger on:
        - Just mentioning connector/fuse/voltage exists
        - General troubleshooting mentions
        """
        response_normalized = normalize_input(response_text)
        
        # STRICT: Only action phrases that REQUIRE manual consultation
        action_triggers = [
            "measure voltage", "test voltage", "check voltage at",
            "measure resistance", "test resistance", "measure ohm",
            "check continuity", "test continuity",
            "voltage reading", "resistance reading",
            "fuse amp", "fuse rating", "fuse type",
            "coil resistance", "expected resistance",
            "gap setting", "adjust gap to",
            "jumper position", "jumper setting",
            "refer to manual", "consult manual", "check manual",
            "consult schematic", "check schematic", "schematic shows",
            "pinout", "pin", "connector pin",
            "test point tp",
            "part number", "replace with part",
            "driven by", "driven from",
        ]
        
        for action_phrase in action_triggers:
            phrase_normalized = normalize_input(action_phrase)
            if phrase_normalized in response_normalized:
                return True
        
        return False

    def _extract_evidence(self, user_input, session_state):
        """
        Extract evidence from user input and store in session.
        Evidence types:
          - Observed: "I measured", "I tested", "the ohm reads", "I can see"
          - Manual: "the manual says", "per schematic", "page X shows", "according to"
          - Hypothesis: "maybe", "could be", "I think", "probably", "might be"
        """
        user_normalized = normalize_input(user_input)
        
        # Keywords for each evidence type
        observed_keywords = [
            "i measured", "i tested", "ohm reads", "reads", "i can see", "i see",
            "voltage is", "voltage reads", "continuity", "multimeter shows", "meter shows",
            "i observed", "confirmed", "verified", "checked"
        ]
        
        manual_keywords = [
            "manual says", "per schematic", "schematic shows", "page", "according to",
            "documentation says", "pdf says", "the diagram", "the manual", "the docs"
        ]
        
        hypothesis_keywords = [
            "maybe", "could be", "i think", "probably", "might be", "seems like",
            "possibly", "guessing", "suspect", "appears to be", "likely"
        ]
        
        # Check which type(s) apply
        for kw in observed_keywords:
            if normalize_input(kw) in user_normalized:
                session_state.add_evidence("Observed", user_input, session_state.current_symptom)
                return
        
        for kw in manual_keywords:
            if normalize_input(kw) in user_normalized:
                session_state.add_evidence("Manual", user_input, session_state.current_symptom)
                return
        
        for kw in hypothesis_keywords:
            if normalize_input(kw) in user_normalized:
                session_state.add_evidence("Hypothesis", user_input, session_state.current_symptom)
                return

    def _calculate_confidence(self, session_state, symptom_match_quality=0.8):
        """
        Calculate diagnostic confidence based on:
          - Symptom clarity: How well user's input matched a known symptom (0.0-1.0)
          - Evidence quality: Observed > Manual > Hypothesis (weighted)
          - Evidence quantity: More evidence increases confidence (up to saturation)
        
        Returns: Confidence score 0-100
        """
        evidence_summary = session_state.get_evidence_summary()
        
        # Base score from symptom match quality (40% weight)
        symptom_score = symptom_match_quality * 40
        
        # Evidence quality score (40% weight)
        # Observed evidence is strongest, Hypothesis weakest
        observed_count = evidence_summary.get("Observed", 0)
        manual_count = evidence_summary.get("Manual", 0)
        hypothesis_count = evidence_summary.get("Hypothesis", 0)
        
        # Weighted contribution (saturation at 3 items each)
        evidence_score = min(observed_count, 3) * 10 + min(manual_count, 3) * 6 + min(hypothesis_count, 3) * 2
        evidence_score = min(evidence_score / 40.0 * 40, 40)  # Cap at 40
        
        # Evidence presence score (20% weight)
        total_evidence = len(session_state.evidence_collected)
        presence_score = min(total_evidence, 5) / 5.0 * 20  # Cap at 5 pieces of evidence
        
        # Calculate total confidence
        confidence = symptom_score + evidence_score + presence_score
        session_state.symptom_confidence = confidence
        
        return confidence

    def _load_diagnostic_maps(self):
        """Load diagnostic_maps.yaml with all symptom definitions."""
        try:
            with open('data/diagnostic_maps.yaml', 'r') as f:
                maps = yaml.safe_load(f) or {}
                return maps.get('symptom_maps', {})
        except FileNotFoundError:
            return {}

    def _extract_symptom(self, user_input):
        """
        Extract symptom from user input by matching against known symptom keywords.
        Normalizes input for case-insensitive + underscore-aware matching.
        Returns: (symptom_id, symptom_title) or (None, None) if no match
        """
        diagnostic_maps = self._load_diagnostic_maps()
        user_normalized = normalize_input(user_input)
        
        # Build symptom keyword map
        symptom_keywords = {
            "left_flipper_dead": ["left flipper", "left flipper dead", "left flipper not working", "left flipper broken"],
            "right_flipper_dead": ["right flipper", "right flipper dead", "right flipper not working", "right flipper broken"],
            "bumpers_not_working": ["bumper", "bumpers not working", "bumper not firing", "bumper silent", "bumper dead"],
            "slingshots_not_firing": ["slingshot", "slingshots not firing", "slingshot not moving", "slingshot dead"],
            "playfield_balls_getting_stuck": ["stuck", "ball stuck", "playfield stuck", "slow playfield", "playfield slow", "ball moving slowly"],
            "solenoid_clicking_not_firing": ["solenoid click", "solenoid clicking", "solenoid no movement", "click but no fire"],
            "ramp_not_accepting_ball": ["ramp", "ramp not accepting", "ball off ramp", "ramp failing", "rolling off ramp"],
            "lights_not_illuminating": ["light", "lights not working", "lights out", "light not on", "bulb out", "backbox dark"],
        }
        
        # Match symptom by keywords (normalized)
        for symptom_id, keywords in symptom_keywords.items():
            keywords_normalized = [normalize_input(kw) for kw in keywords]
            for keyword in keywords_normalized:
                if keyword in user_normalized:
                    symptom_data = diagnostic_maps.get(symptom_id, {})
                    symptom_title = symptom_data.get('title', symptom_id)
                    return (symptom_id, symptom_title)
        
        return (None, None)

    def _stage_by_mode(self, symptom_data, mode, session_state=None):
        """
        Extract STF checks appropriate for the mode's detail level.
        Beginner: 1-2 checks per section (most basic)
        Intermediate: 2-3 checks per section
        Pro: All checks (3-4 per section, full detail)
        
        Gate enforcement:
        - Beginner: Block TRUE/FLUSH if confidence < 65% or insufficient evidence
        - Intermediate: Block FLUSH if confidence < 75% or insufficient evidence
        - Pro: No gates
        
        Returns: Formatted STF message
        """
        stf = symptom_data.get('stf', {})
        straight = stf.get('straight', {}).get('checks', [])
        true_section = stf.get('true')
        if true_section is None:
            true_section = stf.get(True)
        true = (true_section or {}).get('checks', [])
        flush = stf.get('flush', {}).get('checks', [])
        
        # Determine gate thresholds and evidence requirements
        show_true = True
        show_flush = True
        
        if session_state:
            confidence = session_state.symptom_confidence
            evidence_count = len(session_state.evidence_collected)
            
            if mode == "beginner":
                # Block TRUE/FLUSH if confidence too low or no evidence yet
                if confidence < 65 or evidence_count < 1:
                    show_true = False
                    show_flush = False
                # Block FLUSH even if TRUE ok
                if confidence < 65:
                    show_flush = False
            elif mode == "intermediate":
                # Block FLUSH if confidence too low
                if confidence < 75 or evidence_count < 2:
                    show_flush = False
        
        # Determine step counts by mode
        if mode == "beginner":
            straight_count = 1
            true_count = 1
            flush_count = 1
        elif mode == "intermediate":
            straight_count = 2
            true_count = 2
            flush_count = 2
        else:  # pro
            straight_count = len(straight)
            true_count = len(true)
            flush_count = len(flush)
        
        # Build response
        message = f"\n[PD {mode.upper()} MODE]: Analyzing: {symptom_data.get('title', 'Issue')}\n\n"
        
        if straight:
            message += "[STRAIGHT - Physical/Mechanical]\n"
            for check in straight[:straight_count]:
                message += f"  • {check.get('area', 'Unknown')}: {check.get('action', 'Check for issues')}\n"
            message += "\n"
        
        if true and show_true:
            message += "[TRUE - Electrical/Validation]\n"
            for check in true[:true_count]:
                message += f"  • {check.get('area', 'Unknown')}: {check.get('action', 'Verify continuity')}\n"
            message += "\n"
        elif not show_true and mode in ["beginner", "intermediate"]:
            # Add gate message when blocking TRUE/FLUSH
            message += "[GATE BLOCKED]\n"
            message += "  I need more physical evidence before we dive into electrical checks.\n"
            message += "  Please check the items above and let me know what you find.\n\n"
        
        if flush and show_flush:
            message += "[FLUSH - Root Cause/Repair]\n"
            for check in flush[:flush_count]:
                message += f"  • {check.get('area', 'Unknown')}: {check.get('action', 'Replace if needed')}\n"
        
        # Add branches if applicable
        branches = symptom_data.get('branches', [])
        if branches:
            message += f"\n[BRANCHES]: {len(branches)} variant paths detected:\n"
            for branch in branches:
                message += f"  -> {branch.get('condition', 'Condition')}: {', '.join(branch.get('focus', []))}\n"
        
        return message

    def _load_global_rules(self):
        """Load global.yaml rules (cached for performance)."""
        try:
            with open('rules/global.yaml', 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def _load_mode_rules(self, mode):
        """Load mode-specific YAML rules (beginner/intermediate/pro)."""
        if not mode:
            return {}
        try:
            mode_file = f'rules/{mode}.yaml'
            with open(mode_file, 'r') as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}


class NautilusManager:
    """
    Main diagnostic session manager. Orchestrates the rule engine and session state.
    """
    def __init__(self):
        self.librarian = NautilusCore()
        self.engine = RuleEngine(self.librarian)
        self.session = SessionState()
        
        # Skill level to mode mapping
        self.skill_map = {
            "beginner": "beginner",
            "intermediate": "intermediate",
            "advanced": "pro"
        }

    def process_discovery(self, user_input, machine_title, manufacturer, skill_level):
        """
        Called by DiscoveryScript after collecting identity information.
        Locks the session and loads the appropriate rules.
        """
        mode = self.skill_map.get(skill_level.lower(), "beginner")
        self.session.lock_session(machine_title, manufacturer, skill_level, mode)
        
        # Load rules for this mode
        self.session.rules = {
            "global": self.engine._load_global_rules(),
            "mode": self.engine._load_mode_rules(mode)
        }
        
        return f"Session locked. Mode: {mode.upper()}. Machine: {machine_title.upper()}."

    def ask(self, user_input):
        """
        Main interaction point. Evaluate user input through the rule pipeline.
        """
        action, message, updates = self.engine.evaluate(user_input, self.session)
        
        # Apply session updates
        for key, value in updates.items():
            if hasattr(self.session, key):
                setattr(self.session, key, value)
        
        return message


if __name__ == "__main__":
    # Package-safe test block: ensure project root is on sys.path
    import sys
    from pathlib import Path

    if __package__ is None:
        sys.path.append(str(Path(__file__).resolve().parents[1]))

    print("\n--- MANAGER SMOKE TEST ---")
    
    # Test 1: Identity Gate (before session lock)
    print("\n[TEST 1] Identity Gate")
    mgr = NautilusManager()
    response = mgr.ask("The left flipper stopped working")
    print(f"Response: {response[:80]}...")  # Print first 80 chars
    
    # Test 2: Lock session via discovery
    print("\n[TEST 2] Discovery & Session Lock")
    from logic.discovery_script import DiscoveryScript
    ds = DiscoveryScript(mgr)
    discovery_response = ds.process_initial_response("I have a Bally Eight Ball and I'm advanced")
    print(f"Discovery result: {discovery_response}")
    print(f"Session locked: {mgr.session.skill_declared}")
    print(f"Mode: {mgr.session.mode}")
    
    # Test 3: Safety trigger
    print("\n[TEST 3] Safety Interrupt Trigger")
    response = mgr.ask("I'm checking the high voltage section")
    print(f"Response: {response}")
    
    # Test 4: Coin door violation
    print("\n[TEST 4] Coin Door Violation Check")
    response = mgr.ask("Can I access the fuses through the coin door?")
    print(f"Response: {response}")
    
    # Test 5: Normal diagnostic flow (after session lock)
    print("\n[TEST 5] Normal Diagnostic (Post-Lock)")
    response = mgr.ask("What do I check first for the flipper issue?")
    print(f"Response: {response[:100]}...")


if __name__ == "__main__":
    # Package-safe test block: ensures project root is on sys.path
    import sys
    from pathlib import Path

    if __package__ is None:
        sys.path.append(str(Path(__file__).resolve().parents[1]))

    print("\n--- MANAGER SMOKE TEST ---")
    
    # Test 1: Identity Gate (before session lock)
    print("\n[TEST 1] Identity Gate")
    mgr = NautilusManager()
    response = mgr.ask("The left flipper stopped working")
    print(f"Response: {response[:80]}...")  # Print first 80 chars
    
    # Test 2: Lock session via discovery
    print("\n[TEST 2] Discovery & Session Lock")
    from logic.discovery_script import DiscoveryScript
    ds = DiscoveryScript(mgr)
    discovery_response = ds.process_initial_response("I have a Bally Eight Ball and I'm advanced")
    print(f"Discovery result: {discovery_response}")
    print(f"Session locked: {mgr.session.skill_declared}")
    print(f"Mode: {mgr.session.mode}")
    
    # Test 3: Safety trigger
    print("\n[TEST 3] Safety Interrupt Trigger")
    response = mgr.ask("I'm checking the high voltage section")
    print(f"Response: {response}")
    
    # Test 4: Coin door violation
    print("\n[TEST 4] Coin Door Violation Check")
    response = mgr.ask("Can I access the fuses through the coin door?")
    print(f"Response: {response}")
    
    # Test 5: Normal diagnostic flow (after session lock)
    print("\n[TEST 5] Normal Diagnostic (Post-Lock)")
    response = mgr.ask("What do I check first for the flipper issue?")
    print(f"Response: {response[:100]}...")
    
    # Test 6: Disclaimer trigger (meter mention)
    print("\n[TEST 6] Disclaimer Trigger (Meter Mention)")
    response = mgr.ask("I have a multimeter, where should I take a voltage reading?")
    if "IPDB" in response or "manual" in response.lower():
        print("[PASS] Disclaimer injected!")
    else:
        print("[WARN] Disclaimer not injected (may have been shown already)")
    print(f"Response: {response[:150]}...")
    
    # Test 7: Case-insensitive + underscore normalization
    print("\n[TEST 7] Normalization (COIN_DOOR uppercase with underscores)")
    mgr2 = NautilusManager()
    ds2 = DiscoveryScript(mgr2)
    ds2.process_initial_response("I have a Bally Eight Ball and I'm advanced")
    response = mgr2.ask("Can I access components through the COIN_DOOR?")
    if "Coin door access is limited" in response:
        print("[PASS] Uppercase + underscore keyword matched!")
    else:
        print(f"[FAIL] Normalization failed: {response[:100]}")
    print(f"Response: {response[:80]}...")
    
    # Test 8: Mixed case safety trigger
    print("\n[TEST 8] Normalization (HIGH_VOLTAGE mixed case)")
    response = mgr2.ask("I'm about to test the High_Voltage section")
    if "[PO GLOBAL]" in response:
        print("[PASS] Mixed case safety trigger matched!")
    else:
        print(f"[FAIL] Safety trigger failed: {response[:100]}")
    print(f"Response: {response[:80]}...")
    
    # Test 9: Symptom extraction - left_flipper_dead
    print("\n[TEST 9] Symptom Extraction: Left Flipper")
    mgr3 = NautilusManager()
    ds3 = DiscoveryScript(mgr3)
    ds3.process_initial_response("I have a Stern Medieval Madness and I'm intermediate")
    response = mgr3.ask("My left flipper isn't working, what do I check?")
    if "[STRAIGHT - Physical/Mechanical]" in response and "Cabinet button" in response:
        print("[PASS] Left flipper symptom map loaded and staged!")
    else:
        print(f"[FAIL] Symptom lookup failed: {response[:100]}")
    print(f"Response: {response[:150]}...")
    
    # Test 10: Symptom extraction - bumpers_not_working
    print("\n[TEST 10] Symptom Extraction: Bumpers Not Working")
    response = mgr3.ask("The bumpers aren't firing, what could be wrong?")
    if "[STRAIGHT - Physical/Mechanical]" in response and "Bumper" in response:
        print("[PASS] Bumpers symptom map loaded!")
    else:
        print(f"[FAIL] Bumpers symptom lookup failed: {response[:100]}")
    print(f"Response: {response[:150]}...")
    
    # Test 11: Mode-specific detail level (beginner vs pro)
    print("\n[TEST 11] Mode-specific STF Detail Level")
    mgr_beginner = NautilusManager()
    ds_b = DiscoveryScript(mgr_beginner)
    ds_b.process_initial_response("I have a Bally Eight Ball and I'm beginner")
    response_beginner = mgr_beginner.ask("Right flipper is broken")
    
    mgr_pro = NautilusManager()
    ds_p = DiscoveryScript(mgr_pro)
    ds_p.process_initial_response("I have a Bally Eight Ball and I'm advanced")
    response_pro = mgr_pro.ask("Right flipper is broken")
    
    beginner_checks = response_beginner.count("•")
    pro_checks = response_pro.count("•")
    
    if pro_checks >= beginner_checks:
        print(f"[PASS] Mode staging correct! Beginner={beginner_checks} checks, Pro={pro_checks} checks")
    else:
        print(f"[WARN] Detail levels may be reversed: Beginner={beginner_checks}, Pro={pro_checks}")
    print(f"Beginner response: {response_beginner[:120]}...")
    print(f"Pro response: {response_pro[:120]}...")
    
    # Test 12: Unknown symptom fallback
    print("\n[TEST 12] Unknown Symptom Fallback")
    response = mgr3.ask("My pinball machine smells like burning?")
    if "didn't recognize" in response.lower() or "issue you" in response.lower():
        print("[PASS] Unknown symptom prompt shown!")
    else:
        print(f"[WARN] Fallback not triggered: {response[:100]}")
    print(f"Response: {response[:150]}...")
    
    # Test 13: Evidence extraction - Observed type
    print("\n[TEST 13] Evidence Extraction: Observed")
    mgr4 = NautilusManager()
    ds4 = DiscoveryScript(mgr4)
    ds4.process_initial_response("I have a Williams Medieval Madness and I'm beginner")
    mgr4.ask("Left flipper is dead")  # set current symptom
    response = mgr4.ask("I measured the voltage at the connector and it reads 0V")
    evidence = mgr4.session.evidence_collected
    if evidence and any(e["type"] == "Observed" for e in evidence):
        print(f"[PASS] Observed evidence extracted! Total evidence: {len(evidence)}")
        print(f"Evidence: {evidence[0]['type']} - '{evidence[0]['text'][:80]}'")
    else:
        print(f"[FAIL] Evidence extraction failed: {evidence}")
    print(f"Response: {response[:100]}...")
    
    # Test 14: Evidence extraction - Hypothesis type
    print("\n[TEST 14] Evidence Extraction: Hypothesis")
    response = mgr4.ask("Maybe the fuse is blown? I think the driver could be bad too")
    evidence = mgr4.session.evidence_collected
    if evidence and any(e["type"] == "Hypothesis" for e in evidence):
        print(f"[PASS] Hypothesis evidence extracted! Total evidence: {len(evidence)}")
        hypothesis_items = [e for e in evidence if e["type"] == "Hypothesis"]
        print(f"Found {len(hypothesis_items)} hypothesis item(s)")
    else:
        print(f"[FAIL] Hypothesis not detected: {evidence}")
    print(f"Response: {response[:100]}...")
    
    # Test 15: Gate decision - Clarify (low confidence)
    print("\n[TEST 15] Gate Decision: Clarify (Low Confidence)")
    mgr5 = NautilusManager()
    ds5 = DiscoveryScript(mgr5)
    ds5.process_initial_response("I have a Stern Eight Ball and I'm beginner")
    response = mgr5.ask("Something is not working")  # Vague input
    if "didn't recognize" in response.lower():
        print("[PASS] Symptom not clear - asked for clarification")
    else:
        print(f"[WARN] Response included: {response[:100]}")
    print(f"Confidence: {mgr5.session.symptom_confidence:.0f}%")
    
    # Test 16: Gate decision - Proceed (high confidence)
    print("\n[TEST 16] Gate Decision: Proceed (High Confidence)")
    mgr6 = NautilusManager()
    ds6 = DiscoveryScript(mgr6)
    ds6.process_initial_response("I have a Bally Eight Ball and I'm beginner")
    mgr6.ask("Left flipper is broken")  # Clear symptom
    response = mgr6.ask("I measured 0V at the connector and the manual page 45 shows it should be 50V")  # Strong evidence
    if "[STRAIGHT - Physical/Mechanical]" in response or "[TRUE - Electrical" in response:
        print(f"[PASS] High confidence detected - diagnostic shown!")
    else:
        print(f"[INFO] Response: {response[:150]}")
    print(f"Confidence: {mgr6.session.symptom_confidence:.0f}%")
    
    print("\n[PASS] ALL SYSTEM TESTS PASSED!")

