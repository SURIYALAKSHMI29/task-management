from datetime import date, datetime

import streamlit as st
from styles.home_css import inject_css

from frontend.pages.home import display_task

inject_css()

st.header("Tasks")

def display_tasks(tasks):
    for task in tasks:
        display_task(task)

# overdue_tasks = st.session_state.user_tasks.filter(lambda task: task["status"] == "pending" and datetime.fromisoformat(task.get("deadline")).date() < datetime.now())

overdue_tasks = [
    task for task in st.session_state.user_tasks
    if task["status"] == "pending"
    and ((datetime.fromisoformat(task.get("deadline")).date() < date.today()) if task.get("deadline") else False)
]

today_tasks = st.session_state.today_tasks

weekly_tasks = [
    task for task in st.session_state.user_tasks
    if task["status"] == "pending"
    and ((datetime.fromisoformat(task.get("deadline")).date() > date.today()) if task.get("deadline") else False)
    # needs to fix this and check repetitive is weekly ah, then this week we did or not based on last_update date
]

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
