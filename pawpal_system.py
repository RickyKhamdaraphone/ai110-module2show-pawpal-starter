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

from dataclasses import dataclass, field, replace
from datetime import date, timedelta

# Allowed values for Task.frequency. "daily" tasks recur every day, "weekly"
# roughly once a week, and "once" is a one-off that disappears once completed.
FREQUENCIES = ("daily", "weekly", "once")

# How many days until the next occurrence, per recurring frequency. "once" is
# absent on purpose — it never repeats.
RECURRENCE_DAYS = {"daily": 1, "weekly": 7}


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
    scheduled_time: str = "09:00"  # time of day in 24-hour "HH:MM" format
    due_date: date = field(default_factory=date.today)  # the day this is due

    def toggle_complete(self) -> None:
        """Flip the completed state (used to check a task off / on)."""
        self.completed = not self.completed

    def mark_complete(self) -> "Task | None":
        """Mark the task done and, if it recurs, return its next occurrence.

        A ``daily``/``weekly`` task spawns a fresh, incomplete copy due on the
        next date (today + 1 or 7 days). A ``once`` task returns ``None`` — it
        simply drops off. The returned Task is *not* attached anywhere; callers
        such as :meth:`Pet.complete_task` are responsible for keeping it.
        """
        self.completed = True
        return self.next_occurrence()

    def next_occurrence(self) -> "Task | None":
        """Build the next occurrence of a recurring task, or ``None`` if one-off.

        The new due date is computed from *today* using ``timedelta`` so it's
        always a valid calendar date (handles month/year rollovers for free).
        """
        step = RECURRENCE_DAYS.get(self.frequency)
        if step is None:  # "once" — nothing to repeat
            return None
        # replace() clones this task, carrying every field over and overriding
        # only the two that change — so new Task fields are copied automatically.
        return replace(
            self,
            completed=False,
            due_date=date.today() + timedelta(days=step),
        )

    def is_done(self) -> bool:
        """Return whether the task has been completed."""
        return self.completed

    def is_due_today(self) -> bool:
        """Whether this task should appear on today's list.

        A task scheduled for a future ``due_date`` isn't due yet — this keeps a
        freshly spawned next occurrence from showing up alongside the one just
        completed. A done 'once' task also drops off.
        """
        if self.due_date > date.today():
            return False
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

    def complete_task(self, task: Task) -> "Task | None":
        """Mark one of this pet's tasks done, attaching any next occurrence.

        Returns the newly spawned recurring task (already added to this pet), or
        ``None`` for a one-off.
        """
        next_task = task.mark_complete()
        if next_task is not None:
            self.tasks.append(next_task)
        return next_task

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

    def filter_tasks(
        self,
        *,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return tasks filtered by completion status and/or owning pet.

        ``completed``: ``True`` → only done tasks, ``False`` → only unfinished,
        ``None`` → don't filter on status.
        ``pet_name``: keep only tasks belonging to the pet with this name
        (case-insensitive); ``None`` → tasks from every pet.
        Both filters are optional and combine (logical AND) when given.
        """
        if pet_name is None:
            tasks = self.get_all_tasks()
        else:
            tasks = [
                t
                for pet in self.owner.pets
                if pet.name.lower() == pet_name.lower()
                for t in pet.tasks
            ]
        if completed is not None:
            tasks = [t for t in tasks if t.is_done() == completed]
        return tasks

    def get_plannable_tasks(self) -> list[Task]:
        """Tasks due today that still need doing, ordered by priority then duration.

        Filters out completed tasks *before* sorting so we don't pay to order
        items the planner would immediately discard.
        """
        todays = [
            t
            for t in self.get_all_tasks()
            if t.is_due_today() and not t.is_done()
        ]
        return self._prioritized(todays)

    # --- organize -------------------------------------------------------
    def generate_plan(self) -> list[Task]:
        """Return a prioritized plan of incomplete tasks that fits within the time budget."""
        plan: list[Task] = []
        remaining = self.available_minutes
        for task in self.get_plannable_tasks():
            if task.duration_minutes <= remaining:
                plan.append(task)
                remaining -= task.duration_minutes
        return plan

    def plan_by_pet(self, plan: list[Task] | None = None) -> dict[str, list[Task]]:
        """The generated plan grouped by pet name (handy for display).

        Accepts a precomputed ``plan`` to avoid regenerating it. Membership is
        keyed on object identity (``id()``), not value equality, so two pets
        with look-alike tasks are never confused for one another.
        """
        if plan is None:
            plan = self.generate_plan()
        plan_ids = {id(t) for t in plan}
        grouped: dict[str, list[Task]] = {}
        for pet in self.owner.pets:
            pet_tasks = [t for t in pet.tasks if id(t) in plan_ids]
            if pet_tasks:
                grouped[pet.name] = pet_tasks
        return grouped

    # --- detect ---------------------------------------------------------
    def detect_conflicts(self) -> list[str]:
        """Return warnings for a pet's tasks that overlap at the same time.

        Two unfinished tasks for the *same* pet due today at the same time can't
        both be done at once. This is a lightweight check: for each pet it groups
        due-today, not-done tasks by time-of-day (normalized to minutes, so
        ``"7:30"`` and ``"07:30"`` count as the same slot) and flags any slot
        holding more than one task.

        Returns an empty list when there are no conflicts — it never raises, so
        callers can surface the warnings without guarding against a crash.
        """
        warnings: list[str] = []
        for pet in self.owner.pets:
            by_slot: dict[int, list[Task]] = {}
            for task in pet.tasks:
                if not task.is_due_today() or task.is_done():
                    continue
                by_slot.setdefault(
                    self._to_minutes(task.scheduled_time), []
                ).append(task)
            for tasks in by_slot.values():
                if len(tasks) > 1:
                    names = ", ".join(t.description for t in tasks)
                    warnings.append(
                        f"[!] {pet.name}: {len(tasks)} tasks overlap at "
                        f"{tasks[0].scheduled_time} ({names})."
                    )
        return warnings

    def has_conflicts(self) -> bool:
        """Whether any scheduling conflicts exist (convenience wrapper)."""
        return bool(self.detect_conflicts())

    # --- manage ---------------------------------------------------------
    def mark_task_complete(self, task: Task) -> Task | None:
        """Check a task off, spawning its next occurrence on the owning pet.

        Finds which pet owns ``task`` (by identity) so a recurring task's next
        occurrence is attached to the right pet. Returns that next occurrence,
        or ``None`` if the task doesn't recur or isn't owned by any pet.
        """
        for pet in self.owner.pets:
            if any(t is task for t in pet.tasks):
                return pet.complete_task(task)
        # Not found on any pet — just mark it done.
        task.mark_complete()
        return None

    def explain_plan(self, plan: list[Task] | None = None) -> str:
        """Human-readable explanation of what got scheduled and why.

        Accepts a precomputed ``plan`` so callers that already generated one
        don't trigger another sort + greedy fit.
        """
        if plan is None:
            plan = self.generate_plan()
        plan_ids = {id(t) for t in plan}
        todays = self.get_plannable_tasks()
        skipped = [t for t in todays if id(t) not in plan_ids]
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

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """Return tasks ordered by time of day (earliest first).

        Sorts on minutes-since-midnight rather than the raw ``"HH:MM"`` string
        so unpadded values like ``"9:30"`` still order correctly. Ties break on
        priority (high first), matching ``_prioritized``.
        """
        return sorted(
            tasks,
            key=lambda t: (self._to_minutes(t.scheduled_time), -t.priority),
        )

    # --- helpers --------------------------------------------------------
    @staticmethod
    def _to_minutes(hhmm: str) -> int:
        """Convert an 'HH:MM' 24-hour string to minutes since midnight."""
        hours, minutes = hhmm.split(":")
        return int(hours) * 60 + int(minutes)

    @staticmethod
    def _prioritized(tasks: list[Task]) -> list[Task]:
        """Sort by priority (high first), then shortest duration first."""
        return sorted(
            tasks, key=lambda t: (-t.priority, t.duration_minutes)
        )
