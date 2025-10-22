import streamlit as st
from styles.home_css import inject_css

from frontend.pages.tasks import display_tasks

inject_css()

st.header("Completed Tasks")

completed_tasks = [
    task for task in st.session_state.user_tasks
    if task["status"] == "completed"
]

display_tasks(completed_tasks)
