import streamlit as st
from utils.task_util import categorize_tasks, get_user_history, get_user_tasks


def load_and_categorize_tasks():
    get_user_tasks()
    get_user_history(st.session_state.user_email)
    user_tasks = st.session_state.user_tasks
    user_task_history = st.session_state.user_task_history
    categorize_tasks(user_tasks, user_task_history)


def load_user_details():
    user_data = st.session_state.user
    st.session_state.user_email = user_data["email"]
    st.session_state.user_workspaces = user_data["workspaces"]
    st.session_state.user_groups = user_data["user_groups"]
    workspace_groups = []
    workspace_groups = [
        group for ws in st.session_state.user_workspaces for group in ws["groups"]
    ]
    st.session_state.user_groups.extend(workspace_groups)
    st.session_state.user_workspace = st.session_state.user_workspaces[0]
    load_and_categorize_tasks()
