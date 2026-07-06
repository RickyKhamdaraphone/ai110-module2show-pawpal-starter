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
    biscuit.add_task(Task("Morning walk", duration_minutes=30, priority=3))
    biscuit.add_task(Task("Feeding", duration_minutes=10, priority=3))
    biscuit.add_task(
        Task("Enrichment play", duration_minutes=45, priority=1)
    )
    mochi.add_task(Task("Litter cleaning", duration_minutes=10, priority=2))
    mochi.add_task(
        Task("Medication", duration_minutes=5, frequency="once", priority=3)
    )

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


def main() -> None:
    owner = build_household()
    print_todays_schedule(owner, available_minutes=60)


if __name__ == "__main__":
    main()
