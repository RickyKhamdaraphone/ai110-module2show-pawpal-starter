"""Basic tests for PawPal+ core classes."""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


def test_mark_complete_changes_status():
    """mark_complete() should flip a task from not-done to done."""
    task = Task("Morning walk", duration_minutes=30)

    assert task.is_done() is False  # starts incomplete

    task.mark_complete()

    assert task.is_done() is True


def test_daily_task_spawns_next_occurrence_tomorrow():
    """Completing a daily task returns a fresh copy due tomorrow."""
    task = Task("Feeding", duration_minutes=10, frequency="daily")

    next_task = task.mark_complete()

    assert task.is_done() is True
    assert next_task is not None
    assert next_task.is_done() is False  # the new one starts fresh
    assert next_task.due_date == date.today() + timedelta(days=1)
    assert next_task.description == "Feeding"


def test_weekly_task_spawns_next_occurrence_in_seven_days():
    """Completing a weekly task schedules the next one a week out."""
    task = Task("Bath", duration_minutes=30, frequency="weekly")

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=7)


def test_once_task_does_not_recur():
    """A one-off task returns no next occurrence."""
    task = Task("Vet visit", duration_minutes=60, frequency="once")

    assert task.mark_complete() is None


def test_pet_complete_task_attaches_next_occurrence():
    """Pet.complete_task keeps the completed task and adds the next one."""
    pet = Pet(name="Biscuit", weight=30.0, age=4, species="dog", breed="Golden")
    task = Task("Walk", duration_minutes=20, frequency="daily")
    pet.add_task(task)

    next_task = pet.complete_task(task)

    assert len(pet.get_tasks()) == 2  # original (done) + spawned occurrence
    assert next_task in pet.get_tasks()
    assert next_task.due_date == date.today() + timedelta(days=1)


def test_future_occurrence_not_due_today():
    """The spawned occurrence (due tomorrow) is excluded from today's plan."""
    owner = Owner(name="Jordan", email="j@example.com", location="Home")
    pet = Pet(name="Biscuit", weight=30.0, age=4, species="dog", breed="Golden")
    pet.add_task(Task("Walk", duration_minutes=20, frequency="daily"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner, available_minutes=60)
    scheduler.mark_task_complete(pet.tasks[0])

    # Two tasks exist, but only the completed original was ever "today"; the
    # spawned one is due tomorrow, so nothing is left to plan today.
    assert len(pet.tasks) == 2
    assert scheduler.generate_plan() == []


def test_detect_conflicts_flags_same_pet_same_time():
    """Two same-pet tasks at the same time produce exactly one warning."""
    owner = Owner(name="Jordan", email="j@example.com", location="Home")
    pet = Pet(name="Mochi", weight=10.0, age=2, species="cat", breed="Tabby")
    pet.add_task(Task("Litter", duration_minutes=10, scheduled_time="12:00"))
    pet.add_task(Task("Brushing", duration_minutes=10, scheduled_time="12:00"))
    owner.add_pet(pet)

    scheduler = Scheduler(owner, available_minutes=60)
    conflicts = scheduler.detect_conflicts()

    assert scheduler.has_conflicts() is True
    assert len(conflicts) == 1
    assert "Mochi" in conflicts[0]
    assert "12:00" in conflicts[0]


def test_detect_conflicts_normalizes_unpadded_times():
    """'9:00' and '09:00' are the same slot and should conflict."""
    owner = Owner(name="Jordan", email="j@example.com", location="Home")
    pet = Pet(name="Biscuit", weight=30.0, age=4, species="dog", breed="Golden")
    pet.add_task(Task("Walk", duration_minutes=20, scheduled_time="9:00"))
    pet.add_task(Task("Feed", duration_minutes=10, scheduled_time="09:00"))
    owner.add_pet(pet)

    assert Scheduler(owner, available_minutes=60).has_conflicts() is True


def test_no_conflict_across_different_pets():
    """Same time on DIFFERENT pets is fine — not a conflict."""
    owner = Owner(name="Jordan", email="j@example.com", location="Home")
    dog = Pet(name="Biscuit", weight=30.0, age=4, species="dog", breed="Golden")
    cat = Pet(name="Mochi", weight=10.0, age=2, species="cat", breed="Tabby")
    dog.add_task(Task("Walk", duration_minutes=20, scheduled_time="08:00"))
    cat.add_task(Task("Feed", duration_minutes=10, scheduled_time="08:00"))
    owner.add_pet(dog)
    owner.add_pet(cat)

    assert Scheduler(owner, available_minutes=60).detect_conflicts() == []


def test_completed_task_does_not_conflict():
    """A finished task no longer occupies its slot."""
    owner = Owner(name="Jordan", email="j@example.com", location="Home")
    pet = Pet(name="Mochi", weight=10.0, age=2, species="cat", breed="Tabby")
    done = Task("Litter", duration_minutes=10, scheduled_time="12:00")
    done.mark_complete()
    pet.add_task(done)
    pet.add_task(Task("Brushing", duration_minutes=10, scheduled_time="12:00"))
    owner.add_pet(pet)

    assert Scheduler(owner, available_minutes=60).detect_conflicts() == []


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should grow that pet's task list by one."""
    pet = Pet(name="Biscuit", weight=30.0, age=4, species="dog", breed="Golden Retriever")

    assert len(pet.get_tasks()) == 0  # no tasks yet

    pet.add_task(Task("Feeding", duration_minutes=10))

    assert len(pet.get_tasks()) == 1


def test_plan_by_pet_keeps_lookalike_tasks_with_their_own_pet():
    """Two pets with identical-looking tasks must not be confused.

    ``Task`` is a dataclass with value-based equality, so a `t in pet.tasks`
    membership check would match a look-alike task on the wrong pet. Grouping
    must key on object identity instead.
    """
    owner = Owner(name="Jordan", email="j@example.com", location="Home")

    dog = Pet(name="Biscuit", weight=30.0, age=4, species="dog", breed="Golden")
    cat = Pet(name="Mochi", weight=10.0, age=1, species="cat", breed="Tabby")
    # Identical field values on purpose: these compare equal under dataclass __eq__.
    dog.add_task(Task("Feeding", duration_minutes=10))
    cat.add_task(Task("Feeding", duration_minutes=10))
    owner.add_pet(dog)
    owner.add_pet(cat)

    scheduler = Scheduler(owner, available_minutes=60)
    grouped = scheduler.plan_by_pet()

    # Each pet keeps exactly its own task — no cross-contamination.
    assert len(grouped["Biscuit"]) == 1
    assert len(grouped["Mochi"]) == 1
    assert grouped["Biscuit"][0] is dog.tasks[0]
    assert grouped["Mochi"][0] is cat.tasks[0]


def test_explain_plan_reports_skipped_tasks_over_budget():
    """A task that doesn't fit the time budget is reported as skipped."""
    owner = Owner(name="Jordan", email="j@example.com", location="Home")
    pet = Pet(name="Biscuit", weight=30.0, age=4, species="dog", breed="Golden")
    pet.add_task(Task("Short walk", duration_minutes=10, priority=3))
    pet.add_task(Task("Long grooming", duration_minutes=90, priority=1))
    owner.add_pet(pet)

    scheduler = Scheduler(owner, available_minutes=30)
    plan = scheduler.generate_plan()

    assert [t.description for t in plan] == ["Short walk"]
    assert "Skipped 1 task(s)" in scheduler.explain_plan(plan)


def test_sort_by_time_orders_chronologically_with_unpadded_hours():
    """Tasks sort by time of day, even when hours aren't zero-padded."""
    owner = Owner(name="Jordan", email="j@example.com", location="Home")
    scheduler = Scheduler(owner, available_minutes=60)

    tasks = [
        Task("Afternoon meds", duration_minutes=5, scheduled_time="13:05"),
        Task("Early walk", duration_minutes=20, scheduled_time="9:30"),  # unpadded
        Task("Breakfast", duration_minutes=10, scheduled_time="07:00"),
    ]

    ordered = scheduler.sort_by_time(tasks)

    # "9:30" must land between 07:00 and 13:05 — a plain string sort would
    # push it to the end ('9' > '1'), so this proves minutes-based sorting.
    assert [t.description for t in ordered] == [
        "Breakfast",
        "Early walk",
        "Afternoon meds",
    ]


def test_sort_by_time_breaks_ties_by_priority():
    """Same time of day → higher priority comes first."""
    owner = Owner(name="Jordan", email="j@example.com", location="Home")
    scheduler = Scheduler(owner, available_minutes=60)

    tasks = [
        Task("Low", duration_minutes=5, priority=1, scheduled_time="08:00"),
        Task("High", duration_minutes=5, priority=3, scheduled_time="08:00"),
    ]

    ordered = scheduler.sort_by_time(tasks)

    assert [t.description for t in ordered] == ["High", "Low"]
