import time

import requests
import streamlit as st
from streamlit_modal import Modal
from utils.load_data import load_user_details


def register_page(modal: Modal):
    name = st.text_input("Name", key="name")
    email = st.text_input("Email", key="email")
    password = st.text_input("Password", type="password", key="password")
    cnf_password = st.text_input(
        "Confirm Password", type="password", key="cnf_password"
    )

    workspace = st.text_input("Workspace Name", key="workspace")

    if st.button("Register"):
        if password != cnf_password:
            st.error("Passwords do not match")
        elif len(password) < 8:
            st.error("Password must be at least 8 characters long")
        elif name and email and password and cnf_password:
            try:
                backend_url = st.secrets["backend"]["user_url"]
                payload = {
                    "name": name,
                    "email": email,
                    "password": password,
                }
                if workspace:
                    payload["workspace"] = [workspace]
                response = requests.post(f"{backend_url}/register", json=payload)
                if response.status_code == 201:
                    data = response.json()
                    st.success("Registered successfully!")
                    st.session_state.logged_in = True
                    time.sleep(1)
                    st.session_state.access_token = data.get("access_token")
                    st.session_state.user = data.get("user")
                    load_user_details()
                    st.session_state.pending_registration = None
                    st.session_state.active_modal = None
                    modal.close()
                elif response.status_code == 409:
                    st.error(response.json()["detail"])
                else:
                    st.error("Unable to register the user right now, Try again later")
            except Exception as e:
                st.error(f"Error: {e}")
        else:
            st.error("Please enter name, email and password")
