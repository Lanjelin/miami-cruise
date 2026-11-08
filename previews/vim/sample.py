# Parse a work log and report overdue tasks
from dataclasses import dataclass

DEFAULT_LIMIT = 25


@dataclass
class Task:
    name: str
    due: int | None = None
    done: bool = False


def count_overdue(tasks: list[Task], today: int) -> int:
    """Return how many open tasks are past their due date."""
    total = 0
    for task in tasks:
        if task.due and task.due < today and not task.done:
            total += 1
            print(f"overdue: {task.name} ({today - task.due} days)")
    return total


try:
    raise RuntimeError("TODO: handle missing file")
except RuntimeError as err:
    print(err)
