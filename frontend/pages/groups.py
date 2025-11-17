import streamlit as st

user_groups = st.session_state.user_groups


def switch_group_type():
    st.session_state.user_group_view = not st.session_state.user_group_view


def search_groups(): ...


group_cols = st.columns([2, 0.1, 0.2])

group_type = (
    "Personal Task Groups"
    if st.session_state.user_group_view
    else "WorkSpace Task Groups"
)
with group_cols[0]:
    st.subheader(group_type)
with group_cols[1]:
    if group_type == "Personal Task Groups":
        switch_group_icon = "👤"
    else:
        switch_group_icon = "👥"
    switch_group = st.button(
        switch_group_icon, type="tertiary", on_click=switch_group_type
    )
with group_cols[2]:
    add_group = st.button("Add Group", on_click=None, type="secondary")


st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
st.markdown(" ")

st.text_input(
    "Search Task Groups",
    "",
    key="group_search",
    label_visibility="hidden",
    placeholder="Search Task Groups",
    on_change=search_groups,
    width=500,
)


if st.session_state.user_group_view:
    for group_id, task_list in st.session_state.personal_groups.items():
        st.write("Group ID:", group_id)
        st.write("Tasks:", task_list)
    # print("here inside personal groups")

else:
    # print("here inside workspace groups")
    for workspace_id, groups in st.session_state.workspace_groups.items():
        st.write("Workspace ID:", workspace_id)
        print(workspace_id, groups)
        for group_id, task_list in groups.items():
            st.write("  Group ID:", group_id)
            st.write("  Tasks:", task_list)
