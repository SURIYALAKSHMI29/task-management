import os
import sys

import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from pages.login import login_page
from pages.register import register_page
from streamlit_modal import Modal
from styles.home_css import inject_home_css
from styles.task_css import inject_css
from utils.fetch_tasks import load_and_categorize_tasks
from utils.task_card import display_tasks

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

inject_css()
inject_home_css()


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

col1, col2 = st.columns([6, 1])

with col1:
    st.markdown('<h1 class="stTitle">GoGetter</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="stTagline">A goal without a timeline is just a Dream</p>',
        unsafe_allow_html=True,
    )

with col2:
    if not st.session_state.logged_in:
        cols = st.columns([1, 1])
        with cols[0]:
            login_bt = st.button("Log in", key="login_btn")
        with cols[1]:
            register_bt = st.button("Register", key="register_btn")
        if login_bt:
            st.session_state.active_modal = "login-modal"
            login_modal.open()
        if register_bt:
            st.session_state.active_modal = "register-modal"
            register_modal.open()
    else:
        st.button("Log out", on_click=logout, key="logout_btn")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# OAuth handling
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
        print(params)
        code = params.get("code")
        print("code:", code)
        oauth.fetch_token(
            token_url,
            code=code,
        )

        user_info = oauth.get(userinfo_endpoint).json()
        st.session_state.user_email = user_info["email"]
        print("Successfully set user_email:", st.session_state.user_email)
        st.session_state.active_modal = "register-modal"
        register_modal.open()

    except Exception as e:
        print("Error fetching token:", e)

if not st.session_state.logged_in:
    st.markdown(
        """
        <div class="welcome-card">
            <h2>Welcome to GoGetter</h2>
            <p>Transform your dreams into achievable goals!</p>
            <ul class="feature-list">
                <li>📅 Plan and organize by timeline</li>
                <li>📌 Pin tasks that matter most</li>
                <li>✅ Track and complete with ease</li>
                <li>🎯 Focus on what drives you forward</li>
            </ul>
            <p class="login-text">Log in or register to start achieving your goals today!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    name = st.session_state.user["name"] or "Guest"
    st.markdown(
        f"""
        <div class="greeting-card">
            <h2>Welcome back, <span class="user-name">{name.capitalize()}</span>!</h2>
            <p>Let's make today productive!</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    load_and_categorize_tasks()
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
                st.markdown(
                    """
                    <div class="empty-state">
                        <p>No tasks scheduled for today!</p>
                        <p class="empty-subtext">Add a new goal and make it happen!</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with task_columns[1]:
            st.markdown("### Pinned Tasks ")
            if len(pinned_tasks) >= 1:
                display_tasks(
                    pinned_tasks,
                    icon="&#128204;",
                    section_name="pinned",
                    task_width=3,
                    button_width=1,
                )
            else:
                st.markdown(
                    """
                    <div class="empty-state">
                        <p>No pinned tasks yet!</p>
                        <p class="empty-subtext">Pin important goals to stay focused</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

if st.session_state.active_modal == "login-modal":
    if login_modal.is_open():
        with login_modal.container():
            login_page(login_modal)

if st.session_state.active_modal == "register-modal":
    if register_modal.is_open():
        with register_modal.container():
            register_page(register_modal)
