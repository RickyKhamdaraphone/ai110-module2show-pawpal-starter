"""Basic tests for PawPal+ core classes."""

from pawpal_system import Pet, Task


def test_mark_complete_changes_status():
    """mark_complete() should flip a task from not-done to done."""
    task = Task("Morning walk", duration_minutes=30)

    assert task.is_done() is False  # starts incomplete

    task.mark_complete()

    assert task.is_done() is True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should grow that pet's task list by one."""
    pet = Pet(name="Biscuit", weight=30.0, age=4, species="dog", breed="Golden Retriever")

    assert len(pet.get_tasks()) == 0  # no tasks yet

    pet.add_task(Task("Feeding", duration_minutes=10))

    assert len(pet.get_tasks()) == 1
