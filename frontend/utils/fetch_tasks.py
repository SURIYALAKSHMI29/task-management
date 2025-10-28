import streamlit as st
from utils.task_util import categorize_tasks, get_user_history, get_user_tasks


def load_and_categorize_tasks():
    get_user_tasks()
    get_user_history(st.session_state.user_email)
    user_tasks = st.session_state.user_tasks
    user_task_history = st.session_state.user_task_history
    categorize_tasks(user_tasks, user_task_history)
