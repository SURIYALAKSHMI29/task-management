import streamlit as st
from styles.app_css import inject_css

inject_css()
st.header("Your Workspace")

st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


user_workspace = st.session_state.user_workspace

if user_workspace:
    st.write(user_workspace)

else:
    st.write("No workspace found")
