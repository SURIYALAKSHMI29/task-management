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
            "group": None,
        },
    }
    st.session_state["edit_task"] = task
    return task


@st.dialog("Task Details", width="medium")
def show_task():
    st.markdown(
        """
        <style>
            .stTextInput, .stTextArea, .stSelectbox, .stDateInput {
                margin-bottom: 0.4rem !important;
            }
            .section-title {
                font-weight: 600;
                font-size: 2rem;
                margin-top: 0.6rem;
                margin-bottom: 0.3rem;
                display: flex;
                align-items: center;
                gap: 0.3rem;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    task = st.session_state["edit_task"]
    if task is None:
        task = create_edit_task_schema()
    show_status = task.get("id") is not None
    extended_props = task["extendedProps"]

    st.markdown(
        '<p class="section-title">Basic Info</p>',
        unsafe_allow_html=True,
    )
    title = st.text_input("Title", value=task.get("title"))
    description = st.text_area("Description", value=extended_props.get("description"))

    priority = st.selectbox(
        "Priority",
        ["low", "medium", "high"],
        index=["low", "medium", "high"].index(extended_props.get("priority")),
        format_func=lambda priority: priority.capitalize(),
    )
    if not show_status:
        status = "pending"
    else:
        status = st.selectbox(
            "Status",
            ["pending", "completed"],
            index=["pending", "completed"].index(extended_props.get("status")),
            format_func=lambda status: status.capitalize(),
        )
    st.divider()

    st.markdown(
        '<p class="section-title">Group</p>',
        unsafe_allow_html=True,
    )
    st.caption("Group tasks for better organization — personal or workspace")

    group_cols = st.columns([1.2, 0.9, 0.7])

    group_options = [{"name": "None", "id": None}] + [
        {"name": group.name, "id": group.id}
        for group in st.session_state["user_groups"]
    ]
    group_names = [g["name"] for g in group_options]
    current_group_id = extended_props.get("group")
    current_group_name = "None"
    for g in group_options:
        if g["id"] == current_group_id:
            current_group_name = g["name"]
            break

    if "new_group_input" not in st.session_state:
        st.session_state.new_group_input = ""

    with group_cols[0]:
        selected_group_name = st.selectbox(
            "Group",
            group_names,
            index=(
                group_names.index(current_group_name)
                if current_group_name in group_names
                else 0
            ),
            disabled=bool(st.session_state.new_group_input),
        )
        selected_group_id = None
        for g in group_options:
            if g["name"] == selected_group_name:
                selected_group_id = g["id"]
                break

    with group_cols[1]:
        new_group = st.text_input(
            "New Group? ", value=st.session_state.new_group_input, key="new_group"
        )
        if new_group != st.session_state.new_group_input:
            st.session_state.new_group_input = new_group
        # if selected_group_name != "None" and st.session_state.new_group_input:
        #     st.session_state.new_group_input = ""
        #     st.rerun()

    workspace = None
    with group_cols[2]:
        st.markdown(" ")
        workspace = st.checkbox(
            "Workspace?",
            value=False,
            key="belongs_to_workspace",
            help="Make group visible to workspace members",
        )

    st.divider()

    st.markdown(
        '<p class="section-title">Options</p>',
        unsafe_allow_html=True,
    )

    checkboxes = st.columns([1, 1, 1])
    with checkboxes[0]:
        is_recurring = extended_props.get("repetitive") is not None
        repetitive_status = st.checkbox(
            "Repetitive task",
            value=extended_props.get("repetitive"),
            disabled=is_recurring,
            help="Automatically repeat this task",
        )
    with checkboxes[1]:
        pinned = st.checkbox(
            "Pinned",
            value=extended_props.get("pinned"),
            help="Keep task on top for easy access",
        )

    if repetitive_status:
        if is_recurring:
            # ensure that remove recurrence is shown only if task is recurring
            with checkboxes[2]:
                remove_recurring = st.checkbox(
                    "Remove Recurrence", value=False, help="Stop recurring"
                )
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
    st.divider()

    st.markdown(
        '<p class="section-title">Schedule</p>',
        unsafe_allow_html=True,
    )
    deadline = st.date_input(
        "Deadline", value=extended_props.get("deadline"), help="Task deadline"
    )

    if not st.session_state.get("user"):
        st.warning("Log in to add tasks")
    buttons = st.columns([1.1, 1, 1.2, 0.6])
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

        if new_group:
            payload = {"task_in": task, "new_group": new_group, "workspace": workspace}
        elif selected_group_id is not None:
            task["group_id"] = selected_group_id
            payload = {"task_in": task}
        else:
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
    st.session_state.reset_calendar_state = True
