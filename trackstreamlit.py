import streamlit as st
import plotly.express as px
from datetime import datetime

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------

st.set_page_config(
    page_title="Task Tracker Pro",
    page_icon="🚀",
    layout="wide"
)

# --------------------------------------------------
# DARK STYLE
# --------------------------------------------------

st.markdown("""
<style>

.stApp {
    background-color: #0e1117;
}

[data-testid="stMetric"] {
    background-color: #1c1f26;
    padding: 15px;
    border-radius: 12px;
}

div[data-testid="stVerticalBlock"] > div:has(div.task-card){
    width:100%;
}

</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "tasks" not in st.session_state:
    st.session_state.tasks = []

# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title("🚀 Task Tracker Pro")
st.caption("Stay organized. Stay productive.")

# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("➕ Add Task")

    with st.form("task_form", clear_on_submit=True):

        task_type = st.selectbox(
            "Task Type",
            ["Work", "Personal"]
        )

        title = st.text_input("Task Title")

        category = st.text_input("Category")

        priority = st.selectbox(
            "Priority",
            ["High", "Medium", "Low"]
        )

        due_date = st.date_input(
            "Due Date"
        )

        submitted = st.form_submit_button(
            "Add Task"
        )

        if submitted:

            if title.strip():

                st.session_state.tasks.append(
                    {
                        "title": title,
                        "category": category,
                        "priority": priority,
                        "type": task_type,
                        "due_date": due_date,
                        "completed": False,
                    }
                )

                st.success("✅ Task Added")

# --------------------------------------------------
# TASK DATA
# --------------------------------------------------

tasks = st.session_state.tasks

total = len(tasks)

completed = sum(
    task["completed"]
    for task in tasks
)

pending = total - completed

progress = (
    completed / total
    if total > 0
    else 0
)

score = completed * 10

# --------------------------------------------------
# TOP METRICS
# --------------------------------------------------

m1, m2, m3, m4 = st.columns(4)

m1.metric(
    "📋 Total",
    total
)

m2.metric(
    "✅ Completed",
    completed
)

m3.metric(
    "⌛ Pending",
    pending
)

m4.metric(
    "🔥 Productivity",
    score
)

st.progress(progress)

# --------------------------------------------------
# ACHIEVEMENTS
# --------------------------------------------------

badges = []

if completed >= 1:
    badges.append("🥉 First Completion")

if completed >= 5:
    badges.append("🥈 Task Crusher")

if completed >= 10:
    badges.append("🥇 Productivity Hero")

if completed >= 20:
    badges.append("👑 Task Master")

if badges:
    st.success(" | ".join(badges))

# --------------------------------------------------
# HEATMAP
# --------------------------------------------------

high = len([
    t for t in tasks
    if t["priority"] == "High"
    and not t["completed"]
])

medium = len([
    t for t in tasks
    if t["priority"] == "Medium"
    and not t["completed"]
])

low = len([
    t for t in tasks
    if t["priority"] == "Low"
    and not t["completed"]
])

st.subheader("🔥 Workload Heatmap")

h1, h2, h3 = st.columns(3)

h1.metric("🔴 High", high)
h2.metric("🟡 Medium", medium)
h3.metric("🟢 Low", low)

# --------------------------------------------------
# ALERTS
# --------------------------------------------------

urgent_tasks = []

for task in tasks:

    if not task["completed"]:

        days_left = (
            task["due_date"]
            - datetime.now().date()
        ).days

        if days_left <= 2:
            urgent_tasks.append(task)

if urgent_tasks:

    st.error(
        f"🚨 {len(urgent_tasks)} task(s) due within 2 days!"
    )

# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

if total > 0:

    st.subheader("📊 Analytics")

    fig = px.pie(
        names=[
            "Completed",
            "Pending"
        ],
        values=[
            completed,
            pending
        ],
        hole=0.55
    )

    fig.update_layout(
        paper_bgcolor="#0e1117",
        font_color="white"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# --------------------------------------------------
# FILTERS
# --------------------------------------------------

st.subheader("🔍 Filter Tasks")

f1, f2 = st.columns(2)

with f1:

    filter_type = st.selectbox(
        "Task Type",
        [
            "All",
            "Work",
            "Personal"
        ]
    )

with f2:

    search = st.text_input(
        "Search"
    )

# --------------------------------------------------
# TASK LIST
# --------------------------------------------------

st.subheader("📌 Tasks")

if not tasks:

    st.info(
        "No tasks yet. Add one from the sidebar."
    )

for i, task in enumerate(tasks):

    if filter_type != "All":

        if task["type"] != filter_type:
            continue

    if search:

        if search.lower() not in task["title"].lower():
            continue

    days_left = (
        task["due_date"]
        - datetime.now().date()
    ).days

    if days_left > 0:
        countdown = f"⏳ {days_left} day(s) left"

    elif days_left == 0:
        countdown = "📅 Due Today"

    else:
        countdown = f"🚨 Overdue by {abs(days_left)} day(s)"

    if task["priority"] == "High":
        badge = "🔴 HIGH"

    elif task["priority"] == "Medium":
        badge = "🟡 MEDIUM"

    else:
        badge = "🟢 LOW"

    status = (
        "✅ Completed"
        if task["completed"]
        else "⌛ Pending"
    )

    with st.container(border=True):

        st.markdown(
            f"### {task['title']}  {badge}"
        )

        c1, c2 = st.columns(2)

        with c1:

            st.write(
                f"📁 Category: {task['category']}"
            )

            st.write(
                f"🏷 Type: {task['type']}"
            )

        with c2:

            st.write(
                f"📅 Due: {task['due_date'].strftime('%d %b %Y')}"
            )

            st.write(status)

        st.info(countdown)

        b1, b2 = st.columns(2)

        with b1:

            if not task["completed"]:

                if st.button(
                    "✅ Complete",
                    key=f"complete_{i}"
                ):
                    task["completed"] = True
                    st.rerun()

        with b2:

            if st.button(
                "🗑 Delete",
                key=f"delete_{i}"
            ):
                st.session_state.tasks.pop(i)
                st.rerun()

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Built with Streamlit • Task Tracker Pro"
)