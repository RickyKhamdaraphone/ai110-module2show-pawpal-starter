"""PawPal+ core system classes.

Skeleton generated from diagrams/uml.mmd. Method bodies are stubs
(no logic yet) — fill them in incrementally per the README workflow.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Pet:
    """A pet the owner cares for."""

    name: str
    weight: float
    age: int
    species: str
    breed: str
    health_conditions: list[str] = field(default_factory=list)

    def update_info(self, weight: float, age: int, breed: str) -> None:
        """Update mutable pet details."""
        raise NotImplementedError

    def add_health_condition(self, condition: str) -> None:
        """Record a health condition that scheduling should account for."""
        raise NotImplementedError


@dataclass
class Task:
    """A single care task (walk, feeding, meds, etc.)."""

    description: str
    category: str
    duration_minutes: int
    priority: int
    completed: bool = False

    def toggle_complete(self) -> None:
        """Flip the completed state (used to check tasks off)."""
        raise NotImplementedError

    def is_done(self) -> bool:
        """Return whether the task has been completed."""
        raise NotImplementedError


@dataclass
class Owner:
    """The pet owner — identity and ownership hub."""

    name: str
    email: str
    location: str
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        raise NotImplementedError

    def update_info(self, name: str, email: str, location: str) -> None:
        """Update owner details."""
        raise NotImplementedError


class Scheduler:
    """Builds a daily plan from tasks, constraints, and priorities."""

    def __init__(self, available_minutes: int, location: str) -> None:
        self.available_minutes = available_minutes
        self.location = location
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Register a task to be scheduled."""
        raise NotImplementedError

    def generate_plan(self) -> list[Task]:
        """Return an ordered plan that fits within the constraints."""
        raise NotImplementedError

    def get_todays_tasks(self) -> list[Task]:
        """Return the tasks scheduled for today."""
        raise NotImplementedError

    def explain_plan(self) -> str:
        """Explain why the scheduler chose this plan."""
        raise NotImplementedError
