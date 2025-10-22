import time

import requests
import streamlit as st
from streamlit_modal import Modal


def login_page(modal: Modal):
    email = st.text_input("Email", key="email")
    password = st.text_input("Password", type="password", key="password")
    if st.button("Submit"):
        if email and password:
            try:
                backend_url = st.secrets["backend"]["user_url"]
                response = requests.post(
                    f"{backend_url}/login",
                    json={"email": email, "password": password},
                )
                if response.status_code == 200:
                    data = response.json()
                    st.session_state.logged_in = True
                    st.success("Logged in successfully!")
                    time.sleep(2)
                    st.session_state.access_token = data.get("access_token")
                    st.session_state.user = data.get("user")
                    st.session_state.user_email = data.get("user")["email"]
                    st.session_state.active_modal = None
                    modal.close()
                else:
                    print(response.json())
                    st.error("Invalid credentials")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please enter email and password")
