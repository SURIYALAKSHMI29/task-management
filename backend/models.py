from datetime import datetime
from typing import List, Optional

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel
from helpers.enums import RecurrenceType, TaskPriority, TaskStatus

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    password: str
    email: EmailStr = Field(unique=True)
    created_at: datetime = Field(default_factory=datetime.now)
    tasks: List["Task"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

class Task(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    title: str
    description: str
    deadline: Optional[datetime] = Field(default=None)
    priority: Optional[TaskPriority] = Field(default=TaskPriority.MEDIUM)
    status: Optional[TaskStatus] = Field(default=TaskStatus.PENDING)
    pinned: Optional[bool] = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    user: "User" = Relationship(back_populates="tasks")
    recurring_task: Optional["RecurringTask"] = Relationship(
        back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class RecurringTask(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    task_id: int = Field(foreign_key="task.id")
    repetitive_type: RecurrenceType | None = Field(default=RecurrenceType.MONTHLY)
    repeat_until: datetime | None = Field(default=None)
    task: "Task" = Relationship(back_populates="recurring_task")
