from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from backend.helpers.enums import RecurrenceType, TaskPriority, TaskStatus


class UserIn(BaseModel):
    name: str
    password: str
    email: EmailStr


class UserOut(BaseModel):
    name: str
    email: EmailStr
    model_config = {"from_attributes": True}


class UserLoginResponse(BaseModel):
    user: UserOut
    access_token: str
    token_type: str


class TaskIn(BaseModel):
    user_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    status: Optional[TaskStatus] = TaskStatus.PENDING
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    pinned: Optional[bool] = False


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    deadline: datetime | None
    priority: TaskPriority
    status: TaskStatus
    pinned: bool
    repetitive_type: Optional[RecurrenceType] = None
    repeat_until: Optional[datetime] = None

    model_config = {"from_attributes": True}  # allows reading from ORM/SQLModel objects
