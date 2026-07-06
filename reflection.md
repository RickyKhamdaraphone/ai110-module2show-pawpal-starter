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

Yes — significantly.

- If yes, describe at least one change and why you made it.

The biggest change was *where tasks live*. In my first UML, a Task held a reference back to its Pet and the Scheduler owned the master list of tasks. A design review pointed out that two relationships I'd drawn (Owner → Scheduler and Pet → Task) weren't actually in my code, and that a Task orphaned from its Pet meant that once I had more than one pet I couldn't tell whose task was whose. So I flipped it: each Pet now owns its own list of Tasks, and the Scheduler reads across all pets through the Owner. That gave me one clear source of truth. I also added fields the first design didn't have at all — `scheduled_time`, `due_date`, and a `next_occurrence()` method — once I realized "see today's tasks" and daily/weekly recurrence needed real date awareness.

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

I used AI across every phase: brainstorming the UML (including what the under-specified Owner class should hold), implementing the scheduling logic, generating the pytest suite, and drafting documentation.

- What kinds of prompts or questions were most helpful?

The most useful prompts asked for critique rather than code for example, "are there missing relationships or potential bottlenecks?" caught real design gaps.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

When grouping the plan by pet, the first version checked task in pet.tasks. However, two pets with identical-looking tasks (same description and duration) would compare equal, so a task could be attributed to the wrong pet. I changed it to group by object identity instead.
- How did you evaluate or verify what the AI suggested?

I ran main.py to watch the actual output, ran the pytest suite after every change, and read the code instead of pasting it blindly.

**c. AI strategy**

- Which AI coding assistant features were most effective for building your scheduler?

When I described each class's fields and responsibilities, it gave clean dataclasses I could refine. Also, running my code and tests in the same loop helped a lot, because a change was immediately verified against main.py and pytest instead of me guessing.

- Give one example of an AI suggestion you rejected or modified to keep your system design clean.

Early on, the Scheduler kept its own list of tasks and each Pet kept theirs. When tasks moved onto Pet, I dropped the Scheduler's separate task list entirely and had it read through the Owner instead, so a task lives in exactly one place.

- How did using separate chat sessions for different phases help you stay organized?

Splitting the work into phase-specific sessions kept each conversation's context focused on one job, so the suggestions stayed relevant and I wasn't scrolling past unrelated history.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

I focused on the scheduling behaviors easiest to get wrong: marking a task complete flips its status; adding a task grows the pet's list; recurrence, conflict detection, time normalization for unpadded hours, different pets don't conflict, completed tasks don't conflict.

- Why were these tests important?

They cover the core logic and the exact spots where small mistakes hide. The whole app depends on these behaviors, so a silent bug here can cause undesired behavior or crashes.

**b. Confidence**

- How confident are you that your scheduler works correctly?

Fairly confident for the implemented feature set since all tests pass.

- What edge cases would you test next if you had more time?

Conflicts based on overlapping durations rather than identical start times.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The recurrence feature, and how cleanly it fell out of the design. Completing a daily/weekly task spawns its next occurrence with dataclasses.replace, so every field copies forward automatically and only the date and completion flag change.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I'd push more of the captured but unused constraints into the actual plan: time of day feasibility (would you even be awake at this time?) and health conditions.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

AI is a fast, capable implementer, but the design judgment has to stay with me. Keeping a single source of truth and verifying by actually running the code mattered more than any suggestions.
