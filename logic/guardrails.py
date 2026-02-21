class SafetyGuardrail:
    def __init__(self):
        self.triggers = ["monitor", "cap", "power supply", "transformer"]
    def check(self, text):
        if any(w in text.lower() for w in self.triggers): return "INTERRUPT: High Voltage!"
        return "CLEAR"
if __name__ == "__main__":
    g = SafetyGuardrail()
    print(f"Safety: {g.check('Check the transformer')}")
