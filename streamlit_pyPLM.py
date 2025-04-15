import streamlit as st
import pandas as pd
import time
from datetime import datetime

# Initialize page config first
st.set_page_config(
    page_title="PyPLM - Product Lifecycle Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
CURRENT_UTC = "2025-04-15 13:18:19"
CURRENT_USER = "nexerax-collab"

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

# Sidebar navigation - Define this first before any content
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

def show_interactive_intro():
    if st.session_state.session_state['intro_step'] == 0:
        st.markdown("### 🎯 What's your goal today?")
        goal = st.selectbox(
            "Select your primary objective:",
            [
                "Choose a goal...",
                "🏗️ Start a new software project",
                "📈 Improve existing project management",
                "🔄 Learn about change management",
                "📚 Understand PLM concepts"
            ]
        )
        
        if goal != "Choose a goal...":
            st.info(f"Great choice! Let's help you {goal.split(' ', 1)[1]}")
            if st.button("Continue ➡️"):
                st.session_state.session_state['intro_step'] = 1
                st.rerun()
    
    elif st.session_state.session_state['intro_step'] == 1:
        st.markdown("### 📚 Quick PLM Overview")
        concept = st.selectbox(
            "What would you like to learn about first?",
            [
                "What is PLM?",
                "Modules & Components",
                "Change Management",
                "Version Control"
            ]
        )
        
        if concept == "What is PLM?":
            st.info("""
            PLM (Product Lifecycle Management) in software:
            - Manages entire software lifecycle
            - Tracks changes and versions
            - Ensures quality and compliance
            - Facilitates collaboration
            
            Traditional PLM terms in Software:
            - Parts = Modules/Services
            - Assemblies = Systems/Applications
            - Bill of Materials = Dependencies
            """)
        
        if st.button("Next Step ➡️"):
            st.session_state.session_state['intro_step'] = 2
            st.rerun()
    
    elif st.session_state.session_state['intro_step'] == 2:
        st.markdown("### 🛠️ Let's Create Your First Module")
        
        with st.form("first_module"):
            module_name = st.text_input("Module Name", placeholder="my-first-service")
            module_type = st.selectbox(
                "Module Type",
                [
                    "🌐 Microservice",
                    "📚 Library",
                    "🧩 Plugin"
                ]
            )
            description = st.text_area("Description", placeholder="What does this module do?")
            
            submitted = st.form_submit_button("Create Module")
            if submitted and module_name:
                st.success("🎉 Congratulations! You've created your first module!")
                st.session_state.session_state['module_created'] = True
                st.session_state.session_state['intro_step'] = 3
                st.rerun()
    
    elif st.session_state.session_state['intro_step'] == 3:
        st.markdown("### 🎯 Next Steps")
        st.info("""
        Great progress! Here's what you can do next:
        1. Explore Module Management
        2. Learn about Change Control
        3. Check out Analytics
        """)
        
        if st.button("Start Exploring 🚀"):
            st.session_state.session_state['intro_step'] = 4
            st.rerun()
    
    # Show progress
    progress = (st.session_state.session_state['intro_step'] + 1) / 5
    st.progress(progress, f"Progress: {int(progress * 100)}%")

def show_module_management():
    st.header("📦 Module Management")
    tabs = st.tabs(["Create", "Browse", "Learn"])
    
    with tabs[0]:
        show_module_creation()
    
    with tabs[1]:
        show_module_browser()
    
    with tabs[2]:
        show_module_learning()

def show_change_control():
    st.header("🔄 Change Control")
    tabs = st.tabs(["Submit", "Review", "Learn"])
    
    with tabs[0]:
        show_change_submission()
    
    with tabs[1]:
        show_change_review()
    
    with tabs[2]:
        show_change_learning()

def show_analytics():
    st.header("📊 Analytics")
    # Add analytics content here

# Main content router
if main_menu == "🏠 Introduction":
    show_interactive_intro()
elif main_menu == "📦 Module Management":
    show_module_management()
elif main_menu == "🔄 Change Control":
    show_change_control()
elif main_menu == "📊 Analytics":
    show_analytics()

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
