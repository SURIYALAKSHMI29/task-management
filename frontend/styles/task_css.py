import streamlit as st

CSS = """

.taskIcon{
    position: absolute;
    top: 10px;
    left: 10px;
}

.taskTitle{
    font-weight: bold;
    font-size: 1.2em;
    margin-bottom: 5px;
}

.taskTitle.icon{
    margin-right: 5px;
}

.taskInfo{
    display: flex;
    gap: 10px;
    align-items: left;
    font-size: 1em;
    color: #999;
    font: sans-serif;
    margin-bottom: 10px;
}

.completedDate{
    font-size: 1em;
    font-weight: bold;
}

"""


def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
