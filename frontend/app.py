import streamlit as st
from initialize_sessions import initialize_sessions
from styles.app_css import inject_css

inject_css()

st.set_page_config(layout="wide", initial_sidebar_state="expanded")

initialize_sessions()

home_page = st.Page("pages/home.py", title="GoGetter", icon=":material/home:")
tasks_page = st.Page("pages/tasks.py", title="Tasks", icon=":material/hourglass_top:")
profile_page = st.Page(
    "pages/profile.py", title="Profile", icon=":material/account_circle:"
)
upcoming_tasks_page = st.Page(
    "pages/upcoming_tasks.py", title="Upcoming tasks", icon=":material/schedule:"
)
completed_tasks_page = st.Page(
    "pages/completed_tasks.py", title="Completed tasks", icon=":material/check_circle:"
)

pg = st.navigation(
    {
        "": [home_page, profile_page],
        "Tasks": [tasks_page, upcoming_tasks_page, completed_tasks_page],
    }
)

pg.run()
