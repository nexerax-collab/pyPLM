import streamlit as st
import json
import os
from enum import Enum
from datetime import datetime

# === Basic Configuration ===
st.set_page_config(
    page_title="Change Management System",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === Constants ===
CURRENT_TIME = "2025-04-25 13:05:59"
CURRENT_USER = "nexerax-collab"
DATA_FILE = "change_data.json"

# === Enums ===
class Status(Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    APPROVED = "Approved"
    PENDING = "Pending"
    COMPLETED = "Completed"

# === Session State Initialization ===
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.authenticated = False
    st.session_state.role = None

# === Role Selection Page ===
def show_role_selection():
    st.title("🔐 Role Selection")
    
    # Show current user and time
    st.info(f"Current User: {CURRENT_USER}")
    st.info(f"Current Time (UTC): {CURRENT_TIME}")
    
    st.markdown("### Please select your role to continue")
    
    # Role selection buttons in columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### Change Initiator
        - Creates new changes
        - Documents initial requests
        - Starts the process
        """)
        if st.button("👤 Select Initiator", key="btn_initiator"):
            st.session_state.role = "Change Initiator"
            st.session_state.authenticated = True
    
    with col2:
        st.markdown("""
        #### Change Coordinator
        - Reviews changes
        - Manages workflow
        - Approves steps
        """)
        if st.button("👥 Select Coordinator", key="btn_coordinator"):
            st.session_state.role = "Change Coordinator/Manager"
            st.session_state.authenticated = True
    
    with col3:
        st.markdown("""
        #### Change Contributor
        - Implements changes
        - Updates status
        - Validates work
        """)
        if st.button("🛠️ Select Contributor", key="btn_contributor"):
            st.session_state.role = "Change Contributors"
            st.session_state.authenticated = True

# === Main Application ===
def show_main_app():
    # Sidebar
    with st.sidebar:
        st.header("Session Info")
        st.info(f"Role: {st.session_state.role}")
        st.info(f"User: {CURRENT_USER}")
        st.info(f"Time: {CURRENT_TIME}")
        if st.button("Change Role"):
            st.session_state.authenticated = False
            st.session_state.role = None
            st.rerun()
    
    # Main content
    st.title("🔧 Change Management System")
    
    # Display content based on role
    if st.session_state.role == "Change Initiator":
        show_initiator_view()
    elif st.session_state.role == "Change Coordinator/Manager":
        show_coordinator_view()
    elif st.session_state.role == "Change Contributors":
        show_contributor_view()

def show_initiator_view():
    st.header("1️⃣ Change Initiation")
    
    # Simple form for creating a change request
    with st.form("change_request_form"):
        title = st.text_input("Change Title")
        description = st.text_area("Change Description")
        priority = st.selectbox("Priority", ["Low", "Medium", "High"])
        submitted = st.form_submit_button("Submit Change Request")
        
        if submitted and title:
            st.success(f"Change request '{title}' submitted successfully!")

def show_coordinator_view():
    st.header("2️⃣ Change Coordination")
    
    # Tabs for different coordinator activities
    tab1, tab2 = st.tabs(["Review Changes", "Manage Workflow"])
    
    with tab1:
        st.subheader("Pending Reviews")
        st.info("No pending changes to review")
    
    with tab2:
        st.subheader("Active Workflows")
        st.info("No active workflows")

def show_contributor_view():
    st.header("3️⃣ Change Implementation")
    
    # Simple task view
    st.subheader("Assigned Tasks")
    st.info("No tasks currently assigned")
    
    with st.expander("Completed Tasks"):
        st.write("No completed tasks")

# === Main Application Flow ===
def main():
    if not st.session_state.authenticated:
        show_role_selection()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
