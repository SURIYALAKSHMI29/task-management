from datetime import date
from typing import List, Optional

from pydantic import EmailStr
from sqlmodel import Field, Index, Relationship, SQLModel

from backend.helpers.enums import RecurrenceType, TaskPriority, TaskStatus


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    password: str
    email: EmailStr = Field(unique=True)
    created_at: date = Field(default_factory=date.today)
    tasks: List["Task"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    __table_args__ = (Index("idx_email", "email"),)


class Task(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    title: str
    description: Optional[str] = Field(default=None)
    deadline: Optional[date] = Field(default=None)
    priority: Optional[TaskPriority] = Field(default=TaskPriority.MEDIUM)
    status: Optional[TaskStatus] = Field(default=TaskStatus.PENDING)
    pinned: Optional[bool] = Field(default=False)
    created_at: date = Field(default_factory=date.today)
    updated_at: date = Field(default_factory=date.today)
    user: "User" = Relationship(back_populates="tasks")
    recurring_task: Optional["RecurringTask"] = Relationship(
        back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    task_history: List["TaskHistory"] = Relationship(
        back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_pinned", "pinned"),
        Index("idx_status", "status"),
    )


class RecurringTask(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    task_id: int = Field(foreign_key="task.id")
    repetitive_type: RecurrenceType
    repeat_until: date | None = Field(default=None)
    task: "Task" = Relationship(back_populates="recurring_task")
    __table_args__ = (Index("idx_recurring_task_task_id", "task_id"),)


class TaskHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    task_id: int = Field(foreign_key="task.id")
    start: date
    end: date
    completed_at: Optional[date] = None
    task: "Task" = Relationship(back_populates="task_history")

    __table_args__ = (Index("idx_history_task_id", "task_id"),)
