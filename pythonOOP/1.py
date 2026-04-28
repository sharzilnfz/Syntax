from dataclasses import dataclass, field
from typing import Any
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

# @dataclass
# class TaskResult:
#   sucess: bool
#   error: str | None = None
#   message: str
#   metadata: dict[str, Any] = field(default_factory=dict)
  
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
    print(task.summary())  
