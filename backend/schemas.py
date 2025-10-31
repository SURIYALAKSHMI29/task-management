from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr

from backend.helpers.enums import RecurrenceType, TaskPriority, TaskStatus
from backend.models import Workspace


class UserIn(BaseModel):
    name: str
    password: str
    email: EmailStr
    workspaces: List[str] = []


class BaseUserOut(BaseModel):
    name: str
    email: EmailStr


class TaskIn(BaseModel):
    user_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    deadline: Optional[date] = None
    status: Optional[TaskStatus] = TaskStatus.PENDING
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    pinned: Optional[bool] = False


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    deadline: date | None
    priority: TaskPriority
    status: TaskStatus
    pinned: bool
    repetitive_type: Optional[RecurrenceType] = None
    repeat_until: Optional[date] = None
    model_config = {"from_attributes": True}  # allows reading from ORM/SQLModel objects


class GroupOut(BaseModel):
    id: int
    name: str
    tasks: List[TaskOut] = []
    created_by: int
    model_config = {"from_attributes": True}


class WorkspaceOut(BaseModel):
    id: int
    name: str
    groups: List[GroupOut] = []
    created_by: int
    model_config = {"from_attributes": True}


class UserOut(BaseModel):
    name: str
    email: EmailStr
    user_groups: List[GroupOut] = []
    workspaces: List[WorkspaceOut] = []
    model_config = {"from_attributes": True}


class UserLoginResponse(BaseModel):
    user: UserOut
    access_token: str
    token_type: str
