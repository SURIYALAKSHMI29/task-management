from backend.database import get_session
from backend.helpers.auth.auth_utils import get_current_user
from backend.models import Group, User, UserWorkspaceLink, Workspace
from backend.routers.users import get_user_by_email
from backend.schemas import BaseUserOut
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

router = APIRouter()


def is_member(workspace_id, user_email, session: Session):
    user_id = get_user_by_email(user_email, session).id
    is_member = session.exec(
        select(UserWorkspaceLink).where(
            UserWorkspaceLink.workspace_id == workspace_id
            and UserWorkspaceLink.user_id == user_id
        )
    ).first()
    return is_member


@router.post("/create-workspace")
def create_workspace(
    workspace_name: str = Body(...),
    workspace_desc: str = Body(...),
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user_email = current_user["user_email"]
    user = get_user_by_email(user_email, session)

    workspace = Workspace(
        name=workspace_name, description=workspace_desc, created_by=user.id
    )
    session.add(workspace)
    session.commit()
    session.refresh(workspace)

    workspace_link = UserWorkspaceLink(
        user_id=user.id,
        workspace_id=workspace.id,
    )
    session.add(workspace_link)
    session.commit()

    print(workspace)
    return workspace


@router.get("/{workspace_id}")
def get_workspace(
    workspace_id: int,
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if is_member(workspace_id, current_user["user_email"], session):
        users = session.exec(
            select(User)
            .join(UserWorkspaceLink)
            .where(UserWorkspaceLink.workspace_id == workspace_id)
        ).all()

        members = [
            BaseUserOut(id=user.id, name=user.name, email=user.email) for user in users
        ]
        groups = session.exec(
            select(Group)
            .where(Group.workspace_id == workspace_id)
            .options(selectinload(Group.tasks))
        ).all()

        return {"members": members, "groups": groups}
    raise HTTPException(status_code=403, detail="Not allowed, access forbidden")


@router.post("/join-workspace")
def join_workspace(
    workspace_name: str = Body(...),
    current_user=Depends(get_current_user),
    session: Session = Depends(get_session),
):
    user = get_user_by_email(current_user["user_email"], session)
    workspace = session.exec(
        select(Workspace).where(Workspace.name == workspace_name)
    ).first()

    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")

    workspace_link = UserWorkspaceLink(
        user_id=user.id,
        workspace_id=workspace.id,
    )
    session.add(workspace_link)
    session.commit()

    return workspace
