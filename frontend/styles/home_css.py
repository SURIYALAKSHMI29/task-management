import streamlit as st

CSS = """
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen', 'Ubuntu', 'Cantarell', sans-serif;
    color: white;
}

.stTitle {
    background: linear-gradient(90deg, #4f46e5 0%, darkgray 50%, #222 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: 3.5rem;
    font-weight: 800;
    text-align: left;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
    line-height: 1.2;
}

.stTagline {
    color: white;
    font-size: 1.1rem;
    font-weight: 500;
    text-align: left;
    margin-top: 0;
    margin-bottom: 20px;
    line-height: 1.4;
}

.welcome-card {
    border-radius: 10px;
    padding: 3rem;
    margin: 2rem auto;
    max-width: 900px;
    margin-top: 4rem;
}

.welcome-card h2 {
    color: lightgray;
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 1rem;
    line-height: 1.3;
}

.welcome-card > p {
    color: darkgray;
    font-size: 1.1rem;
    line-height: 1.6;
    margin-bottom: 2rem;
}

.feature-list {
    list-style: none;
    padding: 0;
    margin: 2rem 0;
}

.feature-list li {
    display: flex;
    background: #333;
    align-items: flex-start;
    gap: 1rem;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    border-radius: 8px;
    transition: all 0.3s ease;
    font-size: 1.2rem;
}

.feature-list li:hover {
    background: #555;
    transform: translateX(8px);
}

.login-text{
    color: white;
    font-size: 1.1rem;
    font-weight: 500;
    text-align: center;
    margin-top: 0;
    margin-bottom: 20px;
    color: #4f46e5;
}

.greeting-card {
    padding: 1rem;
    margin: 1rem 0;
    margin-bottom: 4rem;
    color: white;
    position: relative;
    overflow: hidden;
}

.greeting-card h2 {
    font-size: 1.8rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    color: white;
    position: relative;
    z-index: 1;
}

.greeting-card .user-name {
    background: linear-gradient(90deg, #4f46e5 0%, #4f46e5 40%, darkgray 95%, #111 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.greeting-card p {
    font-size: 1rem;
    opacity: 0.95;
    margin: 0;
    position: relative;
    z-index: 1;
}

.empty-state {
    margin-top: 2rem;
    background: #1e1e1e;
    padding: 3rem 2rem;
    text-align: center;
    border-radius: 10px
    transition: all 0.3s ease;
}

.empty-state:hover {
    background: #333;
    scale: 1.01;
}

.empty-state p {
    font-size: 1.05rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.empty-state .empty-subtext {
    color: darkgray;
    font-size: 0.95rem;
    font-weight: 400;
}


"""


def inject_home_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
