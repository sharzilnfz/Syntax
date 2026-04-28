# 🗺️ Mastery Roadmap: From Tutorial Follower → Senior AI Engineer

> **The Rule:** Don't just read code. Read it, break it, explain it, then rebuild it.
> That is the only path to true mastery. Following a tutorial tells you *what*. Mastery means you know *why*.

---

## The Core Strategy (Do This For Every File)

Before you read a single phase, internalize this loop. Apply it to **every file** you study:

```
1. READ     — Read the whole file top to bottom without stopping
2. QUESTION — Write down every line you don't understand
3. BREAK    — Delete or comment out something and run it. See what crashes
4. EXPLAIN  — Write 3 sentences explaining what this file does, in plain English
5. REBUILD  — Close the file and rewrite it from scratch (even badly)
```

If you can do Step 5, you own that file. If you can't, you only recognise it — that's not mastery.

---

## Phase 1 — Foundation (Week 1–2)
**Goal:** Understand the building blocks every other file is built on.

### Files to Study First:
| File | Why It Matters |
| :--- | :--- |
| `tools/base.py` | The blueprint every single tool follows. This is OOP in action — abstract classes, dataclasses, enums |
| `config/config.py` | How the whole system is configured. Teaches you dataclasses and Enums at a real scale |
| `agent/events.py` | A tiny file that defines how information flows through the whole agent |

### What You Must Understand From `tools/base.py`:
- Why is `Tool` an `abc.ABC` (abstract class)? What happens if you try to use it directly?
- What is `@dataclass` and why is it used for `ToolResult`, `ToolInvocation`, `ToolConfirmation`?
- What does `ToolResult.error_result(...)` mean? Why is it a `@classmethod` instead of a normal method?
- What does `to_openai_schema()` produce and *why does the LLM need it*?

### Your Proof-of-Mastery Exercise:
> Create your own tool from scratch called `TimeTool` that returns the current date and time.
> It must extend `Tool`, have a `schema`, and return a proper `ToolResult`.
> Do NOT look at existing tools until you try yourself first.

---

## Phase 2 — Core Mechanics (Week 3–4)
**Goal:** Understand the "heartbeat" of the agent — the loop that makes it autonomous.

### Files to Study:
| File | Why It Matters |
| :--- | :--- |
| `agent/agent.py` | **This is the most important file.** The `_agentic_loop` is the core of everything |
| `agent/session.py` | The "glue" — assembles every component of the system into one object |
| `tools/registry.py` | How tools are stored, found, validated, and executed |
| `context/manager.py` | How messages are stored, tracked by token count, and pruned |

### The Critical Thing to Understand in `agent/agent.py`:
The `_agentic_loop` method (lines 37–165) is the entire soul of this project. Trace through it manually:

```
1. Ask LLM (client.chat_completion) →
2. LLM replies with text or tool calls →
3. If text only → done, return response
4. If tool calls → execute each tool → feed results back to LLM →
5. Repeat from Step 1 (this is the LOOP)
```

> **Ask yourself:** What stops this from looping forever?
> Answer: The `loop_detector`, the `max_turns` limit, and the `no tool_calls` check on line 104.

### What You Must Understand From `context/manager.py`:
- Why does every message track its `token_count`?
- What is `needs_compression()` checking and at what percentage of the limit?
- What does `prune_tool_outputs()` do and why does it only prune OLD tool results, not new ones?
- Why does `replace_with_summary()` add 3 messages, not just 1?

### Your Proof-of-Mastery Exercise:
> On paper (or in a doc), draw the full flow of what happens when you type a message.
> Start from `main.py` → `CLI.run_interactive()` → `agent.run()` → `_agentic_loop()` → tool execution → back to loop.
> Label every step. If you can draw this without looking, you understand the system.

---

## Phase 3 — Advanced Systems (Week 5–6)
**Goal:** Understand the "invisible infrastructure" that makes the agent reliable and safe.

### Files to Study:
| File | Why It Matters |
| :--- | :--- |
| `safety/approval.py` | How dangerous operations are gated behind user approval |
| `context/loop_detector.py` | How the agent knows it's stuck and breaks the cycle |
| `context/compaction.py` | How the agent summarizes old conversations to save tokens |
| `hooks/hook_system.py` | How external scripts can plug in without touching core code |
| `agent/persistence.py` | How sessions are saved to disk and restored |

### Key Questions For This Phase:
- In `safety/approval.py`, what are the 4 approval policies? What does `yolo` actually allow?
- In `loop_detector.py`, how does it detect a loop? What pattern does it look for?
- In `compaction.py`, what prompt does it send the LLM to generate the summary?
- In `hooks/hook_system.py`, what is a "hook" and why is this better than putting that logic directly in the agent?
- In `persistence.py`, what format are sessions saved in? JSON? Binary? Something else?

### Your Proof-of-Mastery Exercise:
> Deliberately break the loop detector. Make the agent call the same tool twice in a row by sending a message that forces repetition.
> Watch how the loop is detected and what message gets injected to break it.
> Then read `context/loop_detector.py` and understand exactly what triggered.

---

## Phase 4 — Build Something New (Week 7–8)
**Goal:** Prove you own the codebase by extending it without the tutorial telling you what to do.

### Extension Challenge 1 — New Tool (Easy)
> Build a `WeatherTool` that calls a free weather API and returns current weather for a city.
> It must: extend `Tool`, use a Pydantic `BaseModel` for params, return a `ToolResult`, and register itself.

### Extension Challenge 2 — New Command (Medium)
> Add a `/history` command to the CLI (`main.py`) that prints the last 5 messages from `context_manager`.
> You must understand `get_messages()` and how to format them for the terminal UI.

### Extension Challenge 3 — New Safety Rule (Hard)
> Add a new safety rule to `safety/approval.py` that **auto-rejects** any shell command containing `rm -rf`.
> It must integrate with the existing `ApprovalDecision` system, not be a hacky patch.

### Extension Challenge 4 — New Persistence Feature (Hard)
> Add the ability to list all saved sessions with their turn count and last message preview.
> The `/sessions` command exists but only shows IDs. Make it richer.

---

## Phase 5 — Senior-Level Mindset (Ongoing)
**Goal:** Think like the person who *designed* this, not just the person who reads it.

### Ask "Why" Questions, Not "What" Questions

Most learners ask: *"What does this line do?"*
Seniors ask: *"Why was this designed this way? What would break if it was different?"*

Practice these on this codebase:

| Question | What It Teaches You |
| :--- | :--- |
| Why is `Session` separate from `Agent`? | Separation of Concerns, testability |
| Why does `ContextManager` store `MessageItem` objects instead of raw dicts? | Type safety, adding metadata (token counts, pruned timestamps) |
| Why does the `_agentic_loop` use `yield` instead of `return`? | Async generators, streaming, real-time event delivery |
| Why does `ToolRegistry` use a dictionary keyed by tool name? | O(1) lookup, preventing duplicates, easy override |
| Why does `get_confirmation()` return `None` for read-only tools? | Skipping unnecessary user prompts for safe operations |

### The Senior Habit: Leave Comments That Explain WHY
When you touch a file, don't just understand it. Add a comment above every non-obvious block:
```python
# We prune OLDEST tool results first to preserve recent context,
# which is more relevant to the current task. The 40k token buffer
# ensures we never prune results the LLM is actively using.
```
Writing this forces you to *actually* understand it.

### Read The Git History
```
git log --oneline
```
If there is one, the git history tells you exactly what decisions were made and in what order. This is how you reverse-engineer a senior engineer's thinking process.

---

## The Fastest Learning Technique: Rubber Duck Debugging

Every day, pick ONE function and explain it out loud to yourself (or literally to a rubber duck) as if teaching a 10-year-old. If you stumble or can't explain something, **that is exactly what to study next.**

The functions in this codebase to explain first:
1. `_agentic_loop()` in `agent/agent.py`
2. `invoke()` in `tools/registry.py`
3. `prune_tool_outputs()` in `context/manager.py`
4. `check_approval()` in `safety/approval.py`

---

## Realistic Timeline

| Phase | Time | Milestone |
| :--- | :--- | :--- |
| Phase 1 — Foundation | 2 weeks | You can build a new `Tool` from scratch |
| Phase 2 — Core Mechanics | 2 weeks | You can draw the full agent loop from memory |
| Phase 3 — Advanced Systems | 2 weeks | You understand how the agent is kept safe and reliable |
| Phase 4 — Build Extensions | 2 weeks | You add features without the tutorial's help |
| Phase 5 — Senior Mindset | Ongoing | You question every design decision and have an opinion |

> [!IMPORTANT]
> **The rule:** Never move to the next phase until you can complete the Proof-of-Mastery exercise for the current one. Speed without understanding is just memorization — it collapses under interview pressure.

---

## What To Do With The Tutorial

Use the tutorial to **understand what** the code does.
Then **pause it** and ask yourself **why** before continuing.

The moment the tutorial explains something, stop it and try to predict what comes next.
If you're wrong, that gap in understanding is your next study target.

> [!TIP]
> The tutorial is your starting point. The questions you ask *after* the tutorial is where real learning happens. The goal is to reach a point where you could *teach* this tutorial, not just follow it.
