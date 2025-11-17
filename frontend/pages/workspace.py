import time
from datetime import datetime

import requests
import streamlit as st
from styles.app_css import inject_css
from styles.workspace_css import inject_workspace_css
from utils.add_group import show_add_group_dialog

inject_css()
inject_workspace_css()

if not st.session_state.get("logged_in"):
    st.warning("Please log in to view your workspace.")
    st.stop()


def create_workspace(workspace_name, workspace_desc):
    backend_url = st.secrets["backend"]["workspace_url"]
    header = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.post(
        f"{backend_url}/create-workspace",
        headers=header,
        json={
            "workspace_name": workspace_name,
            "workspace_desc": workspace_desc,
        },
    )

    if response.status_code == 200:
        st.success("Workspace created!")
        st.session_state.user_workspace = response.json()
        # print(
        #     "returning user_workspace: ",
        #     st.session_state.user_workspace,
        # )
        time.sleep(1)
        st.cache_data.clear()
        st.rerun()
    else:
        print("Failed to create workspaces: ", response.status_code, response.text)
        st.error("Failed to create workspace")


def join_workspace(workspace_name):
    backend_url = st.secrets["backend"]["workspace_url"]
    header = {"Authorization": f"Bearer {st.session_state.access_token}"}
    response = requests.post(
        f"{backend_url}/join-workspace",
        headers=header,
        json=workspace_name,
    )

    if response.status_code == 200:
        st.success("Joined workspace!")
        st.session_state.user_workspace = response.json()
        # print(
        #     "returning user_workspace: ",
        #     st.session_state.user_workspace,
        # )
        time.sleep(1)
        st.cache_data.clear()
        st.rerun()
    else:
        print("Failed to join workspace: ", response.status_code, response.text)
        st.error("Failed to join workspace")


# Fetch workspace data
def get_workspace_data():
    workspace = st.session_state.user_workspace
    # print("User workspace:", workspace)

    if workspace:
        backend_url = st.secrets["backend"]["workspace_url"]
        header = {"Authorization": f"Bearer {st.session_state.access_token}"}
        response = requests.get(f"{backend_url}/{workspace['id']}", headers=header)

        if response.status_code == 200:
            workspace_data = response.json()
            # print("Workspace data", workspace_data)
        else:
            st.error(
                f"Failed to fetch workspaces: {response.status_code} - {response.text}"
            )

        members = workspace_data["members"]

        groups = workspace_data["groups"]
        user = st.session_state.user

        if user and workspace:
            return {
                "workspace": {
                    "id": workspace["id"],
                    "name": workspace["name"],
                    "description": workspace["description"],
                    "created_at": datetime.fromisoformat(workspace["created_at"]),
                    "created_by": workspace["created_by"],
                },
                "user_id": user["id"],
                "members": [
                    {"id": m["id"], "name": m["name"], "email": m["email"]}
                    for m in members
                ],
                "groups": [
                    {
                        "id": g["id"],
                        "name": g["name"],
                        "task_count": len(g.get("tasks") or []),
                        "created_at": datetime.fromisoformat(g["created_at"]),
                    }
                    for g in groups
                ],
            }

    return None


user_email = st.session_state.user_email
workspace_data = get_workspace_data()

if not workspace_data:
    st.markdown("## Welcome to Workspaces")
    st.markdown("Collaborate with your team and organize your tasks efficiently.")
    st.divider()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown("### 🆕 Create Workspace")
        st.markdown("Start your own workspace and invite your team.")

        with st.form("create_workspace"):
            workspace_name = st.text_input(
                "Workspace Name", placeholder="My Team Workspace"
            )

            workspace_desc = st.text_input(
                "Description", placeholder="A place where developers collaborate"
            )

            if st.form_submit_button(
                "Create Workspace", use_container_width=True, type="primary"
            ):
                if workspace_name and workspace_desc:
                    create_workspace(workspace_name, workspace_desc)
                else:
                    st.error("Please enter a workspace name and its description")

    with col2:
        st.markdown("### 🤝 Join Workspace")
        st.markdown("Know your Workspace name? Join your team.")

        with st.form("join_workspace"):
            workspace_name = st.text_input(
                "Workspace Name", placeholder="e.g., sample workspace"
            )

            if st.form_submit_button("Join Workspace", use_container_width=True):
                if workspace_name:
                    join_workspace(workspace_name)
                else:
                    st.error("Please enter a workspace name")

    st.stop()

# workspace exists
ws = workspace_data["workspace"]
members = workspace_data["members"]
groups = workspace_data["groups"]
current_user_id = workspace_data["user_id"]
is_creator = ws["created_by"] == current_user_id


# Workspace Header
st.markdown(
    f"""
        <div class="workspace-header">
        <h1 class="workspace-title">🏢 {ws['name']}</h1>
        <h3 class="workspace-description">{ws['description']}</h3>
        <p class="workspace-meta">Created {ws['created_at'].strftime('%B %d, %Y')}</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Stats
col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-value">{len(groups)}</div>
            <div class="stat-label">📁 Groups</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    total_tasks = sum(g["task_count"] for g in groups)
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-value">{total_tasks}</div>
            <div class="stat-label">✅ Tasks</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f"""
        <div class="stat-card">
            <div class="stat-value">{len(members)}</div>
            <div class="stat-label">👥 Members</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)


members_col, groups_col = st.columns([1, 2.5], gap="large")

# members
with members_col:
    st.markdown(
        '<h3 class="section-title">👥 Team Members</h3>', unsafe_allow_html=True
    )

    for member in members:
        is_current = member["email"] == user_email
        is_member_creator = member["id"] == ws["created_by"]

        role_badge = ""
        card_class = "member-card"

        if is_current:
            role_badge = '<span class="member-role you">You</span>'
            card_class += " current"
        elif is_member_creator:
            role_badge = '<span class="member-role creator">Creator</span>'

        st.markdown(
            f"""
            <div class="{card_class}">
                <div class="member-name">{member['name']}<span style="float: right">{role_badge}</span></span></div>
                <div class="member-email">{member['email']}</div>
                
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # if is_creator:
    #     if st.button(" Add Member"):
    #         st.session_state.show_add_member = True
    # else:
    #     if st.button("🚪 Leave Workspace"):
    #         st.session_state.show_leave_confirm = True


with groups_col:
    col_title, col_btn = st.columns([1, 0.2])
    with col_title:
        st.markdown(
            '<h3 class="section-title">📁 Task Groups</h3>', unsafe_allow_html=True
        )
    with col_btn:
        if st.button("➕ New Group", type="tertiary", help="Add new Group"):
            st.session_state.show_create_group = True
            st.rerun()

    if groups:
        for group in groups:
            cols = st.columns([10, 1])

            with cols[0]:
                st.markdown(
                    f"""
                    <div class="group-card">
                        <div class="group-header">
                            <h4 class="group-title">{group['name']}</h4>
                        </div>
                        <div class="group-stats">
                            <div class="stat-item">
                                <span>✅</span>
                                <span><strong>{group['task_count']}</strong> tasks</span>
                            </div>
                            <div class="stat-item">
                                <span>📅</span>
                                <span>Created {group['created_at'].strftime('%b %d, %Y')}</span>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with cols[1]:
                if st.button(
                    "🔗",
                    key=f"view_{group['id']}",
                    help=f"View tasks in {group['name']}",
                    type="tertiary",
                ):
                    pass
                    # st.session_state.selected_group_id = group["id"]
                    # st.session_state.selected_group_name = group["name"]
                    # st.switch_page("pages/group.py")

    else:
        st.markdown(
            """
            <div class="empty-state">
                <div class="empty-icon">📁</div>
                <div class="empty-title">No groups yet</div>
                <div class="empty-text">Create your first group to start organizing tasks</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


if st.session_state.get("show_create_group"):
    show_add_group_dialog(ws["id"], True)
    st.session_state.show_create_group = False
