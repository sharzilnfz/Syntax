# Codebase Architecture: AI Coding Agent

---

## 1. 🏛️ The Architectural Pattern: **Event-Driven Layered Architecture**

This codebase uses a **Layered Architecture** (also called "N-Tier" or "Onion" architecture) with an **event-driven inner core**.

There are clearly separated layers stacked on top of each other, where each layer only talks to the layer directly below it — never to a layer it skips.

---

## 2. 🍕 Real-World Analogy: A Restaurant

Think of this system like a restaurant:

| Restaurant Role | Code Equivalent |
|---|---|
| **Customer** at the table | You (the user typing in the terminal) |
| **Waiter** (takes your order, delivers food) | `ui/tui.py` + `main.py` |
| **Head Chef / Kitchen Manager** | `agent/agent.py` |
| **Sous-chefs** (specialists per task) | `tools/builtin/` — each tool is a specialist |
| **Fridge / Pantry** (what ingredients are available) | `context/manager.py` |
| **Food supplier** (brings raw ingredients from outside) | `client/llm_client.py` |
| **Health Inspector** (approves risky actions) | `safety/approval.py` |
| **Restaurant rulebook** | `config/config.py` |
| **Event log / Kitchen bell system** | `agent/events.py` |

Just as a restaurant customer never walks into the kitchen to cook, **each layer only calls the one directly below it**.

---

## 3. 🗂️ Folder → Layer Mapping

```
┌──────────────────────────────────────────────────────┐
│  LAYER 1: ENTRY POINT & PRESENTATION                 │
│  main.py         ← boots the app, CLI commands        │
│  ui/tui.py       ← pretty terminal display (TUI)      │
└───────────────────────────┬──────────────────────────┘
                            │ calls
┌───────────────────────────▼──────────────────────────┐
│  LAYER 2: ORCHESTRATION (The Brain)                   │
│  agent/agent.py      ← the "agentic loop" — drives   │
│                         the think → act → repeat     │
│  agent/session.py    ← holds ALL state for one chat   │
│  agent/events.py     ← defines what "signals" exist  │
│  agent/persistence.py← save/load sessions to disk    │
└───────────────────────────┬──────────────────────────┘
                            │ calls
┌───────────────────────────▼──────────────────────────┐
│  LAYER 3: SERVICES (Specialist Modules)               │
│  client/llm_client.py  ← talks to OpenAI/OpenRouter   │
│  context/manager.py    ← manages conversation history │
│  context/compaction.py ← shrinks history when too big │
│  context/loop_detector.py ← detects infinite loops   │
│  tools/registry.py     ← knows all available tools   │
│  tools/discovery.py    ← finds tools dynamically     │
│  tools/subagents.py    ← spawns sub-agents            │
│  safety/approval.py    ← decides what needs approval  │
│  hooks/hook_system.py  ← runs code before/after acts  │
└───────────────────────────┬──────────────────────────┘
                            │ calls
┌───────────────────────────▼──────────────────────────┐
│  LAYER 4: TOOLS (The Hands)                           │
│  tools/base.py         ← the "rules" every tool must  │
│                          follow (abstract base class) │
│  tools/builtin/        ← actual tools (read file,     │
│                          write file, run shell, etc.) │
│  tools/mcp/            ← external tools via MCP       │
│                          protocol                     │
└───────────────────────────┬──────────────────────────┘
                            │ reads from
┌───────────────────────────▼──────────────────────────┐
│  LAYER 5: FOUNDATION (Shared Config & Utilities)      │
│  config/config.py   ← all settings live here          │
│  config/loader.py   ← loads settings from files/env  │
│  prompts/system.py  ← the system prompt text          │
│  utils/             ← tiny helpers (paths, errors)    │
└──────────────────────────────────────────────────────┘
```

---

## 4. 📖 Reading Order — Start Here

Follow this exact order to understand the system from bottom to top:

### 🟢 Step 1 — Understand the settings (Foundation)
1. **`config/config.py`** — What settings exist? (`model_name`, `approval`, `max_turns`, etc.)
2. **`config/loader.py`** — How are those settings loaded from files or environment variables?

### 🟡 Step 2 — Understand the "Tool" concept (Layer 4)
3. **`tools/base.py`** ← *You already have this open!* — What is a Tool? What rules must every tool follow? Read the `Tool` abstract class and `ToolResult`.
4. **`tools/builtin/`** — Pick one simple built-in tool (e.g., `read_file.py`) and see how it *implements* the rules from `base.py`.

### 🟠 Step 3 — Understand the Services (Layer 3)
5. **`tools/registry.py`** — How are tools stored and invoked? Note the `invoke()` method — it validates params, checks safety, then calls the tool.
6. **`client/llm_client.py`** — How does the system talk to the AI model? How does streaming work?
7. **`context/manager.py`** — How is the conversation history (the list of messages) stored and managed?
8. **`safety/approval.py`** — How does the system ask the user "Are you sure?" before dangerous actions?

### 🔴 Step 4 — Understand the Brain (Layer 2)
9. **`agent/session.py`** — This is the "state container." It creates and holds every service from Layer 3.
10. **`agent/events.py`** — What kinds of signals can the agent fire? (`TEXT_DELTA`, `TOOL_CALL_START`, etc.)
11. **`agent/agent.py`** ← **The most important file.** The `_agentic_loop()` method is the heart of the entire system.

### 🔵 Step 5 — Understand the Entry Point (Layer 1)
12. **`main.py`** — How does the program start? How does the `CLI` class listen to agent events and display them?
13. **`ui/tui.py`** — How is output rendered in the terminal?

---

## 5. 🏆 The Single Most Important File: `agent/agent.py`

Specifically, the `_agentic_loop()` method inside it.

**Why?** Because it implements the core intelligence loop that makes this an *agent* rather than just a chatbot. Here's what it does in plain English:

```
1. Ask the AI model: "Here's the conversation history. What should I do next?"
2. The AI responds with either:
   a. Text → stream it to the user, we're done for this turn.
   b. Tool calls → "I want to read a file" / "I want to run a command"
3. For each tool call:
   a. Check safety (does the user need to approve this?)
   b. Execute the tool
   c. Add the tool result back into the conversation history
4. Go back to Step 1 — the AI now knows the tool result and can decide again.
5. Repeat until the AI gives a final text answer (no more tool calls).
```

This `think → act → observe → think again` loop is the fundamental idea behind all AI agents. Every other file in the codebase exists to **support this loop**:
- `client/` gives it the AI's response
- `tools/` gives it the actions it can take
- `context/` gives it the memory of what happened
- `safety/` guards what it's allowed to do
- `ui/` shows the user what's happening
- `config/` controls its behavior

Without `agent.py`, nothing works. Everything else is a support player.
