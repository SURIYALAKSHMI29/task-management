import time
import uuid

import requests
import streamlit as st


def close_task():
    st.session_state["edit_task"] = None
    st.rerun()
    # dialog can be closed programmatically by rerun alone
    # inherits behaviour from st.fragment -> user interactions reruns the dialog only


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
    return task


@st.dialog("Task Details", width="medium")
def show_task():
    task = st.session_state["edit_task"]
    if task is None:
        task = create_edit_task_schema()
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
        is_recurring = extended_props.get("repetitive") is not None
        repetitive_status = st.checkbox(
            "Repetitive task",
            value=extended_props.get("repetitive"),
            disabled=is_recurring,
        )
    with checkboxes[1]:
        pinned = st.checkbox("Pinned", value=extended_props.get("pinned"))

    if repetitive_status:
        if is_recurring:
            # ensure that remove recurrence is shown only if task is recurring
            with checkboxes[2]:
                remove_recurring = st.checkbox("Remove Recurrence", value=False)
        repetitive_type = st.selectbox(
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

    if not st.session_state.get("user"):
        st.warning("Log in to add tasks")
    buttons = st.columns([0.8, 0.9, 1.2, 0.5])
    with buttons[1]:
        cancel = st.button("Cancel")
    with buttons[2]:
        save = st.button("Save Changes", disabled=st.session_state.get("user") is None)
    if save:
        # local import to avoid circular dependency
        # show_task is called from task_util
        from utils.task_util import categorize_tasks, remove_task_from_categories

        task = {
            "title": title,
            "description": description,
            "priority": priority,
            "status": status,
            "pinned": pinned,
            "deadline": str(deadline) if deadline else None,
        }
        payload = {"task_in": task}
        if is_recurring:
            payload["remove_recurring"] = remove_recurring
        if repetitive_status:
            payload["repetitive_type"] = repetitive_type
            payload["repeat_until"] = str(repeat_until) if repeat_until else None

        print(payload)

        backend_url = st.secrets["backend"]["task_url"]
        header = {"Authorization": f"Bearer {st.session_state.access_token}"}

        if st.session_state["edit_task"].get("id") == None:
            response = requests.post(
                f"{backend_url}/add-task",
                headers=header,
                json=payload,
            )
            if response.status_code == 200:
                new_task = response.json()
                categorize_tasks([new_task], [])
                st.success("Task added successfully.")
            else:
                st.error(
                    f"Failed to add task: {response.status_code} - {response.text}"
                )
        else:
            response = requests.patch(
                f"{backend_url}/update-task/{st.session_state['edit_task'].get('id')}",
                headers=header,
                json=payload,
            )
            if response.status_code == 200:
                updated_task = response.json()
                categories = [
                    "today_tasks",
                    "weekly_tasks",
                    "pinned_tasks",
                    "overdue_tasks",
                    "upcoming_tasks",
                ]
                remove_task_from_categories(st.session_state["edit_task"], categories)
                categorize_tasks([updated_task], [])

            else:
                st.error(
                    f"Failed to update task: {response.status_code} - {response.text}"
                )
            st.success("Task updated successfully.")
        time.sleep(2)
        close_task()

    if cancel:
        close_task()
