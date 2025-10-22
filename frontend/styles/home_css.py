import streamlit as st

CSS = """

.taskContainer{
    padding: 10px;
    margin-bottom: 10px;
    background-color: #222;
}

.taskContainer:hover{
    background-color: #333;
    transition: 0.3s;
    cursor: pointer;
}
.taskTitle{
    font-weight: bold;
    font-size: 1.2em;
    margin-bottom: 5px;
}

.taskInfo{
    display: flex;
    gap: 10px;
    align-items: left;
    font-size: 1em;
    color: #999;
}
"""

def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
