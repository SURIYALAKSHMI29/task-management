import streamlit as st

from frontend.styles.task_css import inject_css
from frontend.task_util import display_tasks

inject_css()

st.header("Completed Tasks")

icon = "\N{HEAVY CHECK MARK}"

completed_tasks = st.session_state.completed_tasks
display_tasks(completed_tasks, completed=True, icon=icon)
