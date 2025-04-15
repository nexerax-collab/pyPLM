import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime

# Constants
CURRENT_UTC = "2025-04-15 13:09:30"
CURRENT_USER = "nexerax-collab"

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.user_data = {
        'login': CURRENT_USER,
        'session_id': f"SESSION_{int(time.time())}",
        'start_time': CURRENT_UTC
    }

# Page configuration must be called once and at the top
st.set_page_config(
    page_title="PyPLM - Product Lifecycle Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application header
st.markdown(f"""
    <div style='background-color: #f0f2f6; padding: 1em; border-radius: 5px; margin-bottom: 1em;'>
        <h1 style='margin:0'>PyPLM</h1>
        <small style='color: #666;'>Product Lifecycle Management</small>
        <br>
        <small style='font-family: monospace;'>
            🕒 {CURRENT_UTC} UTC • 👤 {CURRENT_USER}
        </small>
    </div>
""", unsafe_allow_html=True)

# Sidebar navigation
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

# Session info in sidebar
with st.sidebar:
    st.markdown("### 🔍 Session Info")
    st.code(f"""
UTC Time : {CURRENT_UTC}
User     : {CURRENT_USER}
Session  : {st.session_state.user_data['session_id']}
    """)

    if st.checkbox("🐛 Debug Mode"):
        st.write("Session State:", st.session_state)

# Module Management Section
def show_module_management():
    st.header("📦 Module Management")
    
    tabs = st.tabs(["Create", "Browse", "Learn"])
    
    with tabs[0]:
        with st.form("create_module"):
            st.subheader("Create New Module")
            module_name = st.text_input("Module Name", placeholder="e.g., auth-service")
            module_type = st.selectbox(
                "Module Type",
                ["Microservice", "Library", "Plugin"]
            )
            submitted = st.form_submit_button("Create Module")
            if submitted and module_name:
                st.success(f"Module '{module_name}' created!")
                st.balloons()
    
    with tabs[1]:
        st.subheader("Browse Modules")
        # Add module browsing functionality here
        
    with tabs[2]:
        st.subheader("Learning Resources")
        st.markdown("""
        ### CM of the Future
        Learn about modern Configuration Management practices:
        
        1. **AI-Assisted Version Control**
           - Predictive conflict resolution
           - Smart branching strategies
        
        2. **Automated Impact Analysis**
           - Real-time dependency tracking
           - Risk assessment
        
        3. **Smart Compliance**
           - Policy enforcement
           - Audit trails
        """)

# Change Control Section
def show_change_control():
    st.header("🔄 Change Control")
    
    tabs = st.tabs(["Submit", "Review"])
    
    with tabs[0]:
        with st.form("submit_change"):
            st.subheader("Submit Change")
            change_type = st.selectbox(
                "Change Type",
                ["Feature", "Bug Fix", "Enhancement"]
            )
            submitted = st.form_submit_button("Submit")
            if submitted:
                st.success("Change submitted successfully!")

    with tabs[1]:
        st.subheader("Review Changes")
        # Add change review functionality here

# Analytics Section
def show_analytics():
    st.header("📊 Analytics")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Modules", "5", "+2")
    with col2:
        st.metric("Active Changes", "3", "-1")

# Learning Resources Section
def show_learning_resources():
    st.header("📚 Learning Resources")
    
    st.markdown("""
    ### Configuration Management Evolution
    
    #### Modern CM Practices (2025)
    1. **AI-Driven Development**
       - Automated conflict resolution
       - Smart dependency management
    
    2. **Intelligent Change Management**
       - Impact prediction
       - Risk assessment
    
    3. **Future of PLM**
       - Predictive maintenance
       - Automated compliance
    """)
    
    # Interactive learning elements
    if st.checkbox("Take CM Maturity Assessment"):
        st.slider("Version Control Maturity", 1, 5, 3)
        st.slider("Change Management Maturity", 1, 5, 3)
        if st.button("Calculate Score"):
            st.success("Your CM Maturity Score: 3.5/5.0")

# Main content router
if main_menu == "🏠 Introduction":
    st.header("Welcome to PyPLM")
    st.markdown("""
    ### Getting Started
    1. Create modules in Module Management
    2. Track changes in Change Control
    3. Monitor progress in Analytics
    4. Learn best practices in Learning Resources
    """)

elif main_menu == "📦 Module Management":
    show_module_management()

elif main_menu == "🔄 Change Control":
    show_change_control()

elif main_menu == "📊 Analytics":
    show_analytics()

elif main_menu == "📚 Learning Resources":
    show_learning_resources()
