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
CURRENT_UTC = "2025-04-15 13:24:32"
CURRENT_USER = "nexerax-collab"

# Initialize session state
if 'session_state' not in st.session_state:
    st.session_state.session_state = {
        'login': CURRENT_USER,
        'session_id': f"SESSION_{int(time.time())}",
        'start_time': CURRENT_UTC,
        'intro_step': 0,
        'completed_steps': set(),
        'changes': [],
        'modules': []
    }

# Helper Functions
def show_plm_context(term, description):
    """Helper function to show PLM terminology context"""
    with st.expander(f"📖 Learn more about {term}"):
        st.markdown(description)

def calculate_risk_score(risks):
    """Calculate risk score based on selected risk areas"""
    risk_weights = {
        "Performance Impact": 3,
        "Security Impact": 4,
        "Data Impact": 3,
        "UI Impact": 2,
        "API Impact": 3
    }
    return sum(risk_weights[risk] for risk in risks)

# Interactive Introduction
def show_interactive_intro():
    st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 1em; border-radius: 5px; margin-bottom: 1em;'>
            <h1 style='margin:0'>PyPLM</h1>
            <p style='color: #666;'>Product Lifecycle Management</p>
            <small style='font-family: monospace;'>
                🕒 {CURRENT_UTC} UTC • 👤 {CURRENT_USER}
            </small>
        </div>
    """, unsafe_allow_html=True)

    # Introduction Text
    st.markdown("""
    ### Welcome to Modern Software PLM
    
    In software development, managing complexity and change is critical—especially when working on large, evolving products. 
    This is where Product Lifecycle Management (PLM) and Configuration Management (CM) come in.
    
    PLM helps track the entire lifecycle of a software product, from initial concept and development to deployment, maintenance, 
    and end-of-life. It ensures everyone involved—from engineers to stakeholders—has a clear view of the current state of the 
    product, helping teams collaborate efficiently and make informed decisions.
    
    CM, a key part of PLM, focuses specifically on managing changes to the software and its related artifacts (like code, 
    documentation, and configurations). It ensures that every version and change is tracked, traceable, and controlled. 
    This prevents issues like code conflicts, missing dependencies, or misaligned releases—common problems in complex 
    development environments.
    
    Together, PLM and CM bring order and visibility to the software development process, enabling better quality, faster 
    delivery, and smoother coordination across teams.
    """)

    step = st.session_state.session_state.get('intro_step', 0)
    
    if step == 0:
        st.markdown("### 🎯 Let's Start Your PLM Journey")
        col1, col2 = st.columns([2,1])
        
        with col1:
            goal = st.selectbox(
                "What would you like to achieve?",
                [
                    "Choose your goal...",
                    "🏗️ Set up PLM for a new project",
                    "📈 Improve existing project management",
                    "🔄 Learn about change management",
                    "📚 Understand PLM concepts"
                ]
            )
            
            if goal != "Choose your goal...":
                st.markdown(f"### Perfect! Let's help you {goal.split('️ ')[1]}")
                if st.button("Begin Journey ➡️"):
                    st.session_state.session_state['intro_step'] = 1
                    st.rerun()
        
        with col2:
            st.info("""
            💡 **Quick Tip**
            Your choice helps us personalize:
            - Learning materials
            - Suggested workflows
            - Practical examples
            """)

    elif step == 1:
        st.markdown("### Understanding Your Context")
        
        col1, col2 = st.columns([3,2])
        with col1:
            experience = st.select_slider(
                "What's your experience with PLM/CM?",
                options=["Beginner", "Some Experience", "Intermediate", "Advanced"],
                value="Beginner"
            )
            
            project_size = st.select_slider(
                "What's your project size?",
                options=["Small", "Medium", "Large", "Enterprise"],
                value="Medium"
            )
            
            focus_areas = st.multiselect(
                "What areas are you most interested in?",
                [
                    "Version Control",
                    "Change Management",
                    "Release Planning",
                    "Documentation",
                    "Compliance",
                    "Team Collaboration"
                ]
            )
        
        with col2:
            st.markdown("""
            ### Why This Matters
            Your context helps us:
            - Customize your learning path
            - Provide relevant examples
            - Focus on your priorities
            - Suggest best practices
            """)
        
        if experience and project_size and focus_areas:
            if st.button("Continue to Learning Path ➡️"):
                st.session_state.session_state['intro_step'] = 2
                st.rerun()

    elif step == 2:
        st.markdown("### Your Personalized Learning Path")
        
        col1, col2 = st.columns([2,1])
        with col1:
            st.markdown("#### Recommended Steps")
            steps_completed = 0
            for i, (step, desc) in enumerate([
                ("PLM Fundamentals", "Understand basic concepts and terminology"),
                ("Module Setup", "Create your first module and understand its lifecycle"),
                ("Change Management", "Learn to track and control changes effectively"),
                ("Progress Tracking", "Monitor and analyze your PLM implementation")
            ], 1):
                if st.checkbox(f"{i}. {step}", help=desc, key=f"step_{i}"):
                    steps_completed += 1
        
        with col2:
            st.markdown("### 🎯 Quick Actions")
            if st.button("📦 Create First Module"):
                st.session_state.session_state['intro_step'] = 3
                st.session_state.session_state['next_section'] = 'module'
                st.rerun()
            if st.button("🔄 Submit Change Request"):
                st.session_state.session_state['intro_step'] = 3
                st.session_state.session_state['next_section'] = 'change'
                st.rerun()
            if st.button("📊 View Analytics"):
                st.session_state.session_state['intro_step'] = 3
                st.session_state.session_state['next_section'] = 'analytics'
                st.rerun()

        # Show progress
        progress = steps_completed / 4
        st.progress(progress, f"Learning Progress: {int(progress * 100)}%")

    else:
        st.success("""
        🎉 **Welcome aboard!**
        
        You're all set to start using PyPLM. Use the navigation menu on the left to:
        - Manage modules
        - Control changes
        - Track progress
        - Learn more about PLM
        """)

# Would you like me to continue with the next part of the implementation?
