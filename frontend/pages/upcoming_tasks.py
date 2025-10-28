from datetime import date, datetime

import streamlit as st
from streamlit_calendar import calendar
from styles.task_css import inject_css
from utils.add_task import show_task
from utils.fetch_tasks import load_and_categorize_tasks

inject_css()

st.header("Upcoming Tasks")

upcoming_tasks = st.session_state.upcoming_tasks

if st.session_state.refresh_user_tasks:
    load_and_categorize_tasks()
    st.session_state.refresh_user_tasks = False

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

custom_css = """
        .fc-event-past {
            opacity: 0.8;
        }
        .fc-event-time {
            display: none;
        }
        .fc-event-title {
            font-weight: 700;
        }
        .fc-toolbar-title {
            font-size: 2rem;
        }
    """


def get_isoformat_date(inp_date):
    if type(inp_date) != date:
        inp_date = datetime.strptime(inp_date, "%Y-%m-%d").date()
    return inp_date.isoformat()


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
                "repetitive": task.get("repetitive"),
                "repeat_until": task.get("repeat_until"),
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
    key=st.session_state["calendar_key"],
    custom_css=custom_css,
)


if state.get("callback") == "eventClick":
    st.session_state["edit_task"] = state["eventClick"]["event"]


if state.get("callback") == "dateClick":
    print("Date clicked")
    date = state["dateClick"]["date"]
    st.session_state["edit_task"] = {
        "title": "",
        "id": None,
        "extendedProps": {
            "description": "",
            "priority": "medium",
            "status": "pending",
            "deadline": date,
            "pinned": False,
        },
    }
    print(st.session_state["edit_task"])


if state.get("callback") == "eventDrop":
    event = state["eventDrop"]["event"]
    task_id = event["id"]
    task_deadline = event["start"].isoformat()

    for task in st.session_state["user_tasks"]:
        if str(task["id"]) == task_id:
            task["deadline"] = task_deadline
            break

if st.session_state["edit_task"]:
    show_task()
