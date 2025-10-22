import time

import requests
import streamlit as st
from streamlit_modal import Modal


def register_page(modal: Modal):
    if "pending_registration" not in st.session_state:
        st.session_state.pending_registration = None

    # Verify email via Google login
    if st.session_state.user_email is None:
        st.write("Please verify your email using Google login")

        verify_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth"
            f"?client_id={st.secrets['auth']['client_id']}"
            f"&redirect_uri={st.secrets['auth']['redirect_uri']}"
            f"&response_type=code&scope=openid email profile"
        )
        st.write("Redirect URI used:", st.secrets["auth"]["redirect_uri"])
        st.markdown(
            f'<a href="{verify_url}" target="_self"><button>Continue with Google</button></a>',
            unsafe_allow_html=True,
        )

    # registration process with verified email
    else:
        if st.session_state.pending_registration is None:
            st.write("Complete your registration")

            name = st.text_input("Name", key="name")
            st.text_input("Email (verified)", value=st.session_state.user_email, disabled=True)
            password = st.text_input("Password", type="password", key="password")
            cnf_password = st.text_input("Confirm Password", type="password", key="cnf_password")

            if st.button("Submit"):
                if password != cnf_password:
                    st.error("Passwords do not match")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters long")
                elif name:
                    st.session_state.pending_registration = {
                        "name": name,
                        "email": st.session_state.user_email,
                        "password": password,
                    }
                    st.rerun() 

        # Submit registration data to backend
        if st.session_state.pending_registration is not None:
            st.write("Registering your account, please wait...")
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
