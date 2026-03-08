# Colang 2.0 Documentation - Complete Index

This is your **COMPLETE Colang 2.0 language specification** compiled from the official NVIDIA NeMo-Guardrails documentation.

---

## 📚 Documents Included

You now have **4 comprehensive documents**:

### 1. **COLANG_2_0_COMPLETE_SPECIFICATION.md**
The authoritative language reference covering:
- ✅ Overview and core concepts
- ✅ Complete language syntax
- ✅ All keywords and reserved words
- ✅ Variables and expressions (all operators)
- ✅ Events and actions
- ✅ Flow definition and control
- ✅ Python actions integration
- ✅ LLM integration
- ✅ Error messages
- ✅ Quick reference tables
- ✅ Best practices
- ✅ Complete feature checklist

**When to use:** Need authoritative reference for syntax, want to understand every feature, building from scratch.

---

### 2. **COLANG_2_0_WORKING_EXAMPLES.md**
20 real, working examples from the official repository, including:
- Example 1: Hello World (basic)
- Example 2: Multi-turn conversation
- Example 3: Flexible input with variables
- Example 4: Conditional logic (if/elif/else)
- Example 5: Event-based branching (when/or when/else)
- Example 6: Function-like flows with parameters
- Example 7: Loops with counters
- Example 8: Validation and error handling
- Example 9: Event-based error handling
- Example 10: Parallel/concurrent actions
- Example 11: Python action integration
- Example 12: LLM intent matching
- Example 13: NLD (Natural Language Description)
- Example 14: Complex state management
- Example 15: Interaction loops (multimodal)
- Example 16: String expressions/formatting
- Example 17: Flow activation and restart
- Example 18: Custom flow naming
- Example 19: Error handling patterns
- Example 20: Complete mini chatbot

**When to use:** Want to see working code, need implementation examples, learning by example.

---

### 3. **COLANG_2_0_STANDARD_LIBRARY.md**
Complete reference for pre-built flows:
- ✅ Core library (`import core`)
  - User input flows
  - Bot output flows
  - State tracking flows
  - Debug utilities
- ✅ LLM module (`import llm`)
  - Intent detection
  - Bot generation
- ✅ Timing module (`import timing`)
- ✅ Avatars module (`import avatars`)
- ✅ Guardrails module (`import guardrails`)
- ✅ Attention module (`import attention`)
- ✅ Custom library pattern
- ✅ NLD (Natural Language Descriptions)

**When to use:** Need to use library flows, want to know what's available, creating reusable libraries.

---

### 4. **COLANG_2_0_SPECIFIC_PATTERNS.md**
Direct answers to your specific questions:
- ✅ **How to capture user input** (7 patterns)
- ✅ **How to call Python functions** (THE CORRECT SYNTAX)
- ✅ **How variables persist** across statements
- ✅ **Nested vs flat flow structure**
- ✅ **Variable lifecycle and scope**
- ✅ **Variable persistence with loops**
- ✅ **Summary table of scope rules**
- ✅ **Final checklist**

**When to use:** Have specific implementation questions, need clarity on critical patterns.

---

## 🎯 Quick Start Navigation

### I want to...

**Build my first chatbot**
1. Read: Example 1 (Hello World) in `COLANG_2_0_WORKING_EXAMPLES.md`
2. Reference: "Core Library" section in `COLANG_2_0_STANDARD_LIBRARY.md`
3. Run: `nemoguardrails chat --config=./config`

**Understand user input capture**
1. Read: "Question 1: How to Capture User Input" in `COLANG_2_0_SPECIFIC_PATTERNS.md`
2. Study: Examples 3, 11, 12 in `COLANG_2_0_WORKING_EXAMPLES.md`
3. Reference: "User Input Flows" in `COLANG_2_0_STANDARD_LIBRARY.md`

**Call Python functions from Colang**
1. Read: "Question 2: How to Call Python Functions" in `COLANG_2_0_SPECIFIC_PATTERNS.md`
2. Study: Example 11 in `COLANG_2_0_WORKING_EXAMPLES.md`
3. Reference: "Python Actions" section in `COLANG_2_0_COMPLETE_SPECIFICATION.md`

**Integrate LLM**
1. Read: "LLM Integration" in `COLANG_2_0_COMPLETE_SPECIFICATION.md`
2. Study: Examples 12, 13, 20 in `COLANG_2_0_WORKING_EXAMPLES.md`
3. Use: `import llm` and reference `COLANG_2_0_STANDARD_LIBRARY.md`

**Understand flow control**
1. Read: "Flow Control Statements" in `COLANG_2_0_COMPLETE_SPECIFICATION.md`
2. Study: Examples 4, 5, 7 in `COLANG_2_0_WORKING_EXAMPLES.md`
3. Reference: Summary tables in `COLANG_2_0_COMPLETE_SPECIFICATION.md`

**Use the standard library**
1. Read: `COLANG_2_0_STANDARD_LIBRARY.md` completely
2. Study: Which flows solve your problem
3. Reference: Official patterns in `COLANG_2_0_WORKING_EXAMPLES.md`

**Debug variable issues**
1. Read: "Question 3: How Variables Persist" in `COLANG_2_0_SPECIFIC_PATTERNS.md`
2. Reference: "Variable Scope" section in `COLANG_2_0_COMPLETE_SPECIFICATION.md`
3. Study: Examples 6, 14 in `COLANG_2_0_WORKING_EXAMPLES.md`

---

## 📖 Reading Order by Purpose

### For Complete Learning:
1. Read `COLANG_2_0_COMPLETE_SPECIFICATION.md` - Overview section first
2. Look at `COLANG_2_0_WORKING_EXAMPLES.md` - Examples 1-5
3. Read `COLANG_2_0_STANDARD_LIBRARY.md` - Core module section
4. Study `COLANG_2_0_SPECIFIC_PATTERNS.md` - Your specific questions

### For Quick Implementation:
1. Find closest example in `COLANG_2_0_WORKING_EXAMPLES.md`
2. Copy and adapt
3. Reference `COLANG_2_0_COMPLETE_SPECIFICATION.md` for syntax clarity
4. Check `COLANG_2_0_STANDARD_LIBRARY.md` for available flows

### For Advanced Patterns:
1. Study Examples 14-20 in `COLANG_2_0_WORKING_EXAMPLES.md`
2. Read "More on Flows" section in `COLANG_2_0_COMPLETE_SPECIFICATION.md`
3. Review `COLANG_2_0_SPECIFIC_PATTERNS.md` - nested vs flat structures

---

## 💡 Key Concepts Quick Reference

### Events
- `send <Event>()` - Generate event
- `match <Event>()` - Wait for event
- Events drive everything
- Reference: Section "Events & Actions" in Specification

### Variables
- `$variable = value` - Declare locally
- `global $var` - Share across flows
- `return $value` - Pass to caller
- Persist within flow, cleaned up on flow end
- Reference: "Question 3: How Variables Persist" in Specific Patterns

### Flows
- `flow <name>` - Define interaction pattern
- `flow main` - Entry point
- `await <flow>` - Call and wait
- `start <flow>` - Start without waiting
- `activate <flow>` - Run repeatedly
- Reference: Section "Flows & Flow Control" in Specification

### Python Actions
```python
@action(name="MyAction")
async def my_function(param: type):
    return result
```
**Called from Colang:**
```colang
$result = await MyAction(param=value)
```
- Name MUST end with `Action`
- All functions MUST be async
- Parameters MUST be type-hinted
- Reference: "Question 2" in Specific Patterns

### LLM Integration
```colang
import llm

$result = ..."Instruction for LLM"
```
- Use NLD (Natural Language Descriptions)
- Configure in config.yml
- Reference: "LLM Integration" section in Specification

### Standard Library
```colang
import core
import llm

user said "text"
bot say "response"
```
- Core provides user/bot abstractions
- LLM adds AI capabilities
- Reference: `COLANG_2_0_STANDARD_LIBRARY.md`

---

## 🔍 Syntax Cheat Sheet

```colang
# Variables
$var = value
global $shared_var

# Events
match EventName(param=value) as $ref
send EventName(param=value)

# Flows
flow name $param -> $return
    await other_flow
    return $return

# Control flow
if condition
    statements
elif condition
    statements
else
    statements

while condition
    statements
    break
    continue

when event
    statements
or when event
    statements

# Actions
start MyAction() as $ref
await MyAction()
match $ref.Finished()

# Python actions
@action(name="MyAction")
async def my_action(param: type) -> type:
    return result

# Imports
import core
import llm
```

---

## 📋 Files in Your Project

All 4 documents are in:
```
c:\Users\Gonzalez Family\Documents\project_nautilus\
├── COLANG_2_0_COMPLETE_SPECIFICATION.md
├── COLANG_2_0_WORKING_EXAMPLES.md
├── COLANG_2_0_STANDARD_LIBRARY.md
└── COLANG_2_0_SPECIFIC_PATTERNS.md
```

---

## ✅ What This Documentation Covers

- ✅ Complete Colang 2.0 syntax specification
- ✅ All keywords and operators
- ✅ 20 working examples from official repo
- ✅ Python action integration (correct syntax)
- ✅ LLM integration with NLD
- ✅ Variable scoping and persistence
- ✅ Flow lifecycle and management
- ✅ Standard library reference
- ✅ Error handling patterns
- ✅ Best practices and conventions
- ✅ Multi-turn conversations
- ✅ Parallel/concurrent flows
- ✅ Conditional and event-based branching
- ✅ Loops and flow control
- ✅ State management
- ✅ Custom flows and modularity
- ✅ Interaction loops
- ✅ Multimodal support
- ✅ Debuggiing helpers

---

## 🚀 Getting Started Template

**config/config.yml:**
```yaml
colang_version: "2.x"

models:
  - type: main
    engine: openai
    model: gpt-4-turbo
```

**config/main.co:**
```colang
import core
import llm

flow main
    activate automating intent detection
    
    bot say "Hello! What can I help you with?"
    
    while True
        when user expressed greeting
            bot say "Hi there!"
        
        or when user expressed goodbye
            bot say "Bye!"
            return
        
        or when unhandled user intent
            llm continue interaction
        
        match RestartEvent()

flow user expressed greeting
    user said "hi" or user said "hello"

flow user expressed goodbye
    user said "bye" or user said "goodbye"
```

**Run:**
```bash
export OPENAI_API_KEY="your-key"
nemoguardrails chat --config=./config
```

---

## 📚 Official Resources

- **Documentation**: https://docs.nvidia.com/nemo/guardrails/
- **GitHub**: https://github.com/NVIDIA/NeMo-Guardrails
- **Paper**: https://arxiv.org/abs/2310.10501

---

## ❓ Still Have Questions?

1. **About syntax?** → Check `COLANG_2_0_COMPLETE_SPECIFICATION.md`
2. **About implementation?** → Check `COLANG_2_0_WORKING_EXAMPLES.md`
3. **About specific pattern?** → Check `COLANG_2_0_SPECIFIC_PATTERNS.md`
4. **About library flows?** → Check `COLANG_2_0_STANDARD_LIBRARY.md`
5. **Need example code?** → Search in `COLANG_2_0_WORKING_EXAMPLES.md`

---

## 📝 Version Information

- **Colang Version**: 2.0 (Beta and stable)
- **NeMo Guardrails**: v0.17.0
- **Source**: Official NVIDIA GitHub Repository
- **Compilation Date**: February 24, 2026

---

## 🎯 Project-Specific Notes

You have files in your project that reference Colang:
- Check `config/rails/` for example .co files
- Look at `data/diagnostic_maps.yaml` for configuration
- Review `APP_GROUND_RULES.md` for your specific implementation requirements
- Use these documents as your authoritative reference

---

**You now have COMPLETE Colang 2.0 documentation. Everything you need is here.**

Start with Example 1 in `COLANG_2_0_WORKING_EXAMPLES.md` and build from there!
