import streamlit as st
import pandas as pd
import time
from datetime import datetime
import uuid
from typing import Dict, List, Optional

# Initialize page config first
st.set_page_config(
    page_title="PyPLM - Product Lifecycle Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
CURRENT_UTC = "2025-04-25 11:25:56"
CURRENT_USER = "nexerax-collab"

# Risk Areas for Change Management
RISK_AREAS = {
    "Performance Impact": 3,
    "Security Impact": 4,
    "Data Impact": 3,
    "UI Impact": 2,
    "API Impact": 3,
    "Documentation Impact": 1,
    "Testing Impact": 2
}

# Initialize session state
if 'session_state' not in st.session_state:
    st.session_state.session_state = {
        'login': CURRENT_USER,
        'session_id': f"SESSION_{int(time.time())}",
        'start_time': CURRENT_UTC,
        'intro_step': 0,
        'completed_steps': set(),
        'module_created': False,
        'change_submitted': False
    }

# Function definitions stay the same as in your file
[Previous functions: show_module_creation(), show_module_browser(), etc.]

# Main navigation
main_menu = st.sidebar.selectbox(
    "Navigation",
    [
        "🏠 Introduction",
        "📦 Module Management",
        "🔄 Change Control",
        "📊 Analytics",
        "📚 Learning Resources"
    ]
)

# Header section
st.markdown(f"""
    <div style='background-color: #f0f2f6; padding: 1em; border-radius: 5px; margin-bottom: 1em;'>
        <h1 style='margin:0'>PyPLM</h1>
        <p style='color: #666;'>Product Lifecycle Management</p>
        <small style='font-family: monospace;'>
            🕒 {CURRENT_UTC} UTC • 👤 {CURRENT_USER}
        </small>
    </div>
""", unsafe_allow_html=True)

# Main content router
if main_menu == "🏠 Introduction":
    st.title("Welcome to PyPLM")
    st.markdown("""
    ### Modern Software PLM
    
    Product Lifecycle Management (PLM) helps track the entire lifecycle of your software products,
    from initial concept through development, deployment, and maintenance.
    
    This tool helps you:
    - Manage software modules and components
    - Track changes and their impacts
    - Ensure quality and compliance
    - Monitor project progress
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 Create New Module"):
            main_menu = "📦 Module Management"
            st.rerun()
    with col2:
        if st.button("🔄 Submit Change"):
            main_menu = "🔄 Change Control"
            st.rerun()

elif main_menu == "📦 Module Management":
    tabs = st.tabs(["Create", "Browse", "Learn"])
    
    with tabs[0]:
        show_module_creation()
    
    with tabs[1]:
        show_module_browser()
    
    with tabs[2]:
        show_module_learning()

elif main_menu == "🔄 Change Control":
    tabs = st.tabs(["Submit", "Review", "Learn"])
    
    with tabs[0]:
        show_change_submission()
    
    with tabs[1]:
        show_change_review()
    
    with tabs[2]:
        show_change_learning()

elif main_menu == "📊 Analytics":
    st.title("Analytics Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Module Statistics")
        modules = st.session_state.get('modules', [])
        if modules:
            df_modules = pd.DataFrame(modules)
            st.bar_chart(df_modules['type'].value_counts())
        else:
            st.info("No modules data available")
    
    with col2:
        st.subheader("Change Statistics")
        changes = st.session_state.get('changes', [])
        if changes:
            df_changes = pd.DataFrame(changes)
            st.bar_chart(df_changes['type'].value_counts())
        else:
            st.info("No changes data available")
    
    # Risk Analysis
    st.subheader("Risk Analysis")
    if changes:
        high_risk = len([c for c in changes if c.get('risk_score', 0) > 7])
        medium_risk = len([c for c in changes if 4 <= c.get('risk_score', 0) <= 7])
        low_risk = len([c for c in changes if c.get('risk_score', 0) < 4])
        
        col3, col4, col5 = st.columns(3)
        col3.metric("High Risk Changes", high_risk)
        col4.metric("Medium Risk Changes", medium_risk)
        col5.metric("Low Risk Changes", low_risk)
    else:
        st.info("No risk data available")

elif main_menu == "📚 Learning Resources":
    st.title("Learning Resources")
    
    with st.expander("🎓 PLM Fundamentals"):
        st.markdown("""
        ### Product Lifecycle Management (PLM)
        
        PLM in software development helps manage:
        - Product planning and conception
        - Development and implementation
        - Testing and validation
        - Deployment and maintenance
        - End-of-life and archival
        """)
    
    with st.expander("🔄 Change Management"):
        st.markdown("""
        ### Change Management Best Practices
        
        1. Clear Process Definition
        2. Risk Assessment
        3. Impact Analysis
        4. Review and Approval
        5. Implementation Control
        6. Documentation
        7. Post-implementation Review
        """)
    
    with st.expander("📈 Metrics and KPIs"):
        st.markdown("""
        ### Key Performance Indicators
        
        1. Product Quality Metrics
        2. Development Efficiency
        3. Change Success Rate
        4. Risk Management
        5. Compliance Metrics
        """)

# Sidebar info
with st.sidebar:
    st.markdown("### 🔍 Session Info")
    st.code(f"""
UTC Time : {CURRENT_UTC}
User     : {CURRENT_USER}
Session  : {st.session_state.session_state['session_id']}
    """)
    
    # Debug mode
    if st.checkbox("🐛 Debug Mode"):
        st.write("Session State:", st.session_state.session_state)
