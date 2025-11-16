from typing import List, Optional

from backend.database import get_session
from backend.helpers.auth.auth_utils import get_current_user
from backend.models import Group, Task, Workspace
from backend.routers.users import get_user_by_email
from backend.routers.workspaces import is_member
from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import EmailStr
from sqlmodel import Session, select

router = APIRouter()


@router.post("/create-group")
def create_group(
    group_data: dict = Body(...),
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user = get_user_by_email(current_user["user_email"], session)

    task_ids = group_data.pop("task_ids", [])
    workspace_id = group_data.get("workspace_id")

    if workspace_id:
        workspace = session.get(Workspace, workspace_id)
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")

        if not is_member(workspace_id, current_user["user_email"], session):
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to create groups in this workspace",
            )

    group = Group(**group_data, created_by=user.id)
    session.add(group)
    session.flush()  # Get the group.id before committing

    if task_ids:
        for task_id in task_ids:
            task = session.get(Task, task_id)
            if not task:
                raise HTTPException(
                    status_code=404, detail=f"Task with id {task_id} not found"
                )

            task.group_id = group.id

    session.commit()
    session.refresh(group)

    return group
