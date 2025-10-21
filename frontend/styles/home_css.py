import streamlit as st

CSS = """
/* Page background and general text */
body {
    background-color: #f5f5f5;
    font-family: 'Arial', sans-serif;
}

/* App title */
.stTitle {
    color: #1f2937;
    font-size: 3rem;
    font-weight: bold;
    text-align: left;
    margin-bottom: 0.5rem;
}
.stHeader {
    color: #4b5563;
    font-size: 1.2rem;
    text-align: left;
    margin-bottom: 2rem;
}
/* Subheader */
.stSubheader {
    color: #4b5563;
    font-size: 1rem;
    text-align: center;
    margin-bottom: 2rem;
}

/* Buttons */
div.stButton > button {
    background-color: #4f46e5;
    color: white;
    font-size: 1rem;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    transition: 0.3s;
}
div.stButton > button:hover {
    background-color: #4338ca;
    cursor: pointer;
}

/* Modals */
.stModal > div {
    border-radius: 15px;
    padding: 20px;
    box-shadow: 0px 4px 30px rgba(0, 0, 0, 0.2);
}

/* Logged-in user info */
.user-info {
    text-align: right;
    font-size: 0.9rem;
    color: #374151;
    margin-top: -2rem;
}
"""


def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
