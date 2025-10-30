import calendar
from datetime import date, datetime, timedelta

import requests
import streamlit as st
from pydantic import EmailStr
from utils.add_task import show_task


def get_user_tasks():
    backend_url = st.secrets["backend"]["user_url"]
    header = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.get(f"{backend_url}/tasks", headers=header)

    if response.status_code == 200:
        st.session_state.user_tasks = response.json()
        print("returning user_tasks: ", st.session_state.user_tasks)
    else:
        st.error(f"Failed to fetch tasks: {response.status_code} - {response.text}")


def get_user_history(user_email: EmailStr):
    payload = {"email": user_email}
    # print("Payload", payload)
    backend_url = st.secrets["backend"]["task_url"]
    header = {"Authorization": f"Bearer {st.session_state.access_token}"}
    # print("Before response", user_email)
    response = requests.post(
        f"{backend_url}/history",
        headers=header,
        json=user_email,
    )

    # print(response.status_code, response.json())

    if response.status_code == 200:
        st.session_state.user_task_history = response.json()
    else:
        st.error(f"Failed to fetch history: {response.status_code} - {response.text}")


def get_task_history(task_id):
    backend_url = st.secrets["backend"]["task_url"]
    header = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.get(f"{backend_url}/history/{task_id}", headers=header)

    if response.status_code == 200:
        st.session_state.user_task_history = response.json()
        # print("returning user_task_history: ", st.session_state.user_task_history)
    else:
        st.error(
            f"Failed to fetch task history: {response.status_code} - {response.text}"
        )


def sort_tasks(tasks, priority):
    return sorted(tasks, key=lambda task: (task.get("end"), priority[task["priority"]]))


def check_task_status(task_id, start, end):
    start = str(start)
    end = str(end)
    for task in st.session_state.completed_tasks:
        if task["id"] == task_id and task["start"] == start and task["end"] == end:
            return False
    return True


def extend_tasks_and_sort(tasks, category, priority_order):
    st.session_state[category].extend(tasks)
    st.session_state[category] = sort_tasks(st.session_state[category], priority_order)

    print("\n category:", category, "\n", st.session_state[category], "\n")


def categorize_tasks(user_tasks, user_task_history):
    print("\n\ntasks came in to categorize", user_tasks, "\n")
    today = date.today()
    nearest_sunday = date.today() + timedelta(days=(6 - today.weekday()) % 6)
    nearest_monday = date.today() - timedelta(days=today.weekday())
    today_tasks = []
    pinned_tasks = []
    weekly_tasks = []
    completed_tasks = []
    overdue_tasks = []
    upcoming_tasks = []
    # print("User tasks (inside the categorize task function)", user_tasks, "\n")

    priority_order = {"high": 1, "medium": 2, "low": 3}

    for task in user_task_history:
        end_date = (
            datetime.strptime(task.get("end"), "%Y-%m-%d").date()
            if type(task.get("end")) == str
            else task.get("end")
        )
        if task.get("completed_at"):
            # print("added to complete tasks\n")
            completed_tasks.append(task)
        elif end_date < today:
            # print("added to overdue tasks\n")
            overdue_tasks.append(task)

    extend_tasks_and_sort(completed_tasks, "completed_tasks", priority_order)
    extend_tasks_and_sort(overdue_tasks, "overdue_tasks", priority_order)

    for task in user_tasks:
        status = task.get("status")
        deadline_str = task.get("deadline")
        deadline = (
            datetime.strptime(deadline_str, "%Y-%m-%d").date()
            if type(deadline_str) == str
            else deadline_str
        )
        pinned = task.get("pinned")
        repetitive_type = task.get("repetitive_type")
        repeat_until_str = task.get("repeat_until")
        repeat_until = (
            datetime.strptime(repeat_until_str, "%Y-%m-%d").date()
            if repeat_until_str
            else None
        )

        if status == "pending":
            if pinned:
                pinned_tasks.append(task)

            if repetitive_type is not None and (
                repeat_until is None or today <= repeat_until
            ):
                if repetitive_type == "daily" and check_task_status(
                    task["id"], today, today
                ):
                    task["deadline"] = today
                    task["start"] = today
                    task["end"] = today
                    today_tasks.append(task)
                    weekly_tasks.append(task)
                    upcoming_tasks.append(task)

                elif repetitive_type == "weekly" and check_task_status(
                    task["id"], nearest_monday, nearest_sunday
                ):
                    task["deadline"] = nearest_sunday
                    task["start"] = nearest_monday
                    task["end"] = nearest_sunday
                    weekly_tasks.append(task)
                    upcoming_tasks.append(task)

                elif repetitive_type == "monthly":
                    last_day = calendar.monthrange(today.year, today.month)[1]
                    last_date = date(today.year, today.month, last_day)
                    last_monday = last_date - timedelta((last_date.weekday() - 0) % 7)
                    task["deadline"] = last_date
                    task["start"] = date(today.year, today.month, 1)
                    task["end"] = last_date

                    if check_task_status(task["id"], task["start"], last_date):
                        upcoming_tasks.append(task)

                        if today >= last_monday:
                            task_copy = task.copy()
                            task_copy["start"] = last_monday
                            weekly_tasks.append(task_copy)
                        if today == last_monday:
                            task_copy = task.copy()
                            task_copy["start"] = today
                            today_tasks.append(task_copy)
            elif deadline and check_task_status(task["id"], deadline, deadline):
                task["start"] = deadline
                task["end"] = deadline
                if deadline == today:
                    today_tasks.append(task)
                if deadline >= today:
                    if deadline <= nearest_sunday:
                        weekly_tasks.append(task)
                    upcoming_tasks.append(task)
                else:
                    overdue_tasks.append(task)

    print("After categorizing,\n")
    extend_tasks_and_sort(today_tasks, "today_tasks", priority_order)
    extend_tasks_and_sort(pinned_tasks, "pinned_tasks", priority_order)
    extend_tasks_and_sort(weekly_tasks, "weekly_tasks", priority_order)
    st.session_state.upcoming_tasks.extend(upcoming_tasks)


def get_str_date(date):
    return str(date) if type(date) == date else date


def remove_task_from_categories(task, categories, remove_all=False):

    # removes a task from given categories
    # If remove_all=True, removes teh entire task and its recurrences (same id)
    # else, removes only the specific task (matching start & end)
    task_start = get_str_date(task.get("start"))
    task_end = get_str_date(task.get("end"))

    print("\n\nTask came to remove:", task)
    for category in categories:
        st.session_state[category] = [
            t
            for t in st.session_state[category]
            if not (
                t.get("id") == task["id"]
                and (
                    remove_all
                    or (
                        get_str_date(t.get("start")) == task_start
                        and get_str_date(t.get("end")) == task_end
                    )
                )
            )
        ]
        print("Removed task from category:", category, "\n", st.session_state[category])


def edit_task(task):
    st.session_state["edit_task"] = task
    show_task()


def complete_task(task):
    start = task.get("start")
    start = (
        (datetime.strptime(start, "%Y-%m-%d").date()) if type(start) == str else start
    )
    end = task.get("end")
    end = datetime.strptime(end, "%Y-%m-%d").date() if type(end) == str else end

    backend_url = st.secrets["backend"]["task_url"]
    header = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.patch(
        f"{backend_url}/complete-task/{task.get('id')}/{start}/{end}", headers=header
    )

    if response.status_code == 200:
        st.cache_data.clear()
        task["status"] = "completed"
        task["completed_at"] = date.today()
        categories = [
            "today_tasks",
            "pinned_tasks",
            "weekly_tasks",
            "upcoming_tasks",
            "overdue_tasks",
        ]
        remove_task_from_categories(task, categories)
        st.session_state.completed_tasks.append(task)
    else:
        st.error(f"Failed to fetch tasks: {response.status_code} - {response.text}")


def delete_task(task):
    backend_url = st.secrets["backend"]["task_url"]
    header = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.delete(
        f"{backend_url}/delete-task/{task.get('id')}", headers=header
    )

    if response.status_code == 200:
        st.cache_data.clear()
        categories = [
            "today_tasks",
            "weekly_tasks",
            "pinned_tasks",
            "overdue_tasks",
            "upcoming_tasks",
            "completed_tasks",
        ]
        # task and its recurrences
        remove_task_from_categories(task, categories, remove_all=True)
        print("Task deleted successfully!")
    else:
        print(f"Failed to fetch tasks: {response.status_code} - {response.text}")
