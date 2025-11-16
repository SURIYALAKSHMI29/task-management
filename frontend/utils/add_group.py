import time
from datetime import date, datetime

import requests
import streamlit as st


def format_date(date_value):
    if not isinstance(date_value, date):
        return datetime.strptime(date_value, "%Y-%m-%d").date()
    return date_value


def toggle_task_selection(task_id):
    if task_id in st.session_state.selected_task_ids:
        st.session_state.selected_task_ids.discard(task_id)
    else:
        st.session_state.selected_task_ids.add(task_id)


def filter_tasks_by_status(tasks, status):
    """Filter tasks by completion status"""
    if status == "All":
        return tasks
    if status == "Completed":
        return [t for t in tasks if t.get("completed_at")]
    if status == "Upcoming":
        return [
            t
            for t in tasks
            if t.get("status") == "pending"
            and format_date(t.get("end")) >= date.today()
        ]
    if status == "Overdue":
        return [
            t
            for t in tasks
            if not t.get("completed_at") and format_date(t.get("end")) < date.today()
        ]
    return tasks


def filter_tasks_by_scope(tasks, scope):
    """Filter tasks by workspace/personal scope"""
    if scope == "All":
        return tasks
    if scope == "Workspace":
        return [t for t in tasks if t.get("workspace_id")]
    if scope == "Personal":
        return [t for t in tasks if not t.get("workspace_id")]
    return tasks


def filter_tasks_by_timeline(tasks, timeline):
    """Filter tasks by timeline"""
    today = date.today()
    if timeline == "All Time":
        return tasks
    if timeline == "Today":
        return [
            t
            for t in tasks
            if format_date(t.get("start")) == today
            or format_date(t.get("end")) == today
        ]
    if timeline == "This Week":
        from datetime import timedelta

        week_end = today + timedelta(days=7)
        return [
            t
            for t in tasks
            if format_date(t.get("start")) <= week_end
            or format_date(t.get("end")) <= week_end
        ]
    if timeline == "This Month":
        return [
            t
            for t in tasks
            if format_date(t.get("start")).month == today.month
            or format_date(t.get("end")).month == today.month
        ]
    return tasks


def search_tasks(tasks, query):
    """Search tasks by title or description"""
    if not query:
        return tasks
    query_lower = query.lower()
    return [
        t
        for t in tasks
        if query_lower in t.get("title", "").lower()
        or query_lower in t.get("description", "").lower()
    ]


def get_priority_color(priority):
    priority_colors = {
        "high": "#ef4444",  # Red
        "medium": "#f59e0b",  # Orange
        "low": "#10b981",  # Green
    }
    return priority_colors.get(priority.lower() if priority else "medium", "#6b7280")


def get_status_badge(task):
    if task.get("completed_at"):
        return "✓ Completed"
    elif task.get("end") and format_date(task.get("end")) < date.today():
        return "⚠ Overdue"
    return "○ Upcoming"


def get_status_color(task):
    if task.get("completed_at"):
        return "#10b981"
    elif task.get("end") and format_date(task.get("end")) < date.today():
        return "#ef4444"
    else:
        return "#3b82f6"


def render_task_item(task, is_selected):
    """Render a single task item with dark theme styling"""
    priority_color = get_priority_color(task.get("priority", "medium"))
    status_badge = get_status_badge(task)
    status_color = get_status_color(task)

    desc = task.get("description", "No description")
    desc_short = desc[:80] + "..." if len(desc) > 80 else desc

    scope_icon = "🏢" if task.get("workspace_id") else "👤"

    end_date = format_date(task.get("end"))
    date_str = f"Due: {end_date.strftime('%b %d, %Y')}" if end_date else "No due date"

    # Dark theme with selection highlight
    background_color = "#1a1a1a" if is_selected else "#222222"
    border_style = f"1px solid {priority_color}" if is_selected else "1px solid #333333"

    st.markdown(
        f"""
        <div style="
            border-left: 4px solid {priority_color};
            background: {background_color};
            padding: 12px;
            margin: 8px 0;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
            border: {border_style};
        ">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="font-weight: 600; font-size: 14px; color: #f9f9f9; margin-bottom: 4px;">
                        {scope_icon} {task.get('title', 'Untitled')}
                    </div>
                    <div style="font-size: 12px; color: #999999; margin-bottom: 6px;">
                        {desc_short}
                    </div>
                    <div style="display: flex; gap: 12px; align-items: center; font-size: 11px;">
                        <span style="color: {status_color}; font-weight: 500;">
                            {status_badge}
                        </span>
                        <span style="color: #666666;">
                            {date_str}
                        </span>
                        {f'<span style="background: {priority_color}; color: white; padding: 2px 6px; border-radius: 3px;">Priority: {task.get("priority", "medium").title()}</span>' if task.get("priority") else ''}
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.dialog("Create Group", width="large")
def show_add_group_dialog(workspace_id, belongs_to_workspace=False):

    group_name = st.text_input(
        "Group Name", key="group_name", placeholder="ex: Feature Development 1"
    )
    group_desc = st.text_area(
        "Description",
        key="group_desc",
        placeholder="ex: Login module development group",
    )

    checkbox_group = st.columns([1, 1])

    with checkbox_group[0]:
        belongs_to_workspace = st.checkbox(
            "Belongs to Workspace",
            value=belongs_to_workspace,
            key="belongs_to_workspace",
            disabled=belongs_to_workspace,
        )

    with checkbox_group[1]:
        add_tasks = st.checkbox(
            "Show tasks to add to Group", value=False, key="add_tasks"
        )

    if add_tasks:
        st.markdown("---")

        tasks = (
            st.session_state.get("completed_tasks", [])
            + st.session_state.get("upcoming_tasks", [])
            + st.session_state.get("overdue_tasks", [])
        )

        tasks = [task for task in tasks if task.get("group_id") is None]

        count_placeholder = st.empty()

        header_cols = st.columns([3, 1])
        with header_cols[0]:
            st.subheader("Select Tasks")
        with header_cols[1]:
            with count_placeholder.container():
                st.markdown(
                    f"""<div style="text-align: right; padding-top: 8px;">
                    <span style="background: #ef4444; color: white; padding: 4px 12px; 
                    border-radius: 12px; font-size: 14px; font-weight: 600;">
                    {len(st.session_state.selected_task_ids)} Selected
                    </span></div>""",
                    unsafe_allow_html=True,
                )

        filter_cols = st.columns([3, 2, 2, 2])

        with filter_cols[0]:
            search_query = st.text_input(
                "Search tasks",
                key="task_search",
                placeholder="Search by title or description...",
            )

        with filter_cols[1]:
            task_status = st.selectbox(
                "Status",
                ["All", "Completed", "Upcoming", "Overdue"],
                key="task_status",
            )

        with filter_cols[2]:
            task_scope = st.selectbox(
                "Scope",
                ["All", "Workspace", "Personal"],
                key="task_scope",
            )

        with filter_cols[3]:
            task_timeline = st.selectbox(
                "Timeline",
                ["All Time", "Today", "This Week", "This Month"],
                key="task_timeline",
            )

        filtered_tasks = tasks
        filtered_tasks = search_tasks(filtered_tasks, search_query)
        filtered_tasks = filter_tasks_by_status(filtered_tasks, task_status)
        filtered_tasks = filter_tasks_by_scope(filtered_tasks, task_scope)
        filtered_tasks = filter_tasks_by_timeline(filtered_tasks, task_timeline)

        st.caption(f"Showing {len(filtered_tasks)} of {len(tasks)} tasks")

        if filtered_tasks:
            with st.container():
                for task in filtered_tasks:
                    task_col1, task_col2 = st.columns([0.5, 9.5])

                    task_id = task["id"]
                    is_selected = task_id in st.session_state.selected_task_ids

                    with task_col1:
                        checkbox_state = st.checkbox(
                            "select task",
                            value=is_selected,
                            key=f"task_select_{task_id}",
                            label_visibility="collapsed",
                            on_change=lambda tid=task_id: toggle_task_selection(tid),
                        )

                    with task_col2:
                        render_task_item(
                            task, task_id in st.session_state.selected_task_ids
                        )
        else:
            st.info("No tasks found matching the filters.")

    st.markdown("---")

    col1, col2, col3 = st.columns([2, 1, 1])

    with col3:
        if st.button("Cancel", use_container_width=True):
            st.session_state.selected_task_ids = set()
            st.rerun()

    with col2:
        if st.button("Save Group", use_container_width=True, type="primary"):
            if not group_name:
                st.error("Group name cannot be empty")
                return

            payload = {
                "name": group_name,
                "description": group_desc,
                "task_ids": list(st.session_state.selected_task_ids),
                "belongs_to_workspace": belongs_to_workspace,
            }

            if belongs_to_workspace:
                payload["workspace_id"] = workspace_id

            backend_url = st.secrets["backend"]["group_url"]
            headers = {"Authorization": f"Bearer {st.session_state.access_token}"}

            response = requests.post(
                f"{backend_url}/create-group",
                json=payload,
                headers=headers,
            )

            if response.status_code == 200 or response.status_code == 201:
                st.success("Group saved successfully!")
                st.session_state.selected_task_ids = set()
                time.sleep(1)
                st.rerun()
            else:
                st.error(
                    f"Failed to save group: {response.status_code} - {response.text}"
                )
