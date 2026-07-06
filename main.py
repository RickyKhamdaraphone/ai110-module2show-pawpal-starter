"""PawPal+ demo script.

Builds a small household (one owner, two pets, several tasks) and prints
today's schedule to the terminal. Run with:  python main.py
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def build_household() -> Owner:
    """Create a sample owner with two pets and their care tasks."""
    owner = Owner(name="Ricky", email="ricky@example.com", location="Home")

    biscuit = Pet(
        name="Biscuit",
        weight=30.0,
        age=4,
        species="dog",
        breed="Golden Retriever",
    )
    mochi = Pet(
        name="Mochi",
        weight=4.5,
        age=2,
        species="cat",
        breed="Tabby",
    )
    owner.add_pet(biscuit)
    owner.add_pet(mochi)

    # Tasks with different durations and priorities (1=low, 2=med, 3=high).
    # scheduled_time values are intentionally added OUT OF chronological order
    # so sort_by_time() has something real to reorder.
    biscuit.add_task(
        Task("Enrichment play", duration_minutes=45, priority=1,
             scheduled_time="16:00")
    )
    biscuit.add_task(
        Task("Morning walk", duration_minutes=30, priority=3,
             scheduled_time="7:30")  # unpadded hour on purpose
    )
    biscuit.add_task(
        Task("Feeding", duration_minutes=10, priority=3,
             scheduled_time="08:00")
    )
    mochi.add_task(
        Task("Litter cleaning", duration_minutes=10, priority=2,
             scheduled_time="12:00")
    )
    mochi.add_task(
        Task("Medication", duration_minutes=5, frequency="once", priority=3,
             scheduled_time="09:15")
    )
    # Conflict on purpose: another Mochi task at the SAME time as litter
    # cleaning ("12:00" vs unpadded "12:00") so detect_conflicts() has a hit.
    mochi.add_task(
        Task("Brushing", duration_minutes=10, priority=1,
             scheduled_time="12:00")
    )

    # Mark one task done so the completion filter has something to separate.
    biscuit.tasks[2].mark_complete()  # Feeding

    return owner


def print_todays_schedule(owner: Owner, available_minutes: int) -> None:
    """Print today's schedule for the owner, grouped by pet."""
    scheduler = Scheduler(owner, available_minutes=available_minutes)
    owner.scheduler = scheduler

    print("=" * 44)
    print(f"  Today's Schedule for {owner.name}")
    print(f"  Time available: {available_minutes} min")
    print("=" * 44)

    plan_by_pet = scheduler.plan_by_pet()
    if not plan_by_pet:
        print("  Nothing scheduled today. 🎉")
        return

    for pet in owner.pets:
        tasks = plan_by_pet.get(pet.name)
        if not tasks:
            continue
        print(f"\n{pet.name} ({pet.breed}):")
        for task in tasks:
            box = "[x]" if task.is_done() else "[ ]"
            print(
                f"  {box} {task.description} "
                f"({task.duration_minutes} min, priority {task.priority})"
            )

    print("\n" + "-" * 44)
    print(scheduler.explain_plan())


def _fmt(task: Task) -> str:
    """One-line description of a task for terminal output."""
    box = "[x]" if task.is_done() else "[ ]"
    return (
        f"  {box} {task.scheduled_time}  {task.description} "
        f"({task.duration_minutes} min, priority {task.priority})"
    )


def demo_sorting_and_filtering(owner: Owner) -> None:
    """Prove sort_by_time() and filter_tasks() work against real data."""
    scheduler = Scheduler(owner, available_minutes=60)

    print("\n" + "=" * 44)
    print("  Sorting & Filtering Demo")
    print("=" * 44)

    # 1) Sorting: all tasks were added out of chronological order above.
    all_tasks = scheduler.get_all_tasks()
    print("\nAll tasks in insertion order (unsorted):")
    for task in all_tasks:
        print(_fmt(task))

    print("\nSame tasks via sort_by_time() (chronological):")
    for task in scheduler.sort_by_time(all_tasks):
        print(_fmt(task))

    # 2) Filter by pet name.
    print("\nfilter_tasks(pet_name='Biscuit'):")
    for task in scheduler.sort_by_time(scheduler.filter_tasks(pet_name="Biscuit")):
        print(_fmt(task))

    # 3) Filter by completion status.
    print("\nfilter_tasks(completed=False) -- still to do:")
    for task in scheduler.filter_tasks(completed=False):
        print(_fmt(task))

    print("\nfilter_tasks(completed=True) -- already done:")
    for task in scheduler.filter_tasks(completed=True):
        print(_fmt(task))

    # 4) Both filters combined (logical AND).
    print("\nfilter_tasks(pet_name='Biscuit', completed=False):")
    for task in scheduler.filter_tasks(pet_name="Biscuit", completed=False):
        print(_fmt(task))


def demo_recurrence(owner: Owner) -> None:
    """Show a recurring task spawning its next occurrence on completion."""
    scheduler = Scheduler(owner, available_minutes=60)
    biscuit = owner.pets[0]

    print("\n" + "=" * 44)
    print("  Recurrence Demo")
    print("=" * 44)

    walk = next(t for t in biscuit.tasks if t.description == "Morning walk")
    print(f"\nBefore: {biscuit.name} has {len(biscuit.tasks)} task(s).")
    print(f"Completing '{walk.description}' (daily, due {walk.due_date})...")

    spawned = scheduler.mark_task_complete(walk)

    print(f"After:  {biscuit.name} has {len(biscuit.tasks)} task(s).")
    if spawned is not None:
        print(
            f"  -> spawned next occurrence of '{spawned.description}' "
            f"due {spawned.due_date} (done={spawned.is_done()})"
        )


def demo_conflicts(owner: Owner) -> None:
    """Show lightweight conflict detection warning instead of crashing."""
    scheduler = Scheduler(owner, available_minutes=60)

    print("\n" + "=" * 44)
    print("  Conflict Detection Demo")
    print("=" * 44)

    conflicts = scheduler.detect_conflicts()
    if not conflicts:
        print("\nNo scheduling conflicts.")
        return

    print(f"\nFound {len(conflicts)} conflict warning(s):")
    for warning in conflicts:
        print(f"  {warning}")


def main() -> None:
    owner = build_household()
    print_todays_schedule(owner, available_minutes=60)
    demo_sorting_and_filtering(owner)
    demo_recurrence(owner)
    demo_conflicts(owner)


if __name__ == "__main__":
    main()
