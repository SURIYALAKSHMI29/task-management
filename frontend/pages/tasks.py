from datetime import date, datetime, timedelta

import streamlit as st
from styles.home_css import inject_css

from frontend.task_util import display_task

inject_css()

st.header("Tasks")


def display_tasks(tasks):
    for task in tasks:
        display_task(task)


# overdue_tasks = st.session_state.user_tasks.filter(lambda task: task["status"] == "pending" and datetime.fromisoformat(task.get("deadline")).date() < datetime.now())

overdue_tasks = st.session_state.overdue_tasks
today_tasks = st.session_state.today_tasks

nearest_sunday = date.today() + timedelta(days=(6 - date.today().weekday()) % 6)
weekly_tasks = st.session_state.weekly_tasks
user_tasks = st.session_state.user_tasks

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
