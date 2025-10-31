import streamlit as st
from styles.app_css import inject_css
from utils.initialize_sessions import initialize_sessions

inject_css()

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

initialize_sessions()

home_page = st.Page("pages/home.py", title="Home", icon=":material/home:")
tasks_page = st.Page(
    "pages/tasks.py", title="All Tasks", icon=":material/hourglass_top:"
)
upcoming_tasks_page = st.Page(
    "pages/upcoming_tasks.py", title="Upcoming", icon=":material/schedule:"
)
completed_tasks_page = st.Page(
    "pages/completed_tasks.py", title="Completed", icon=":material/check_circle:"
)

workspace_page = st.Page(
    "pages/workspace.py", title="Workspace", icon=":material/workspaces:"
)

groups_page = st.Page("pages/groups.py", title="Task Groups", icon=":material/layers:")

pg = st.navigation(
    {
        "GoGetter": [
            home_page,
        ],
        "My Workspace": [workspace_page],
        "Tasks": [tasks_page, groups_page, upcoming_tasks_page, completed_tasks_page],
    }
)

pg.run()
