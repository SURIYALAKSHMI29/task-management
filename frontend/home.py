import time

import requests
import streamlit as st
from pages.login import login_page
from pages.register import register_page
from streamlit_modal import Modal

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "active_modal" not in st.session_state:
    st.session_state.active_modal = None

login_modal = Modal("Login", key="login-modal", padding=20, max_width=900)

register_modal = Modal("Register", key="register-modal", padding=20, max_width=900)

# def open_login_modal():
#     st.session_state.active_modal = "login-modal"
# def open_register_modal():
#     st.session_state.active_modal = "register-modal"


def logout():
    st.session_state.logged_in = False


if st.session_state.active_modal == "login-modal":
    if login_modal.is_open():
        with login_modal.container():
            login_page(login_modal)

if st.session_state.active_modal == "register-modal":
    if register_modal.is_open():
        with register_modal.container():
            register_page(register_modal)


st.title("GoGetter")

if not st.session_state.logged_in:
    with st.container():
        login_bt = st.button("Log in")
        register_bt = st.button("Register")
        if login_bt:
            st.session_state.active_modal = "login-modal"
            login_modal.open()
        if register_bt:
            st.session_state.active_modal = "register-modal"
            register_modal.open()
else:
    with st.container():
        st.button("Log out", on_click=logout)


st.header("A goal without a timeline is just a Dream")
st.subheader("Manage your tasks Efficiently!")

if not st.session_state.logged_in:
    st.write("Get better experience by loggin in")

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
        "Search": [search_page],
        "Tasks": [tasks_page, upcoming_tasks_page, completed_tasks_page],
        "Profile": [profile_page],
    }
)

pg.run()
