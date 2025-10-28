import os
import sys

import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from pages.login import login_page
from pages.register import register_page
from streamlit_modal import Modal
from styles.task_css import inject_css
from utils.task_card import display_tasks
from utils.task_util import categorize_tasks, get_user_history, get_user_tasks

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.helpers.enums import RecurrenceType, TaskStatus

inject_css()


def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]


login_modal = Modal("Login", key="login-modal", padding=20, max_width=400)
register_modal = Modal("Register", key="register-modal", padding=20, max_width=900)

st.markdown(
    """
    <style>
        div[data-modal-container="true"] > div > div {
            width: 700px !important;      
            min-width: 500px !important;   
            max-width: 90vw !important;  
        }
        div[data-modal-container="true"] > div > div >div{
            min-width: 500px !important;      
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<h1 class="stTitle">GoGetter</h1>', unsafe_allow_html=True)
st.markdown(
    '<h2 class="stHeader">A goal without a timeline is just a Dream</h2>',
    unsafe_allow_html=True,
)
st.markdown(
    '<h3 class="stSubheader">Manage your tasks Efficiently!</h3>',
    unsafe_allow_html=True,
)

params = st.query_params
if "code" in params and st.session_state.get("user_email") is None:
    client_id = st.secrets["auth"]["client_id"]
    client_secret = st.secrets["auth"]["client_secret"]
    redirect_uri = st.secrets["auth"]["redirect_uri"]
    token_url = "https://oauth2.googleapis.com/token"
    userinfo_endpoint = "https://www.googleapis.com/oauth2/v2/userinfo"

    oauth = OAuth2Session(
        client_id,
        client_secret,
        redirect_uri=redirect_uri,
        scope="openid email profile",
    )
    try:
        # if "counter" not in st.session_state:
        #     st.session_state.counter = 0
        print(params)
        # st.session_state.counter += 1
        # print("Token fetching attempt: {st.session_state.counter}")
        code = params.get("code")
        print("code:", code)
        oauth.fetch_token(
            token_url,
            code=code,
        )
        # print("Token fetched{st.session_state.counter}")

        user_info = oauth.get(userinfo_endpoint).json()
        st.session_state.user_email = user_info["email"]
        print("Successfully set user_email:", st.session_state.user_email)
        st.session_state.active_modal = "register-modal"
        register_modal.open()

    except Exception as e:
        print("Error fetching token:", e)

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
    st.write("Get better experience by loggin in")

else:
    with st.container():
        st.button("Log out", on_click=logout)

    st.write(f"Have an energetic day {st.session_state.user["name"].capitalize()}!")
    get_user_tasks()
    get_user_history(st.session_state.user_email)
    user_tasks = st.session_state.user_tasks
    user_task_history = st.session_state.user_task_history
    categorize_tasks(user_tasks, user_task_history)
    pinned_tasks = st.session_state.pinned_tasks
    today_tasks = st.session_state.today_tasks

    with st.container():
        task_columns = st.columns([2, 1])
        with task_columns[0]:
            if len(st.session_state.today_tasks) >= 1:
                st.markdown("### Today's Tasks ")
                display_tasks(
                    today_tasks, section_name="today", task_width=7, button_width=1
                )

            else:
                st.info("No tasks scheduled for today! ")
        with task_columns[1]:
            if len(pinned_tasks) >= 1:
                st.markdown("### Pinned Tasks ")
                display_tasks(
                    pinned_tasks,
                    icon="&#128204;",
                    section_name="pinned",
                    task_width=3,
                    button_width=1,
                )
            else:
                st.info("No pinned tasks found! ")


if st.session_state.active_modal == "login-modal":
    if login_modal.is_open():
        with login_modal.container():
            login_page(login_modal)

if st.session_state.active_modal == "register-modal":
    if register_modal.is_open():
        with register_modal.container():
            register_page(register_modal)
