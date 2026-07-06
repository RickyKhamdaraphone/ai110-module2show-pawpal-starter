# PawPal+ Project Reflection

## 1. System Design

Three core actions:
1. The user should be able to see and check off today's tasks.
2. The user should be able to enter information about their pet, such as weight, breed, etc.
3. The user should be able to enter constraints, such as scheduling, location, potential health conditions, etc.

Main objects:
- Owner: Should hold information about owner.
- Pet: Should hold various information about the pet such as: name, weight, age, species and/or breed.
- Task: Should hold amount of time to do, a brief description of the task (walking, feeding, etc). 
- Scheduler: Should hold user inputted constraints, tasks and account for time taken to do them.


**a. Initial design**

- Briefly describe your initial UML design.
The owner owns their pet and uses the scheduler. The scheduler schedules a task and the pet needs the task.

- What classes did you include, and what responsibilities did you assign to each?
I included a class for each component, which is the Owner, Pet, Task, and Scheduler. The Owner class is able to update the info of the Scheduler, while being able to create Pet classes. The Scheduler class is able to create Task classes, or create a list of them and explain the what to do. The Pet class doesn't do much itself other than update its own information. The Task class can check itself as complete when finished.



**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
The scheduler enforces three constraints when building a plan:
1. **Time budget** — `available_minutes` is a hard cap; a task is only added if it still fits in the remaining time.
2. **Priority** — the primary sort key, so important tasks (e.g. medication) are placed before optional ones.
3. **Duration** — a tie-breaker: among equal-priority tasks, shorter ones go first so more tasks fit.

It also gates eligibility by **date/recurrence** (`is_due_today()` hides completed one-offs and future recurring occurrences). A few things are *captured but not yet enforced* in the plan: time-of-day (used only for sorting and conflict warnings), location, and pet health conditions.

- How did you decide which constraints mattered most?

I ranked them by how hard each constraint is. Time is physical — you can't do a 45-minute task in 30 minutes — so it gates everything. Priority is the actual goal of the app (make sure the important tasks happen), so it's the primary ordering. Duration doesn't express what the user wants, it's just a packing heuristic, so it's only a tie-breaker. In short: feasibility constraints gate, goal constraints rank, efficiency heuristics break ties.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

It uses a greedy, priority-first fit rather than an optimal time-packing. Because tasks are sorted by priority before fit is checked, it will always take a high-priority task even if skipping it would let several lower-priority tasks fit instead (e.g. one 45-min high-priority task blocks three 15-min medium tasks that would have filled the same hour).

- Why is that tradeoff reasonable for this scenario?

It matches user intent — a missed medication matters more than two skipped enrichment tasks, so maximizing task count would be the wrong objective. It's also cheap and predictable (O(n log n) vs. a knapsack DP that's overkill for a handful of daily tasks), and it stays explainable: `explain_plan()` can plainly list what was scheduled and what was skipped for lack of time. (Relatedly, conflict detection *warns* about two same-time tasks rather than rejecting the plan — it surfaces the problem and lets the human decide, instead of over-constraining a first version.)

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
