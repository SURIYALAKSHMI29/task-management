import time
import uuid

import requests
import streamlit as st


def force_calendar_rerender():
    st.session_state["calendar_key"] = str(uuid.uuid4())
    st.rerun()


def close_task():
    st.session_state["edit_task"] = None
    force_calendar_rerender()


def create_edit_task_schema():
    task = {
        "title": "",
        "id": None,
        "extendedProps": {
            "description": "",
            "priority": "medium",
            "status": "pending",
            "pinned": False,
        },
    }
    st.session_state["edit_task"] = task


@st.dialog("Task Details")
def show_task():
    task = st.session_state["edit_task"]
    if task is None:
        create_edit_task_schema()
    title = st.text_input("Title", value=task.get("title"))
    extended_props = task["extendedProps"]

    description = st.text_area("Description", value=extended_props.get("description"))
    priority = st.selectbox(
        "Priority",
        ["low", "medium", "high"],
        index=["low", "medium", "high"].index(extended_props.get("priority")),
        format_func=lambda priority: priority.capitalize(),
    )
    status = st.selectbox(
        "Status",
        ["pending", "completed"],
        index=["pending", "completed"].index(extended_props.get("status")),
        format_func=lambda status: status.capitalize(),
    )

    checkboxes = st.columns([1, 1, 1])
    with checkboxes[0]:
        repetitive_status = st.checkbox(
            "Repetitive task", value=extended_props.get("repetitive")
        )
    with checkboxes[1]:
        pinned = st.checkbox("Pinned", value=extended_props.get("pinned"))

    if repetitive_status:
        is_recurring = st.selectbox(
            "Repetitive Type",
            ["daily", "weekly", "monthly"],
            index=["daily", "weekly", "monthly"].index(
                extended_props.get("repetitive")
                if extended_props.get("repetitive")
                else "daily"
            ),
            format_func=lambda repetitive: repetitive.capitalize(),
        )
        repeat_until = st.date_input(
            "Repeat until", value=extended_props.get("repeat_until")
        )

    deadline = st.date_input("Deadline", value=extended_props.get("deadline"))

    st.write()
    buttons = st.columns([0.8, 0.9, 1.2, 0.5])
    with buttons[1]:
        cancel = st.button("Cancel")
    with buttons[2]:
        save = st.button("Save Changes")
    if save:
        task = {
            "title": title,
            "description": description,
            "priority": priority,
            "status": status,
            "pinned": pinned,
            "deadline": str(deadline) if deadline else None,
        }
        payload = {"task_in": task}
        if repetitive_status:
            payload["repetitive_type"] = is_recurring
            payload["repeat_until"] = str(repeat_until) if repeat_until else None

        backend_url = st.secrets["backend"]["task_url"]
        header = {"Authorization": f"Bearer {st.session_state.access_token}"}

        if st.session_state["edit_task"].get("id") == None:
            response = requests.post(
                f"{backend_url}/add-task",
                headers=header,
                json=payload,
            )
            if response.status_code != 200:
                st.error(
                    f"Failed to add task: {response.status_code} - {response.text}"
                )
            else:
                st.success("Task added successfully.")
        else:
            response = requests.patch(
                f"{backend_url}/update-task/{st.session_state['edit_task'].get('id')}",
                headers=header,
                json=payload,
            )
            if response.status_code != 200:
                st.error(
                    f"Failed to update task: {response.status_code} - {response.text}"
                )
            st.success("Task updated successfully.")
        st.session_state.refresh_user_tasks = True
        time.sleep(2)
        close_task()

    if cancel:
        close_task()
