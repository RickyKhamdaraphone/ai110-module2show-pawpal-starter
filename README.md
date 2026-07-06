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

## ✨ Features

The algorithms and behaviors implemented in `pawpal_system.py`:

- **Priority-based daily planning** — a greedy planner (`generate_plan()`) orders
  today's unfinished tasks by priority (high first), then shortest duration, and
  packs them until the day's time budget runs out.
- **Sorting by time of day** — `sort_by_time()` orders tasks chronologically on
  minutes-since-midnight, so unpadded hours like `"9:30"` sort correctly against
  `"13:05"`, with priority as the tie-breaker.
- **Conflict warnings** — `detect_conflicts()` flags two unfinished tasks for the
  *same pet* at the *same time slot* (times normalized, so `"7:30"` == `"07:30"`),
  returning human-readable warnings without ever raising.
- **Daily / weekly recurrence** — completing a recurring task spawns its next
  occurrence (due `today + 1 day` or `today + 7 days` via `timedelta`); `once`
  tasks don't repeat.
- **Due-date awareness** — `is_due_today()` hides future-dated occurrences from
  today's plan, so a freshly spawned task doesn't appear next to the one just
  completed.
- **Task filtering** — `filter_tasks()` narrows by completion status and/or pet
  name (case-insensitive), combinable with logical AND.
- **Per-pet plan grouping** — `plan_by_pet()` groups the plan by pet using object
  identity, so two pets with look-alike tasks are never confused.
- **Plan explanation** — `explain_plan()` reports what was scheduled, total time
  used, and which tasks were skipped for lack of time and why.

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

PawPal+ has two front ends over the same core logic: an interactive **Streamlit
app** (`app.py`) and a scripted **CLI demo** (`main.py`).

### The Streamlit UI (`app.py`)

Run it with `python -m streamlit run app.py`. The page is organized top-to-bottom
into four sections, and a single `Owner` is kept alive across reruns in
`st.session_state` so nothing you enter is lost when the script re-runs:

- **Owner** — enter the owner's name and location.
- **Add a Pet** — enter name, species, breed, weight, and age, then click
  **Add pet**; it calls `Owner.add_pet()` and the pet appears in the list.
- **Schedule a Task** — pick which pet the task is for, then enter a title,
  duration, priority (low/medium/high), and frequency (daily/weekly/once).
  **Add task** calls `Pet.add_task()`; each pet's current tasks are listed below.
- **Build Schedule** — set the minutes available today and click
  **Generate schedule** to see today's plan grouped by pet, followed by an
  explanation of what was scheduled and what was skipped.

### Example workflow

1. Fill in the **Owner** name (e.g. "Ricky").
2. In **Add a Pet**, enter `Biscuit`, species `dog`, breed `Golden Retriever`,
   then click **Add pet**.
3. In **Schedule a Task**, with Biscuit selected, add `Morning walk`, 30 min,
   priority `high`, frequency `daily`, then click **Add task**. Repeat to add a
   few more tasks (and add a second pet if you like).
4. In **Build Schedule**, set *Time available today* to `60` and click
   **Generate schedule**.
5. Read the resulting **Today's Schedule** (grouped per pet) and the
   **Why this plan** explanation showing scheduled vs. skipped tasks.

### Key Scheduler behaviors on display

The CLI demo (`main.py`) builds a sample household — two pets, tasks added *out of
chronological order*, one task pre-completed, and a deliberate same-time clash —
to exercise every algorithm at once:

- **Priority planning + budget skipping** — the 45-min "Enrichment play" is
  skipped because it doesn't fit the remaining time in a 60-min budget.
- **Sorting by time** — the same tasks are re-printed in chronological order,
  correctly placing the unpadded `7:30` first.
- **Filtering** — tasks are filtered by pet, by completion status, and by both
  combined.
- **Daily recurrence** — completing "Morning walk" (due today) spawns a fresh
  copy due tomorrow, attached to the same pet.
- **Conflict warnings** — Mochi's "Litter cleaning" and "Brushing", both at
  `12:00`, produce a single overlap warning.

### Sample CLI output (`python main.py`)

```
============================================
  Today's Schedule for Ricky
  Time available: 60 min
============================================

Biscuit (Golden Retriever):
  [ ] Morning walk (30 min, priority 3)

Mochi (Tabby):
  [ ] Litter cleaning (10 min, priority 2)
  [ ] Medication (5 min, priority 3)
  [ ] Brushing (10 min, priority 1)

--------------------------------------------
Planned 4 task(s) using 55 of 60 min available (location: Home).
  - Medication (5 min, priority 3)
  - Morning walk (30 min, priority 3)
  - Litter cleaning (10 min, priority 2)
  - Brushing (10 min, priority 1)
Skipped 1 task(s) for lack of time:
  - Enrichment play (45 min)

============================================
  Sorting & Filtering Demo
============================================

All tasks in insertion order (unsorted):
  [ ] 16:00  Enrichment play (45 min, priority 1)
  [ ] 7:30  Morning walk (30 min, priority 3)
  [x] 08:00  Feeding (10 min, priority 3)
  [ ] 12:00  Litter cleaning (10 min, priority 2)
  [ ] 09:15  Medication (5 min, priority 3)
  [ ] 12:00  Brushing (10 min, priority 1)

Same tasks via sort_by_time() (chronological):
  [ ] 7:30  Morning walk (30 min, priority 3)
  [x] 08:00  Feeding (10 min, priority 3)
  [ ] 09:15  Medication (5 min, priority 3)
  [ ] 12:00  Litter cleaning (10 min, priority 2)
  [ ] 12:00  Brushing (10 min, priority 1)
  [ ] 16:00  Enrichment play (45 min, priority 1)

filter_tasks(pet_name='Biscuit'):
  [ ] 7:30  Morning walk (30 min, priority 3)
  [x] 08:00  Feeding (10 min, priority 3)
  [ ] 16:00  Enrichment play (45 min, priority 1)

filter_tasks(completed=False) -- still to do:
  [ ] 16:00  Enrichment play (45 min, priority 1)
  [ ] 7:30  Morning walk (30 min, priority 3)
  [ ] 12:00  Litter cleaning (10 min, priority 2)
  [ ] 09:15  Medication (5 min, priority 3)
  [ ] 12:00  Brushing (10 min, priority 1)

filter_tasks(completed=True) -- already done:
  [x] 08:00  Feeding (10 min, priority 3)

filter_tasks(pet_name='Biscuit', completed=False):
  [ ] 16:00  Enrichment play (45 min, priority 1)
  [ ] 7:30  Morning walk (30 min, priority 3)

============================================
  Recurrence Demo
============================================

Before: Biscuit has 3 task(s).
Completing 'Morning walk' (daily, due 2026-07-06)...
After:  Biscuit has 4 task(s).
  -> spawned next occurrence of 'Morning walk' due 2026-07-07 (done=False)

============================================
  Conflict Detection Demo
============================================

Found 1 conflict warning(s):
  [!] Mochi: 2 tasks overlap at 12:00 (Litter cleaning, Brushing).
```
