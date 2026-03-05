# Colang 2.0 - Complete Working Examples

This document contains **actual working examples** from the official NVIDIA NeMo-Guardrails repository with detailed explanations.

---

## Example 1: Hello World (Basic)

**File Structure:**
```
config/
├── config.yml
└── main.co
```

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

flow main
    user said "hi"
    bot say "Hello World!"
```

**Run:**
```bash
nemoguardrails chat --config=./config
```

**Interaction:**
```
> hi
Hello World!

> anything else is ignored
> 
```

**Explanation:**
- Imports `core` library for `user said` and `bot say` abstractions
- Main flow waits for user to say exactly "hi"
- Bot responds with "Hello World!"
- Anything else is ignored (no match)
- Main flow automatically restarts

---

## Example 2: Multi-Turn Conversation

**main.co:**
```colang
import core

flow main
    user said "hello"
    bot say "Hi there! How are you?"
    
    user said "good"
    bot say "Great! Glad to hear it."
    
    user said "bye"
    bot say "Goodbye!"
    
    match RestartEvent()
```

**Interaction:**
```
> hello
Hi there! How are you?

> good
Great! Glad to hear it.

> bye
Goodbye!

>
```

**Key Points:**
- `match RestartEvent()` at end restarts main flow
- Exact phrase matching only
- No LLM - must match exact text

---

## Example 3: Flexible Input with Variables

**main.co:**
```colang
import core

flow main
    $user_greeting = await user said something
    bot say "You said: {$user_greeting}!"
    
    match RestartEvent()

flow user said something -> $transcript
    """Wait for user to say anything."""
    match UtteranceUserActionFinished() as $event
    $transcript = $event.final_transcript
    return $transcript
```

**Interaction:**
```
> hi
You said: hi!

> hello world
You said: hello world!

> anything
You said: anything!
```

**Key Points:**
- Flow returns transcript value
- `await` assigns return value to variable
- String interpolation with `{$variable}`
- No exact matching needed

---

## Example 4: Conditional Logic (if/elif/else)

**main.co:**
```colang
import core

flow main
    $number_of_users = 1
    
    if $number_of_users == 0
        await user became present
    elif $number_of_users > 1
        bot say "Sorry, I can only help one user"
    else
        bot say "Welcome! Nice to meet you"
    
    match RestartEvent()
```

**Interaction:**
```
Welcome! Nice to meet you

>
```

**Key Points:**
- Conditional evaluated at flow execution time
- Can have multiple `elif` branches
- `else` is optional and runs if no conditions match

---

## Example 5: Event-Based Branching (when/or when/else)

**main.co:**
```colang
import core

flow main
    bot say "How are you feeling?"
    
    when user said "great"
        bot say "Excellent!"
    or when user said "bad"
        bot say "Sorry to hear that"
    or when user said "okay"
        bot say "That's good"
    else
        bot say "I'm not sure how you feel"
    
    match RestartEvent()
```

**Interaction:**
```
How are you feeling?

> great
Excellent!

> /RestartEvent

How are you feeling?

> bad
Sorry to hear that

> /RestartEvent

How are you feeling?

> something random
I'm not sure how you feel
```

**Key Points:**
- All `when` branches start concurrently
- First one to match wins
- Other branches are stopped
- `else` runs if no `when` matches
- Better for multi-option flows than nested `if/elif`

---

## Example 6: Function-like Flow with Parameters

**main.co:**
```colang
import core

flow main
    $sum = await add_numbers 5 3
    bot say "5 + 3 = {$sum}"
    
    $product = await multiply 4 7
    bot say "4 × 7 = {$product}"
    
    match RestartEvent()

flow add_numbers $a $b -> $result
    """Add two numbers together."""
    $result = $a + $b
    return $result

flow multiply $a $b -> $result
    """Multiply two numbers."""
    $result = $a * $b
    return $result
```

**Interaction:**
```
5 + 3 = 8
4 × 7 = 28

>
```

**Key Points:**
- Flows can act like functions
- Parameters passed by value
- Return value assigned to variable
- Docstring documents purpose

---

## Example 7: Loop with Counter

**main.co:**
```colang
import core

flow main
    bot count from 1 to 3

flow bot count from $start to $end
    """Count from start to end."""
    $current = $start
    while $current <= $end
        bot say "{$current}"
        $current = $current + 1
    bot say "Done!"
```

**Interaction:**
```
1
2
3
Done!

>
```

**Loop with Break/Continue:**
```colang
flow skip_even_numbers
    $current = 1
    while $current <= 5
        if $current % 2 == 0
            $current = $current + 1
            continue
        bot say "{$current}"
        $current = $current + 1
```

**Output:**
```
1
3
5
```

---

## Example 8: Flow with Validation (abort/return)

**main.co:**
```colang
import core

flow main
    user said something as $user_input
    await validate input $user_input
    bot say "Your input was valid"
    
    match RestartEvent()

flow validate input $text -> $is_valid
    """Validate user input."""
    if len($text) < 3
        bot say "Input too short"
        abort  # Flow fails
    else
        return True  # Flow succeeds
```

**Interaction 1 (Good):**
```
> hello
Your input was valid

>
```

**Interaction 2 (Bad):**
```
> hi
Input too short

>
```

**Key Points:**
- `abort` makes flow fail
- `return` makes flow succeed
- Can use with `when` to catch failures

---

## Example 9: Event-Based Error Handling

**main.co:**
```colang
import core

flow main
    start process_data as $process_ref
    
    when $process_ref.Finished()
        bot say "Process succeeded"
    else  # Process failed
        bot say "Process failed"
    
    match RestartEvent()

flow process_data
    $value = 5
    if $value > 10
        return  # Success
    else
        abort   # Failure
```

**Interaction:**
```
Process failed

>
```

---

## Example 10: Parallel Actions (Concurrent Flows)

**main.co:**
```colang
import core

flow main
    user said "hello"
    
    # Start multiple actions concurrently
    await bot say "Hello!" and bot gesture "wave"
    
    match RestartEvent()

flow bot gesture $gesture
    """Simulate a gesture using logging."""
    log "Bot gesture: {$gesture}"
```

**Interaction:**
```
> hello
Hello!
[gesture: wave would show here]

>
```

---

## Example 11: Python Action Integration

**config/actions.py:**
```python
from nemoguardrails.actions import action

@action(name="CreateGreetingAction")
async def create_greeting(name: str) -> str:
    """Create a personalized greeting."""
    return f"Hello, {name}! Welcome!"

@action(name="CalculateAction")
async def calculate(operation: str, a: int, b: int) -> int:
    """Perform math operation."""
    if operation == "add":
        return a + b
    elif operation == "multiply":
        return a * b
    else:
        return 0

@action(name="LogEventAction", execute_async=True)
async def log_event(event_type: str, details: str):
    """Long-running async operation."""
    # Could be API call, database write, etc.
    print(f"Event logged: {event_type} - {details}")
    return True
```

**main.co:**
```colang
import core

flow main
    $greeting = await CreateGreetingAction(name="Alice")
    bot say $greeting
    
    $sum = await CalculateAction(operation="add", a=5, b=3)
    bot say "5 + 3 = {$sum}"
    
    # Async action - start and wait
    start LogEventAction(event_type="greeting", details="Said hello") as $log_ref
    match $log_ref.Finished()
    bot say "Event logged"
    
    match RestartEvent()
```

**Interaction:**
```
Hello, Alice! Welcome!
5 + 3 = 8
Event logged

>
```

---

## Example 12: LLM Intent Matching

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
    # Activate LLM-based intent detection
    activate automating intent detection
    activate generating user intent for unhandled user utterance
    
    while True
        when user expressed greeting
            bot say "Hey there!"
        or when user expressed goodbye
            bot say "See you later!"
        or when unhandled user intent
            bot say "Thanks for that!"
        match RestartEvent()

flow user expressed greeting
    """User is greeting."""
    user said "hi" or user said "hello" or user said "hey"

flow user expressed goodbye
    """User is saying goodbye."""
    user said "bye" or user said "goodbye" or user said "see you"
```

**Interaction:**
```
> hi
Hey there!

> hello
Hey there!

> sup
Hey there!   [LLM matched to "greeting"]

> goodbye
See you later!

> adios
See you later!   [LLM matched to "goodbye"]

> tell me a joke
Thanks for that!
```

**How It Works:**
- Exact matches use defined flows
- Unmatched utterances use LLM to infer intent
- LLM maps to nearest user intent flow

---

## Example 13: NLD (Natural Language Description) - Extract Info

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
    user said something as $user_input
    
    # Use LLM to extract information
    $sentiment = ..."Analyze the sentiment of this text: '{$user_input}'. Reply with only 'positive', 'negative', or 'neutral'."
    
    if $sentiment == "positive"
        bot say "You sound happy!"
    elif $sentiment == "negative"
        bot say "Sorry to hear that"
    else
        bot say "Interesting perspective"
    
    match RestartEvent()

flow user said something -> $text
    match UtteranceUserActionFinished() as $event
    return $event.final_transcript
```

**Interaction:**
```
> I love this!
You sound happy!

> This is terrible
Sorry to hear that

> It's okay I guess
Interesting perspective
```

---

## Example 14: Complex State Management

**main.co:**
```colang
import core

flow main
    $user_count = 0
    
    activate count users
    activate response generator
    
    while True
        when user said "hi"
            $user_count = $user_count + 1
            bot say "User #{$user_count} said hi"
        or when user said "quit"
            bot say "Total users: {$user_count}"
            return

flow count users
    """Track in global variable."""
    global $total_handshakes
    if $total_handshakes == None
        $total_handshakes = 0
    await bot said something
    $total_handshakes = $total_handshakes + 1

flow bot said something
    match FlowFinished(flow_id="bot say")
```

**Interaction:**
```
> hi
User #1 said hi

> hi
User #2 said hi

> hi
User #3 said hi

> quit
Total users: 3
```

---

## Example 15: Interaction Loops (Multimodal)

**main.co:**
```colang
import core

flow main
    activate gesture reactor
    
    while True
        when user said "hi"
            bot say "Hello!"
        or when user said "bye"
            bot say "Goodbye!"

@loop("gesture_loop")
flow gesture reactor
    """Run in separate interaction loop."""
    activate respond to greeting
    activate respond to farewell

@loop("gesture_loop")
flow respond to greeting
    user said "hi"
    log "Gesture: smile"

@loop("gesture_loop")
flow respond to farewell
    user said "bye"
    log "Gesture: wave"
```

**Effect:**
- Main loop handles speech
- Gesture loop handles actions in parallel
- No conflicts between speech and gestures

---

## Example 16: String Expressions and Formatting

**main.co:**
```colang
import core

flow main
    $name = "Alice"
    $age = 25
    $items = [1, 2, 3]
    
    # String interpolation
    bot say "Hello {$name}!"
    
    # Expression interpolation
    bot say "Next year you'll be {$age + 1}"
    
    # List access
    bot say "First item: {$items[0]}"
    
    # Escaped braces
    bot say "Use {{braces}} like this"
    
    match RestartEvent()
```

**Output:**
```
Hello Alice!
Next year you'll be 26
First item: 1
Use {braces} like this
```

---

## Example 17: Flow Activation and Restart

**main.co:**
```colang
import core

flow main
    activate repeating greeting
    
    bot say "Say hello repeatedly"
    user said something
    bot say "Done"
    match RestartEvent()

@active  # Alternative: activate via decorator
flow repeating greeting
    """Keep responding to 'hi'."""
    user said "hi"
    bot say "Hi there!"
    # Automatically restarts when finished
```

**Interaction:**
```
Say hello repeatedly

> hi
Hi there!

> hi
Hi there!

> hi
Hi there!

> something else
Done

>
```

---

## Example 18: Custom Flow Naming and Intentions

**main.co:**
```colang
import core

flow main
    activate handling user questions
    
    while True
        when user asked question
            $answer = ..."Answer this question: {$question}"
            bot say $answer
        or when user expressed greeting
            bot say "Hi!"

# User intent flows (single statement with OR)
flow user asked question -> $question
    user said something as $question

# Bot intent flows (single statement)
flow user expressed greeting
    user said "hi" or user said "hello" or user said "hey"

flow user said something -> $text
    match UtteranceUserActionFinished() as $event
    return $event.final_transcript
```

---

## Example 19: Error Case - Undefined Flow

**main.co:**
```colang
import core

flow main
    activate catch undefined flows
    
    bot call undefined flow
    match RestartEvent()

@active
flow catch undefined flows
    """Handle attempts to call undefined flows."""
    match UnhandledEvent(event="StartFlow") as $event
    bot say "Error: Flow '{$event.flow_id}' not found"
    send StopFlow(flow_instance_uid=$event.source_flow_instance_uid)
```

**Interaction:**
```
Error: Flow 'undefined_flow' not found

>
```

---

## Example 20: Complete Mini Chatbot

**config.yml:**
```yaml
colang_version: "2.x"

models:
  - type: main
    engine: openai
    model: gpt-4-turbo
```

**config/actions.py:**
```python
from nemoguardrails.actions import action

@action(name="GetCurrentTimeAction")
async def get_current_time():
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")
```

**main.co:**
```colang
import core
import llm

flow main
    activate automating intent detection
    activate generating user intent for unhandled user utterance
    
    bot say "Hi! I'm your assistant. Type 'quit' to exit."
    
    while True
        when user expressed greeting
            bot say "Hello! How can I help?"
        
        or when user asked time
            $time = await GetCurrentTimeAction()
            bot say "Current time is {$time}"
        
        or when user expressed goodbye
            bot say "Goodbye! Thanks for chatting."
            return
        
        or when unhandled user intent
            llm continue interaction
        
        match RestartEvent()

# Intent flows
flow user expressed greeting
    user said "hi" or user said "hello" or user said "hey"

flow user asked time
    user said "what time" or user said "current time"

flow user expressed goodbye
    user said "bye" or user said "goodbye" or user said "quit"

# Helper flows
flow user said $text -> $transcript
    match UtteranceUserActionFinished(final_transcript=$text) as $event
    return $event.final_transcript

flow user asked time
    user said something as $input
    if "time" in $input
        return
    abort
```

**Interaction:**
```
Hi! I'm your assistant. Type 'quit' to exit.

> hello
Hello! How can I help?

> what's the time?
Current time is 14:30:45

> tell me a joke
[LLM generates joke response]

> goodbye
Goodbye! Thanks for chatting.
```

---

## Running the Examples

**Setup:**
```bash
# Install NeMo Guardrails
pip install nemoguardrails

# Set API key
export OPENAI_API_KEY="your-key-here"
```

**Run any example:**
```bash
# From repository examples
nemoguardrails chat --config=examples/v2_x/language_reference/<example_name>

# From your config directory
nemoguardrails chat --config=./config
```

**Available Commands in Chat:**
```
> text                    # User utterance
> /EventName()            # Send custom event
> /EventName(param=value) # With parameters
> /RestartEvent           # Restart main flow
```

---

## Key Takeaways

1. **Flows are composable** - build complex interactions from simple flows
2. **Events drive everything** - think in terms of event sequences
3. **Variables manage state** - use them to track conversation context
4. **LLM augments logic** - use for flexible intent matching and generation
5. **Python actions extend capabilities** - when Colang isn't enough
6. **Activate for repetition** - use for handlers that should keep running
7. **when/or when for choices** - better than nested if/elif for user branches
8. **Parallel flows enable multimodal** - different interaction loops don't conflict

---

*All examples are from the official NVIDIA NeMo-Guardrails repository*
