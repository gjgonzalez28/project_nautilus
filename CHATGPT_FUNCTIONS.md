# ChatGPT Function Definitions for Project Nautilus

## Your ngrok URL:
```
https://unaspiringly-accommodable-remington.ngrok-free.dev
```

---

## How to Add Functions to ChatGPT:

1. Go to ChatGPT: https://chatgpt.com
2. Start a new chat
3. Click the **paperclip icon** (📎) at the bottom left
4. Select **"Create custom action"** or **"Add actions"**
5. Copy and paste each function definition below

---

## Function 1: initialize_nautilus_session

```json
{
  "name": "initialize_nautilus_session",
  "description": "Initialize a new Project Nautilus diagnostic session. Call this at the start of every new troubleshooting conversation.",
  "parameters": {
    "type": "object",
    "properties": {
      "user_name": {
        "type": "string",
        "description": "The technician's name"
      },
      "skill_level": {
        "type": "string",
        "enum": ["beginner", "intermediate", "pro"],
        "description": "Technician skill level: beginner (65% confidence gate), intermediate (75% gate), or pro (no gates)"
      }
    },
    "required": ["user_name", "skill_level"]
  },
  "method": "POST",
  "url": "https://unaspiringly-accommodable-remington.ngrok-free.dev/initialize"
}
```

---

## Function 2: nautilus_ask

```json
{
  "name": "nautilus_ask",
  "description": "Send the user's message to Project Nautilus for diagnostic analysis. Use this for every user message during troubleshooting.",
  "parameters": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "The user's message describing symptoms, observations, or answers to questions"
      }
    },
    "required": ["message"]
  },
  "method": "POST",
  "url": "https://unaspiringly-accommodable-remington.ngrok-free.dev/ask"
}
```

---

## Function 3: nautilus_set_mode

```json
{
  "name": "nautilus_set_mode",
  "description": "Change the skill level mode during a session. Use when user requests to change difficulty or detail level.",
  "parameters": {
    "type": "object",
    "properties": {
      "mode": {
        "type": "string",
        "enum": ["beginner", "intermediate", "pro"],
        "description": "New skill level: beginner (65% confidence gate), intermediate (75% gate), or pro (no gates)"
      }
    },
    "required": ["mode"]
  },
  "method": "POST",
  "url": "https://unaspiringly-accommodable-remington.ngrok-free.dev/set-mode"
}
```

---

## Function 4: nautilus_get_state

```json
{
  "name": "nautilus_get_state",
  "description": "Get current session state including evidence, confidence scores, and diagnostic progress. Use when user asks about current status.",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  },
  "method": "GET",
  "url": "https://unaspiringly-accommodable-remington.ngrok-free.dev/state"
}
```

---

## Function 5: nautilus_end_session

```json
{
  "name": "nautilus_end_session",
  "description": "End the diagnostic session and generate a compliance report. Call when troubleshooting is complete or user wants to end.",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  },
  "method": "POST",
  "url": "https://unaspiringly-accommodable-remington.ngrok-free.dev/end-session"
}
```

---

## Function 6: nautilus_reset

```json
{
  "name": "nautilus_reset",
  "description": "Reset the session completely. Use only when starting completely fresh or when explicitly requested.",
  "parameters": {
    "type": "object",
    "properties": {},
    "required": []
  },
  "method": "POST",
  "url": "https://unaspiringly-accommodable-remington.ngrok-free.dev/reset"
}
```

---

## Testing Instructions:

Once you've added all functions to ChatGPT:

1. **Start a session:**
   - "Initialize a new Nautilus session for technician John, skill level beginner"
   
2. **Send diagnostic messages:**
   - "My flipper is weak"
   - "The ball doesn't make it all the way up"
   
3. **Check progress:**
   - "What's the current diagnostic state?"
   
4. **End session:**
   - "End the diagnostic session"

---

## Important Notes:

- **Keep both terminals running** (Flask server + ngrok tunnel)
- If you restart ngrok, the URL will change and you'll need to update all functions
- Test each skill level: beginner, intermediate, and pro
- Watch for evidence collection, confidence scoring, and gating behavior

---

**Ready to test!** 🚀
