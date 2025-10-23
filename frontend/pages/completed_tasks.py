import streamlit as st
from styles.home_css import inject_css

from frontend.task_util import display_task

inject_css()

st.header("Completed Tasks")

completed_tasks = st.session_state.completed_tasks


def display_tasks(completed_tasks):
    for task in completed_tasks:
        display_task(task)
