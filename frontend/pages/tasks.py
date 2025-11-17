from datetime import date, datetime, timedelta

import requests
import streamlit as st
from pages.calendar_view import calendar_view
from styles.task_css import inject_css
from utils.add_task import show_task
from utils.load_data import load_and_categorize_tasks
from utils.task_card import display_tasks

inject_css()


def sync_workspace():
    load_and_categorize_tasks()


def reset_edit_task():
    st.session_state["edit_task"] = None
    show_task()


task_header = st.columns([1, 0.1])
with task_header[0]:
    st.markdown(
        """
        <h2 style="padding-bottom:20px;">Tasks</h2>
        """,
        unsafe_allow_html=True,
    )
with task_header[1]:
    st.markdown(" ")
    st.button("Add Task", on_click=reset_edit_task)

overdue_tasks = st.session_state.overdue_tasks
today_tasks = st.session_state.today_tasks

nearest_sunday = date.today() + timedelta(days=(6 - date.today().weekday()) % 6)
weekly_tasks = st.session_state.weekly_tasks
upcoming_tasks = st.session_state.upcoming_tasks
user_tasks = overdue_tasks + upcoming_tasks

priority = {"high": 1, "medium": 2, "low": 3}
user_tasks.sort(
    key=lambda task: (
        (
            task.get("end")
            if type(task.get("end")) == date
            else datetime.strptime(task.get("end"), "%Y-%m-%d").date()
        ),
        priority[task["priority"]],
    )
)


def change_task_view():
    st.session_state.list_view = not st.session_state.list_view


def search_task_list(tasks, search_term):
    return [task for task in tasks if task["title"].lower().find(search_term) != -1]


def search_tasks():
    search_term = st.session_state.search_task.lower()
    global today_tasks, weekly_tasks, overdue_tasks, user_tasks

    today_tasks = search_task_list(today_tasks, search_term)
    weekly_tasks = search_task_list(weekly_tasks, search_term)
    overdue_tasks = search_task_list(overdue_tasks, search_term)
    user_tasks = search_task_list(user_tasks, search_term)


def filter_task_list(tasks, prop, value):
    return [task for task in tasks if task[prop] == value]


def filter_tasks(prop, value):
    global today_tasks, weekly_tasks, overdue_tasks, user_tasks

    today_tasks = filter_task_list(today_tasks, prop, value)
    weekly_tasks = filter_task_list(weekly_tasks, prop, value)
    overdue_tasks = filter_task_list(overdue_tasks, prop, value)
    user_tasks = filter_task_list(user_tasks, prop, value)


calendar_options = {
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "",
    },
    "initialView": "dayGridMonth",
    "editable": False,
    "selectable": False,
}

toolbar_cols = st.columns([3, 1.8, 0.15, 0.15, 0.8, 0.8])

with toolbar_cols[0]:
    st.text_input(
        "Search",
        key="search_task",
        placeholder="Search task",
        label_visibility="collapsed",
    )

if st.session_state.user_workspace:
    with toolbar_cols[2]:
        st.button(
            "🔄",
            type="tertiary",
            help="Sync workspace",
            on_click=sync_workspace,
        )

with toolbar_cols[3]:
    if st.session_state.list_view:
        st.button(
            "🗓️",
            type="tertiary",
            help="Calendar View",
            on_click=change_task_view,
        )
    else:
        st.button(
            "📋",
            type="tertiary",
            help="List View",
            on_click=change_task_view,
        )

with toolbar_cols[4]:
    st.selectbox(
        "Filter",
        ["Repetivity", "Daily", "Weekly", "Monthly"],
        key="repetitive_type",
        label_visibility="collapsed",
    )

with toolbar_cols[5]:
    st.selectbox(
        "Filter",
        ["Priority", "High", "Medium", "Low"],
        key="priority",
        label_visibility="collapsed",
    )

st.write("")

if st.session_state.search_task:
    search_tasks()

if st.session_state.priority != "Priority":
    filter_tasks("priority", st.session_state.priority.lower())

if st.session_state.repetitive_type != "Repetivity":
    filter_tasks("repetitive_type", st.session_state.repetitive_type.lower())

if st.session_state.list_view:
    with st.container():
        tabs = st.tabs(["Today", "This Week", "Overdue", "All Tasks"])

        with tabs[0]:
            display_tasks(today_tasks, section_name="today")
        with tabs[1]:
            display_tasks(weekly_tasks, section_name="weekly")
        with tabs[2]:
            display_tasks(overdue_tasks, section_name="overdue")
        with tabs[3]:
            display_tasks(user_tasks, section_name="user_tasks")
else:
    calendar_view(user_tasks, calendar_options, True)
