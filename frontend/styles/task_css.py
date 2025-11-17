import streamlit as st

CSS = """
    .task-card {
        background: #222327;
        border-radius: 8px;
        padding: 16px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
    }

    .task-card:hover {
        background: #2a2a2f;
    }

    .task-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 12px;
    }

    .task-title-row {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;
    }

    .task-scope-icon {
        font-size: 16px;
        flex-shrink: 0;
    }

    .task-title {
        font-size: 16px;
        font-weight: 600;
        color: #f9f9f9;
        line-height: 1.4;
    }

    .task-priority-badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
        color: white;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        flex-shrink: 0;
    }

    .task-description {
        color: #999;
        font-size: 13px;
        line-height: 1.5;
        margin-bottom: 12px;
    }

    .task-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-bottom: 10px;
    }

    .task-badge {
        padding: 3px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }

    .task-badge-group {
        background: rgba(115, 109, 230, 0.2);
        color: #b8b3ff;
        border: 1px solid rgba(115, 109, 230, 0.3);
    }

    .task-badge-workspace {
        background: rgba(59, 130, 246, 0.2);
        color: #93c5fd;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    .task-badge-repeat {
        background: rgba(168, 85, 247, 0.2);
        color: #d8b4fe;
        border: 1px solid rgba(168, 85, 247, 0.3);
    }

    .task-metadata {
        display: flex;
        gap: 12px;
        align-items: center;
        font-size: 12px;
        color: #666;
    }

    .task-deadline {
        display: flex;
        align-items: center;
        gap: 4px;
    }

    .task-completed-stamp {
        margin-top: 12px;
        padding: 8px 12px;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 6px;
        color: #10b981;
        font-size: 12px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
    }
"""


def inject_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
