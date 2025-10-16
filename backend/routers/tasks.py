from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, func, select

from backend.database import get_session
from backend.helpers.auth.auth_utils import get_current_user, verify_current_user
from backend.helpers.enums import RecurrenceType, TaskPriority, TaskStatus
from backend.models import RecurringTask, Task, User
from backend.routers.users import get_user_by_email
from backend.schemas import TaskIn, TaskOut

router = APIRouter()


# used to get task by id
# if not found httpexception is raised, Otherwise task
def get_task_by_id(id: int, session: Session):
    task = session.get(Task, id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not Found")
    return task


# add contents to database
def add_to_db(obj, session: Session):
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


# bind task and its recurrence info
def bind_task_details(task: Task) -> TaskOut:
    task_details = TaskOut.model_validate(task)
    if task.recurring_task:
        task_details.repetitive_type = task.recurring_task.repetitive_type
        task_details.repeat_until = task.recurring_task.repeat_until
    return task_details


def check_pinned_tasks(user_id: int, session: Session):
    stmt = (
        select(Task)
        .where(Task.user_id == user_id, Task.pinned == True)
        .order_by(Task.updated_at)
    )
    pinned_tasks = session.exec(stmt).all()
    if len(pinned_tasks) >= 2:
        for task in pinned_tasks[:-1]:
            task.pinned = False
        session.commit()

    return True


@router.get("/{id}", response_model=TaskOut)
def get_task(
    id: int,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    task = get_task_by_id(id, session)
    if verify_current_user(task.user_id, current_user["user_email"], session):
        return bind_task_details(task)
    return


@router.post("/add-task", response_model=TaskOut)
def add_task(
    task_in: TaskIn,
    repetitive_type: Optional[RecurrenceType] = None,
    repeat_until: Optional[datetime] = None,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_email = current_user["user_email"]
    user = get_user_by_email(user_email, session)

    task_data = task_in.model_dump(exclude_unset=True)
    task_data["user_id"] = user.id

    task_data["pinned"] = task_data["pinned"] and check_pinned_tasks(user.id, session)

    task = add_to_db(Task(**task_data), session)
    if repetitive_type or repeat_until:
        recurring_task = RecurringTask(
            task_id=task.id, repetitive_type=repetitive_type, repeat_until=repeat_until
        )
        task.recurring_task = recurring_task
        add_to_db(recurring_task, session)
    return bind_task_details(task)


@router.patch("/update-task/{id}")
def update_task(
    id: int,
    task_in: TaskIn,
    repetitive_type: Optional[RecurrenceType] = None,
    repeat_until: Optional[datetime] = None,
    remove_recurring: Optional[bool] = False,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_email = current_user["user_email"]
    task = get_task_by_id(id, session)
    if not verify_current_user(task.user_id, user_email, session):
        raise HTTPException(status_code=403, detail="Unauthorized access")

    task_data = task_in.model_dump(exclude_unset=True)
    for key, value in task_data.items():
        if key == "pinned":
            value = task_data["pinned"] and check_pinned_tasks(task.user_id, session)
        setattr(task, key, value)

    if remove_recurring:
        if task.recurring_task:
            session.delete(task.recurring_task)
            task.recurring_task = None

    elif repetitive_type or repeat_until:
        if task.recurring_task:
            if repetitive_type:
                task.recurring_task.repetitive_type = repetitive_type
            if repeat_until:
                task.recurring_task.repeat_until = repeat_until
        else:
            recurring_task = RecurringTask(
                task_id=task.id,
                repetitive_type=repetitive_type,
                repeat_until=repeat_until,
            )
            task.recurring_task = recurring_task
            session.add(recurring_task)

    session.add(task)
    session.commit()
    session.refresh(task)
    return bind_task_details(task)


@router.delete("/delete-task/{id}")
def delete_task(
    id: int,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    task = get_task_by_id(id, session)
    msg = "Access denied"
    if verify_current_user(task.user_id, current_user["user_email"], session):
        session.delete(task)
        session.commit()
        msg = "Task Deleted successfully"
    return {"message": msg}
