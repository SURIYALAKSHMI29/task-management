import os
import sys
from datetime import date, datetime

import requests
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from pages.login import login_page
from pages.register import register_page
from streamlit_modal import Modal
from styles.home_css import inject_css

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    
from backend.helpers.enums import RecurrenceType, TaskStatus

inject_css()

def logout():
    st.session_state.logged_in = False

@st.cache_data(ttl=60)
def get_user_tasks():
    backend_url = st.secrets["backend"]["user_url"]
    header = {
        "Authorization" : f"Bearer {st.session_state.access_token}"
    }
    response = requests.get(f"{backend_url}/tasks", headers=header)

    if response.status_code == 200:
        st.session_state.user_tasks = response.json()
    else:
        st.error(f"Failed to fetch tasks: {response.status_code} - {response.text}")

def display_task(task):
    st.markdown(f"""
        <div class="taskContainer">
            <div class="taskTitle">{task['title']}</div>
            <div class="taskDescription">{task['description']}</div>
            <div class="taskInfo">
                <div class="taskDeadline">{task['deadline']}</div>
                <div class="taskPriority">{task['priority']}</div>
                <div class="taskRepetitiveType">{task['repetitive_type']}</div>
            </div
        </div>
    """, unsafe_allow_html=True)

           


login_modal = Modal("Login", key="login-modal", padding=20, max_width=900)
register_modal = Modal("Register", key="register-modal", padding=20, max_width=900)

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
else:
    with st.container():
        st.button("Log out", on_click=logout)

if not st.session_state.logged_in:
    st.write("Get better experience by loggin in")
else:
    st.write(f"Have an energetic day {st.session_state.user["name"].capitalize()}!")
    get_user_tasks()
    user_tasks = st.session_state.user_tasks

    today = date.today()
    today_tasks = []
    pinned_tasks = []

    for task in user_tasks:
        print(task)
        status = task.get("status")
        if status == "pending":
            if task.get("pinned"):
                print("pinned", task)
                task["deadline"] = datetime.fromisoformat(task.get("deadline")).date() if task.get("deadline") else None
                pinned_tasks.append(task)
            else:
                deadline = task.get("deadline")
                repetitive_type = task.get("repetitive_type")
                repeat_until = task.get("repeat_until")

                if deadline:
                    print("today deadline", task)
                    task_date = datetime.fromisoformat(deadline).date()
                    if task_date == today:
                        task["deadline"] = task_date
                        today_tasks.append(task)
                
                elif repetitive_type == RecurrenceType.DAILY and today<repeat_until:
                    print("repeating", task)
                    today_tasks.append(task)
        
        print("today tasks: \n", today_tasks)
        print("pinned tasks: \n", pinned_tasks)
        print()

    st.session_state.today_tasks = today_tasks

    with st.container():
        task_columns = st.columns([2,1])
        with task_columns[0]:
            if len(st.session_state.today_tasks) >= 1:
                st.markdown("### Today's Tasks 🗓️")
                for task in today_tasks:
                    display_task(task)
                    
            else:
                st.info("No tasks scheduled for today! ")
        with task_columns[1]:
            if len(pinned_tasks) >= 1:
                st.markdown("### Pinned Tasks ")
                for task in pinned_tasks:
                    display_task(task)
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