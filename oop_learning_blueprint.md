# 🏗️ OOP in Python — Learning Blueprint
### Tailored to Your AI Coding Agent Codebase

---

## ❓ Should You Build a Project?

**Yes — building a project is the most effective way to learn OOP**, especially for you because:

- You already have a *real codebase* (`base.py`, `tools/`, `agent/`) to compare against
- OOP concepts only "click" when you feel the *problem they solve*, not just read about them
- Each concept below exists **verbatim** in your codebase — you'll build a mental bridge

> **Strategy**: Build one progressive project from scratch. Each new feature *forces* you to use one new OOP concept. By the end, you'll recognize every pattern in `base.py` instantly.

---

## 🎯 The Project: `TaskFlow` — A Smart CLI Task Manager

You'll build a command-line task manager that grows in complexity with each OOP lesson. This mirrors how your AI agent is structured: a base class, multiple tools that inherit from it, enums for categories, dataclasses for data, etc.

**Final features:**
- Create tasks of different types (Work, Personal, Urgent)
- Each task type has different behavior (priority, formatting, reminders)
- Tasks have statuses tracked via Enums
- A "Task Runner" executes tasks polymorphically
- Validation using class methods and properties
- Plugin-style architecture (mirrors `Tool` base class)

---

## 📚 Phase-by-Phase Curriculum

---

### Phase 1 — The Foundation: Classes & Objects
**Concept**: What a class is, `__init__`, instance vs class variables, `self`

**What to build**: A simple `Task` class

```python
# task.py
class Task:
    # Class variable — shared by ALL instances
    total_tasks = 0

    def __init__(self, title: str, description: str):
        self.title = title              # instance variable
        self.description = description  # instance variable
        self.is_done = False
        Task.total_tasks += 1          # modifying class variable

    def complete(self):
        self.is_done = True

    def __repr__(self):
        status = "✅" if self.is_done else "⬜"
        return f"{status} [{self.title}] - {self.description}"


# main.py
t1 = Task("Buy groceries", "Milk, eggs, bread")
t2 = Task("Read a book", "Finish chapter 5")

print(t1)                    # ⬜ [Buy groceries] - Milk, eggs, bread
t1.complete()
print(t1)                    # ✅ [Buy groceries] - Milk, eggs, bread
print(Task.total_tasks)      # 2
```

**🔗 Where in your codebase**: `ToolResult.__init__`, `Tool.__init__(self, config: Config)`

---

### Phase 2 — Enums: Named Constants
**Concept**: `Enum`, why we use it instead of plain strings, `str, Enum` trick

**What to build**: `TaskStatus` and `TaskKind` enums

```python
# enums.py
from enum import Enum

class TaskStatus(str, Enum):
    PENDING   = "pending"
    IN_PROGRESS = "in_progress"
    DONE      = "done"
    CANCELLED = "cancelled"

class TaskKind(str, Enum):
    WORK     = "work"
    PERSONAL = "personal"
    URGENT   = "urgent"


# Now update Task to use them
class Task:
    def __init__(self, title: str, kind: TaskKind):
        self.title = title
        self.kind = kind
        self.status = TaskStatus.PENDING   # default

    def start(self):
        self.status = TaskStatus.IN_PROGRESS

    def complete(self):
        self.status = TaskStatus.DONE
```

**Why `str, Enum`?** Because `TaskStatus.DONE == "done"` is `True` — you can compare it with plain strings and serialize it easily. This is exactly why your codebase uses `class ToolKind(str, Enum)`.

**🔗 Where in your codebase**: `ToolKind(str, Enum)` with `READ`, `WRITE`, `SHELL`, `NETWORK`, etc.

---

### Phase 3 — Dataclasses: Data Containers
**Concept**: `@dataclass`, `field()`, auto-generated `__init__` and `__repr__`, default values

**What to build**: A `TaskResult` dataclass (mirrors `ToolResult`)

```python
# results.py
from dataclasses import dataclass, field
from typing import Any

@dataclass
class TaskResult:
    success: bool
    message: str
    error: str | None = None              # optional, defaults to None
    metadata: dict[str, Any] = field(default_factory=dict)  # mutable default!

    # Why field(default_factory=dict)?
    # If you write metadata: dict = {}  ← WRONG, all instances share ONE dict
    # field(default_factory=dict) creates a NEW dict for each instance ✅
```

**The `field()` lesson** — this is a subtle but critical Python gotcha:
```python
# ❌ WRONG — mutable default
@dataclass
class Bad:
    items: list = []          # ALL instances share this same list!

# ✅ CORRECT — use field
@dataclass  
class Good:
    items: list = field(default_factory=list)  # each gets its own list
```

**🔗 Where in your codebase**: `ToolResult`, `ToolConfirmation`, `FileDiff`, `ToolInvocation` — ALL are dataclasses. Notice `metadata: dict[str, Any] = field(default_factory=dict)` on line 60 of `base.py`.

---

### Phase 4 — Inheritance: Reusing & Extending
**Concept**: `class Child(Parent)`, `super()`, overriding methods, `isinstance()`

**What to build**: Specialized task types that extend `Task`

```python
# tasks.py
class Task:
    def __init__(self, title: str):
        self.title = title
        self.status = TaskStatus.PENDING

    def summary(self) -> str:
        return f"[Task] {self.title}"


class UrgentTask(Task):
    def __init__(self, title: str, deadline: str):
        super().__init__(title)   # call parent's __init__
        self.deadline = deadline  # add new attribute

    # Override parent's method
    def summary(self) -> str:
        return f"🚨 [URGENT - Due {self.deadline}] {self.title}"


class WorkTask(Task):
    def __init__(self, title: str, project: str):
        super().__init__(title)
        self.project = project

    def summary(self) -> str:
        return f"💼 [{self.project}] {self.title}"


# Usage
tasks = [
    Task("Buy milk"),
    UrgentTask("Submit report", deadline="5pm"),
    WorkTask("Fix bug", project="AI Agent"),
]

for task in tasks:
    print(task.summary())   # each calls its OWN summary() — Polymorphism!
```

**🔗 Where in your codebase**: Every tool (e.g. `ReadFileTool`, `ShellTool`) inherits from `Tool(abc.ABC)`.

---

### Phase 5 — Abstract Classes: Enforcing Contracts
**Concept**: `abc.ABC`, `@abc.abstractmethod`, why abstract classes exist

**What to build**: An abstract `BaseRunner` that forces subclasses to implement `run()`

```python
# runner.py
import abc

class BaseRunner(abc.ABC):
    """
    Abstract base class. Cannot be instantiated directly.
    Forces any subclass to implement the 'run' method.
    """

    name: str = "base_runner"

    @abc.abstractmethod
    def run(self, task: Task) -> TaskResult:
        """Subclasses MUST implement this."""
        pass

    def validate(self, task: Task) -> bool:
        """Concrete method — subclasses CAN override but don't have to."""
        return task.status == TaskStatus.PENDING

    def describe(self) -> str:
        return f"Runner: {self.name}"


class WorkRunner(BaseRunner):
    name = "work_runner"

    def run(self, task: Task) -> TaskResult:
        task.start()
        # ... do work-specific logic
        task.complete()
        return TaskResult(success=True, message=f"Completed: {task.title}")


class UrgentRunner(BaseRunner):
    name = "urgent_runner"

    def run(self, task: Task) -> TaskResult:
        print(f"🚨 Running URGENT task: {task.title}")
        task.complete()
        return TaskResult(success=True, message=f"Urgent done: {task.title}")


# This will FAIL — you can't instantiate abstract classes:
# runner = BaseRunner()  ← TypeError: Can't instantiate abstract class
```

**Why this matters**: Abstract classes are a *contract*. They say: "If you want to be a `Runner`, you MUST have a `run()` method." This prevents bugs where a subclass forgets to implement critical behavior.

**🔗 Where in your codebase**: `class Tool(abc.ABC)` with `@abc.abstractmethod async def execute(...)` on line 122 of `base.py`. Every tool *must* implement `execute()` or Python raises an error.

---

### Phase 6 — Class Methods & Static Methods
**Concept**: `@classmethod`, `@staticmethod`, `cls` vs `self`

**What to build**: Factory methods on `TaskResult` (exactly mirrors `ToolResult`)

```python
@dataclass
class TaskResult:
    success: bool
    message: str
    error: str | None = None

    @classmethod
    def success_result(cls, message: str) -> "TaskResult":
        """Factory method — creates a successful result"""
        return cls(success=True, message=message, error=None)
        #     ^^^— cls is the class itself, like calling TaskResult(...)

    @classmethod
    def error_result(cls, error: str) -> "TaskResult":
        """Factory method — creates a failed result"""
        return cls(success=False, message="", error=error)

    @staticmethod
    def format_status(success: bool) -> str:
        """Static method — no access to instance or class, just a utility"""
        return "✅ Success" if success else "❌ Failed"


# Usage
result = TaskResult.success_result("Task completed!")  # no need to pass success=True
print(TaskResult.format_status(True))                  # ✅ Success
```

**`@classmethod` vs `@staticmethod`**:
| | Access `self`? | Access `cls`? | Use case |
|---|---|---|---|
| Regular method | ✅ | ❌ | Instance behavior |
| `@classmethod` | ❌ | ✅ | Factory / alternate constructors |
| `@staticmethod` | ❌ | ❌ | Pure utility functions |

**🔗 Where in your codebase**: `ToolResult.error_result()` and `ToolResult.success_result()` on lines 66-82 of `base.py`.

---

### Phase 7 — Properties: Controlled Attribute Access
**Concept**: `@property`, `@setter`, why not to use `get_x()` methods

**What to build**: A `priority` property on `Task`

```python
class Task:
    def __init__(self, title: str, kind: TaskKind):
        self.title = title
        self.kind = kind
        self._priority = 0   # convention: _ prefix = "private"

    @property
    def priority(self) -> int:
        """Getter — access like an attribute: task.priority"""
        return self._priority

    @priority.setter
    def priority(self, value: int):
        """Setter — validate before storing"""
        if not (0 <= value <= 10):
            raise ValueError(f"Priority must be 0-10, got {value}")
        self._priority = value

    @property
    def is_high_priority(self) -> bool:
        """Read-only computed property"""
        return self._priority >= 8


# Usage
task = Task("Deploy app", TaskKind.URGENT)
task.priority = 9        # triggers the setter
print(task.priority)     # 9 — triggers the getter
print(task.is_high_priority)  # True

task.priority = 15       # ❌ ValueError: Priority must be 0-10
```

**🔗 Where in your codebase**: `@property def schema(self)` on line 117-119 of `base.py`. It's a property that raises `NotImplementedError` forcing subclasses to define their own.

---

### Phase 8 — Polymorphism: One Interface, Many Behaviors
**Concept**: Same method call, different behavior based on object type

**What to build**: A `TaskManager` that runs any type of runner polymorphically

```python
class TaskManager:
    def __init__(self):
        self.runners: dict[TaskKind, BaseRunner] = {
            TaskKind.WORK:    WorkRunner(),
            TaskKind.URGENT:  UrgentRunner(),
            TaskKind.PERSONAL: PersonalRunner(),
        }

    def execute(self, task: Task) -> TaskResult:
        runner = self.runners.get(task.kind)
        if not runner:
            return TaskResult.error_result(f"No runner for {task.kind}")

        # Polymorphism: we call runner.run(task) without caring WHICH runner it is
        # WorkRunner.run(), UrgentRunner.run() — all called the same way
        return runner.run(task)
```

This is the **core power of OOP**: `TaskManager` doesn't need `if task.kind == "work": ... elif task.kind == "urgent": ...`. It just calls `.run()` and the right behavior happens automatically.

**🔗 Where in your codebase**: The agent calls `tool.execute(invocation)` without caring if it's a file tool, shell tool, or network tool. They're all `Tool` subclasses.

---

### Phase 9 — Encapsulation & `__dunder__` Methods
**Concept**: Private/protected attributes, `__repr__`, `__str__`, `__len__`, `__eq__`

**What to build**: Polish the `Task` class

```python
class Task:
    def __init__(self, title: str):
        self.title = title
        self._id = id(self)    # "private" — internal use only

    def __repr__(self) -> str:
        """Used by debugger, print(), repr()"""
        return f"Task(title={self.title!r}, status={self.status})"

    def __str__(self) -> str:
        """Used by str() and f-strings"""
        return f"[{self.status.value.upper()}] {self.title}"

    def __eq__(self, other: object) -> bool:
        """Defines =="""
        if not isinstance(other, Task):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        """Needed when __eq__ is defined, allows use in sets/dicts"""
        return hash(self._id)
```

---

### Phase 10 — Composition Over Inheritance
**Concept**: Instead of inheriting everything, *contain* objects as attributes

**What to build**: A `Notifier` that `Task` *has* rather than *is*

```python
# Bad approach (deep inheritance):
class TaskWithEmailAndSlack(Task): ...   # gets messy fast

# Good approach (composition):
class EmailNotifier:
    def notify(self, message: str):
        print(f"📧 Email: {message}")

class SlackNotifier:
    def notify(self, message: str):
        print(f"💬 Slack: {message}")

class Task:
    def __init__(self, title: str, notifier=None):
        self.title = title
        self.notifier = notifier    # Task HAS-A notifier, doesn't extend it

    def complete(self):
        self.status = TaskStatus.DONE
        if self.notifier:
            self.notifier.notify(f"Task '{self.title}' completed!")


# Usage
task = Task("Deploy", notifier=SlackNotifier())
task.complete()   # 💬 Slack: Task 'Deploy' completed!
```

**🔗 Where in your codebase**: `Tool.__init__(self, config: Config)` — `Tool` HAS-A `Config` object stored as `self.config`. It doesn't extend `Config`.

---

### Phase 11 — Type Hints & `from __future__ import annotations`
**Concept**: Type hints, `Any`, `Optional`, `Union`, forward references

```python
from __future__ import annotations  # allows "TaskResult" string as type hint before class is defined
from typing import Any

def process(task: Task, runner: BaseRunner) -> TaskResult:
    ...

# Union types (Python 3.10+ syntax):
error: str | None = None         # means: str OR None
result: TaskResult | str = ...   # means: TaskResult OR str

# Any — opt out of type checking
metadata: dict[str, Any] = {}   # dict with string keys, any value type
```

**Why `from __future__ import annotations`**: Without it, if you write `def foo() -> MyClass` before `MyClass` is defined, Python crashes. This import makes ALL annotations lazy (strings), resolving the forward reference issue. It's the very first line of `base.py`.

**🔗 Where in your codebase**: Line 1 of `base.py`: `from __future__ import annotations`

---

## 🗺️ Complete Project File Structure

```
taskflow/
├── enums.py          # Phase 2  — TaskStatus, TaskKind
├── results.py        # Phase 3  — TaskResult dataclass
├── base_task.py      # Phase 4  — Base Task class
├── tasks.py          # Phase 4  — UrgentTask, WorkTask, PersonalTask
├── runner.py         # Phase 5  — Abstract BaseRunner
├── runners.py        # Phase 8  — WorkRunner, UrgentRunner, PersonalRunner
├── manager.py        # Phase 8  — TaskManager (polymorphism)
├── notifiers.py      # Phase 10 — EmailNotifier, SlackNotifier
└── main.py           # Entry point — ties it all together
```

---

## 🔗 Concept → Codebase Mapping (Quick Reference)

| OOP Concept | Your Project | `base.py` Line |
|---|---|---|
| Class + `__init__` | `Task.__init__` | `Tool.__init__` (L114) |
| Enum | `TaskKind`, `TaskStatus` | `ToolKind` (L13) |
| Dataclass | `TaskResult` | `FileDiff`, `ToolResult` (L22, L56) |
| `field(default_factory)` | `metadata` field | `metadata` (L60), `affected_paths` (L104) |
| Inheritance | `UrgentTask(Task)` | All tools extend `Tool` |
| Abstract class | `BaseRunner(abc.ABC)` | `Tool(abc.ABC)` (L109) |
| `@abstractmethod` | `BaseRunner.run()` | `Tool.execute()` (L122) |
| `@classmethod` | `TaskResult.error_result()` | `ToolResult.error_result()` (L66) |
| `@property` | `task.priority` | `Tool.schema` (L117) |
| Polymorphism | `TaskManager.execute()` | Agent calling `tool.execute()` |
| Composition | `Task` HAS-A `Notifier` | `Tool` HAS-A `Config` (L115) |
| Type hints | `task: Task \| None` | Throughout `base.py` |
| `from __future__` | Top of file | Line 1 of `base.py` |

---

## ⏱️ Suggested Timeline

| Phase | Topic | Time |
|---|---|---|
| 1 | Classes & Objects | 1 day |
| 2 | Enums | 0.5 day |
| 3 | Dataclasses + `field()` | 1 day |
| 4 | Inheritance + `super()` | 1-2 days |
| 5 | Abstract Classes | 1 day |
| 6 | Class/Static Methods | 0.5 day |
| 7 | Properties | 0.5 day |
| 8 | Polymorphism | 1 day |
| 9 | Dunder Methods | 0.5 day |
| 10 | Composition | 0.5 day |
| 11 | Type Hints | 0.5 day |
| **Total** | | **~8-9 days** |

After finishing, open `base.py` again — it will feel like code you wrote yourself.
