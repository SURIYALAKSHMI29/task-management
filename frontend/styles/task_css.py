import streamlit as st

CSS = """

.taskContainer{
    padding: 10px;
    margin-bottom: 10px;
    background-color: #222;
    border-radius: 5px;
}

.taskContainer:hover{
    background-color: #333;
    transition: 0.3s;
    cursor: pointer;
}

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
}

.completedDate{
    position: absolute;
    right: 10px;
    top: 10px;
    font-size: 1em;
    color: green;
    font-weight: bold;
}

.taskContainer .iconBar{
    display: none;
    opacity: 0;
    transition: opacity 0.2s;
    position: absolute;
    top: 10px;
    right: 10px;
}

.taskContainer:hover .iconBar{
    display: flex;
    gap: 6px;
    opacity: 1;
}

.icon-btn {
    border: none;
    background-color: #333;
    margin: 2px;
    cursor: pointer;
    color: #f1f1f1;
    transition: background 0.2s;
    font-size: 1.5em;
}

.icon-btn:hover { 
    box-shadow: 0 2px 8px #0001
}

"""


def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
