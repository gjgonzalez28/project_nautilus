# Project Nautilus: Skill Level System

**Version:** 1.0  
**Created:** March 2, 2026  
**Status:** Active

---

## Overview

Project Nautilus uses a three-tier skill level system to tailor diagnostic guidance based on user experience. Each skill level determines:
- Depth of diagnostic steps provided
- Safety warnings and restrictions
- Technical terminology used
- Tools and equipment assumed available

---

## Skill Levels

### Beginner
**Target Users:** First-time pinball owners, hobbyists with basic tools  
**Safety Priority:** Maximum (restrictive approach)  
**Diagnostic Depth:** STRAIGHT only (basic physical/mechanical checks)

```yaml
skill_level: beginner

characteristics:
  experience: "First machine or less than 1 year ownership"
  tools_available:
    - "Basic screwdriver set"
    - "Multimeter (optional)"
  safety_restrictions:
    - "No high voltage work"
    - "No soldering"
    - "No board-level work"
  diagnostic_approach: "STRAIGHT only - visual inspection and basic tests"
  
intervention_triggers:
  - "transformer"
  - "high voltage"
  - "wall outlet"
  - "soldering"
  - "board work"
  - "component replacement"
```

### Intermediate
**Target Users:** Multi-year hobbyists with extended toolset  
**Safety Priority:** Moderate (guided approach with warnings)  
**Diagnostic Depth:** STRAIGHT + TRUE (includes power, fuses, connections)

```yaml
skill_level: intermediate

characteristics:
  experience: "2-5 years ownership, multiple machines"
  tools_available:
    - "Complete screwdriver set"
    - "Multimeter (required)"
    - "Voltage tester"
    - "Basic soldering iron"
  safety_restrictions:
    - "High voltage allowed with warnings"
    - "Basic soldering permitted"
    - "Component testing allowed"
  diagnostic_approach: "STRAIGHT + TRUE - includes electrical testing"
  
intervention_triggers:
  - "transformer work"
  - "mains voltage"
  - "board repair beyond component swap"
```

### Pro
**Target Users:** Professional technicians, experienced collectors  
**Safety Priority:** Minimal (assumes expert knowledge)  
**Diagnostic Depth:** STRAIGHT + TRUE + FLUSH (full diagnostic path)

```yaml
skill_level: pro

characteristics:
  experience: "5+ years, professional or serious collector"
  tools_available:
    - "Professional diagnostic equipment"
    - "Oscilloscope"
    - "EPROM programmer"
    - "Advanced soldering station"
    - "Test boards and fixtures"
  safety_restrictions: []
  diagnostic_approach: "Full STF progression - all diagnostic depth"
  
intervention_triggers: []
```

---

## Skill Level Detection

### User Input Patterns
The system detects skill level from user input during discovery:

```yaml
skill_detection:
  beginner_keywords:
    - "first machine"
    - "new to pinball"
    - "beginner"
    - "just bought"
    - "don't know much"
  
  intermediate_keywords:
    - "intermediate"
    - "some experience"
    - "owned a few"
    - "comfortable with"
  
  pro_keywords:
    - "professional"
    - "technician"
    - "advanced"
    - "expert"
    - "collector"
```

### Default Behavior
If skill level cannot be determined from user input:
- **Always default to BEGINNER** for maximum safety
- Request explicit confirmation before proceeding
- Offer skill level upgrade if user demonstrates knowledge

---

## Safety Rules by Skill Level

### Global Safety (All Levels)

```yaml
global_safety:
  coin_door_restriction:
    rule_id: "0C.R19"
    allowed_activities:
      - "interlock switch"
      - "service buttons"
      - "volume button"
      - "lockdown bar release"
    prohibited:
      - "fuse access"
      - "connector access"
      - "wiring work"
      - "component testing"
    redirect: "Remove glass and raise playfield for proper access"
  
  power_safety:
    rule_id: "0C.S1"
    requirement: "Always verify power is OFF before any diagnostic work"
    exceptions: "Voltage testing only (with proper safety equipment)"
```

### Beginner Safety

```yaml
beginner_safety:
  high_voltage_block:
    trigger_keywords:
      - "transformer"
      - "high voltage"
      - "capacitor"
      - "power supply"
    action: "BLOCK"
    message: "High voltage work requires professional assistance. Contact a qualified technician."
  
  soldering_block:
    trigger_keywords:
      - "solder"
      - "desolder"
      - "reflow"
    action: "BLOCK"
    message: "Soldering work is not recommended for beginners. Consider upgrading skill level or seeking assistance."
```

### Intermediate Safety

```yaml
intermediate_safety:
  high_voltage_warning:
    trigger_keywords:
      - "transformer"
      - "high voltage"
      - "mains voltage"
    action: "WARN"
    message: "⚠️ HIGH VOLTAGE WORK: Ensure power is OFF and disconnected. Use proper insulated tools."
  
  soldering_guidance:
    trigger_keywords:
      - "solder"
      - "desolder"
    action: "GUIDE"
    message: "Soldering required. Use 60/40 rosin core solder, temperature-controlled iron (650-700°F)."
```

### Pro Safety

```yaml
pro_safety:
  assumption: "User has professional knowledge and safety training"
  warnings: "Minimal - only critical safety reminders"
  restrictions: "None - full diagnostic access"
```

---

## Skill Level Upgrade Path

Users can upgrade their skill level mid-session if they demonstrate competence:

```yaml
upgrade_conditions:
  beginner_to_intermediate:
    - "User correctly identifies era-specific components"
    - "User uses proper technical terminology"
    - "User mentions owning multiple machines"
    - "User shows understanding of basic electrical concepts"
  
  intermediate_to_pro:
    - "User references specific board components by part number"
    - "User discusses oscilloscope traces or signal analysis"
    - "User mentions professional tools or test equipment"
    - "User demonstrates deep system knowledge"
  
  confirmation_required: true
  message: "Based on your responses, you seem to have [SKILL_LEVEL] experience. Would you like to upgrade to that skill level for more detailed diagnostics?"
```

---

## Integration with Diagnostic Flows

### Discovery Flow
```yaml
discovery_flow:
  step: "skill_capture"
  actions:
    - "Ask user for skill level"
    - "Detect from natural language if not explicitly stated"
    - "Default to beginner if uncertain"
    - "Store in session: $skill_level"
```

### Diagnostic Flow
```yaml
diagnostic_flow:
  step: "generate_steps"
  logic:
    if_beginner:
      - "Provide STRAIGHT steps only"
      - "Use simple language"
      - "Include detailed safety warnings"
    if_intermediate:
      - "Provide STRAIGHT + TRUE steps"
      - "Use technical terminology"
      - "Include moderate safety warnings"
    if_pro:
      - "Provide full STF progression"
      - "Use professional terminology"
      - "Minimal safety warnings"
```

### Safety Gate
```yaml
safety_gate:
  step: "validate_action"
  logic:
    - "Check proposed action against skill level restrictions"
    - "If restricted: BLOCK and suggest alternative"
    - "If allowed with warning: WARN and require confirmation"
    - "If fully allowed: PROCEED with minimal caution"
```

---

## Example Session Variables

```yaml
session_state:
  machine_name: "Medieval Madness"
  manufacturer: "Williams"
  era: "WPC_90s"
  skill_level: "intermediate"
  
  allowed_actions:
    - "fuse_testing"
    - "voltage_measurement"
    - "connector_inspection"
    - "switch_testing"
    - "basic_soldering"
  
  restricted_actions:
    - "transformer_work"
    - "board_level_repair"
    - "eprom_programming"
```

---

## Future Enhancements

### Planned Features
- **Skill Level Quiz:** Optional assessment to determine accurate skill level
- **Progressive Disclosure:** Unlock more advanced diagnostics as user demonstrates competence
- **Certification Tracking:** Track user progress toward intermediate/pro levels
- **Custom Tool Profiles:** Allow users to specify available tools for better guidance

### Consideration
```yaml
future_skill_system:
  dynamic_assessment: true
  learning_path: "Track user progress across multiple sessions"
  achievement_milestones:
    - "Completed first full diagnostic"
    - "Successfully tested voltage"
    - "Correct component identification"
  upgrade_automation: "Suggest skill upgrade after X successful diagnostics"
```

---

_Last Updated: March 2, 2026_
