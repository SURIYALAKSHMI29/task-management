import calendar
from datetime import date, datetime, timedelta

import requests
import streamlit as st
from pydantic import EmailStr
from styles.task_css import inject_css
from utils.add_task import show_task

inject_css()


@st.cache_data(ttl=60)
def get_user_tasks():
    backend_url = st.secrets["backend"]["user_url"]
    header = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.get(f"{backend_url}/tasks", headers=header)

    if response.status_code == 200:
        st.session_state.user_tasks = response.json()
    else:
        st.error(f"Failed to fetch tasks: {response.status_code} - {response.text}")


@st.cache_data(ttl=60)
def get_user_history(user_email: EmailStr):
    payload = {"email": user_email}
    # print("Payload", payload)
    backend_url = st.secrets["backend"]["task_url"]
    header = {"Authorization": f"Bearer {st.session_state.access_token}"}
    # print("Before response", user_email)
    response = requests.post(
        f"{backend_url}/history",
        headers=header,
        json=user_email,
    )

    print(response.status_code, response.json())

    if response.status_code == 200:
        st.session_state.user_task_history = response.json()
    else:
        st.error(f"Failed to fetch history: {response.status_code} - {response.text}")


def get_task_history(task_id):
    backend_url = st.secrets["backend"]["task_url"]
    header = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.get(f"{backend_url}/history/{task_id}", headers=header)

    if response.status_code == 200:
        st.session_state.user_task_history = response.json()
        print("returning user_task_history: ", st.session_state.user_task_history)
    else:
        st.error(
            f"Failed to fetch task history: {response.status_code} - {response.text}"
        )


def sort_tasks(tasks, priority):
    return sorted(tasks, key=lambda task: (task.get("end"), priority[task["priority"]]))


def categorize_tasks(user_tasks, user_task_history):
    today = date.today()
    nearest_sunday = date.today() + timedelta(days=(6 - today.weekday()) % 6)
    nearest_monday = date.today() - timedelta(days=today.weekday())
    today_tasks = []
    pinned_tasks = []
    weekly_tasks = []
    completed_tasks = []
    overdue_tasks = []
    upcoming_tasks = []
    # print("User tasks (inside the categorize task function)", user_tasks, "\n")

    for task in user_tasks:
        status = task.get("status")
        deadline_str = task.get("deadline")
        deadline = (
            datetime.strptime(deadline_str, "%Y-%m-%d").date()
            if type(deadline_str) == str
            else deadline_str
        )
        pinned = task.get("pinned")
        repetitive_type = task.get("repetitive_type")
        repeat_until_str = task.get("repeat_until")
        repeat_until = (
            datetime.strptime(repeat_until_str, "%Y-%m-%d").date()
            if repeat_until_str
            else None
        )

        if status == "pending":
            if pinned:
                pinned_tasks.append(task)

            if repetitive_type is not None and (
                repeat_until is None or today <= repeat_until
            ):
                if repetitive_type == "daily":
                    task["deadline"] = today
                    task["start"] = today
                    task["end"] = today
                    today_tasks.append(task)
                    weekly_tasks.append(task)
                    upcoming_tasks.append(task)

                elif repetitive_type == "weekly":
                    task["deadline"] = nearest_sunday
                    task["start"] = nearest_monday
                    task["end"] = nearest_sunday
                    weekly_tasks.append(task)
                    upcoming_tasks.append(task)

                else:
                    last_day = calendar.monthrange(today.year, today.month)[1]
                    last_date = date(today.year, today.month, last_day)
                    last_monday = last_date - timedelta((last_date.weekday() - 0) % 7)
                    task["deadline"] = last_date
                    task["start"] = date(today.year, today.month, 1)
                    task["end"] = last_date

                    upcoming_tasks.append(task)

                    if today >= last_monday:
                        task_copy = task.copy()
                        task_copy["start"] = last_monday
                        weekly_tasks.append(task_copy)
                    if today == last_monday:
                        task_copy = task.copy()
                        task_copy["start"] = today
                        today_tasks.append(task_copy)
            elif deadline:
                if deadline == today:
                    task["start"] = today
                    task["end"] = today
                    today_tasks.append(task)
                elif deadline >= today:
                    task["start"] = deadline
                    task["end"] = deadline
                    upcoming_tasks.append(task)

    for task in user_task_history:
        # print("\n", task)
        if task.get("completed_at"):
            # print("added to complete tasks\n")
            completed_tasks.append(task)
        elif datetime.strptime(task.get("end"), "%Y-%m-%d").date() < today:
            # print("added to overdue tasks\n")
            overdue_tasks.append(task)

    priority_order = {"high": 1, "medium": 2, "low": 3}
    st.session_state.today_tasks = sort_tasks(today_tasks, priority_order)
    st.session_state.pinned_tasks = sort_tasks(pinned_tasks, priority_order)
    st.session_state.weekly_tasks = sort_tasks(weekly_tasks, priority_order)
    st.session_state.completed_tasks = sort_tasks(completed_tasks, priority_order)
    st.session_state.overdue_tasks = sort_tasks(overdue_tasks, priority_order)
    st.session_state.upcoming_tasks = upcoming_tasks


st.markdown(
    """
    <style>
        div[data-testid="stHorizontalBlock"] {
            padding: 20px;
            margin-bottom: 10px;
            background-color: #222;
            border-radius: 5px;
        }

        div[data-testid="stHorizontalBlock"]:hover {
            background-color: #333;
            transition: 0.3s;
            cursor: pointer;
        }

        div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
            opacity: 0;
            visibility: hidden;
            transition: opacity 0.3s, visibility 0.3s;
            background-color: #333;
        }

        div[data-testid="stHorizontalBlock"]:hover > div:nth-child(2) {
            opacity: 1;
            visibility: visible;
            background-color: #333;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def edit_task(task):
    st.session_state["edit_task"] = task
    show_task()


def complete_task(task):
    print(task["id"], "completed")
    backend_url = st.secrets["backend"]["task_url"]
    header = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.patch(
        f"{backend_url}/complete-task/{task.get('id')}", headers=header
    )

    if response.status_code == 200:
        updated_task = response.json()
        for t in st.session_state.user_tasks:
            if t["id"] == task["id"]:
                t["completed_at"] = date.today()
                t["status"] = "completed"
                break
    else:
        st.error(f"Failed to fetch tasks: {response.status_code} - {response.text}")


def delete_task(task):
    backend_url = st.secrets["backend"]["task_url"]
    header = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.delete(
        f"{backend_url}/delete-task/{task.get('id')}", headers=header
    )

    if response.status_code == 200:
        st.success("Task deleted successfully!")
    else:
        st.error(f"Failed to fetch tasks: {response.status_code} - {response.text}")


def display_task(task, completed, icon, section_name):
    deadline = task.get("deadline")
    # print(type(deadline), deadline, "condition status", (deadline is None))
    if not deadline:
        # print(task.get("start"), task.get("end"), task)
        deadline = f"{task.get('start')} - {task.get('end')}"

    cols = st.columns([10, 1])

    with cols[0]:
        st.markdown(
            f"""
            <div class="taskContainer">
                <span class="taskIcon">{icon if icon else ''}</span>
                <span class="completedDate">{task.get('completed_at') if completed else ''}</span>
                <div class="taskTitle {"icon" if icon else ""}">{task.get('title')}</div>
                <div class="taskDescription">{task['description']}</div>
                <div class="taskInfo">
                    <div class="taskDeadline">{deadline}</div>
                    <div class="taskPriority">{task['priority'].capitalize()}</div>
                    <div class="taskRepetitiveType">{task['repetitive_type'] if task['repetitive_type'] else ""}</div>
                </div>
            </div>

        """,
            unsafe_allow_html=True,
        )

    with cols[1]:
        if not completed:
            buttons = st.columns([1, 1, 1])
            unique_key = f"{section_name}-{task['id']}"
            with buttons[0]:
                task = {
                    "id": task.get("id"),
                    "title": task.get("title"),
                    "start": task.get("start"),
                    "end": task.get("end"),
                    "extendedProps": {
                        "description": task.get("description"),
                        "priority": task.get("priority"),
                        "status": task.get("status"),
                        "pinned": task.get("pinned"),
                        "repetitive": task.get("repetitive"),
                        "repetitive_type": task.get("repetitive_type"),
                        "repeat_until": task.get("repeat_until"),
                        "deadline": task.get("deadline"),
                    },
                }
                st.button(
                    "✎",
                    key=f"edit-{unique_key}-{task.get('start')}",
                    on_click=edit_task,
                    args=[task],
                )
            with buttons[1]:
                st.button(
                    "✔",
                    key=f"done-{unique_key}-{task.get('start')}",
                    on_click=complete_task,
                    args=[task],
                )
            with buttons[2]:
                st.button(
                    "🗑",
                    key=f"delete-{unique_key}-{task.get('start')}",
                    on_click=delete_task,
                    args=[task],
                )


def display_tasks(tasks, completed=False, icon=None, section_name=""):
    for task in tasks:
        display_task(task, completed, icon, section_name)
