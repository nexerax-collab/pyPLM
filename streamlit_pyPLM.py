import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime

# Initialize session state and constants
CURRENT_UTC = "2025-04-15 09:57:26"
CURRENT_USER = "nexerax-collab"

if 'user_data' not in st.session_state:
    st.session_state.user_data = {
        'login': CURRENT_USER,
        'session_id': f"SESSION_{int(time.time())}",
        'start_time': CURRENT_UTC
    }

if 'feature_tour' not in st.session_state:
    st.session_state.feature_tour = {
        'current_step': 0,
        'completed_tours': set(),
        'current_category': None
    }

# Database connection (mock for example)
def get_db_connection():
    return sqlite3.connect(':memory:')

# Configure page
st.set_page_config(
    page_title="PyPLM - Product Lifecycle Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper functions for demo features
def show_module_demo():
    with st.expander("Module Creation Demo"):
        st.write("Create a new module:")
        module_name = st.text_input("Module Name", placeholder="my-service")
        module_type = st.selectbox(
            "Module Type",
            ["Service", "Library", "Component"]
        )
        if st.button("Create Demo Module"):
            st.success(f"Demo module '{module_name}' created!")

def show_change_request_demo():
    with st.expander("Change Request Demo"):
        st.write("Submit a change request:")
        change_type = st.selectbox(
            "Change Type",
            ["Feature", "Bug Fix", "Enhancement"]
        )
        if st.button("Submit Demo Change"):
            st.success("Demo change request submitted!")

def show_feature_demo(category, feature):
    st.markdown(f"### Interactive Demo: {feature}")
    if category == "📦 Module Management":
        show_module_demo()
    elif category == "🔄 Change Control":
        show_change_request_demo()

# Main navigation
main_menu = st.sidebar.selectbox(
    "Navigation",
    [
        "🏠 Introduction",
        "🎮 Interactive Workflow",
        "📦 Module Management",
        "🔄 Change Control",
        "🎯 Feature Discovery",
        "📚 Knowledge Base"
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

# Main content area
if main_menu == "🏠 Introduction":
    st.header("Welcome to PyPLM")
    
    # Quick start section
    st.subheader("🚀 Quick Start")
    action = st.selectbox(
        "Choose an action to get started:",
        [
            "Select an action...",
            "🎮 Try Interactive Tutorial",
            "📦 Create First Module",
            "🔄 Submit Change Request",
            "📚 Read Documentation"
        ]
    )
    
    if action != "Select an action...":
        if action == "🎮 Try Interactive Tutorial":
            show_feature_demo("Tutorial", "Getting Started")

elif main_menu == "🎯 Feature Discovery":
    st.header("Feature Discovery")
    
    # Feature category selection
    category = st.selectbox(
        "Select a feature category:",
        [
            "Choose a category...",
            "📦 Module Management",
            "🔄 Change Control",
            "🔗 Dependencies",
            "📊 Analytics"
        ]
    )
    
    if category != "Choose a category...":
        # Feature selection based on category
        if category == "📦 Module Management":
            feature = st.selectbox(
                "Select a feature to explore:",
                ["Module Creation", "Version Control", "Templates"]
            )
            show_feature_demo(category, feature)
            
        elif category == "🔄 Change Control":
            feature = st.selectbox(
                "Select a feature to explore:",
                ["Change Request", "Review Process", "Impact Analysis"]
            )
            show_feature_demo(category, feature)
            
        # Progress tracking
        if 'completed_features' not in st.session_state:
            st.session_state.completed_features = set()
            
        if st.button("Mark as Completed"):
            st.session_state.completed_features.add(f"{category} - {feature}")
            st.success("Feature marked as completed!")
            
        # Show completion progress
        if st.session_state.completed_features:
            st.markdown("### 🏆 Completed Features")
            for completed in st.session_state.completed_features:
                st.markdown(f"✅ {completed}")

elif main_menu == "📦 Module Management":
    st.header("Module Management")
    
    tab1, tab2, tab3 = st.tabs(["Create", "Browse", "Settings"])
    
    with tab1:
        show_module_demo()
        
    with tab2:
        st.markdown("### Browse Modules")
        # Add module browsing functionality
        
    with tab3:
        st.markdown("### Module Settings")
        # Add settings functionality

elif main_menu == "🔄 Change Control":
    st.header("Change Control")
    
    tab1, tab2 = st.tabs(["Submit Change", "Review Changes"])
    
    with tab1:
        show_change_request_demo()
        
    with tab2:
        st.markdown("### Review Changes")
        # Add change review functionality

# Debug information (if needed)
if st.sidebar.checkbox("Show Debug Info"):
    st.sidebar.write("Session State:", st.session_state)
