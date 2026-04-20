# Context Management & Token Counting — An In-Depth Explanation

When building an AI agent, you don't just send a prompt to the LLM and get a response. You have to send the **entire conversation history** every single time, along with system instructions. Furthermore, because LLMs charge per token and have limited "memory" (context windows), you need to keep track of how much data you are sending.

This brings us to two closely related files you've added:
1. `utils/text.py`: Responsible for calculating the size of messages (tokens).
2. `context/manager.py`: Responsible for storing, formatting, and preparing the conversation history for the LLM.

Let's break them down in depth.

---

## 1. `utils/text.py` — The Token Counter

An LLM doesn't read words or letters; it reads "tokens". A token is a chunk of characters (usually about 3-4 characters long). The `text.py` file ensures your application knows exactly how many tokens a piece of text contains.

### How `tiktoken` Works
This file relies heavily on `tiktoken`, the official tokenization library created by OpenAI.

```python
def get_tokenizer(model: str):
    try:
        encoding = tiktoken.encoding_for_model(model)
        return encoding.encode
    except Exception:
        # Fallback for unknown models (e.g., OpenRouter specific models)
        encoding = tiktoken.get_encoding("cl100k_base")
        return encoding.encode
```
* **Purpose**: This function tries to get the exact tokenization rules (the "encoding") for a specific model (like `gpt-4`).
* **The Fallback**: If you pass an unrecognized model name (like a custom OpenRouter model), `tiktoken` throws an error. The `except` block catches this and defaults to `"cl100k_base"`. This is the standard encoding used by GPT-3.5, GPT-4, and most modern models.

### `count_tokens`
```python
def count_tokens(text: str, model: str = "gpt-4") -> int:
    tokenizer = get_tokenizer(model)
    if tokenizer:
        return len(tokenizer(text))
    return estimate_tokens(text)
```
* **Purpose**: This is the main interface. You pass it text, it gives you an integer representing the token count.
* **Mechanism**: It converts the string into a list of token IDs (`tokenizer(text)`) and simply returns the length of that list. If the tokenizer fails entirely, it falls back to a rough estimation.

### `estimate_tokens`
```python
def estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)
```
* **Purpose**: A fail-safe. If `tiktoken` crashes, this mathematical heuristic assumes that, on average, 1 token = 4 characters.

---

## 2. `context/manager.py` — The Memory Bank

If `text.py` is the scale that weighs your data, `manager.py` is the vault that stores it. The LLM API requires messages in a very specific physical format (a list of dictionaries). `ContextManager` acts as your personal assistant organizing these messages.

### The `MessageItem` Data Class

```python
@dataclass
class MessageItem:
    role: str
    content: str
    tool_call_id: str | None = None
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    token_count: int | None = None
    pruned_at: datetime | None = None
```
Instead of just storing the raw dictionary (e.g., `{"role": "user", "content": "hey"}`), you wrap it in a `MessageItem` object.
*   **Why do this?** Because you need to store *metadata* that the LLM doesn't care about, but your application does! For instance, `token_count` tells us how heavy this message is, and `pruned_at` could be used later to "forget" old messages if the context gets too full.
*   **`to_dict()` Method**: When it's time to actually send the data to the LLM, this method strips away all the Python-specific metadata and outputs the strict JSON-compliant dictionary the API requires.

### The `ContextManager` Class Wrapper

```python
class ContextManager:
    def __init__(self):
        self.system_prompt: str = get_system_prompt()
        self._model_name = "https://openrouter.ai/api/v1"  # Note: Usually this should be the model name, e.g., 'anthropic/claude-3-haiku'
        self._messages: list[MessageItem] = []
```
*   `system_prompt`: Loaded once when the manager initializes. This is the invisible set of instructions giving your agent its persona and rules.
*   `_messages`: This is the actual array that holds the sequential history.

### Adding Messages

You created two separate methods for adding messages: `add_user_message` and `add_assistant_message`. Let's look at what happens when you add an assistant message:

```python
def add_assistant_message(self, content: str, tool_calls: list[dict[str, any]] | None = None) -> None:
    item = MessageItem(
        role="assistant",
        content=content or "",
        token_count=count_tokens(content or "", self._model_name),
        tool_calls=tool_calls or [],  
    )
    self._messages.append(item)
```
**How this hooks into `text.py`:**
Notice the `token_count=count_tokens(...)`? Every time a message is slotted into memory, the `ContextManager` reaches out to `utils/text.py` to weigh it. It calculates the token count *upfront* so you don't have to desperately recalculate everything when the context limit is reached.

*(Note: There is a minor typo in your current `add_user_message` signature: `def add_user_message(self, content, message: str) -> None:`. It asks for both `content` and `message` but only uses `content`)*.

### Formatting for the LLM

When the `Agent` is finally ready to make an API call, it needs the data:

```python
def get_messages(self) -> list[dict[str, Any]]:
    messages = []
    
    # 1. System Prompt always goes first
    if self.system_prompt: # Note: this was originally self._system_prompt in your code
        messages.append({"role": "system", "content": self.system_prompt})

    # 2. Append history
    for item in self._messages:
        messages.append(item.to_dict())

    return messages
```
This is the delivery mechanism. It ensures the System prompt is immutably placed at `index 0`, and then iterates over your `MessageItem` list, calling `to_dict()` to strip out the metadata, producing a perfectly formatted payload for `OpenAI`/`OpenRouter`.

---

## How it All Fits Together (The Future Architecture)

Currently, your `Agent` inside `agent.py` hardcodes the memory:
```python
messages =[{"role":"user", "content": message}]
```
Eventually, you will hook `ContextManager` into the `Agent`. The flow will look like this:

1. **User types "Fix my code"**.
2. **Agent** says: `context_manager.add_user_message("Fix my code")`.
   * -> *`manager.py` calls `text.py` to count tokens.*
   * -> *`manager.py` saves the wrapper object in its list.*
3. **Agent** requests payload: `context_manager.get_messages()`.
4. **Agent** sends that payload to `LLMClient`.
5. **LLM** streams response ("Here is the fix...").
6. **Agent** says: `context_manager.add_assistant_message("Here is the fix...")`.

By using `manager.py` and `text.py`, your application becomes "stateful" (it remembers past turns) and "safe" (it knows exactly how many tokens it is consuming).
