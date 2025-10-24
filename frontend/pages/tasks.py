from datetime import date, datetime, timedelta

import streamlit as st

from frontend.styles.task_css import inject_css
from frontend.task_util import display_tasks

inject_css()

st.header("Tasks")

# overdue_tasks = st.session_state.user_tasks.filter(lambda task: task["status"] == "pending" and datetime.fromisoformat(task.get("deadline")).date() < datetime.now())

overdue_tasks = st.session_state.overdue_tasks
today_tasks = st.session_state.today_tasks

nearest_sunday = date.today() + timedelta(days=(6 - date.today().weekday()) % 6)
weekly_tasks = st.session_state.weekly_tasks
upcoming_tasks = st.session_state.upcoming_tasks
user_tasks = today_tasks + weekly_tasks + overdue_tasks + upcoming_tasks

priority = {"high": 1, "medium": 2, "low": 3}
user_tasks.sort(
    key=lambda task: (
        (
            task.get("end")
            if type(task.get("end")) == date
            else datetime.strptime(task.get("end"), "%Y-%m-%d").date()
        ),
        priority[task["priority"]],
    )
)


def search_task_list(tasks, search_term):
    return [task for task in tasks if task["title"].lower().find(search_term) != -1]


def search_tasks():
    search_term = st.session_state.search_task.lower()
    global today_tasks, weekly_tasks, overdue_tasks, user_tasks

    today_tasks = search_task_list(today_tasks, search_term)
    weekly_tasks = search_task_list(weekly_tasks, search_term)
    overdue_tasks = search_task_list(overdue_tasks, search_term)
    user_tasks = search_task_list(user_tasks, search_term)


def filter_task_list(tasks, prop, value):
    return [task for task in tasks if task[prop] == value]


def filter_tasks(prop, value):
    global today_tasks, weekly_tasks, overdue_tasks, user_tasks

    today_tasks = filter_task_list(today_tasks, prop, value)
    weekly_tasks = filter_task_list(weekly_tasks, prop, value)
    overdue_tasks = filter_task_list(overdue_tasks, prop, value)
    user_tasks = filter_task_list(user_tasks, prop, value)


toolbar_cols = st.columns([3, 2, 1, 1])

with toolbar_cols[0]:
    st.text_input("", key="search_task", placeholder="Search task")

with toolbar_cols[2]:
    st.selectbox(
        "",
        ["Repetivity", "Daily", "Weekly", "Monthly"],
        key="repetitive_type",
    )

with toolbar_cols[3]:
    st.selectbox("", ["Priority", "High", "Medium", "Low"], key="priority")

st.write("")

if st.session_state.search_task:
    search_tasks()

if st.session_state.priority != "Priority":
    filter_tasks("priority", st.session_state.priority.lower())

if st.session_state.repetitive_type != "Repetivity":
    filter_tasks("repetitive_type", st.session_state.repetitive_type.lower())

with st.container():
    tabs = st.tabs(["Today", "This Week", "Overdue", "All Tasks"])

    with tabs[0]:
        display_tasks(today_tasks)
    with tabs[1]:
        display_tasks(weekly_tasks)
    with tabs[2]:
        display_tasks(overdue_tasks)
    with tabs[3]:
        display_tasks(user_tasks)
