import time

import requests
import streamlit as st
from streamlit_modal import Modal


def register_page(modal: Modal):
    name = st.text_input("Name", key="name")
    email = st.text_input("Email", key="email")
    password = st.text_input("Password", type="password", key="password")
    cnf_password = st.text_input(
        "Confirm Password", type="password", key="cnf_password"
    )
    if password != cnf_password:

        st.error("Passwords do not match")

    if len(password) < 8:
        st.error("Password must be at least 8 characters long")

    if st.button("Submit"):
        if name and email and password:
            try:
                response = requests.post(
                    "http://localhost:8000/user/register",
                    json={"name": name, "email": email, "password": password},
                )
                print(response.json())
                if response.status_code == 201:
                    data = response.json()
                    st.session_state.logged_in = True
                    st.success("Registered successfully!")
                    time.sleep(2)
                    st.session_state.access_token = data.get("access_token")
                    st.session_state.user = data.get("user")
                    st.session_state.active_modal = None
                    modal.close()
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error(f"Error: {e}")
