import time
from datetime import date, datetime

import streamlit as st
from streamlit_calendar import calendar
from streamlit_modal import Modal

from frontend.styles.task_css import inject_css

inject_css()

st.header("Upcoming Tasks")

if "edit_task_modal_open" not in st.session_state:
    st.session_state.edit_task_modal_open = False

upcoming_tasks = st.session_state.upcoming_tasks

task_modal = Modal("Task Details", key="task-modal", padding=20, max_width=900)


st.markdown(
    """
    <style>
        div[data-modal-container="true"] > div > div {
            width: 900px !important;      
            min-width: 700px !important;   
            max-width: 90vw !important;  
        }
        div[data-modal-container="true"] > div > div >div{
            min-width: 700px !important;      
        }

    </style>
    """,
    unsafe_allow_html=True,
)


def close_modal(task_modal: Modal):
    st.session_state["edit_task_modal_open"] = False
    task_modal.close()
    st.rerun()


def get_isoformat_date(inp_date):
    if type(inp_date) != date:
        inp_date = datetime.strptime(inp_date, "%Y-%m-%d").date()
    return inp_date.isoformat()


def show_task(task_modal: Modal):
    task = st.session_state["edit_task"]
    title = st.text_input("Title", value=task.get("title"))
    extended_props = task["extendedProps"]

    description = st.text_area("Description", value=extended_props.get("description"))
    priority = st.selectbox(
        "Priority",
        ["low", "medium", "high"],
        index=["low", "medium", "high"].index(extended_props.get("priority")),
    )
    status = st.selectbox(
        "Status",
        ["pending", "completed"],
        index=["pending", "completed"].index(extended_props.get("status")),
    )

    pinned = st.checkbox("Pinned", value=extended_props.get("pinned"))

    deadline = st.date_input("Deadline", value=extended_props.get("deadline"))

    if st.button("Save Changes"):
        if st.session_state["edit_task"].get("id") == None:
            task = {
                "title": title,
                "description": description,
                "priority": priority,
                "status": status,
                "pinned": pinned,
                "deadline": deadline,
            }
            st.session_state["user_tasks"].append(task)
            print("\nAfter adding task:", st.session_state["user_tasks"], "\n")
            st.success("Task added successfully.")
        else:
            for task in st.session_state["user_tasks"]:
                if str(task["id"]) == st.session_state["edit_task"].get("id"):
                    task["title"] = title
                    task["description"] = description
                    task["priority"] = priority
                    task["status"] = status
                    task["pinned"] = pinned
                    task["deadline"] = deadline
                    break
            st.success("Task updated successfully.")
        time.sleep(2)
        close_modal(task_modal)
    if st.button("Cancel"):
        close_modal(task_modal)


events = []
print("\nUpcoming tasks:", upcoming_tasks, "\n\n")
for task in upcoming_tasks:
    deadline = get_isoformat_date(task["end"])

    events.append(
        {
            "id": str(task["id"]),
            "allday": (task["repetitive_type"] == "daily"),
            "title": task["title"],
            "start": deadline,
            "color": (
                "#990000"
                if task.get("priority") == "high"
                else ("#4B7DC9" if task.get("priority") == "medium" else "#AAADAF")
            ),
            "extendedProps": {
                "description": task.get("description", ""),
                "priority": task.get("priority"),
                "status": task.get("status"),
                "pinned": task.get("pinned"),
                "deadline": deadline,
            },
        }
    )
    print(task["title"], task["repetitive_type"])

calendar_options = {
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth listWeek listMonth",
    },
    "initialView": "dayGridMonth",
    "editable": True,
    "selectable": False,
    "eventDisplay": "list-item",
    "buttonText": {
        "dayGridMonth": "Month",
        "listWeek": "Week List",
        "listMonth": "Month List",
    },
}

state = calendar(
    events=events,
    options=calendar_options,
    key="tasks_calendar",
)

if state.get("callback") == "eventClick":
    print("Event clicked")
    st.session_state["edit_task"] = state["eventClick"]["event"]
    print(st.session_state["edit_task"])
    st.session_state["edit_task_modal_open"] = True
    task_modal.open()

if state.get("callback") == "dateClick":
    print("Date clicked")
    st.session_state["edit_task_modal_open"] = True
    date = state["dateClick"]["date"]
    st.session_state["edit_task"] = {
        "title": "",
        "deadline": date,
        "id": None,
        "extendedProps": {
            "description": "",
            "priority": "medium",
            "status": "pending",
            "pinned": False,
        },
    }
    print(st.session_state["edit_task"])
    task_modal.open()

if state.get("callback") == "eventDrop":
    event = state["eventDrop"]["event"]
    task_id = event["id"]
    task_deadline = event["start"].isoformat()

    for task in st.session_state["user_tasks"]:
        if str(task["id"]) == task_id:
            task["deadline"] = task_deadline
            break


if st.session_state.get("edit_task_modal_open"):
    if task_modal.is_open():
        with task_modal.container():
            show_task(task_modal)
