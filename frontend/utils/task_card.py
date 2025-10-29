import streamlit as st
from utils.task_util import complete_task, delete_task, edit_task


def display_task(task, completed, icon, section_name, task_width, button_width):
    deadline = task.get("deadline")
    # print(type(deadline), deadline, "condition status", (deadline is None))
    if not deadline:
        # print(task.get("start"), task.get("end"), task)
        deadline = f"{task.get('start')} - {task.get('end')}"

    unique_key = f"{section_name}-{task['id']}-{task.get('start')}"

    script = """<div id="task_container_outer"></div>"""
    st.markdown(script, unsafe_allow_html=True)
    container = st.container(key=f"taskCard-{unique_key}")

    with container:
        script = """<div id='task_container_inner'></div>"""
        st.markdown(script, unsafe_allow_html=True)
        cols = st.columns([task_width, button_width])
        with cols[0]:
            repetitive_html = ""
            if task.get("repetitive_type"):
                repetitive_html = f'<div class="taskRepetitive">Repetitive: {task["repetitive_type"].capitalize()}</div>'

            st.markdown(
                f"""
                <div class="taskContainer">
                    <span class="taskIcon">{icon if icon else ''}</span>
                    <div class="taskTitle {"icon" if icon else ""}">{task.get('title')}</div>
                    <div class="taskDescription">{task['description']}</div>
                    <div class="taskInfo">
                        <div class="taskDeadline">Deadline: {deadline}</div>
                        <div class="taskPriority">Priority: {task['priority'].capitalize()}</div>
                        {repetitive_html}</div>
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
                        args=[task],
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
                        help="Delete",
                    )
            else:
                st.markdown(
                    f"""
                    <div class="completedDate">
                        {task.get('completed_at')}
                        <span style="font-size:1.2em; color: darkgreen">✓</span>
                    </div>""",
                    unsafe_allow_html=True,
                )

    st.markdown(
        """<style>
            div[data-testid='stVerticalBlock']:has(div#task_container_inner):not(:has(div#task_container_outer)) {
                padding: 0px 10px;
                background-color: #222;
                border-radius: 10px;
                margin-bottom: -30px;
            }

            div[data-testid='stVerticalBlock']:has(div#task_container_inner):not(:has(div#task_container_outer)):hover{
                background-color: #333;
                transform: translateX(8px);
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                transition: 0.3s;
                cursor: pointer;
            }

            div[data-testid='stVerticalBlock']:has(div#button_container_inner):not(:has(div#button_container_outer)) {
                opacity: 0;
            }

            div[data-testid='stVerticalBlock']:has(div#task_container_inner):not(:has(div#task_container_outer)):hover div[data-testid='stVerticalBlock']:has(div#button_container_inner):not(:has(div#button_container_outer)){
                opacity: 1;
                background-color: #333;
                transition: 0.3s;
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
