from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import EmailStr
from sqlmodel import Session, select

from backend.database import get_session
from backend.helpers.auth.auth_utils import (
    generate_user_login_response,
    get_current_user,
)
from backend.helpers.auth.password import hash_password, verify_password
from backend.models import RecurringTask, Task, User
from backend.schemas import TaskOut, UserIn, UserLoginResponse, UserOut

router = APIRouter()


# used to get user by email
# if not found httpexception is raised -> terminates the func and returns the error to the client
# if found, user is returned
def get_user_by_email(email: EmailStr, session: Session):
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not Found")
    return user


def verify_user_password(email: EmailStr, password: str, session: Session) -> User:
    user = get_user_by_email(email, session)
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


# check if the email already exists
def validate_email(email: EmailStr, session: Session) -> bool:
    user = session.exec(select(User).where(User.email == email)).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return True


@router.post("/login", response_model=UserLoginResponse)
def verify_user(
    email: EmailStr = Body(...),
    password: str = Body(...),
    session: Session = Depends(get_session),
) -> UserLoginResponse:
    user = verify_user_password(email, password, session)
    return generate_user_login_response(user)


# add new user
@router.post("/register", response_model=UserLoginResponse, status_code=201)
def register_new_user(user: UserIn, session: Session = Depends(get_session)):
    if validate_email(user.email, session):
        user.password = hash_password(user.password)
        user_data = User(**user.model_dump())
        session.add(user_data)
        session.commit()
        session.refresh(user_data)
        return generate_user_login_response(user_data)
    return


# get all tasks associated to a specific user
@router.get("/tasks", response_model=List[TaskOut])
def get_all_tasks(
    current_user=Depends(get_current_user), session: Session = Depends(get_session)
):
    user_email = current_user["user_email"]
    user = get_user_by_email(user_email, session)
    user_tasks = []

    for task in user.tasks:
        user_task = TaskOut.model_validate(task)
        if task.recurring_task:
            recurring_info = session.get(RecurringTask, task.recurring_task.id)
            if recurring_info:
                user_task.repetitive_type = recurring_info.repetitive_type
                user_task.repeat_until = recurring_info.repeat_until
        user_tasks.append(user_task)
    return user_tasks


# modify the user details
@router.patch("/modify-user", response_model=UserOut)
def modify_user(
    email: Optional[EmailStr] = None,
    name: Optional[str] = None,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_email = current_user["user_email"]
    user = get_user_by_email(user_email, session)
    if name:
        user.name = name
    if email and user.email != email and validate_email(email, session):
        user.email = email
    session.commit()
    session.refresh(user)
    return user


# change password
# verify user existence, check validity, then change password
@router.patch("/change-password")
def change_password(
    old_password: str = Body(...),
    new_password: str = Body(...),
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    email = current_user["user_email"]
    user = verify_user_password(email, old_password, session)
    user.password = hash_password(new_password)
    session.commit()
    return {"message": "Password updated successfully"}


# delete a user
@router.delete("/delete-user")
def delete_user(
    current_user=Depends(get_current_user), session: Session = Depends(get_session)
) -> dict:
    email = current_user["user_email"]
    user = get_user_by_email(email, session)
    session.delete(user)
    session.commit()
    return {"message": "User deleted successfully"}
