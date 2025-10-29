from datetime import date as date_module
from datetime import datetime

import streamlit as st
from streamlit_calendar import calendar
from utils.add_task import show_task


def calendar_view(tasks, calendar_options, include_end=False):
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
        if type(inp_date) != date_module:
            inp_date = datetime.strptime(inp_date, "%Y-%m-%d").date()
        return inp_date.isoformat()

    events = []
    for task in tasks:
        start = get_isoformat_date(task["end"])
        end = get_isoformat_date(task["end"])
        if include_end:
            start = get_isoformat_date(task["start"])

        events.append(
            {
                "id": str(task["id"]),
                "allday": (task["repetitive_type"] == "daily"),
                "title": task["title"],
                "start": start,
                "end": end,
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
                    "deadline": end,
                    "repetitive": task.get("repetitive"),
                    "repeat_until": task.get("repeat_until"),
                },
                "tooltip": task.get("description") or task["title"],
            }
        )
        # print(task["title"], task["repetitive_type"])

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
