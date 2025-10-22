import streamlit as st
from styles.app_css import inject_css

inject_css()

st.set_page_config(
    layout="wide", 
    initial_sidebar_state="expanded"
)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "active_modal" not in st.session_state:
    st.session_state.active_modal = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None

if "pending_registration" not in st.session_state:
    st.session_state.pending_registration = None

if "user_tasks" not in st.session_state:
    st.session_state.user_tasks = []

if "today_tasks" not in st.session_state:
    st.session_state.today_tasks = []

# def open_login_modal():
#     st.session_state.active_modal = "login-modal"
# def open_register_modal():
#     st.session_state.active_modal = "register-modal"


home_page = st.Page("pages/home.py", title="GoGetter", icon=":material/home:")
search_page = st.Page("pages/search.py", title="Search tasks", icon=":material/search:")
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
        "": [home_page,search_page, profile_page],
        "Tasks": [tasks_page, upcoming_tasks_page, completed_tasks_page]
    }
)


print("modal state:", st.session_state.active_modal)
print("logged_in state:", st.session_state.logged_in)
print("user_email:", st.session_state.user_email)
print("pending_registration:",st.session_state.pending_registration)

print()
pg.run()
