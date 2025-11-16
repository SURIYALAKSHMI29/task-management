from html import escape

import streamlit as st
from utils.task_util import complete_task, delete_task, edit_task


def get_priority_color(priority):
    """Get color based on priority level"""
    priority_colors = {
        "high": "#ef4444",
        "medium": "#f59e0b",
        "low": "#10b981",
    }
    return priority_colors.get(priority.lower() if priority else "medium", "#6b7280")


def display_task(task, completed, icon, section_name, task_width, button_width):
    deadline = task.get("deadline")
    if not deadline:
        deadline = f"{task.get('start')} - {task.get('end')}"

    unique_key = f"{section_name}-{task['id']}-{task.get('start')}"
    priority_color = get_priority_color(task.get("priority", "medium"))

    workspace_name = task.get("workspace_name")
    group_name = task.get("group_name")
    scope_icon = "🏢" if workspace_name else "👤"

    script = """<div id="task_container_outer"></div>"""
    st.markdown(script, unsafe_allow_html=True)
    container = st.container(key=f"taskCard-{unique_key}")

    with container:
        script = """<div id='task_container_inner'></div>"""
        st.markdown(script, unsafe_allow_html=True)
        cols = st.columns([task_width, button_width])

        with cols[0]:
            badges_html = ""
            if group_name:
                badges_html += f'<span class="task-badge task-badge-group">📁 {escape(group_name)}</span>'
            if workspace_name:
                badges_html += f'<span class="task-badge task-badge-workspace">🏢 {escape(workspace_name)}</span>'

            repetitive_html = ""
            if task.get("repetitive_type"):
                repetitive_html = f'<span class="task-badge task-badge-repeat">🔄 {task["repetitive_type"].capitalize()}</span>'

            status_html = ""
            if completed:
                status_html = f'<div class="task-completed-stamp">✓ Completed on {task.get("completed_at")}</div>'

            st.markdown(
                f"""
                <div class="task-card {('task-completed' if completed else '')}" style="border-left: 4px solid {priority_color};">
                    <div class="task-header">
                        <div class="task-title-row">
                            <span class="task-scope-icon">{scope_icon}</span>
                            <div class="task-title">{task.get("title")}</div>
                        </div>
                        <div class="task-priority-badge" style="background: {priority_color};">
                            {task['priority'].capitalize()}
                        </div>
                    </div>
                    <div class="task-description">{task.get("description")}</div>
                    <div class="task-badges">{badges_html}{repetitive_html}</div>
                    <div class="task-metadata">
                        <span class="task-deadline">📅 {deadline}</span>
                    </div>
                    {status_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

        script = """<div id="button_container_outer"></div>"""
        st.markdown(script, unsafe_allow_html=True)
        with cols[1]:
            if not completed:
                script = """<div id='button_container_inner'></div>"""
                st.markdown(script, unsafe_allow_html=True)
                buttons = st.columns([1, 1, 1])

                with buttons[0]:
                    edited_task = {
                        "id": task.get("id"),
                        "title": task.get("title"),
                        "start": task.get("start"),
                        "end": task.get("end"),
                        "extendedProps": {
                            "description": task.get("description"),
                            "priority": task.get("priority"),
                            "status": task.get("status"),
                            "pinned": task.get("pinned"),
                            "group": task.get("group_id"),
                            "repetitive": task.get("repetitive_type"),
                            "repeat_until": task.get("repeat_until"),
                            "deadline": task.get("deadline"),
                        },
                    }
                    st.button(
                        "✎",
                        type="tertiary",
                        key=f"edit-{unique_key}",
                        on_click=edit_task,
                        args=[edited_task],
                        help="Edit",
                    )

                with buttons[1]:
                    st.button(
                        "✔",
                        type="tertiary",
                        key=f"done-{unique_key}",
                        on_click=complete_task,
                        args=[task],
                        help="Mark as Done",
                    )

                with buttons[2]:
                    st.button(
                        "🗑",
                        type="tertiary",
                        key=f"delete-{unique_key}",
                        on_click=delete_task,
                        args=[task],
                        help="Deleting a repetitive task will remove its entire history",
                    )

    # Inject custom CSS
    st.markdown(
        """<style>
            div[data-testid='stVerticalBlock']:has(div#task_container_inner):not(:has(div#task_container_outer)) {
                padding: 0px;
                background: #222327;
                border-radius: 8px;
                transition: all 0.2s ease;
                margin-bottom: -30px;
            }

            div[data-testid='stVerticalBlock']:has(div#task_container_inner):not(:has(div#task_container_outer)):hover{
                transform: translateX(4px);
                transition: all 0.2s ease;
                background: #2a2a2f;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.4);
            }

            div[data-testid='stVerticalBlock']:has(div#button_container_inner):not(:has(div#button_container_outer)) {
                opacity: 0;
                transition: opacity 0.2s ease;
            }

            div[data-testid='stVerticalBlock']:has(div#task_container_inner):not(:has(div#task_container_outer)):hover 
            div[data-testid='stVerticalBlock']:has(div#button_container_inner):not(:has(div#button_container_outer)){
                opacity: 1;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def display_tasks(
    tasks, completed=False, icon=None, section_name="", task_width=10, button_width=1
):
    for task in tasks:
        display_task(task, completed, icon, section_name, task_width, button_width)
