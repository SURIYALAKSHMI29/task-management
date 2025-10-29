import streamlit as st
from pages.calendar_view import calendar_view
from styles.task_css import inject_css
from utils.fetch_tasks import load_and_categorize_tasks

inject_css()

st.header("Upcoming Tasks")

if st.session_state.refresh_user_tasks:
    load_and_categorize_tasks()
    st.session_state.refresh_user_tasks = False

upcoming_tasks = st.session_state.upcoming_tasks

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

print("\nUpcoming tasks:", upcoming_tasks, "\n\n")
calendar_options = {
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth listWeek listMonth",
    },
    "initialView": "dayGridMonth",
    "editable": False,
    "selectable": False,
    "eventDisplay": "list-item",
    "buttonText": {
        "dayGridMonth": "Month",
        "listWeek": "Week List",
        "listMonth": "Month List",
    },
}

calendar_view(upcoming_tasks, calendar_options)
