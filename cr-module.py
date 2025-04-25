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
CURRENT_TIME = "2025-04-25 13:09:03"
CURRENT_USER = "nexerax-collab"
DATA_FILE = "change_data.json"

# === Enums ===
class Status(Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    APPROVED = "Approved"
    PENDING = "Pending"
    COMPLETED = "Completed"

# === State Management ===
def save_state():
    state_data = {
        "changes": st.session_state.changes,
        "current_time": CURRENT_TIME,
        "current_user": CURRENT_USER
    }
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(state_data, f, indent=2)
    except Exception as e:
        st.error(f"Failed to save state: {e}")

def load_state():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
                return data.get("changes", {})
        except Exception as e:
            st.error(f"Failed to load state: {e}")
    return {}

# === Session State Initialization ===
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.authenticated = False
    st.session_state.role = None
    st.session_state.changes = load_state()

# === Role Selection Page ===
def show_role_selection():
    st.title("🔐 Role Selection")
    
    st.info(f"Current User: {CURRENT_USER}")
    st.info(f"Current Time (UTC): {CURRENT_TIME}")
    
    st.markdown("### Please select your role to continue")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### Change Initiator
        - Identifies issues
        - Creates initial requests
        - Provides documentation
        """)
        if st.button("👤 Select Initiator", key="btn_initiator"):
            st.session_state.role = "Change Initiator"
            st.session_state.authenticated = True
    
    with col2:
        st.markdown("""
        #### Change Coordinator/Manager
        - Evaluates requests
        - Creates change orders
        - Manages workflow
        """)
        if st.button("👥 Select Coordinator", key="btn_coordinator"):
            st.session_state.role = "Change Coordinator/Manager"
            st.session_state.authenticated = True
    
    with col3:
        st.markdown("""
        #### Change Contributor
        - Implements changes
        - Validates work
        - Updates status
        """)
        if st.button("🛠️ Select Contributor", key="btn_contributor"):
            st.session_state.role = "Change Contributors"
            st.session_state.authenticated = True

def create_change_request():
    with st.form("issue_form"):
        title = st.text_input("Issue Title")
        description = st.text_area("Issue Description")
        impact = st.selectbox("Impact Level", ["Low", "Medium", "High"])
        submitted = st.form_submit_button("Create Issue")
        
        if submitted and title:
            change_id = f"CHG-{len(st.session_state.changes) + 1}"
            st.session_state.changes[change_id] = {
                "id": change_id,
                "title": title,
                "description": description,
                "impact": impact,
                "status": Status.OPEN.value,
                "created_by": CURRENT_USER,
                "created_at": CURRENT_TIME,
                "phase": "Issue",
                "actions": []
            }
            save_state()
            st.success(f"Issue {change_id} created successfully!")

def show_change_list(role):
    st.subheader("Change Requests")
    
    if not st.session_state.changes:
        st.info("No changes found in the system.")
        return
    
    # Filter changes based on role and status
    for change_id, change in st.session_state.changes.items():
        with st.expander(f"{change_id}: {change['title']} ({change['status']})"):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.write(f"**Description:** {change['description']}")
                st.write(f"**Impact:** {change['impact']}")
                st.write(f"**Created by:** {change['created_by']}")
                st.write(f"**Created at:** {change['created_at']}")
                st.write(f"**Current phase:** {change['phase']}")
            
            with col2:
                if role == "Change Coordinator/Manager":
                    if change['phase'] == "Issue" and change['status'] == Status.OPEN.value:
                        if st.button(f"Analyze Impact {change_id}", key=f"analyze_{change_id}"):
                            change['phase'] = "CR"
                            change['status'] = Status.PENDING.value
                            save_state()
                            st.success(f"Change {change_id} moved to CR phase")
                    
                    elif change['phase'] == "CR" and change['status'] == Status.PENDING.value:
                        if st.button(f"Create CO {change_id}", key=f"create_co_{change_id}"):
                            change['phase'] = "CO"
                            change['status'] = Status.OPEN.value
                            save_state()
                            st.success(f"Change Order created for {change_id}")
                
                elif role == "Change Contributors" and change['phase'] == "CO":
                    if st.button(f"Implement {change_id}", key=f"implement_{change_id}"):
                        change['status'] = Status.COMPLETED.value
                        save_state()
                        st.success(f"Change {change_id} marked as completed")
            
            if change['actions']:
                st.write("**Actions:**")
                for action in change['actions']:
                    st.write(f"- {action}")

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
    
    st.title("🔧 Change Management System")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["Change List", "Create Change"])
    
    with tab1:
        show_change_list(st.session_state.role)
    
    with tab2:
        if st.session_state.role == "Change Initiator":
            create_change_request()
        else:
            st.info("Only Change Initiators can create new changes")

# === Main Application Flow ===
def main():
    if not st.session_state.authenticated:
        show_role_selection()
    else:
        show_main_app()

if __name__ == "__main__":
    main()
