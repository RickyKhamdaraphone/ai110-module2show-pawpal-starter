# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Terminal output from running `python main.py` (evidence the system runs correctly):

```
============================================
  Today's Schedule for Ricky
  Time available: 60 min
============================================

Biscuit (Golden Retriever):
  [ ] Feeding (10 min, priority 3)
  [ ] Morning walk (30 min, priority 3)

Mochi (Tabby):
  [ ] Medication (5 min, priority 3)
  [ ] Litter cleaning (10 min, priority 2)

--------------------------------------------
Planned 4 task(s) using 55 of 60 min available (location: Home).
  - Medication (5 min, priority 3)
  - Feeding (10 min, priority 3)
  - Morning walk (30 min, priority 3)
  - Litter cleaning (10 min, priority 2)
Skipped 1 task(s) for lack of time:
  - Enrichment play (45 min)
```

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The 25 tests in `tests/test_pawpal.py` exercise the scheduling behaviors that
are easiest to get wrong:

- **Sorting correctness** — tasks are returned in chronological order by time of
  day, including unpadded hours (`"9:30"`), midnight/end-of-day boundaries, and
  priority tie-breaks; sorting is non-destructive.
- **Recurrence logic** — completing a `daily` task spawns a fresh occurrence due
  the next day (and `weekly` a week out), the copy carries over all fields as a
  distinct object, `once` tasks don't recur, and the new task is attached to the
  correct pet.
- **Conflict detection** — same-pet, same-time overlaps are flagged (including
  3-way overlaps), while different times, different pets, completed tasks, and
  future-dated occurrences correctly do *not* conflict.
- **Planning & filtering** — the time-budget plan skips tasks that don't fit,
  groups by pet without confusing look-alike tasks, and filters by status/pet.

Successful test run:

```
============================= test session starts =============================
platform win32 -- Python 3.14.3, pytest-9.1.1, pluggy-1.6.0
rootdir: c:\Users\mrmel\ai110-module2show-pawpal-starter
collected 25 items

tests\test_pawpal.py .........................                           [100%]

============================= 25 passed in 0.04s ==============================
```

## 📐 Smarter Scheduling

Beyond the basic time-budget plan, PawPal+ implements four "smarter scheduling"
features. Each is summarized below and documented in `pawpal_system.py`.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` (+ `_prioritized()`, `_to_minutes()` helpers) | Chronological order by time of day; priority-then-duration order for planning |
| Filtering | `Scheduler.filter_tasks()` (+ `get_plannable_tasks()`) | By completion status and/or pet name; combinable |
| Conflict handling | `Scheduler.detect_conflicts()` (+ `has_conflicts()`) | Warns on same-pet, same-time overlaps — never crashes |
| Recurring tasks | `Task.mark_complete()` → `Task.next_occurrence()` (attached via `Pet.complete_task()` / `Scheduler.mark_task_complete()`) | Daily/weekly tasks spawn the next occurrence automatically |

### Sorting — `Scheduler.sort_by_time()`

Orders a list of tasks by time of day, earliest first. It sorts on
minutes-since-midnight (via the `_to_minutes()` helper) rather than the raw
`"HH:MM"` string, so an unpadded `"9:30"` still sorts before `"13:05"`; ties
break on priority. Task *planning* order is handled separately by
`_prioritized()`, which sorts by priority (high first) then shortest duration.

### Filtering — `Scheduler.filter_tasks()`

Returns tasks filtered by completion status (`completed=True/False`) and/or
owning pet (`pet_name=`, case-insensitive). Both filters are optional and
combine with logical AND. The planner also uses `get_plannable_tasks()`, which
filters to tasks that are due today and not yet done before ordering them.

### Conflict detection — `Scheduler.detect_conflicts()`

A lightweight check that flags when two unfinished tasks for the **same pet**
are scheduled at the **same time of day**. Times are normalized to minutes
(so `"7:30"` and `"07:30"` count as one slot), and same-time tasks on *different*
pets are not treated as conflicts. It returns a list of human-readable warning
strings (empty when clean) and never raises, so the UI can surface warnings
without crashing. `has_conflicts()` is a boolean convenience wrapper.

### Recurring tasks — `Task.mark_complete()` / `Task.next_occurrence()`

When a `daily` or `weekly` task is marked complete, a fresh, incomplete copy is
created for the next occurrence — due `today + 1 day` (daily) or `today + 7 days`
(weekly), computed with `timedelta`. `once` tasks don't recur. `mark_complete()`
returns the new occurrence; `Pet.complete_task()` and
`Scheduler.mark_task_complete()` attach it to the correct pet automatically. A
future-dated occurrence is hidden from today's plan by `Task.is_due_today()`.

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
