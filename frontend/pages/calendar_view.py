from datetime import date as date_module
from datetime import datetime, timedelta

import streamlit as st
from streamlit_calendar import calendar
from utils.add_task import show_task


def calendar_view(tasks, calendar_options, include_end=False):
    custom_css = """
            .fc-event-past {
                background-color: #990000 !important;
                border-color: #880000 !important;
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
            .fc-event, .fc-daygrid-day {
                cursor: pointer;
            }
        """

    st.session_state["edit_task"] = None

    def get_date(inp_date):
        if type(inp_date) != date_module:
            inp_date = datetime.strptime(inp_date, "%Y-%m-%d").date()
        return inp_date

    events = []
    for task in tasks:
        start = get_date(task["end"]).isoformat()
        end = (get_date(task["end"]) + timedelta(days=1)).isoformat()
        deadline = start
        if include_end:
            start = get_date(task["start"]).isoformat()

        events.append(
            {
                "id": str(task["id"]),
                "allday": (task["repetitive_type"] == "daily"),
                "title": task["title"],
                "start": start,
                "end": end,
                "color": (
                    "#ef4444"
                    if task.get("priority") == "high"
                    else ("#f59e0b" if task.get("priority") == "medium" else "#10b981")
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
                "tooltip": task.get("description") or task["title"],
            }
        )

    state = calendar(events=events, options=calendar_options, custom_css=custom_css)
    print(state)
    if st.session_state.reset_calendar_state:
        state = st.session_state.calendar_state
        st.session_state.reset_calendar_state = False
    st.session_state.calendar_state = state

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

    if st.session_state["edit_task"]:
        show_task()
