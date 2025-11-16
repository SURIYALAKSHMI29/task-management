from datetime import date
from typing import List, Optional

from backend.helpers.enums import RecurrenceType, TaskPriority, TaskStatus
from pydantic import EmailStr
from sqlmodel import Field, Index, Relationship, SQLModel


class UserWorkspaceLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    workspace_id: int = Field(foreign_key="workspace.id", primary_key=True)


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    password: str
    email: EmailStr = Field(unique=True)
    created_at: date = Field(default_factory=date.today)
    tasks: List["Task"] = Relationship(
        back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    groups: List["Group"] = Relationship(
        back_populates="creator",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    workspaces: List["Workspace"] = Relationship(
        back_populates="users", link_model=UserWorkspaceLink
    )
    __table_args__ = (Index("idx_email", "email"),)


class Workspace(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    created_at: date = Field(default_factory=date.today)
    created_by: int = Field(foreign_key="user.id")
    users: List["User"] = Relationship(
        back_populates="workspaces", link_model=UserWorkspaceLink
    )
    groups: List["Group"] = Relationship(
        back_populates="workspace",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    __table_args__ = (Index("idx_workspace_created", "created_by"),)


class Group(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: Optional[str] = Field(default=None)
    workspace_id: Optional[int] = Field(default=None, foreign_key="workspace.id")
    workspace: "Workspace" = Relationship(back_populates="groups")
    tasks: List["Task"] = Relationship(
        back_populates="group", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    creator: Optional["User"] = Relationship(back_populates="groups")
    created_by: int = Field(foreign_key="user.id")
    created_at: date = Field(default_factory=date.today)

    __table_args__ = (
        Index("idx_group_created", "created_by"),
        Index("idx_workspace_id", "workspace_id"),
    )


class Task(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, default=None)
    user_id: int = Field(foreign_key="user.id")
    group_id: Optional[int] = Field(default=None, foreign_key="group.id")
    title: str
    description: Optional[str] = Field(default=None)
    deadline: Optional[date] = Field(default=None)
    priority: Optional[TaskPriority] = Field(default=TaskPriority.MEDIUM)
    status: Optional[TaskStatus] = Field(default=TaskStatus.PENDING)
    pinned: Optional[bool] = Field(default=False)
    created_at: date = Field(default_factory=date.today)
    updated_at: date = Field(default_factory=date.today)

    user: "User" = Relationship(back_populates="tasks")
    group: "Group" = Relationship(back_populates="tasks")
    recurring_task: Optional["RecurringTask"] = Relationship(
        back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )
    task_history: List["TaskHistory"] = Relationship(
        back_populates="task", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )

    __table_args__ = (
        Index("idx_user_id", "user_id"),
        Index("idx_user_status", "user_id", "status"),
        Index("idx_user_pinned", "user_id", "pinned"),
        Index("idx_group_id", "group_id"),
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
    completed_by: Optional[int] = None
    task: "Task" = Relationship(back_populates="task_history")

    __table_args__ = (Index("idx_history_task_id", "task_id"),)
