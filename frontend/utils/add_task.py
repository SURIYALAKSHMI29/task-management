import time

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
                margin-bottom: 0.5rem !important;
            }
            .section-title {
                font-weight: 600;
                font-size: 0.95rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: #999;
                margin-top: 1.2rem;
                margin-bottom: 0.8rem;
                border-bottom: 1px solid #e0e0e0;
                padding-bottom: 0.3rem;
            }
            .section-caption {
                font-size: 0.85rem;
                color: #777;
                margin-bottom: 0.8rem;
                margin-top: -0.5rem;
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
        '<div class="section-title">Basic Information</div>', unsafe_allow_html=True
    )

    title = st.text_input(
        "Task Title", value=task.get("title"), placeholder="Enter task title..."
    )

    description = st.text_area(
        "Description",
        value=extended_props.get("description"),
        placeholder="Add task description...",
        height=100,
    )

    # priority and status
    basic_cols = st.columns(2)
    with basic_cols[0]:
        priority = st.selectbox(
            "Priority",
            ["low", "medium", "high"],
            index=["low", "medium", "high"].index(extended_props.get("priority")),
            format_func=lambda x: x.capitalize(),
        )

    with basic_cols[1]:
        if not show_status:
            status = "pending"
            st.selectbox(
                "Status",
                ["pending"],
                index=0,
                disabled=True,
                help="Status can be updated after task creation",
            )
        else:
            status = st.selectbox(
                "Status",
                ["pending", "completed"],
                index=["pending", "completed"].index(extended_props.get("status")),
                format_func=lambda x: x.capitalize(),
            )

    # group
    st.markdown('<div class="section-title">Group Tasks</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-caption">Assign tasks to groups for better organization</div>',
        unsafe_allow_html=True,
    )

    group_options = [{"name": "None", "id": None}] + [
        {"name": group["name"], "id": group["id"]}
        for group in st.session_state["user_groups"]
    ]
    group_names = [g["name"] for g in group_options]
    current_group_id = extended_props.get("group")

    if current_group_id is not None:
        try:
            current_group_id = int(current_group_id)
        except ValueError:
            pass
    current_group_name = "None"
    for g in group_options:
        if g["id"] == current_group_id:
            current_group_name = g["name"]
            break

    if "new_group_input" not in st.session_state:
        st.session_state.new_group_input = ""

    group_row = st.columns([2, 2, 1])

    with group_row[0]:
        selected_group_name = st.selectbox(
            "Select Existing Group",
            group_names,
            index=(
                group_names.index(current_group_name)
                if current_group_name in group_names
                else 0
            ),
            disabled=bool(st.session_state.new_group_input),
            help="Choose from existing groups",
        )
        selected_group_id = None
        for g in group_options:
            if g["name"] == selected_group_name:
                selected_group_id = g["id"]
                break

    with group_row[1]:
        new_group = st.text_input(
            "Or Create New Group",
            value=st.session_state.new_group_input,
            key="new_group",
            placeholder="Enter new group name...",
        )
        if new_group != st.session_state.new_group_input:
            st.session_state.new_group_input = new_group

    workspace = None
    with group_row[2]:
        st.markdown('<div style="height: 1.8rem;"></div>', unsafe_allow_html=True)
        workspace = st.checkbox(
            "Workspace",
            value=False,
            key="belongs_to_workspace",
            help="Make this group visible to all workspace members",
        )

    # options
    st.markdown('<div class="section-title">Task Options</div>', unsafe_allow_html=True)

    options_row = st.columns([1, 1, 1])

    with options_row[0]:
        is_recurring = extended_props.get("repetitive") is not None
        repetitive_status = st.checkbox(
            "Recurring Task",
            value=extended_props.get("repetitive"),
            disabled=is_recurring,
            help="Automatically repeat this task",
        )

    with options_row[1]:
        pinned = st.checkbox(
            "Pin Task",
            value=extended_props.get("pinned"),
            help="Keep this task pinned at the top",
        )

    if repetitive_status and is_recurring:
        with options_row[2]:
            remove_recurring = st.checkbox(
                "Stop Recurring",
                value=False,
                help="Remove recurring pattern from this task",
            )

    # recurring options (if enabled)
    if repetitive_status:
        st.markdown('<div style="margin-top: 0.8rem;"></div>', unsafe_allow_html=True)
        recur_cols = st.columns(2)

        with recur_cols[0]:
            repetitive_type = st.selectbox(
                "Recurrence Pattern",
                ["daily", "weekly", "monthly"],
                index=["daily", "weekly", "monthly"].index(
                    extended_props.get("repetitive")
                    if extended_props.get("repetitive")
                    else "daily"
                ),
                format_func=lambda x: x.capitalize(),
            )

        with recur_cols[1]:
            repeat_until = st.date_input(
                "Repeat Until",
                value=extended_props.get("repeat_until"),
                help="End date for recurring tasks",
            )

    st.markdown('<div class="section-title">Schedule</div>', unsafe_allow_html=True)

    schedule_cols = st.columns([2, 3])
    with schedule_cols[0]:
        deadline = st.date_input(
            "Deadline",
            value=extended_props.get("deadline"),
            help="Set a deadline for this task",
        )

    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)

    if not st.session_state.get("user"):
        st.warning("Please log in to save tasks")

    button_cols = st.columns([3, 1, 1.2])

    with button_cols[1]:
        cancel = st.button("Cancel", use_container_width=True)

    with button_cols[2]:
        save = st.button(
            "Save Task" if not show_status else "Update Task",
            disabled=st.session_state.get("user") is None,
            type="primary",
            use_container_width=True,
        )

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
                st.success("Task added successfully")
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
                st.success("Task updated successfully")
            else:
                st.error(
                    f"Failed to update task: {response.status_code} - {response.text}"
                )

        time.sleep(2)
        close_task()

    if cancel:
        close_task()

    st.session_state.reset_calendar_state = True
