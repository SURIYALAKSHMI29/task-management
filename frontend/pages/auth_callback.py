import streamlit as st
from authlib.integrations.requests_client import OAuth2Session

params = st.query_params

if "code" in params and st.session_state.get("user_email") is None:
    client_id = st.secrets["auth"]["client_id"]
    client_secret = st.secrets["auth"]["client_secret"]
    redirect_uri = st.secrets["auth"]["redirect_uri"]
    token_url = "https://oauth2.googleapis.com/token"
    userinfo_endpoint = "https://www.googleapis.com/oauth2/v2/userinfo"

    oauth = OAuth2Session(
        client_id,
        client_secret,
        redirect_uri=redirect_uri,
        scope="openid email profile",
    )
    try:
        if "counter" not in st.session_state:
            st.session_state.counter = 0

        st.session_state.counter += 1
        print("Token fetching attempt: {st.session_state.counter}")
        oauth.fetch_token(
            token_url,
            code=params["code"][0],
        )
        print("Token fetched{st.session_state.counter}")

        user_info = oauth.get(userinfo_endpoint).json()
        st.session_state.user_email = user_info["email"]
        print("Successfully set user_email:", st.session_state.user_email)
        st.switch_page("home")
    except Exception as e:
        print("Error fetching token:", e)

else:
    st.write("Redirecting...")
