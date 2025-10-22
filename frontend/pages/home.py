import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from pages.login import login_page
from pages.register import register_page
from streamlit_modal import Modal


def logout():
    st.session_state.logged_in = False


login_modal = Modal("Login", key="login-modal", padding=20, max_width=900)
register_modal = Modal("Register", key="register-modal", padding=20, max_width=900)

st.markdown('<h1 class="stTitle">GoGetter</h1>', unsafe_allow_html=True)
st.markdown(
    '<h2 class="stHeader">A goal without a timeline is just a Dream</h2>',
    unsafe_allow_html=True,
)
st.markdown(
    '<h3 class="stSubheader">Manage your tasks Efficiently!</h3>',
    unsafe_allow_html=True,
)

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
        print(params)
        st.session_state.counter += 1
        print("Token fetching attempt: {st.session_state.counter}")
        code = params.get("code")
        print("code:", code)
        oauth.fetch_token(
            token_url,
            code=code,
        )
        print("Token fetched{st.session_state.counter}")

        user_info = oauth.get(userinfo_endpoint).json()
        st.session_state.user_email = user_info["email"]
        print("Successfully set user_email:", st.session_state.user_email)
        st.session_state.active_modal = "register-modal"
        register_modal.open()
        
    except Exception as e:
        print("Error fetching token:", e)

if not st.session_state.logged_in:
    with st.container():
        login_bt = st.button("Log in")
        register_bt = st.button("Register")
        if login_bt:
            st.session_state.active_modal = "login-modal"
            login_modal.open()
        if register_bt:
            st.session_state.active_modal = "register-modal"
            register_modal.open()
else:
    with st.container():
        st.button("Log out", on_click=logout)

if not st.session_state.logged_in:
    st.write("Get better experience by loggin in")

if st.session_state.active_modal == "login-modal":
    if login_modal.is_open():
        with login_modal.container():
            login_page(login_modal)

if st.session_state.active_modal == "register-modal":
    if register_modal.is_open():
        with register_modal.container():
            register_page(register_modal)
