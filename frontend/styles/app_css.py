import streamlit as st

CSS = """
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

div.stButton > button {
    background-color: #6a64e7ff;
    color: white;
    font-size: 1rem;
    border-radius: 8px;
    padding: 0.4rem 1rem;
    transition: 0.3s;
}
div.stButton > button:hover {
    background-color: #4338ca;
    cursor: pointer;
}
"""


def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
