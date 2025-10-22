from datetime import date, datetime

import streamlit as st
from styles.home_css import inject_css

from frontend.pages.tasks import display_tasks

inject_css()

st.header("Upcoming Tasks")

upcoming_tasks = [
    task for task in st.session_state.user_tasks
    if task["status"] == "pending"
    and ((datetime.fromisoformat(task.get("deadline")).date() > date.today()) if task.get("deadline") else False)
]

display_tasks(upcoming_tasks)
