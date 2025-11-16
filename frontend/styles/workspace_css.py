import streamlit as st

CSS = """
    .member-card {    
        background: #222;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 1px solid #333;
        transition: all 0.2s ease;
        position: relative;
    }
        
    .member-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-color: #667eea;
    }
        
    .member-card.current {
        background: linear-gradient(135deg, #667eea15, #764ba215);
        border: 1px solid #667eea;
    }
        
    .member-name {
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 2px;
    }

    .member-email{
        font-size: 14px;
        color: #999;
        margin-bottom: 4px;
    }
        
    .member-role {
        font-size: 12px;
        color: #666;
        display: inline-block;
        padding: 2px 8px;
        background: #f5f5f5;
        border-radius: 12px;
        font-weight: 500;
    }
        
    .member-role.creator {
        background: #fff3e0;
        color: #f57c00;
    }
        
    .member-role.you {
        background: #e3f2fd;
        color: #1976d2;
    }
        
    .group-card {
        background: #222;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        border: 1px solid #112;
        transition: all 0.2s ease;
    }
        
    .group-card:hover {
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        transform: translateY(-2px);
    }
        
    .group-header {
        display: flex;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .group-title {
        font-size: 18px;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0;
    }
        
    .group-stats {
        display: flex;
        gap: 16px;
        color: #666;
        font-size: 14px;
        margin-bottom: 16px;
    }
        
    .stat-item {
        display: flex;
        align-items: center;
        gap: 4px;
    }
        
    .workspace-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        padding: 32px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
        
    .workspace-title {
        font-size: 32px;
        font-weight: 700;
        margin: 0 0 8px 0;
        color: white;
    }
        
    .workspace-meta {
        font-size: 14px;
        opacity: 0.9;
    }
        
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
        
    .section-title {
        font-size: 20px;
        font-weight: 600;
        color: #1a1a1a;
        margin: 0;
    }
        
    .stat-card {
        background: #112;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #333;
        text-align: center;
    }
        
    .stat-value {
        font-size: 32px;
        font-weight: 700;
        color: #667eea;
        margin-bottom: 4px;
    }
        
    .stat-label {
        font-size: 14px;
        color: #666;
        font-weight: 500;
    }
        
    .empty-state {
        text-align: center;
        padding: 60px 20px;
        background: #222;
        border-radius: 12px;
        border: 2px dashed #444;
    }
        
    .empty-icon {
        font-size: 48px;
        margin-bottom: 16px;
        opacity: 0.5;
    }
        
    .empty-title {
        font-size: 18px;
        font-weight: 600;
        color: #666;
        margin-bottom: 8px;
    }
        
    .empty-text {
        font-size: 14px;
        color: #999;
    }
            
"""


def inject_workspace_css():
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
