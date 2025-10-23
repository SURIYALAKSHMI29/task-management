import calendar
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import joinedload
from sqlmodel import Session, select

from backend.database import engine, get_session
from backend.helpers.auth.auth_utils import get_current_user, verify_current_user
from backend.helpers.enums import RecurrenceType, TaskPriority, TaskStatus
from backend.models import RecurringTask, Task, TaskHistory
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


def scheduled_task_updates():
    with Session(engine) as session:
        stmt = (
            select(Task)
            .join(RecurringTask, Task.id == RecurringTask.task_id, isouter=True)
            .where(
                ((Task.deadline.is_not(None)) & (Task.deadline <= date.today()))
                | (
                    (RecurringTask.repetitive_type.is_not(None))
                    & (
                        (RecurringTask.repeat_until.is_(None))
                        | (RecurringTask.repeat_until >= date.today())
                    )
                ),
                Task.status == TaskStatus.PENDING,
            )
            .options(joinedload(Task.recurring_task))
        )

        tasks = session.exec(stmt).all()
        print(tasks)
        for task in tasks:
            print("\nUpdating for ", task)
            print(task.recurring_task, task.title)
            updateTaskHistory(task, TaskStatus.PENDING, session)


# creates appropriate task history based on its recurring type
def updateTaskHistory(task: Task, status: TaskStatus, session: Session):
    if task.deadline is None and task.recurring_task is None:
        return
    start = task.deadline
    end = task.deadline
    today = date.today()

    # finding appropriate start and end dates
    if task.recurring_task is not None:
        recurring_task = session.get(RecurringTask, task.recurring_task.id)
        if recurring_task.repetitive_type == RecurrenceType.WEEKLY:
            nearest_monday = date.today() - timedelta(days=today.weekday())
            start = nearest_monday
            nearest_sunday = date.today() + timedelta(
                days=(6 - date.today().weekday()) % 7
            )
            end = nearest_sunday
        elif recurring_task.repetitive_type == RecurrenceType.MONTHLY:
            start = date(today.year, today.month, 1)
            _, num_days = calendar.monthrange(today.year, today.month)
            end = date(today.year, today.month, num_days)
        elif recurring_task.repetitive_type == RecurrenceType.DAILY:
            start = today
            end = today

    # find if task history is found with existing data
    task_history = session.exec(
        select(TaskHistory).where(
            TaskHistory.task_id == task.id,
            TaskHistory.start == start,
            TaskHistory.end == end,
        )
    ).first()

    if task_history:
        task_history.completed_at = today if status == TaskStatus.COMPLETED else None
        session.commit()
    else:
        if status == TaskStatus.COMPLETED:
            task_history = TaskHistory(
                task_id=task.id, start=start, end=end, completed_at=today
            )
        else:
            task_history = TaskHistory(task_id=task.id, start=start, end=end)
        add_to_db(task_history, session)

    session.refresh(task)  # updates the in-place relationships
    return


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
    repeat_until: Optional[date] = None,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_email = current_user["user_email"]
    user = get_user_by_email(user_email, session)

    task_data = task_in.model_dump(exclude_unset=True)
    task_data["user_id"] = user.id

    task_data["pinned"] = task_data.get("pinned", False) and check_pinned_tasks(
        user.id, session
    )

    task = add_to_db(Task(**task_data), session)
    if repetitive_type or repeat_until:
        recurring_task = RecurringTask(
            task_id=task.id, repetitive_type=repetitive_type, repeat_until=repeat_until
        )
        add_to_db(recurring_task, session)
        session.refresh(task)  # updates the in-place relationships

    return bind_task_details(task)


@router.patch("/update-task/{id}")
def update_task(
    id: int,
    task_in: TaskIn,
    repetitive_type: Optional[RecurrenceType] = None,
    repeat_until: Optional[date] = None,
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
            task.updated_at = date.today()
        if key == "status" and value:
            value = TaskStatus(value)
        if task.recurring_task and key == "status" and value == TaskStatus.COMPLETED:
            updateTaskHistory(task, value, session)
            continue
        print(key, value)
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

    task = add_to_db(task, session)
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


@router.get("/history/{id}", response_model=list[TaskHistory])
def get_history(
    id: int,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    task = get_task_by_id(id, session)
    if verify_current_user(task.user_id, current_user["user_email"], session):
        return task.task_history


# @router.get("/recurring_tasks")
# def recurring_tasks(session: Session = Depends(get_session)):
#     return session.exec(select(RecurringTask)).all()
