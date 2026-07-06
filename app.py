import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# --- Persist the Owner across reruns -------------------------------------
# Streamlit re-runs this script top-to-bottom on every interaction, so an
# Owner created normally would be wiped out each time. Storing it in
# st.session_state keeps a single instance alive for the whole session:
# create it only if it doesn't already exist, then reuse it everywhere.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="", email="", location="")

owner = st.session_state.owner  # the persistent Owner for this session

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Owner")
# Bind the inputs straight onto the persistent Owner instance.
owner.name = st.text_input("Owner name", value=owner.name or "Jordan")
owner.location = st.text_input("Location", value=owner.location or "Home")

st.divider()

# --- Add a Pet -----------------------------------------------------------
st.subheader("Add a Pet")
pcol1, pcol2 = st.columns(2)
with pcol1:
    new_pet_name = st.text_input("Pet name", value="Mochi")
    new_species = st.selectbox("Species", ["dog", "cat", "other"])
    new_breed = st.text_input("Breed", value="")
with pcol2:
    new_weight = st.number_input("Weight (lbs)", min_value=0.0, value=10.0, step=0.5)
    new_age = st.number_input("Age (years)", min_value=0, value=1, step=1)

if st.button("Add pet"):
    if new_pet_name.strip():
        # Call the real Pet + Owner.add_pet methods.
        owner.add_pet(
            Pet(
                name=new_pet_name.strip(),
                weight=float(new_weight),
                age=int(new_age),
                species=new_species,
                breed=new_breed.strip(),
            )
        )
        st.success(f"Added {new_pet_name.strip()} 🐾")
    else:
        st.error("Please enter a pet name.")

if owner.pets:
    st.write("Your pets:", ", ".join(p.name for p in owner.pets))
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Schedule a Task -----------------------------------------------------
st.subheader("Schedule a Task")
# UI uses friendly labels; Task.priority is an int (1=low ... 3=high).
PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}

if not owner.pets:
    st.info("Add a pet first, then you can add tasks for it.")
else:
    target_pet_name = st.selectbox(
        "For which pet?", [p.name for p in owner.pets]
    )

    tcol1, tcol2, tcol3 = st.columns(3)
    with tcol1:
        task_title = st.text_input("Task", value="Morning walk")
    with tcol2:
        duration = st.number_input(
            "Duration (min)", min_value=1, max_value=240, value=20
        )
    with tcol3:
        priority_label = st.selectbox(
            "Priority", ["low", "medium", "high"], index=2
        )
    frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])

    if st.button("Add task"):
        # Find the chosen Pet and call the real Task + Pet.add_task methods.
        target_pet = next(p for p in owner.pets if p.name == target_pet_name)
        target_pet.add_task(
            Task(
                description=task_title,
                duration_minutes=int(duration),
                frequency=frequency,
                priority=PRIORITY_MAP[priority_label],
            )
        )
        st.success(f"Added '{task_title}' for {target_pet_name}.")

    # Show each pet's current tasks via Pet.get_tasks().
    for pet in owner.pets:
        if pet.get_tasks():
            st.write(f"**{pet.name}** — {len(pet.get_tasks())} task(s):")
            for task in pet.get_tasks():
                st.write(
                    f"- {task.description} ({task.duration_minutes} min, "
                    f"priority {task.priority}, {task.frequency})"
                )

st.divider()

# --- Build Schedule ------------------------------------------------------
st.subheader("Build Schedule")
available = st.number_input(
    "Time available today (min)", min_value=1, max_value=1440, value=60
)

if st.button("Generate schedule"):
    # Hand the whole owner to the Scheduler brain and ask for a plan.
    scheduler = Scheduler(owner, available_minutes=int(available))
    owner.scheduler = scheduler
    # Generate the plan once and reuse it for both the grouped view and the
    # explanation, instead of letting each method recompute it.
    plan = scheduler.generate_plan()
    plan_by_pet = scheduler.plan_by_pet(plan)

    if not plan_by_pet:
        st.warning("Nothing to schedule — add some pets and tasks first.")
    else:
        st.markdown(f"### Today's Schedule ({available} min available)")
        for pet in owner.pets:
            tasks = plan_by_pet.get(pet.name)
            if not tasks:
                continue
            st.markdown(f"**{pet.name}** ({pet.breed or pet.species})")
            for task in tasks:
                st.write(
                    f"- {task.description} ({task.duration_minutes} min, "
                    f"priority {task.priority})"
                )
        st.markdown("#### Why this plan")
        st.code(scheduler.explain_plan(plan))
