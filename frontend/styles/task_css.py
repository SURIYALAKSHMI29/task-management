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

.iconBar{
    display: flex;
    gap: 10px;
    position: absolute;
    top: 10px;
    right: 10px;
}

.icon-btn {
    width: 26px;
    height: 26px;
    color: #f2f2f2;
    font-size: 16px;
    cursor: pointer;
    transition: background 0.2s ease, color 0.2s ease;
}

.icon-btn:hover {
    background-color: #e0e0e0;
    color: #222;
}

.icon-btn:active {
    transform: scale(0.96);
}

.edit::before {
    content: "✎";
}
.delete::before {
    content: "🗑";
}
.done::before {
    content: "✔";
}
"""


def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
