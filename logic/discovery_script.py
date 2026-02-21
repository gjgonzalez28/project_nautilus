# Project Nautilus: Discovery Script Logic
# Handles the initial intake interaction to satisfy Rule 0C.R2 (First-Response Gate)
# Collects: machine title, manufacturer, era (optional), skill level

class DiscoveryScript:
    """
    Guides the user through the identity/skill discovery phase.
    Once complete, locks the session in the manager and transitions to diagnostics.
    """
    def __init__(self, manager_instance):
        self.manager = manager_instance
        self.awaiting_discovery = True
        self.discovery_step = 0
        self.collected = {
            "machine_title": None,
            "manufacturer": None,
            "skill_level": None
        }

    def _identity_prompt(self):
        global_rules = self.manager.engine._load_global_rules()
        session_opening = global_rules.get("session_opening", {})
        greeting = session_opening.get("greeting", "Great, I can help with that.")
        request = session_opening.get(
            "request",
            "Please tell me the title and manufacturer of your game, the model if appropriate, and your skill level."
        )
        return f"{greeting}\n{request}"

    def _build_missing_prompt(self, missing_fields):
        labels = {
            "machine_title": "machine title",
            "manufacturer": "manufacturer",
            "skill_level": "skill level (beginner, intermediate, or advanced)"
        }
        missing_list = [labels[field] for field in missing_fields]
        missing_text = ", ".join(missing_list)
        return f"I still need: {missing_text}."

    def _handle_playfield_confirmation(self, user_text):
        text_lower = user_text.lower()
        yes_tokens = ["yes", "yep", "yeah", "i do", "i know", "i can", "sure"]
        no_tokens = ["no", "nope", "not yet", "dont", "don't", "do not", "never", "not sure"]

        if any(token in text_lower for token in yes_tokens):
            self.manager.session.awaiting_playfield_confirmation = False
            self.manager.session.playfield_access_confirmed = True
            return "Great. Tell me the symptom you want to troubleshoot."

        if any(token in text_lower for token in no_tokens):
            playfield_access = {}
            if self.manager.session.rules and self.manager.session.rules.get("mode"):
                playfield_access = self.manager.session.rules["mode"].get("playfield_access", {})

            question = self._playfield_question()
            steps = []
            steps.extend(playfield_access.get("if_no_lockdown_bar", []))
            steps.extend(playfield_access.get("if_no_modern_clips", []))
            steps.extend(playfield_access.get("playfield_lift", []))

            if steps:
                step_text = "\n".join([f"- {step}" for step in steps])
                return f"{question}\n\n{step_text}\n\nLet me know when you are ready to continue."

            return f"{question}\n\nLet me know when you are ready to continue."

        question = self._playfield_question()
        return f"{question} Please answer yes or no."

    def _playfield_question(self):
        playfield_access = {}
        if self.manager.session.rules and self.manager.session.rules.get("mode"):
            playfield_access = self.manager.session.rules["mode"].get("playfield_access", {})
        return playfield_access.get(
            "question",
            "Do you know how to remove the glass and raise the playfield?"
        )

    def process_initial_response(self, user_text):
        """
        Parses the user's response to the Identity/Skill gate.
        Expects: Machine title, manufacturer, and skill level (beginner/intermediate/advanced).
        
        Returns: Confirmation message if complete, or re-prompt if missing data.
        """
        if self.manager.session.skill_declared and self.manager.session.awaiting_playfield_confirmation:
            return self._handle_playfield_confirmation(user_text)

        text_lower = user_text.lower()

        # Extract skill level
        skill_found = self.collected["skill_level"]
        skill_pos = -1
        if not skill_found:
            for skill in ["beginner", "intermediate", "advanced"]:
                pos = text_lower.find(skill)
                if pos >= 0:
                    skill_found = skill
                    skill_pos = pos
                    break
            if skill_found:
                self.collected["skill_level"] = skill_found
        
        # Extract manufacturer
        manufacturers = ["bally", "williams", "gottlieb", "stern", "data east", "sega", "rare", "midway"]
        manufacturer_found = self.collected["manufacturer"]
        mfg_pos = -1
        mfg_match = None
        for mfg in manufacturers:
            pos = text_lower.find(mfg)
            if pos >= 0 and pos > mfg_pos:
                mfg_match = mfg
                mfg_pos = pos
        if not manufacturer_found and mfg_match:
            manufacturer_found = mfg_match.capitalize()
            self.collected["manufacturer"] = manufacturer_found
        
        # Extract machine title: text between manufacturer and skill keywords
        machine_title = self.collected["machine_title"]
        if not machine_title and mfg_pos >= 0:
            end_pos = skill_pos if skill_pos >= 0 else len(text_lower)
            mfg_end_pos = mfg_pos + len(mfg_match)
            machine_text = text_lower[mfg_end_pos:end_pos].strip()

            if machine_text:
                separators = [" and ", " or ", " with ", " my ", " the ", " i'm ", " i am ", "i have "]
                for sep in separators:
                    if sep in machine_text:
                        machine_text = machine_text.split(sep)[-1].strip()
                machine_text = machine_text.strip(" ,-")
                if machine_text.endswith("pinball machine"):
                    machine_text = machine_text.replace("pinball machine", "").strip()

                if len(machine_text) >= 2:
                    machine_title = " ".join([word.capitalize() for word in machine_text.split()])
                    self.collected["machine_title"] = machine_title
        
        missing_fields = [
            field for field, value in self.collected.items() if not value
        ]
        if missing_fields:
            if not any(self.collected.values()):
                return self._identity_prompt()
            return self._build_missing_prompt(missing_fields)
        
        # Lock the session with discovered identity
        lock_msg = self.manager.process_discovery(
            user_text, 
            self.collected["machine_title"],
            self.collected["manufacturer"],
            self.collected["skill_level"]
        )
        
        self.awaiting_discovery = False
        if self.manager.session.mode == "beginner":
            self.manager.session.awaiting_playfield_confirmation = True
            return self._playfield_question()

        return lock_msg


if __name__ == "__main__":
    # Package-safe test block: ensure project root is on sys.path
    import sys
    from pathlib import Path

    if __package__ is None:
        sys.path.append(str(Path(__file__).resolve().parents[1]))

    # Internal test to verify parsing logic
    from logic.manager import NautilusManager
    
    print("\n--- DISCOVERY SCRIPT TEST ---")
    m = NautilusManager()
    ds = DiscoveryScript(m)
    
    test_input = "I have a Williams Firepower and I'm advanced"
    result = ds.process_initial_response(test_input)
    print(f"Input: {test_input}")
    print(f"Result: {result}")
    print(f"Session locked: {m.session.skill_declared}")
    print(f"Mode: {m.session.mode}")
    print(f"Machine: {m.session.machine_title}")
    print(f"Manufacturer: {m.session.manufacturer}")

if __name__ == "__main__":
    # Package-safe test block: ensure project root is on sys.path
    import sys
    from pathlib import Path

    if __package__ is None:
        sys.path.append(str(Path(__file__).resolve().parents[1]))

    # Internal test to verify parsing logic
    from logic.manager import NautilusManager
    m = NautilusManager()
    ds = DiscoveryScript(m)
    print("\n--- DISCOVERY SCRIPT TEST ---")
    print(ds.process_initial_response("It is a Williams Firepower and I am advanced"))