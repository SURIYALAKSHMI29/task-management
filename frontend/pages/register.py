import time

import requests
import streamlit as st
from streamlit_modal import Modal


def register_page(modal: Modal):
    if "pending_registration" not in st.session_state:
        st.session_state.pending_registration = None

    # Registration form
    if st.session_state.pending_registration is None:
        name = st.text_input("Name", key="name")
        email = st.text_input("Email", key="email")
        password = st.text_input("Password", type="password", key="password")
        cnf_password = st.text_input(
            "Confirm Password", type="password", key="cnf_password"
        )

        if st.button("Submit"):
            if password != cnf_password:
                st.error("Passwords do not match")
            elif len(password) < 8:
                st.error("Password must be at least 8 characters long")
            elif name and email and password:
                st.session_state.pending_registration = {
                    "name": name,
                    "email": email,
                    "password": password,
                }
                st.rerun()

    # Verify email via Google
    if st.session_state.pending_registration:
        st.write("Please verify your email using Google login")

        if not st.session_state.get("logged_in", False):
            verify_url = (
                f"https://accounts.google.com/o/oauth2/v2/auth"
                f"?client_id={st.secrets['auth']['client_id']}"
                f"&redirect_uri={st.secrets['auth']['redirect_uri']}"
                f"&response_type=code&scope=openid email profile"
            )
            st.write("Redirect URI used:", st.secrets["auth"]["redirect_uri"])
            st.markdown(f"[Verify with Google]({verify_url})", unsafe_allow_html=True)

        if st.session_state.get("user_email") is not None:
            google_email = st.session_state.get("user_email")
            if google_email == st.session_state.pending_registration["email"]:
                st.success("Email verified successfully!")

                response = requests.post(
                    "http://localhost:8000/user/register",
                    json=st.session_state.pending_registration,
                )

                if response.status_code == 201:
                    data = response.json()
                    time.sleep(2)
                    st.session_state.access_token = data.get("access_token")
                    st.session_state.user = data.get("user")
                    st.session_state.pending_registration = None
                    st.session_state.active_modal = None
                    st.session_state.logged_in = True
                    modal.close()
                    st.success("Registered successfully!")
                else:
                    st.error("Unable to register the user right now, Try again later")
            else:
                st.error("Google email does not match the entered email")
