# Colang 2.0 - Complete Language Specification

**Source**: Official NVIDIA NeMo-Guardrails GitHub Repository  
**Version**: Colang 2.0 (Beta and stable)  
**Last Updated**: Documentation from NeMo Guardrails v0.17.0

---

## Table of Contents

1. [Overview](#overview)
2. [Core Concepts](#core-concepts)
3. [Language Syntax](#language-syntax)
4. [Variables & Expressions](#variables--expressions)
5. [Events & Actions](#events--actions)
6. [Flows & Flow Control](#flows--flow-control)
7. [Python Actions](#python-actions)
8. [LLM Integration](#llm-integration)
9. [Working Examples](#working-examples)
10. [Standard Library](#standard-library)

---

## Overview

**Colang 2.0** is an event-driven interaction modeling language designed for building flexible and controllable conversational AI applications. It's interpreted by a Python runtime and is part of the NeMo Guardrails toolkit.

### Key Features:
- Event-driven interaction model
- Python-like syntax (easy learning curve)
- Support for parallel/concurrent flows
- Integration with Large Language Models (LLMs)
- Multi-modal interaction support
- Explicit state management

### File Extension
- Colang files use `.co` extension
- Configuration files use `config.yml` or `config.yaml`

### Configuration
```yaml
# config.yml - Minimal Colang 2.0 setup
colang_version: "2.x"

models:
  - type: main
    engine: openai
    model: gpt-4-turbo
```

---

## Core Concepts

### 1. **Events**
Events are the fundamental building blocks representing interactions in the system.

**Event Definition Syntax:**
```colang
<EventName>[(param=<value>[, param=<value>]...)]
```

**Examples:**
```colang
# Simple event
InputEvent()

# Event with parameters
UtteranceUserActionFinished(final_transcript="Hi")
StartUtteranceBotAction(script="Hello", intensity=1.0)
MyCustomEvent(count=42, name="test")
```

**Event Naming Convention:** Pascal case (e.g., `MyEventName`)

### 2. **Actions**
Actions are objects with a lifecycle, containing multiple events:
- `StartXAction` - starts an action
- `XActionStarted` - action has started
- `XActionFinished` - action completed
- `StopXAction` - stops an action

**Common Actions:**
- `UtteranceBotAction(script="...")` - bot speaks
- `UtteranceUserAction.Finished()` - user speaks
- `GestureBotAction(gesture="...")` - bot gesture
- `TimerBotAction(timer_name="...", duration=...)` - delay

### 3. **Flows**
Flows are named sequences of interaction patterns (similar to functions in Python).

**Entry Point:** `flow main` - automatically starts first

**Naming Convention:**
- Use lowercase letters, numbers, underscores, and whitespace
- Convention: Use imperative form for actions (e.g., `bot say $text`)
- Convention: Use past form for events (e.g., `user said something`)

### 4. **Variables**
Variables store data and state throughout flow execution.

**Syntax:** Variables must start with `$` character

**Example:**
```colang
$user_name = "John"
$count = 0
$values = [1, 2, 3]
```

---

## Language Syntax

### Flow Definition

**Complete Syntax:**
```colang
flow <name of flow>[$<in_param_name>[=<default_value>]...] [-> <out_param_name>[=<default_value>][, ...]]
    """<optional docstring>"""
    <interaction pattern>
```

**Examples:**

#### Simple Flow
```colang
flow main
    user said "hi"
    bot say "Hello!"
```

#### Flow with Parameters
```colang
flow bot say $text $volume=1.0
    """Bot says given text."""
    await UtteranceBotAction(script=$text, intensity=$volume)

flow user said $text -> $transcript
    """User said something and return transcript."""
    match UtteranceUserActionFinished(final_transcript=$text) as $event
    return $event.final_transcript
```

#### Flow with Return Values
```colang
flow multiply $number_1 $number_2 -> $result
    $result = $number_1 * $number_2
    return $result

# Usage:
flow main
    $product = await multiply 3 4
    bot say "Result: {$product}"
```

### Statements

#### 1. **Event Matching Statement (`match`)**
```colang
match <Event> [as $<event_ref>] [and|or <Event>]...
```

**Examples:**
```colang
# Simple match
match UtteranceUserActionFinished(final_transcript="Hi")

# Match with reference
match UtteranceUserActionFinished(final_transcript="Hi") as $user_event

# Partial match (fewer parameters specified)
match UtteranceUserActionFinished()

# Match with multiple events (AND)
match UtteranceUserActionFinished(final_transcript="Hi") and GestureUserActionFinished(gesture="Thumbs up")

# Match with multiple events (OR)
match UtteranceUserActionFinished(final_transcript="Hi") or UtteranceUserActionFinished(final_transcript="Hello")
```

**Partial Match Rules:**
- Omit parameters you don't care about
- Match succeeds if specified parameters match
- Less specific matches have lower priority in conflict resolution

#### 2. **Event Generation Statement (`send`)**
```colang
send <Event> [as $<event_ref>] [and|or <Event>]...
```

**Examples:**
```colang
# Simple send
send StartUtteranceBotAction(script="Hello")

# Send with reference
send StartUtteranceBotAction(script="Hello") as $event_ref

# Sequential events (AND)
send StartUtteranceBotAction(script="Hi") and StartGestureBotAction(gesture="Wave")

# Random selection (OR) - picks one at runtime
send StartGestureBotAction(gesture="Smile") or StartGestureBotAction(gesture="Frown")
```

#### 3. **Flow Starting Statement (`start`, `await`)**
```colang
start <Flow> [as $<ref>]    # Start and continue
await <Flow> [as $<ref>]    # Start and wait for Finished event
<Flow>                       # Default is await (can omit keyword)
```

**Examples:**
```colang
# Start without waiting
start bot say "Hi" as $flow_ref
match $flow_ref.Finished()

# Await (start and wait)
await bot say "Hi there"

# Using default (await is implicit)
bot say "Welcome"

# Start multiple flows
start bot say "Hi" and bot gesture "Wave with one hand"

# Wait for one of multiple flows
await bot say "Hi" or bot gesture "Wave"
```

#### 4. **Action Handling**
```colang
# Starting an action
start UtteranceBotAction(script="Hello") as $action_ref

# Waiting for action (common shorthand)
await UtteranceBotAction(script="Hello")

# Stopping an action
send $action_ref.Stop()
```

#### 5. **Variable Assignment**
```colang
$variable = <value or expression>
```

**Examples:**
```colang
$name = "John"
$count = 5
$total = $count + 10
$list = [1, 2, 3]
$dict = {"key": "value"}
$user_input = "text from event"
```

#### 6. **String Interpolation**
```colang
$var = "value"
await UtteranceBotAction(script="Hello {$var}!")
```

**Escaping braces:**
```colang
"Use {{ and }} to include literal braces"
```

#### 7. **Comments**
```colang
# This is a comment
```

---

## Variables & Expressions

### Variable Naming Rules
- Must start with alphabetic character
- Can contain alphanumeric characters and underscore
- Always start with `$` prefix
- Case sensitive
- No whitespace within variable name

**Regex Pattern:** `$[^\W\d]\w*`

### Data Types Supported
```colang
# Strings
$str = "Hello"

# Integers
$int = 42

# Floats  
$float = 3.14159

# Booleans
$bool = True

# Lists
$list = ["one", "two", "three"]
$numbers = [1, 2, 3, 4]

# Sets
$set = {0.1, 0.2, 0.3}

# Dictionaries
$dict = {"key_a": 1, "key_b": 2}

# Special types
$event_ref = <reference to event>
$action_ref = <reference to action>
$flow_ref = <reference to flow>
```

### Expression Evaluation

#### Arithmetic Operators
```colang
21 + 21
21 - 5
5 * 3
10 / 2
10 % 3           # Modulus
2 ** 10          # Power (1024)
```

#### Comparison Operators
```colang
$x == $y         # Equal
$x != $y         # Not equal
$x < $y          # Less than
$x > $y          # Greater than
$x <= $y         # Less or equal
$x >= $y         # Greater or equal
```

#### Logical Operators
```colang
$a and $b        # Logical AND
$a or $b         # Logical OR
not $a           # Logical NOT
```

#### Bitwise Operators
```colang
$x >> $y         # Right shift
$x << $y         # Left shift
$x ^ $y          # XOR
$x | $y          # OR
$x & $y          # AND
~$x              # NOT
```

#### In Operator
```colang
$item in $list
```

#### Conditional Expression
```colang
"equal" if $x == $y else "not equal"
"a" if 1 == 2 else "b" if 2 == 3 else "c"
```

#### Container Access
```colang
$list[0]         # List access by index
$dict["key"]     # Dict access by key
$object.attr     # Object attribute access
```

#### Built-in Functions
```colang
# Type checking
is_bool($x) -> bool
is_int($x) -> bool
is_float($x) -> bool
is_str($x) -> bool
is_regex($x) -> bool

# Conversions
int($string) -> int
float($string) -> float
str($x) -> str
type($x) -> str
list($iterable) -> list

# Container operations
len($obj) -> int
$dict.update({"key": value})

# String operations
escape($string) -> str
pretty_str($x) -> str

# Regular expressions
regex($pattern) -> Pattern
search($pattern, $string) -> bool
findall($pattern, $string) -> List[str]

# Utilities
uid() -> str              # Generate UUID
rand() -> float           # Random [0, 1)
randint($max) -> int      # Random int
flows_info() -> dict      # Get flow info
```

### Variable Scope

#### Local Variables (Default)
```colang
flow my_flow
    $local_var = "only visible in this flow"
```

#### Flow Output Parameters
```colang
flow get_user_input -> $transcript
    match UtteranceUserActionFinished() as $event
    $transcript = $event.final_transcript
    return $transcript

# Usage:
$user_said = await get_user_input
```

#### Global Variables
```colang
flow main
    global $shared_var
    $shared_var = "accessible from any flow"

flow other_flow
    global $shared_var
    # Can now access and modify $shared_var
```

### Flow Member Variables (via $self)
```colang
flow my_flow
    $self.uid              # Unique flow instance ID
    $self.flow_id          # Flow name
    $self.status.value     # Flow state: "waiting", "starting", "started", "stopping", "stopped", "finished"
    $self.loop_id          # Interaction loop ID
    $self.parent_uid       # Parent flow instance UID
    $self.child_flow_uids  # Child flow instance UIDs (list)
    $self.context          # Variable context dict
    $self.priority         # Flow priority [0.0-1.0]
    $self.arguments        # Flow arguments dict
    $self.activate         # Whether flow is activated
```

### Action Member Variables
```colang
start MyAction() as $ref
$ref.uid                   # Action UID
$ref.name                  # Action name
$ref.flow_uid              # Flow that started action
$ref.status.value          # Action status
$ref.context               # Action event parameters
$ref.start_event_arguments # Start arguments dict
```

### Event Member Variables
```colang
match MyEvent(param=value) as $ref
$ref.name                  # Event name
$ref.arguments             # Event arguments dict
$ref.flow                  # (For flow events) Flow reference
```

---

## Events & Actions

### Event Generation (`send`) and Matching (`match`)

#### Complete Event Syntax
```colang
<EventName>[(param1=value1, param2=value2, ...)]
```

#### Event Matching Rules
1. **Exact Match:** All specified parameters must match
2. **Partial Match:** Unspecified parameters are ignored
3. **Parameter Types:** bool, str, float, int, list, set, dict
4. **Regex Patterns:** Use `regex("pattern")` for pattern matching
5. **Specificity Scoring:** Perfect match = 1.0, missing param factor = 0.9 per param

**Example Matching:**
```colang
# Match specific user utterance
match UtteranceUserActionFinished(final_transcript="Hi")

# Match any user utterance (partial match - less specific)
match UtteranceUserActionFinished()

# Match with list parameter
match Event(items=["a", "b", "c"])

# Match with regex
match Event(name=regex("(?i)john.*"))
```

### UMIM Standard Events

#### User Input Events
```colang
# Match when user finishes utterance
UtteranceUserActionFinished(final_transcript="...", action_uid="...", ...)

# Match while user is speaking
UtteranceUserActionTranscriptUpdated(interim_transcript="...", action_uid="...", ...)

# Gesture from user
GestureUserActionFinished(gesture="...", action_uid="...", ...)
```

#### Bot Output Events
```colang
# Send bot utterance
StartUtteranceBotAction(script="...", intensity=1.0)

# Stop bot utterance
send UtteranceBotAction.Stop(action_uid=$action_ref.action_uid)

# Send bot gesture
StartGestureBotAction(gesture="...")

# Match bot finished action
match UtteranceBotAction.Finished(action_uid=$ref.action_uid)
```

#### Flow Internal Events
```colang
# Flow lifecycle events (internal - high priority)
StartFlow(flow_id="...", flow_instance_uid="...", **arguments)
FlowStarted(flow_id="...", flow_instance_uid="...")
FlowFinished(flow_id="...", flow_instance_uid="...", **all_variables)
FlowFailed(flow_id="...", flow_instance_uid="...", **all_variables)
StopFlow(flow_id="...", flow_instance_uid="...", deactivate=False)

# Unhandled event
UnhandledEvent(event="EventName", loop_ids=set(), **parameters)
```

### Event Grouping

#### AND Operator (All must match)
```colang
# Match both events (in order)
match Event1() and Event2()

# Send both events (sequentially)
send Event1() and Event2()

# Start both flows (sequentially)
start flow_a and flow_b

# Await both (wait for both to finish)
await flow_a and flow_b
```

#### OR Operator (Any one matches/random selection)
```colang
# Match whichever comes first
match Event1() or Event2()

# Send one randomly
send Event1() or Event2()

# Start one randomly (no waiting)
start flow_a or flow_b

# Await first one to finish
await flow_a or flow_b
```

#### Complex Groups with Parentheses
```colang
match ((EventA() or EventB()) and EventC())
     or ((EventD() or EventE()) and EventF())
```

---

## Flows & Flow Control

### Flow Lifecycle

#### Starting Flows
```colang
# 1. Implicit await (default, same as await)
user said "hi"

# 2. Explicit await - start and wait for Finished
await user said "hi"

# 3. Start without waiting
start user said "hi" as $flow_ref

# 4. Activate - restart automatically on finish
activate user greeting handler
```

#### Flow Events
```colang
# Reference-based (specific instance)
start bot_greeting as $ref
match $ref.Finished()

# Name-based (any instance of that flow)
match (bot_greeting).Finished()

# Failed event
match $ref.Failed()

# Access flow variables from event
match $ref.Finished() as $event
$result = $event.return_value  # Get return value
$vars = $event.context         # Get all variables
```

### Control Flow Statements

#### 1. **Conditional Branching (if/elif/else)**

**Syntax:**
```colang
if <condition>
    <interaction pattern 1>
[elif <condition>
    <interaction pattern 2>]
...
[else
    <interaction pattern else>]
```

**Example:**
```colang
flow check_users
    $number_of_users = 1
    if $number_of_users == 0
        await user became present
    elif $number_of_users > 1
        bot say "Can only interact with one user"
    else
        bot say "Welcome!"
```

**Rules:**
- Conditions are evaluated immediately using expression evaluation
- Uses Python `if/elif/else` semantics
- All branches are acceptable interaction patterns

#### 2. **Event-based Branching (when/or when/else)**

**Syntax:**
```colang
when <MixedGroup1>
    <interaction pattern 1>
[or when <MixedGroup2>
    <interaction pattern 2>]
...
[else
    <interaction pattern else>]
```

**Example:**
```colang
flow main
    bot say "How are you?"
    when user said "Good" or user said "Great"
        bot say "Great!"
    or when user said "Bad" or user said "Terrible"
        bot say "Sorry to hear"
    else
        bot say "Thanks for sharing"
```

**Behavior:**
- All flows/actions in `when/or when` start concurrently
- First one to finish wins, others are stopped
- Actions/flows treated as `await` statements
- Excellent for multi-turn interactions

#### 3. **Loops (while)**

**Syntax:**
```colang
while <condition>
    <interaction pattern>
```

**Example:**
```colang
flow bot count to $number
    $current = 1
    while $current <= $number
        bot say "{$current}"
        $current = $current + 1
```

**Loop Control:**
```colang
break       # Exit loop immediately
continue    # Skip to next iteration
```

#### 4. **Early Return/Abort (return/abort)**

**Syntax:**
```colang
return [$value]   # Flow succeeds, optionally return value
abort             # Flow fails
```

**Example:**
```colang
flow multiply $a $b -> $result
    $result = $a * $b
    return $result

flow main
    $product = await multiply 3 4
    bot say "Result is {$product}"
```

**Abort Example:**
```colang
flow validate_user
    match user said something as $event
    if "bad_word" in $event.final_transcript
        abort  # Flow fails if bad word detected
    else
        return  # Flow succeeds
```

#### 5. **No-op (pass)**
```colang
when condition_a
    pass  # Do nothing, continue
or when condition_b
    bot say "Something"
```

### Flow Activation and Management

#### Activate a Flow
```colang
# Single activation
activate handling user greeting

# Multiple with parameters
activate handling user said "Hi"
activate handling user said "Bye"

# Group activation
activate handler_a and handler_b
```

**Behavior:**
- Flow automatically restarts when finished
- Same configuration only activates once
- Better than starting at beginning when only needed later

#### Start New Flow Instance
```colang
@active        # Auto-activate at startup
flow my_flow
    user said "Hi"
    start_new_flow_instance:  # Start new instance at this point
    bot say "Hi again"
    user said "Bye"
```

#### Deactivate a Flow
```colang
deactivate handling user greeting

# Deactivate with parameters
deactivate handling user said "Hi"
```

#### Override a Flow
```colang
@override
flow bot say $text
    log "Bot saying: {$text}"
    await UtteranceBotAction(script=$text)
```

**Rules:**
- Must have exactly one `@override` decorator if flow defined twice
- Useful for extending standard library flows

### Interaction Loops

**Syntax:**
```colang
@loop(id="loop_name"[, priority=<int>])
flow <flow_name>
    <interaction pattern>
```

**Example - Parallel Interactions:**
```colang
flow main
    activate gesture_handler      # In different loop
    while True
        when user said "Hi"
            bot say "Hi!"
        or when user said "Bye"
            bot say "Goodbye"

@loop("gestures")
flow gesture_handler
    activate smile_on_greeting
    activate frown_on_goodbye

@loop("gestures")
flow smile_on_greeting
    user said "Hi"
    bot gesture "smile"

@loop("gestures")
flow frown_on_goodbye
    user said "Bye"
    bot gesture "frown"
```

**Rules:**
- Default loop_id is inherited from parent flow
- Default priority is 0 (higher number = higher priority)
- Different loops don't conflict (can execute in parallel)
- Same loop conflicts are resolved by specificity

### Flow Naming Conventions

```colang
# Bot imperatives (what bot should do)
flow bot say $text
flow bot gesture $gesture
flow bot informed

# User past tense (what user did)
flow user said $text
flow user gestured $gesture
flow user expressed greeting

# User intents (only single statement)
flow user greeted
    user said "Hi" or user said "Hello"

# Bot intents (only single statement)
flow bot informed about cancellation
    bot say "Order cancelled" and bot gesture "nod"

# Activity flows (actions/states to manage)
flow handling user greeting
flow tracking bot state
```

### Conflict Resolution and Prioritization

**Matching Score Calculation:**
- Perfect match (all parameters match) = 1.0
- Partial match missing n parameters = 1.0 × (0.9 ^ n)
- Aggregated across event chain

**Example:**
```colang
flow pattern_a
    user said "Hi"              # score: 1.0 (perfect)
    bot say "Hello"

flow pattern_b
    user said something         # score: 0.9 (partial)
    bot say "Sure"
```

When user says "Hi":
- Pattern A: 1.0 (perfect match on "Hi")
- Pattern B: 0.9 (any utterance matches, less specific)
- **Pattern A wins**

**Adjust Priority:**
```colang
flow less_important_pattern
    priority 0.5  # Multiply scores by 0.5
    user said something
    bot say "Fallback"
```

**Force Specificity:**
```colang
flow some_pattern
    user said something
    # This is partial (score 0.9), to make specific:
    match UtteranceUserActionFinished(final_transcript=regex(".*"))
    # Now scores like 1.0 (all params specified)
```

---

## Python Actions

### Defining Python Actions

**File Location:** 
- `actions.py` in config directory, OR
- Any `.py` file in `action/` subdirectory

**Basic Syntax:**
```python
from nemoguardrails.actions import action

@action(name="MyCustomAction")
async def my_custom_action(param1: int, param2: str):
    """Action docstring"""
    result = param1 + len(param2)
    return result
```

**Name Requirements:**
- Must end with `Action` suffix
- Use in Colang as: `MyCustomAction(param1=5, param2="hello")`

### Calling Python Actions from Colang

#### Basic Call
```colang
flow main
    $result = await MyCustomAction(value=5)
    bot say "Result: {$result}"
```

#### Asynchronous Actions
```python
# Python - Long-running operation
@action(name="FetchDataAction", execute_async=True)
async def fetch_data(url: str):
    # Could take time (API call, etc.)
    result = await some_async_operation(url)
    return result
```

**Colang - Option 1: Wait for completion**
```colang
$result = await FetchDataAction(url="https://api.example.com")
bot say "Data: {$result}"
```

**Colang - Option 2: Start and wait separately**
```colang
start FetchDataAction(url="https://api.example.com") as $action_ref
# Do other things...
match $action_ref.Finished() as $event
$result = $event.return_value
bot say "Data: {$result}"
```

### Action Context Parameters

Available in Python action definition:

```python
@action(name="ContextAwareAction")
async def context_action(
    events: list,              # Recent event history
    context: dict,             # Global variables and state
    config: dict,              # config.yml settings
    llm_task_manager,          # LLM manager object
    state,                     # State machine state
):
    # Access context
    var = context.get("$variable_name")
    
    # Check config
    setting = config.get("some_setting")
    
    # Use LLM
    # response = await llm_task_manager....
    
    return result
```

### Accessing Return Values

```colang
# Direct assignment
$result = await MyAction(param=value)

# Via event reference
start MyAction(param=value) as $ref
match $ref.Finished() as $event
$result = $event.return_value
```

### Error Handling

```python
@action(name="ValidatingAction")
async def validate_action(data: str):
    if not data:
        # Return None or raise exception
        return None
    return data.upper()
```

```colang
flow main
    $result = await ValidatingAction(data=$user_input)
    if $result is None
        bot say "Invalid input"
    else
        bot say "Processed: {$result}"
```

---

## LLM Integration

### Configuration

**config.yml:**
```yaml
colang_version: "2.x"

models:
  - type: main
    engine: openai
    model: gpt-4-turbo

# Environment variable required:
# export OPENAI_API_KEY="your-key"
```

### Supported Models

**OpenAI:**
```yaml
engine: openai
model: gpt-3.5-turbo
# or: gpt-4-turbo, gpt-4o, gpt-4o-mini
```

**NVIDIA NIM (NIMs):**
```yaml
engine: nim
model: meta/llama3-8b-instruct
# or: meta/llama3-70b-instruct, meta/llama-3.1-8b-instruct, llama-3.1-70b-instruct
```

### Natural Language Descriptions (NLD)

**Syntax:**
```colang
$variable = ..."Natural language instruction to LLM"
```

**Examples:**

#### Simple NLD
```colang
$greeting = ..."Generate a friendly greeting for the user"
bot say $greeting
```

#### Extract Information
```colang
$user_name = ..."What is the name of the user? Return 'guest' if not available."
bot say "Hello {$user_name}"
```

#### Structured Output
```colang
$order = ..."Extract the products ordered by user in format: ['product1', 'product2']"
```

#### With Context
```colang
$summary = ..."Summarize the conversation so far. Context: '{$previous_messages}'"
bot say $summary
```

#### With Variables
```colang
$response = ..."Given the user's mood: {$mood}, provide an appropriate response"
```

**Best Practices:**
- Be explicit about format: "Return as a single string"
- Specify constraints: "Return only the number, no text"
- Handle missing data: "Return 'unknown' if not available"
- Use context variables in curly braces: `{$variable}`

### User Intent Matching with LLM

```colang
import core
import llm

flow main
    activate automating intent detection
    activate generating user intent for unhandled user utterance

    while True
        when user greeted
            bot say "Hi there!"
        or when user said goodbye
            bot say "Goodbye!"
        or when unhandled user intent
            bot say "Thanks for sharing!"

flow user greeted
    user said "Hi" or user said "Hello"

flow user said goodbye
    user said "Bye" or user said "See you"
```

**Behavior:**
- Exact matches use defined flows
- Unmatched utterances use LLM to infer intent
- LLM maps to closest user intent flow

### Bot Response Generation

```colang
import core
import llm

flow main
    user said something
    llm continue interaction
```

**Effect:** LLM generates contextually appropriate bot response

### Marking User/Bot Actions for LLM

```colang
@meta(user_intent=True)
flow user asked question
    user said "How do I..." or user said "What is..."

@meta(bot_action=True)
flow bot respond helpfully
    bot say "..."
```

---

## Working Examples

### Example 1: Simple Hello World

**main.co:**
```colang
import core

flow main
    user said "hi"
    bot say "Hello World!"
```

**Run:** `nemoguardrails chat --config=<directory>`

**Interaction:**
```
> hi
Hello World!
```

### Example 2: Multi-Turn Conversation

**main.co:**
```colang
import core

flow main
    user said "Hello"
    bot say "Hi! How are you?"
    
    user said "Good and you?"
    bot say "Great! Thanks"
    
    user said "Bye"
    bot say "Goodbye!"
```

### Example 3: Flow with Parameters and Return Value

**main.co:**
```colang
import core

flow main
    $result = await multiply 3 4
    bot say "3 × 4 = {$result}"
    
    match RestartEvent()

flow multiply $a $b -> $result
    $result = $a * $b
    return $result
```

### Example 4: Conditional Logic

**main.co:**
```colang
import core

flow main
    $number = 5
    
    if $number < 5
        bot say "Number is small"
    elif $number == 5
        bot say "Number is exactly 5"
    else
        bot say "Number is large"
    
    match RestartEvent()
```

### Example 5: Event-based Branching

**main.co:**
```colang
import core

flow main
    bot say "Do you like pizza?"
    
    when user said "Yes"
        bot say "Great choice!"
    or when user said "No"
        bot say "That's okay!"
    else
        bot say "I didn't understand"
    
    match RestartEvent()
```

### Example 6: Loop with Counter

**main.co:**
```colang
import core

flow main
    bot count to 3

flow bot count to $number
    $current = 1
    while $current <= $number
        bot say "{$current}"
        $current = $current + 1
    bot say "Blastoff!"
```

**Output:**
```
1
2
3
Blastoff!
```

### Example 7: Python Action Integration

**config/actions.py:**
```python
from nemoguardrails.actions import action

@action(name="GetWeatherAction")
async def get_weather(city: str):
    # Simulate API call
    return f"Sunny in {city}"
```

**main.co:**
```colang
import core

flow main
    user said "What's the weather?"
    $weather = await GetWeatherAction(city="San Francisco")
    bot say $weather
```

### Example 8: User Intent with LLM

**config.yml:**
```yaml
colang_version: "2.x"
models:
  - type: main
    engine: openai
    model: gpt-4-turbo
```

**main.co:**
```colang
import core
import llm

flow main
    activate automating intent detection
    activate generating user intent for unhandled user utterance
    
    while True
        when user expressed greeting
            bot say "Hello!"
        or when user expressed goodbye
            bot say "Bye!"
        or when unhandled user intent
            bot say "Interesting!"

flow user expressed greeting
    user said "Hi" or user said "Hello" or user said "Hey"

flow user expressed goodbye
    user said "Bye" or user said "Goodbye" or user said "See you"
```

### Example 9: Concurrent Flows (Parallel Actions)

**main.co:**
```colang
import core

flow main
    user said "Hi"
    
    # Start two actions concurrently
    await bot say "Hello!" and bot gesture "wave"
    
    user said "Bye"
    bot say "Goodbye!"

flow bot gesture $gesture
    # In real system, this would do actual gesture
    # For CLI simulation, just log it
    pass
```

### Example 10: Flow with Retry Logic

**main.co:**
```colang
import core

flow main
    user said something
    await validate user input
    bot say "Input validated!"
    match RestartEvent()

flow validate user input
    $attempts = 0
    while $attempts < 3
        # Validation logic here
        $attempts = $attempts + 1
        if $attempts >= 3
            abort  # Fail if too many attempts
    return
```

---

## Standard Library

### Core Module (`import core`)

**Available Flows:**

#### User-related Flows:
```colang
user said $text -> $transcript
user said something -> $transcript
user saying $text -> $transcript
user started saying something
user said something unexpected -> $event, $transcript
```

#### Bot-related Flows:
```colang
bot say $text
bot inform $text
bot ask $text
bot respond $text
bot express $text
bot clarify $text
bot suggest $text
bot said $text
bot said something -> $text
```

#### State Tracking Flows:
```colang
tracking bot talking state
tracking user talking state
```

#### Debug/Utility Flows:
```colang
debugging helpers
warning of unexpected user utterance
notification of undefined flow start
```

### LLM Module (`import llm`)

**Available Flows:**

```colang
# Intent matching
automating intent detection
generating user intent for unhandled user utterance

# Generation
llm continue interaction

# Advanced
basic interaction loop
```

### Timing Module (`import timing`)

Events for time-based triggers:
```colang
when user was silent <duration>
    # Triggered after user silent for <duration> seconds
```

### Other Modules

- `avatars` - Avatar pose/gesture flows
- `guardrails` - Safety and filtering flows
- `attention` - Attention/focus management flows

---

## Complete Syntax Reference

### Keywords and Reserved Words

```colang
# Control flow
if, elif, else
when, or when, else
while, break, continue
return, abort, pass

# Flow management
flow, define
start, await, activate, deactivate

# Events/Actions
send, match
and, or

# Variables/Expressions
global, priority

# Imports
import

# Decorators
@override, @active, @loop, @meta

# Comments
# (single line only)
```

### Variable Lifecycle

1. **Local Scope (default):**
   - Defined within a flow
   - Not accessible outside
   - Cleaned up when flow ends

2. **Return Values:**
   - Specified in flow signature: `flow name -> $var`
   - Accessible via return statement
   - Passed to caller via `await`

3. **Global Scope:**
   - Declared with `global` keyword
   - Accessible across all flows
   - Persist through flow lifecycle

4. **Flow Parameters:**
   - Passed by value (copied)
   - Mutable types (list, dict) share references
   - Available via flow invoke

### Syntax Modes

#### Statement Mode
```colang
# Normal Colang statements
user said "hi"
bot say "Hello"
```

#### Expression Mode (parentheses required)
```colang
# Standalone expression statement
($dict.update({"key": value}))

# Expression as flow parameter
bot count to ($number + 1)
```

#### Multiline Strings
```colang
flow my_flow
    """This is a docstring
    that can span multiple lines"""
    # Rest of flow...
```

---

## Error Messages and Debugging

### Common Errors

**Undefined Flow:**
```
ColangError: Failed to start undefined flow: 'flow_name'
```
*Fix: Define the flow or import it*

**Type Mismatch:**
```
Colang error: Type error in expression evaluation
```
*Fix: Check variable types and conversions*

**Syntax Error:**
```
ColangError: Syntax error in .co file
```
*Fix: Check indentation and statement syntax*

### Debugging Flows

```colang
# Enable debug output
import core
activate debugging helpers

flow main
    # Your code here...
```

**Log Statements:**
```colang
log "Debug message: {$variable}"
```

**Observation:**
```colang
activate observation of flow $flow_name
```

### Development and Syntax Highlighting

**VSCode Extension (Recommended):**
- Install Colang syntax highlighting extension
- Enables autocomplete and syntax validation

**File Validation:**
```bash
# Validate Colang syntax
nemoguardrails convert path/to/bots --validate
```

---

## Migration from Colang 1.0 to 2.0

### Key Changes

1. **Flow Syntax:**
   - 1.0: `define flow` → 2.0: `flow`
   - 1.0: `message` → 2.0: events + actions

2. **User/Bot Messages:**
   - 1.0: Special `user message`, `bot message` → 2.0: Standard `UtteranceUserActionFinished()`, `UtteranceBotAction()`

3. **Generation Operator:**
   - New in 2.0: `...` operator for NLD

4. **Parallel Flows:**
   - Much improved in 2.0 with concurrent pattern matching

**Migration Tool:**
```bash
nemoguardrails convert "path/to/2.0-alpha/version/bots" --from-version "2.0-alpha"
```

---

## Best Practices

1. **Use the Core Library:** Import `core` for `bot say`, `user said` abstractions
2. **Flow Naming:** Follow conventions for readability
3. **Error Handling:** Use `abort` for failure cases
4. **Global Variables:** Use sparingly; prefer return values and parameters
5. **Python Actions:** Keep them simple; complex logic in Python is fine
6. **Testing:** Use the CLI chat to test interactively
7. **Comments:** Document complex flow logic
8. **Modularity:** Break up complex flows into smaller reusable flows

---

## Quick Reference

### File Structure
```
config/
├── config.yml           # Main configuration
├── actions.py           # Python actions
└── main.co              # Main Colang flows
```

### Entry Point
```colang
flow main
    # Executed first
    # Main interaction loop
    match RestartEvent()  # Restart after complete
```

### Variable Declaration Pattern
```colang
$var_name = initial_value
```

### Flow Invocation Pattern
```colang
await flow_name $param1 $param2 -> $return_value
```

### Event Pattern
```colang
match EventName(parameter=value) as $ref
send AnotherEvent(parameter=$value)
```

### LLM Integration Pattern
```colang
import llm
$result = ..."Instruction for LLM"
```

---

## Complete Feature Checklist

- ✅ Flow definition with parameters and return values
- ✅ Event matching and generation
- ✅ Event grouping (AND, OR)
- ✅ Actions with start/await semantics
- ✅ Variables with local, global, and parameter scopes
- ✅ Expression evaluation (arithmetic, logical, bitwise)
- ✅ String interpolation
- ✅ Conditional branching (if/elif/else)
- ✅ Event-based branching (when/or when/else)
- ✅ Loops (while) with break/continue
- ✅ Flow lifecycle (start, await, activate, deactivate)
- ✅ Parallel/concurrent flows
- ✅ Interaction loops with priorities
- ✅ Python action integration
- ✅ LLM integration with NLD
- ✅ User intent matching with LLM
- ✅ Bot response generation
- ✅ Flow override mechanism
- ✅ Decorator support (@override, @active, @loop, @meta)
- ✅ Standard library (core, llm, timing, avatars, etc.)
- ✅ Regular expression support
- ✅ Debug helpers

---

## Additional Resources

- **Official Documentation:** https://docs.nvidia.com/nemo/guardrails/
- **GitHub Repository:** https://github.com/NVIDIA/NeMo-Guardrails
- **Examples:** `examples/v2_x/language_reference/` in repository
- **Research Paper:** https://arxiv.org/abs/2310.10501

---

*This specification was compiled from official NVIDIA NeMo-Guardrails documentation (v0.17.0)*
*Last Updated: February 24, 2026*
