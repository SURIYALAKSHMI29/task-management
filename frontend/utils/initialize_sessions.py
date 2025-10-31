import uuid

import streamlit as st


def initialize_sessions():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "active_modal" not in st.session_state:
        st.session_state.active_modal = None

    if "user" not in st.session_state:
        st.session_state.user = None

    if "access_token" not in st.session_state:
        st.session_state.access_token = None

    if "user_email" not in st.session_state:
        st.session_state.user_email = None

    if "user_task_history" not in st.session_state:
        st.session_state.user_task_history = []

    if "user_tasks" not in st.session_state:
        st.session_state.user_tasks = []

    if "pending_registration" not in st.session_state:
        st.session_state.pending_registration = None

    if "user_tasks" not in st.session_state:
        st.session_state.user_tasks = []

    if "today_tasks" not in st.session_state:
        st.session_state.today_tasks = []

    if "weekly_tasks" not in st.session_state:
        st.session_state.weekly_tasks = []

    if "overdue_tasks" not in st.session_state:
        st.session_state.overdue_tasks = []

    if "completed_tasks" not in st.session_state:
        st.session_state.completed_tasks = []

    if "pinned_tasks" not in st.session_state:
        st.session_state.pinned_tasks = []

    if "upcoming_tasks" not in st.session_state:
        st.session_state.upcoming_tasks = []

    if "edit_task" not in st.session_state:
        st.session_state.edit_task = None

    if "list_view" not in st.session_state:
        st.session_state.list_view = True

    if "load_tasks" not in st.session_state:
        st.session_state.load_tasks = True
        
    if "reset_calendar_state" not in st.session_state:
        st.session_state.reset_calendar_state = False

    if "calendar_state" not in st.session_state:
        st.session_state.calendar_state = None
