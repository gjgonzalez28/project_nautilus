# Colang 2.0 - Standard Library Reference

The **Colang Standard Library (CSL)** provides pre-built flows and abstractions for common patterns.

---

## Core Library (`import core`)

The most essential library - provides basic user/bot interaction abstractions.

### User Input Flows

#### `user said $text -> $transcript`
Wait for user to say an exact string.

```colang
import core

flow main
    $message = await user said "hello"
    bot say "You said: {$message}"
```

**Parameters:**
- `$text` (required) - exact text to match
- `$transcript` (return) - the transcript that was matched

**Notes:**
- Case-sensitive exact match
- Returns the final transcript

---

#### `user said something -> $transcript`
Wait for user to say anything.

```colang
import core

flow main
    $input = await user said something
    bot say "Got: {$input}"
```

**Parameters:**
- `$transcript` (return) - the user's utterance

**Usage:**
- Flexible input handling
- Returns whatever user says

---

#### `user saying $text -> $transcript`
Wait for user interim transcript matching text (while speaking).

```colang
import core

flow main
    $interim = await user saying "hel"  # Matches while typing/speaking "hel..."
```

**Parameters:**
- `$text` - pattern to match in interim transcript
- `$transcript` (return) - interim transcript

---

#### `user started saying something`
Detect when user starts speaking/typing.

```colang
import core

flow main
    await user started saying something
    bot say "I hear you typing"
```

---

#### `user said something unexpected -> $event, $transcript`
Match utterance that doesn't match any active flow pattern.

```colang
import core

flow main
    activate handle unexpected
    # Main pattern matching...

@active
flow handle unexpected
    await user said something unexpected as $result
    bot say "That was unexpected: {$result.transcript}"
```

---

### Bot Output Flows

#### `bot say $text`
Make bot speak/output text.

```colang
import core

flow main
    bot say "Hello there!"
    
    # With variable
    $greeting = "Welcome"
    bot say $greeting
    
    # With interpolation
    bot say "Hello {$name}!"
```

**Parameters:**
- `$text` - exact text for bot to say

**Variants (all do same thing, semantic difference):**
- `bot inform $text` - when informing
- `bot ask $text` - when asking question
- `bot respond $text` - when responding
- `bot express $text` - when expressing opinion
- `bot clarify $text` - when clarifying
- `bot suggest $text` - when suggesting

---

#### `bot say $text $volume`
Bot speech with volume control.

```colang
import core

flow main
    bot say "LOUD!" 2.0
    bot say "quiet..." 0.5
    bot say "normal" 1.0  # default
```

**Parameters:**
- `$text` - what to say
- `$volume` (default: 1.0) - intensity/volume [0.0-2.0]

---

#### `bot informed $text`
Similar to `bot say`, implies informing the user.

```colang
import core

flow main
    bot inform "Your order has been processed"
```

---

### Bot Event Monitoring Flows

#### `bot said $text`
Match when bot finished saying specific text.

```colang
import core

flow main
    activate monitor bot
    # ...

@active
flow monitor bot
    await bot said "Hello"
    log "Bot said hello"
```

---

#### `bot said something -> $text`
Match when bot finished saying anything.

```colang
import core

flow main
    activate track statements
    # ...

@active
flow track statements
    await bot said something as $result
    log "Bot said: {$result.text}"
```

---

#### `bot started saying something`
Detect when bot starts saying something.

```colang
import core

flow main
    activate show typing
    # ...

@active
flow show typing
    await bot started saying something
    log "Bot is speaking..."
```

---

### State Tracking Flows

#### `tracking bot talking state`
Global variable `$bot_talking_state` - True when bot speaking, False when finished.

```colang
import core

flow main
    activate tracking bot talking state
    activate monitoring
    # ...

@active
flow monitoring
    if $bot_talking_state == True
        log "Bot is talking"
        await bot said something
        log "Bot finished"
```

---

#### `tracking user talking state`
Global variable `$user_talking_state` - True when user speaking, False when finished.

Also provides `$last_user_transcript` - the final transcript.

```colang
import core

flow main
    activate tracking user talking state
    # Access $user_talking_state
    # Access $last_user_transcript
```

---

### Debug and Utility Flows

#### `debugging helpers`
Activates all debugging helper flows.

```colang
import core

flow main
    activate debugging helpers
    # Now will see debug output for errors
```

**What it activates:**
- `warning of colang errors`
- `warning of undefined flow start`

---

#### `warning of colang errors`
Logs Colang runtime errors.

```colang
import core

flow main
    activate warning of colang errors
    # Errors will be logged
```

---

#### `warning of undefined flow start`
Logs when undefined flow is attempted.

```colang
import core

flow main
    activate warning of undefined flow start
    bot call undefined flow        # This will fail gracefully
    # Warning is logged
```

---

#### `warning of unexpected user utterance`
Logs when user utterance is unmatched.

```colang
import core

flow main
    activate warning of unexpected user utterance
    # Any unmatched user utterance is logged
```

---

### Utility Flows

#### `it finished $ref -> $finished_event`
Wait for flow or action to finish.

```colang
import core

flow main
    start some_flow as $ref
    $event = await it finished $ref
    # $ref is done
```

---

#### `flow_failed $flow_ref -> $failed_event`
Wait for flow to fail.

```colang
import core

flow main
    start risky_flow as $ref
    when $ref.Finished()
        bot say "Flow succeeded"
    or when (flow_failed $ref)
        bot say "Flow failed"
```

---

## LLM Module (`import llm`)

Integrates Large Language Model capabilities.

### Prerequisites
```python
# config.yml must have LLM configured
models:
  - type: main
    engine: openai
    model: gpt-4-turbo
```

---

### Intent Detection Flows

#### `automating intent detection`
Auto-detect user intent flows (those starting with "user").

```colang
import core
import llm

flow main
    activate automating intent detection
    
    while True
        when user expressed greeting
            bot say "Hi!"
        or when user expressed farewell
            bot say "Bye!"
```

**How it works:**
- Scans for flows starting with "user"
- Marks them as intent flows
- LLM uses them for fuzzy matching

---

#### `generating user intent for unhandled user utterance`
Use LLM to match unmatched utterances to defined intents.

```colang
import core
import llm

flow main
    activate automating intent detection
    activate generating user intent for unhandled user utterance
    
    while True
        when user expressed greeting
            bot say "Hello!"
        or when unhandled user intent
            bot say "I don't understand"

flow user expressed greeting
    user said "hi" or user said "hello"
```

**Behavior:**
- Exact matches use defined flows first
- Unmatched utterances run through LLM
- LLM tries to map to intent flows
- Falls back to "unhandled user intent" if no match

**Example matching:**
```colang
flow user said goodbye
    user said "bye" or user said "goodbye"

# User says "see you later" -> LLM maps to "goodbye"
```

---

### Bot Generation Flows

#### `llm continue interaction`
Use LLM to generate appropriate bot response.

```colang
import core
import llm

flow main
    user said something
    llm continue interaction
    match RestartEvent()
```

**Effect:**
- LLM generates contextually appropriate response
- Considers conversation history and system prompts

**Use case:**
- Handling unexpected user inputs
- Natural conversation flow

---

### Complete LLM Example

```colang
import core
import llm

flow main
    activate automating intent detection
    activate generating user intent for unhandled user utterance
    
    bot say "What would you like to know?"
    
    while True
        when user asked weather
            $weather = ..."What's the weather like?"
            bot say $weather
        
        or when user asked time
            $time = ..."What time is it?"
            bot say $time
        
        or when user expressed goodbye
            bot say "Goodbye!"
            return
        
        or when unhandled user intent
            llm continue interaction
        
        match RestartEvent()

# Intent definitions
flow user asked weather
    user said "weather" or user said "how's it outside"

flow user asked time
    user said "time" or user said "what time"

flow user expressed goodbye
    user said "bye" or user said "goodbye"
```

---

## Timing Module (`import timing`)

Time-based interaction patterns.

### Event-based Timing

#### `user was silent <duration>`
Trigger after user silent for N seconds.

```colang
import core
import timing

flow main
    bot say "Tell me something"
    
    while True
        when user said something
            bot say "Thanks!"
        
        or when user was silent 5.0
            bot say "You've been quiet for 5 seconds"
        
        match RestartEvent()
```

**Example:**
```colang
when user was silent 10.0
    $response = ..."Generate an interesting fact"
    bot say $response
```

---

## Avatars Module (`import avatars`)

Bot gesture and animation flows.

### Common Gesture Flows

```colang
import core
import avatars

flow main
    activate gesture handler
    
    while True
        when user expressed greeting
            bot express greeting
        or when user expressed goodbye
            bot express goodbye

@loop("gestures")
flow gesture handler
    activate gesture reactions

@loop("gestures")
flow gesture reactions
    when user expressed greeting
        bot gesture "smile"
    or when user expressed goodbye
        bot gesture "wave"

flow bot express greeting
    bot say "Hello!"

flow bot express goodbye
    bot say "Goodbye!"

flow bot gesture $gesture
    # Implementation depends on avatar system
    log "Gesture: {$gesture}"

flow user expressed greeting
    user said "hi" or user said "hello"

flow user expressed goodbye
    user said "bye" or user said "goodbye"
```

---

## Guardrails Module (`import guardrails`)

Safety and content filtering.

### Available Safeguards

```colang
import core
import guardrails

flow main
    # Input rail - filter user input
    activate check user input

    # Output rail - filter bot output
    activate check bot output
```

**Provides guardrails like:**
- Input moderation
- Output filtering
- Fact checking
- Hallucination detection

---

## Attention Module (`import attention`)

User attention and focus management.

```colang
import core
import attention

flow main
    # Manage user focus in multimodal interactions
```

---

## Custom Library Pattern

You can create your own library flows:

**mylib.co (library file):**
```colang
flow greet user $name
    """Greet user by name."""
    bot say "Hello, {$name}!"

flow ask yes no question $question -> $answer
    """Ask user yes/no question."""
    bot say "{$question}"
    when user said "yes"
        $answer = "yes"
    or when user said "no"
        $answer = "no"
    else
        $answer = None
    return $answer
```

**main.co (using library):**
```colang
import core
import mylib

flow main
    await greet user "Alice"
    
    $response = await ask yes no question "Do you like pizza?"
    bot say "You answered: {$response}"
```

---

## Natural Language Descriptions (NLD) - Part of LLM

### Syntax

```colang
$variable = ..."Natural language instruction"
```

### Examples

**Extract sentiment:**
```colang
$sentiment = ..."Is this positive or negative? '{$text}' Return only: positive, negative, or neutral"
```

**Generate response:**
```colang
$response = ..."Based on the conversation, provide a helpful response about {$topic}"
```

**Classify:**
```colang
$category = ..."What category is this text in? '{$text}' Options: question, statement, greeting, goodbye"
```

**Extract structured data:**
```colang
$order = ..."From this order: '{$order_text}', extract items in format: {'item1': quantity, 'item2': quantity}"
```

---

## Best Practices for Using Standard Library

1. **Always import core** - fundamental flows live here
2. **Use semantic flow names** - follows naming conventions
3. **Combine with LLM** - use `llm` module for flexibility
4. **Activate helpers** - use debugging flows during development
5. **Create your own wrappers** - wrap standard library for consistency

---

## Quick Reference

### Import Patterns
```colang
# Minimal
import core

# With LLM
import core
import llm

# With multiple libraries
import core
import llm
import timing
import avatars
```

### Common Flow Combinations

**Basic chatbot:**
```colang
import core
import llm

flow main
    activate automating intent detection
    activate generating user intent for unhandled user utterance
```

**With timing:**
```colang
import core
import llm
import timing

flow main
    # Handle time-based events
    when user was silent 10.0
        bot say "Hello?"
```

**Multimodal:**
```colang
import core
import llm
import avatars

flow main
    activate gesture reactions
```

---

## Standard Library Module Locations

In NeMo Guardrails repository:
```
nemoguardrails/colang/v2_x/library/
├── core.co
├── llm.co
├── timing.co
├── avatars.co
├── guardrails.co
└── attention.co
```

Each library is a `.co` file containing many flow definitions that you import with `import <name>`.

---

## Next Steps

1. Study the `core` library flows for your use case
2. Add `llm` module for flexible intent matching
3. Use timing for time-based interactions
4. Reference official examples for advanced patterns
5. Create your own library of reusable flows

---

*Reference: Official NVIDIA NeMo-Guardrails Repository*
