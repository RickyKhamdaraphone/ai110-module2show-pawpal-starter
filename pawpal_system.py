"""PawPal+ core system classes.

Model overview:
    - Task     : a single care activity (description, time, frequency, done?).
    - Pet      : pet details + the list of Tasks that pet needs.
    - Owner    : manages multiple Pets and exposes all their Tasks.
    - Scheduler: the "brain" — retrieves, organizes, and manages Tasks
                 across every pet the owner has, subject to a time budget.

Kept in sync with diagrams/uml.mmd.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Allowed values for Task.frequency. "daily" tasks recur every day, "weekly"
# roughly once a week, and "once" is a one-off that disappears once completed.
FREQUENCIES = ("daily", "weekly", "once")


@dataclass
class Task:
    """A single care activity (walk, feeding, meds, enrichment, ...).

    ``duration_minutes`` is the *time* the activity takes to do.
    ``priority`` is kept because the README requires priority-based
    scheduling (higher number = more important).
    """

    description: str
    duration_minutes: int
    frequency: str = "daily"
    priority: int = 2  # 1 = low, 2 = medium, 3 = high
    completed: bool = False

    def toggle_complete(self) -> None:
        """Flip the completed state (used to check a task off / on)."""
        self.completed = not self.completed

    def mark_complete(self) -> None:
        """Mark the task done, regardless of current state (idempotent)."""
        self.completed = True

    def is_done(self) -> bool:
        """Return whether the task has been completed."""
        return self.completed

    def is_due_today(self) -> bool:
        """Whether this task should appear on today's list (a done 'once' task drops off)."""
        if self.frequency == "once":
            return not self.completed
        return True


@dataclass
class Pet:
    """A pet the owner cares for, plus the tasks that pet needs."""

    name: str
    weight: float
    age: int
    species: str
    breed: str
    health_conditions: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def update_info(self, weight: float, age: int, breed: str) -> None:
        """Update mutable pet details."""
        self.weight = weight
        self.age = age
        self.breed = breed

    def add_health_condition(self, condition: str) -> None:
        """Record a health condition that scheduling should account for."""
        if condition not in self.health_conditions:
            self.health_conditions.append(condition)

    def add_task(self, task: Task) -> None:
        """Attach a care task to this pet."""
        self.tasks.append(task)

    def get_tasks(self) -> list[Task]:
        """Return all tasks belonging to this pet."""
        return self.tasks


@dataclass
class Owner:
    """The pet owner — manages multiple pets and access to all their tasks."""

    name: str
    email: str
    location: str
    pets: list[Pet] = field(default_factory=list)
    scheduler: "Scheduler | None" = None

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def update_info(self, name: str, email: str, location: str) -> None:
        """Update owner details."""
        self.name = name
        self.email = email
        self.location = location

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of this owner's pets (flattened)."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    """The brain: retrieves, organizes, and manages tasks across all pets."""

    def __init__(
        self,
        owner: Owner,
        available_minutes: int,
        location: str | None = None,
    ) -> None:
        self.owner = owner
        self.available_minutes = available_minutes
        # Fall back to the owner's location if no override is given.
        self.location = location if location is not None else owner.location

    # --- retrieve -------------------------------------------------------
    def get_all_tasks(self) -> list[Task]:
        """All tasks across every pet, unfiltered."""
        return self.owner.get_all_tasks()

    def get_todays_tasks(self) -> list[Task]:
        """Return tasks due today (completed included), ordered by priority then duration."""
        todays = [t for t in self.get_all_tasks() if t.is_due_today()]
        return self._prioritized(todays)

    # --- organize -------------------------------------------------------
    def generate_plan(self) -> list[Task]:
        """Return a prioritized plan of incomplete tasks that fits within the time budget."""
        plan: list[Task] = []
        remaining = self.available_minutes
        for task in self.get_todays_tasks():
            if task.is_done():
                continue
            if task.duration_minutes <= remaining:
                plan.append(task)
                remaining -= task.duration_minutes
        return plan

    def plan_by_pet(self) -> dict[str, list[Task]]:
        """The generated plan grouped by pet name (handy for display)."""
        plan = self.generate_plan()
        grouped: dict[str, list[Task]] = {}
        for pet in self.owner.pets:
            pet_tasks = [t for t in plan if t in pet.tasks]
            if pet_tasks:
                grouped[pet.name] = pet_tasks
        return grouped

    # --- manage ---------------------------------------------------------
    def mark_task_complete(self, task: Task) -> None:
        """Check a task off."""
        task.mark_complete()

    def explain_plan(self) -> str:
        """Human-readable explanation of what got scheduled and why."""
        plan = self.generate_plan()
        todays = [t for t in self.get_todays_tasks() if not t.is_done()]
        skipped = [t for t in todays if t not in plan]
        used = sum(t.duration_minutes for t in plan)

        lines = [
            f"Planned {len(plan)} task(s) using {used} of "
            f"{self.available_minutes} min available "
            f"(location: {self.location})."
        ]
        for t in plan:
            lines.append(
                f"  - {t.description} ({t.duration_minutes} min, "
                f"priority {t.priority})"
            )
        if skipped:
            lines.append(
                f"Skipped {len(skipped)} task(s) for lack of time:"
            )
            for t in skipped:
                lines.append(
                    f"  - {t.description} ({t.duration_minutes} min)"
                )
        return "\n".join(lines)

    # --- helpers --------------------------------------------------------
    @staticmethod
    def _prioritized(tasks: list[Task]) -> list[Task]:
        """Sort by priority (high first), then shortest duration first."""
        return sorted(
            tasks, key=lambda t: (-t.priority, t.duration_minutes)
        )
