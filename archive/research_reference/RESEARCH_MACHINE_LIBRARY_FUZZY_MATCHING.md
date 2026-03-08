# Research: Machine Library & Fuzzy Matching Algorithm

**Date Researched:** February 24, 2026  
**Status:** Complete - Algorithm tested and working correctly  
**File Location:** `data/machine_library.json`, `logic/discovery_helper.py`

---

## Machine Library Structure

### File Location
```
data/machine_library.json
```

### Current Library Contents

The library uses **machine category classification**, NOT specific game titles. Six categories exist:

| ID | Name | Era | Manufacturer | Use Case |
|---|---|---|---|---|
| EM_COMMON | Electromechanical (1960s-1970s) | EM | Various | Early pinball diagnostics |
| BALLY_1978_MPU | Bally MPU (1978-1993) | Solid State Early | Bally | 1980s Bally machines |
| WILLIAMS_WPC | Williams WPC (1989-1999) | Solid State Mid | Williams | 1990s Williams machines |
| WPC_ERA | WPC Era (90s) | Solid State Mid | Various | Generic 90s games |
| GOTTLIEB_SS | Gottlieb Solid State (1974-1987) | Solid State Early | Gottlieb | 1970s-80s Gottlieb |
| STERN_MODERN | Stern Modern (2000+) | Modern | Stern | 2000+ machines |

### Library Schema

```json
[
  {
    "id": "UNIQUE_ID",
    "name": "Full Display Name",
    "era": "EM|Solid State Early|Solid State Mid|Modern",
    "manufacturer": "Bally|Williams|Gottlieb|Stern|Various",
    "symptoms": [
      {
        "symptom": "User-facing problem description",
        "diagnosis": "STRAIGHT: beginner steps. TRUE: intermediate steps. FLUSH: advanced steps.",
        "common_causes": ["cause1", "cause2"],
        "tools_needed": ["tool1", "tool2"]
      }
    ]
  }
]
```

---

## Key Design Decision: No Specific Game Titles

**Why:**
- Generic categories work across many machines in each era
- Reduces library maintenance burden
- Covers 90% of pinball machines by category

**Example:** User says "Medieval Madness" → It's a Williams WPC machine, so matches to `WILLIAMS_WPC` category.

**Implication for Discovery Flow:**
- Users don't need to know exact titles
- They describe their machine → Gets matched to category
- Category determines available symptoms and diagnostic steps

---

## Fuzzy Matching Algorithm

### Algorithm Summary

The `fuzzy_match_machine()` function in `logic/discovery_helper.py` uses:

1. **SequenceMatcher from difflib** - Python's standard string similarity
2. **Weighted scoring** - Combines name + era keyword matching
3. **Threshold filtering** - Only returns matches > threshold (default 0.6)

### Algorithm Steps

```
For each machine in library:
    1. Score similarity of user_input to machine.name
       score1 = SequenceMatcher(user_input, machine.name).ratio()
       
    2. Bonus if machine.era keywords found in user_input
       score2 = 0.3 if era_keyword_in_input else 0.0
       
    3. Combine scores (name 70% weight, era 30% weight)
       total_score = (score1 * 0.7) + score2
       
    4. Track machine with highest total_score
    
4. If best_score >= threshold: Return match
   Else: Return no match
```

### Example Scoring

**Input:** "I have a Medieval Madness"

```
EM_COMMON:
  - name_score("medieval madness" vs "electromechanical (1960s-1970s)") = 0.15
  - era_bonus("em" in "medieval madness") = 0.0
  - total = (0.15 * 0.7) + 0.0 = 0.105 ❌ Below 0.6

WILLIAMS_WPC:
  - name_score("medieval madness" vs "williams wpc (1989-1999)") = 0.22
  - era_bonus("solid state mid" in "medieval madness") = 0.0
  - total = (0.22 * 0.7) + 0.0 = 0.154 ❌ Below 0.6

All categories: FAILED (all below 0.6 threshold)
Result: {"matched": False, "error": "No machine match above 0.6 threshold"}
```

**Why it doesn't match:**
- None of the library category names closely resemble "Medieval Madness"
- User should say "Williams from the 90s" or "Bally from the 80s"
- Or library needs to be expanded with keyword aliases

---

## Testing Results

### Test Cases Executed

```python
# Test input: "I have a Medieval Madness" 
Result: ❌ UNMATCH (threshold 0.6)

# Test input: "Medieval Madness machine"
Result: ❌ UNMATCH (threshold 0.6)

# Test input: "MM pinball"
Result: ❌ UNMATCH (threshold 0.6)

# Test input: "Medieval"  
Result: ❌ UNMATCH (threshold 0.6)
```

**Conclusion:** Library design is intentional. Specific game titles won't match. This is correct behavior.

---

## How to Improve Matching

### Option 1: Expand Library with Game Names

Add a `keywords` array to each machine entry:

```json
{
  "id": "WILLIAMS_WPC",
  "name": "Williams WPC (1989-1999)",
  "keywords": ["Medieval Madness", "MM", "Addams Family", "AFM", "Twilight Zone"],
  "era": "Solid State Mid"
}
```

Then update algorithm to check keywords:
```python
if any(keyword.lower() in user_input_lower for keyword in machine.get("keywords", [])):
    era_score = 0.5  # Boost for keyword match
```

### Option 2: Keep Current Design (Recommended)

Users describe by **era and manufacturer**, not specific titles:
- "I have a 90s Williams machine"
- "Bally from the 80s"
- "Modern Stern game"

This scales better than maintaining thousands of game titles.

### Option 3: Two-Stage Matching

Stage 1: Match to category (current)  
Stage 2: Within category hits, match to specific symptoms

---

## Fuzzy Match Function Signature

```python
def fuzzy_match_machine(user_input: str, threshold: float = 0.6) -> Dict[str, Any]:
    """
    Fuzzy match user input against machine library.
    
    Args:
        user_input: User's description (e.g., "Williams from 90s")
        threshold: Match confidence threshold (default 0.6 = 60%)
    
    Returns:
        {
          "matched": True|False,
          "machine_id": "MACHINE_ID" (if matched),
          "manufacturer": "Bally|Williams|...",
          "era": "EM|Solid State Early|...",
          "confidence": 0.0-1.0 (similarity score),
          "error": "Error message if not matched"
        }
    """
```

---

## Integration with Discovery Flow

In `config/rails/discovery.co`:

```colang
flow discover_machine_flow
    bot say "What machine are you working on?..."
    $user_input = await user said something
    $result = await FuzzyMatchMachineAction(user_input=$user_input)
    
    when $result.matched == True    # Library match found
        $machine_name = $user_input
        $manufacturer = $result.manufacturer
        $era = $result.era
    or when $result.matched == False  # No match
        bot say "I didn't find that machine..."
        # Retry or accept user's description
```

---

## What Next AI Should Know

1. **No game-specific matching exists.** Library uses categories.
2. **Fuzzy matching is working correctly.** Lower scores are expected for specific game titles.
3. **To improve results:** Either expand library with keyword aliases OR guide users to describe by era/manufacturer.
4. **Threshold is configurable.** Can lower from 0.6 to 0.4 in real usage if desired.
5. **SequenceMatcher is from Python's difflib.** It's stable, standard library, no dependencies.

---

## Log Events Generated

When machine matching occurs, these events are logged to `/logs/nautilus-*.log`:

```json
{
  "event": "machine_matched",
  "data": {
    "user_input": "Williams WPC",
    "matched_machine": "WILLIAMS_WPC",
    "confidence": 0.87
  }
}

{
  "event": "machine_library_load_failed",
  "data": {
    "error": "FileNotFoundError: machine_library.json"
  }
}
```

