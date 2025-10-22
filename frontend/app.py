import streamlit as st
from styles.home_css import inject_css

inject_css()

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "active_modal" not in st.session_state:
    st.session_state.active_modal = None

if "user_email" not in st.session_state:
    st.session_state.user_email = None


# def open_login_modal():
#     st.session_state.active_modal = "login-modal"
# def open_register_modal():
#     st.session_state.active_modal = "register-modal"


home_page = st.Page("pages/home.py", title="Home", icon=":material/home:")
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
        "Home": [home_page],
        "Search": [search_page],
        "Tasks": [tasks_page, upcoming_tasks_page, completed_tasks_page],
        "Profile": [profile_page],
    }
)

print("user_email:", st.session_state.user_email)

pg.run()
