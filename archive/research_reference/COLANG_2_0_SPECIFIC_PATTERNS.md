# Colang 2.0 - Specific Patterns & Q&A

This document answers the most critical questions about Colang 2.0 syntax and behavior.

---

## Question 1: How to Capture User Input

### Pattern 1: Match Exact Text
```colang
flow main
    user said "hello"
    bot say "You said hello"
```

**Capture the matched text:**
```colang
flow main
    user said "hello" as $event
    bot say "Text was: {$event.final_transcript}"
```

### Pattern 2: Capture Any User Input
```colang
flow main
    $user_text = await user said something
    bot say "You said: {$user_text}"
```

**How it works:**
1. `user said something` is a standard library flow that returns transcript
2. `await` waits for it to finish and captures return value
3. `$user_text` receives the transcript

### Pattern 3: Match with Regex
```colang
flow main
    match UtteranceUserActionFinished(final_transcript=regex("hello|hi")) as $event
    bot say "You greeted me!"
```

### Pattern 4: Capture and Use in Expression
```colang
flow main
    match UtteranceUserActionFinished(final_transcript=regex("\\d+")) as $event
    $number = int($event.final_transcript)
    bot say "You said number: {$number}"
```

### Pattern 5: Extract Multiple Times
```colang
flow main
    $first_input = await user said something
    bot say "First: {$first_input}"
    
    $second_input = await user said something
    bot say "Second: {$second_input}"
    
    $both = "{$first_input} then {$second_input}"
    bot say "Combined: {$both}"
```

### Pattern 6: Conditional Capture
```colang
flow main
    when user said "yes"
        $choice = "yes"
    or when user said "no"
        $choice = "no"
    else
        $choice = "unknown"
    
    bot say "Choice: {$choice}"
```

### Pattern 7: Capture in Custom Flow
```colang
flow main
    $user_emotion = await get user emotion

flow get user emotion -> $emotion
    """Ask and capture user emotion."""
    bot say "How do you feel?"
    when user said "happy"
        $emotion = "happy"
    or when user said "sad"
        $emotion = "sad"
    else
        $emotion = "neutral"
    return $emotion
```

### Complete User Input Capture Example
```colang
import core

flow main
    # Simple capture
    $name = await get user name
    bot say "Nice to meet you, {$name}"
    
    # Multiple captures
    await simple_responses
    
    match RestartEvent()

flow get user name -> $name
    """Ask for name and capture."""
    bot ask "What's your name?"
    match UtteranceUserActionFinished() as $event
    $name = $event.final_transcript
    return $name

flow simple_responses
    bot ask "Do you like pizza?"
    when user said "yes"
        bot say "Great!"
    or when user said "no"
        bot say "That's okay"
    else
        bot say "Maybe?"
```

---

## Question 2: How to Call Python Functions - THE CORRECT SYNTAX

### The WRONG Way (Won't work)
```colang
# INCORRECT - This doesn't work!
$result = my_python_function()
$result = calculate(5, 3)
$data = fetch_data()
```

### The CORRECT Way

#### Step 1: Define Python Action with @action decorator

**File: config/actions.py**
```python
from nemoguardrails.actions import action

@action(name="CalculateAction")
async def calculate_sum(a: int, b: int):
    """Add two numbers."""
    return a + b

@action(name="ProcessTextAction")
async def process_text(text: str):
    """Convert text to uppercase."""
    return text.upper()

@action(name="FetchWeatherAction", execute_async=True)
async def fetch_weather(city: str):
    """Fetch weather (simulating API call)."""
    import asyncio
    # Simulate async operation
    await asyncio.sleep(0.1)
    return f"Sunny in {city}"
```

#### Step 2: Call from Colang with Exact Name Match

**File: config/main.co**
```colang
import core

flow main
    # MUST use exact action name
    $sum = await CalculateAction(a=5, b=3)
    bot say "5 + 3 = {$sum}"
    
    $uppercase = await ProcessTextAction(text="hello")
    bot say "Uppercase: {$uppercase}"
    
    # Async action (long-running)
    $weather = await FetchWeatherAction(city="San Francisco")
    bot say "Weather: {$weather}"
    
    match RestartEvent()
```

### Rules for Python Actions

1. **Name must end with `Action`**
   - ✅ `CalculateAction`
   - ✅ `GetWeatherAction`
   - ❌ `Calculate` (missing)
   - ❌ `calculate_sum` (wrong casing)

2. **Use exact name from @action decorator**
   ```python
   @action(name="MySpecialAction")  # Use exactly this name in Colang
   async def some_function():
       pass
   ```
   
   ```colang
   $result = await MySpecialAction()  # Must match exactly
   ```

3. **File location matters**
   - `config/actions.py` - automatically loaded, OR
   - `config/actions/<anything>.py` - automatically loaded, OR
   - `config/<anything>.py` - NOT loaded, must import

4. **All functions must be async**
   ```python
   # CORRECT
   @action(name="MyAction")
   async def my_function():
       return result
   
   # INCORRECT (won't work)
   @action(name="MyAction")
   def my_function():
       return result
   ```

5. **Parameters must be type-hinted**
   ```python
   # CORRECT
   @action(name="AddAction")
   async def add(a: int, b: int):
       return a + b
   
   # Also correct with type hints
   @action(name="ConcatAction")
   async def concat(text1: str, text2: str) -> str:
       return text1 + text2
   ```

6. **Call with keyword arguments**
   ```colang
   # CORRECT
   $result = await CalculateAction(a=5, b=3)
   
   # INCORRECT (positional won't work in Colang)
   $result = await CalculateAction(5, 3)
   ```

### Complete Python Action Example

**config/actions.py:**
```python
from nemoguardrails.actions import action
import asyncio

@action(name="ValidateEmailAction")
async def validate_email(email: str) -> bool:
    """Check if email format is valid."""
    return "@" in email and "." in email

@action(name="GetRandomJokeAction")
async def get_random_joke() -> str:
    """Return a random joke."""
    jokes = ["Why did the chicken cross the road?", "What do you call a bear with no teeth?"]
    import random
    return random.choice(jokes)

@action(name="SlowDatabaseQueryAction", execute_async=True)
async def slow_query(query: str) -> str:
    """Simulate slow database query."""
    await asyncio.sleep(2)  # Simulate delay
    return f"Results for: {query}"

@action(name="GetUserAgeAction")
async def get_user_age(context: dict) -> int:
    """Access context variables."""
    # context has $variables
    name = context.get("$user_name", "Unknown")
    return 25  # Simulated

@action(name="ComplexCalculationAction")
async def complex_calc(values: list, operation: str) -> float:
    """Perform calculation on list."""
    if operation == "sum":
        return sum(values)
    elif operation == "avg":
        return sum(values) / len(values)
    else:
        return 0.0
```

**config/main.co:**
```colang
import core

flow main
    # 1. Simple action
    $is_valid = await ValidateEmailAction(email="john@example.com")
    if $is_valid
        bot say "Email is valid"
    else
        bot say "Invalid email"
    
    # 2. Action returning string
    $joke = await GetRandomJokeAction()
    bot say $joke
    
    # 3. Slow async action (execute_async=True)
    start SlowDatabaseQueryAction(query="users") as $db_ref
    bot say "Querying database..."
    match $db_ref.Finished() as $result
    bot say "Got: {$result.return_value}"
    
    # 4. Action with list parameter
    $result = await ComplexCalculationAction(values=[1, 2, 3, 4], operation="avg")
    bot say "Average: {$result}"
    
    match RestartEvent()
```

### Accessing Return Values

#### Option 1: Direct Assignment
```colang
$result = await MyAction(param=value)
# $result now contains the return value
```

#### Option 2: Via Event Reference
```colang
start MyAction(param=value) as $ref
# ... do other things
match $ref.Finished() as $event
$result = $event.return_value
```

### Using Context and Config

```python
@action(name="ContextAwareAction")
async def context_action(
    context: dict,     # User variables
    config: dict,      # config.yml content
    events: list,      # Event history
):
    # Access variable
    user_name = context.get("$user_name")
    
    # Access config
    api_key = config.get("api_key")
    
    # Check events
    last_event = events[-1] if events else None
    
    return f"User: {user_name}"
```

---

## Question 3: How Variables Persist Across Statements

### Scope Rules

#### Local Variables (Default)
```colang
flow my_flow
    $x = 5
    $y = 10
    $sum = $x + $y
    # $x, $y, $sum exist and are used here
    # They are cleaned up when flow ends

flow other_flow
    # $x, $y, $sum do NOT exist here
    $x = 100  # This is a NEW variable, not the same $x
```

#### Persistence Within a Flow

```colang
flow main
    # Variables persist across statements
    $count = 0
    
    user said "hi"  # Statement 1
    $count = $count + 1
    
    bot say "Count: {$count}"  # Statement 2 - can access updated $count
    
    user said "bye"  # Statement 3
    $count = $count + 1
    
    bot say "Final: {$count}"  # Statement 4 - $count is 2
```

#### Via Flow Return Values
```colang
# Flow A computes value
flow compute_value -> $result
    $intermediate = 5
    $result = $intermediate * 2
    return $result

# Flow B receives it
flow main
    $value = await compute_value
    # $value = 10
    # $intermediate does NOT exist (local to compute_value)
```

#### Global Variables
```colang
flow flow_a
    global $shared_var
    $shared_var = "set in A"

flow flow_b
    global $shared_var
    # Can now access $shared_var = "set in A"
    bot say $shared_var
```

#### Flow Parameters
```colang
flow add_numbers $a $b -> $result
    # Parameters passed by value
    $result = $a + $b
    return $result

flow main
    $x = 5
    $y = 3
    $z = await add_numbers $x $y
    # $a and $b don't exist in main
    # $z = 8
    # $x and $y still exist and unchanged
```

### Variable Lifecycle Example

```colang
import core

flow main
    # Variable created
    $attempts = 0
    
    while $attempts < 3
        # Variables persist through loop iterations
        $attempts = $attempts + 1
        bot say "Attempt {$attempts}"
        
        # Local loop variables
        $msg = "trying..."
        bot say $msg
    
    # $attempts = 3 (persists after loop)
    # $msg still accessible
    bot say "Done after {$attempts} attempts"
    
    # Call flow
    $output = await my_flow
    # $output = return value
    # Variables inside my_flow don't escape
    
    match RestartEvent()

flow my_flow -> $output
    $internal_var = "only here"
    $output = "result"
    return $output
    # $internal_var is cleaned up
```

### Persistence with Conditionals

```colang
flow main
    $value = 0
    
    if user_condition
        $value = 10
        # $value = 10 here
    else
        $value = 20
    
    # $value persists after if/else (value is 10 or 20)
    bot say "Value: {$value}"
```

### Persistence with Events

```colang
flow main
    match UtteranceUserActionFinished() as $event
    # $event persists after match
    
    bot say "You said: {$event.final_transcript}"
    # Can still access $event.final_transcript
    
    when user said "yes"
        # $event still exists here
        bot say "You said: {$event.final_transcript}"
    or when user said "no"
        # $event still exists here too
        bot say "You said: {$event.final_transcript}"
```

---

## Question 4: Nested vs Flat Flow Structure

### Flat Structure (Recommended)

**Pattern:**
```colang
flow main
    step_a
    step_b
    step_c

flow step_a
    user said "hi"

flow step_b
    bot say "Hello"

flow step_c
    user said "bye"
    bot say "Goodbye"
```

**Advantages:**
- ✅ Modular and reusable
- ✅ Easy to test individual flows
- ✅ Clear separation of concerns
- ✅ Used throughout standard library

### Nested Structure (Possible but not recommended)

**Pattern:**
```colang
flow main
    user said "hi"
    sub_flow
    user said "bye"

flow sub_flow
    bot say "Hello"
    user said something
    bot say "Got it"
```

**Issues:**
- ❌ Harder to reuse sub_flow
- ❌ Less clear flow of control
- ❌ Tightly coupled flows
- ❌ Contradicts standard library style

### Comparison Example

#### NESTED (NOT Recommended)
```colang
flow main
    greeting_sequence
    interaction_loop

flow greeting_sequence
    bot say "Hello"
    user said something as $name
    bot say "Hi {$name}"

flow interaction_loop
    while True
        when user asked question
            answer_question
        or when user said goodbye
            farewell_sequence

flow answer_question
    bot say "I don't know"

flow farewell_sequence
    bot say "Goodbye"
```

#### FLAT (Recommended)
```colang
import core
import llm

flow main
    activate greeting
    activate questions
    activate farewells

@active
flow greeting
    bot say "Hello"
    $name = await user said something
    bot say "Hi {$name}"

@active
flow questions
    when user asked question
        $answer = ..."Answer the question"
        bot say $answer

@active
flow farewells
    when user said goodbye
        bot say "Goodbye"
        return
```

### When to Use Nested Flows

**Acceptable use cases:**

1. **Helper flows called once:**
```colang
flow main
    $result = await complex_calculation $data
    bot say $result

flow complex_calculation $input -> $output
    # Actual calculation logic here
    return $output
```

2. **Temporary state management:**
```colang
flow main
    activate state_tracker
    
    # Main interaction

@loop("state")
flow state_tracker
    await track state changes
```

3. **Conditional sub-flows:**
```colang
flow main
    if is_vip_user
        await vip_greeting
    else
        await regular_greeting

flow vip_greeting
    bot say "Welcome, VIP!"

flow regular_greeting
    bot say "Welcome!"
```

### Best Practice: Modular Design

```colang
import core
import llm

# Main orchestrator
flow main
    activate dialog_handler
    activate error_handler

# Dialog handler
@active
flow dialog_handler
    activate greeting
    activate question_answering
    activate farewell

# Greeting module
@active
flow greeting
    user said "hi"
    bot say "Hello!"

# Q&A module
@active
flow question_answering
    when user asked question
        llm continue interaction

# Farewell module
@active
flow farewell
    when user said goodbye
        bot say "Goodbye"
        return

# Error handling
@active
flow error_handler
    match ColangError() as $error
    log "Colang error: {$error.type}"
```

---

## Question 5: Variable Persistence with Activated Flows

```colang
flow main
    $counter = 0
    activate increment_counter

flow increment_counter
    # This flow restarts automatically
    while True
        user said "increment"
        # Can $counter be accessed?
        # NO - $counter is local to main
        # Need to use global
        pass

# CORRECT WAY
flow main
    global $counter
    $counter = 0
    activate increment_counter

@active
flow increment_counter
    global $counter
    user said "increment"
    $counter = $counter + 1
    bot say "Count: {$counter}"
```

---

## Question 6: Variables in Loops

```colang
flow main
    $sum = 0
    $count = 0
    
    while $count < 5
        $sum = $sum + $count
        $count = $count + 1
    
    # After loop
    bot say "Sum: {$sum}"  # $sum = 0+1+2+3+4 = 10
    bot say "Count: {$count}"  # $count = 5
```

**Variables in loop:**
- Persist across iterations
- Can be modified
- Updated state available after loop

---

## Summary Table

| Scope | Declaration | Access | Cleanup |
|-------|------------|--------|---------|
| Local | `$var = value` in flow | Within flow only | On flow end |
| Return | `flow name -> $var` + `return $var` | Via `await` caller | Caller decides |
| Global | `global $var` in each flow | All flows declaring it | On system shutdown |
| Parameter | `flow name $param` | Within flow | On flow end |
| Event | `match Event() as $ref` | Use reference | When new event matches |

---

## Final Checklist: Are You Using Variables Correctly?

- ✅ Variables start with `$`
- ✅ Variables created with `=` assignment
- ✅ For cross-flow access, use `global` keyword
- ✅ To return values, use `return` + flow return params
- ✅ Python actions use `@action` decorator
- ✅ Python action names end with `Action`
- ✅ Python actions called with `await ActionName(params)`
- ✅ Variables persist within same flow
- ✅ Use flat flow structure (activate flows)
- ✅ Access event data via `as $ref` notation

---

*This document covers the most critical patterns for successful Colang development*
