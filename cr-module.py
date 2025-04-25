import streamlit as st
import json
import os
from enum import Enum
from datetime import datetime
import pytz

# === Constants and Enums ===
class Status(Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    APPROVED = "Approved"
    PENDING = "Pending"
    COMPLETED = "Completed"

class Role(Enum):
    INITIATOR = "Change Initiator"
    COORDINATOR = "Change Coordinator/Manager"
    CONTRIBUTOR = "Change Contributors"

# === Session State Management ===
def init_session_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = "nexerax-collab"
    if "current_time" not in st.session_state:
        st.session_state.current_time = "2025-04-25 13:00:05"

# === Authentication Page ===
def show_auth_page():
    st.title("🔐 Role Selection & Authentication")
    
    # Display current user and time
    st.info(f"Current User: {st.session_state.user}")
    st.info(f"Current Time (UTC): {st.session_state.current_time}")
    
    # Role selection
    st.header("Select Your Role")
    
    role_descriptions = {
        Role.INITIATOR.value: """
        **Change Initiator**
        - Identifies and documents new changes
        - Creates initial change requests
        - Provides initial documentation
        """,
        Role.COORDINATOR.value: """
        **Change Coordinator/Manager**
        - Evaluates change requests
        - Plans and coordinates changes
        - Approves change implementations
        """,
        Role.CONTRIBUTOR.value: """
        **Change Contributors**
        - Implements assigned changes
        - Validates changes
        - Updates change status
        """
    }
    
    # Create three columns for role selection
    col1, col2, col3 = st.columns(3)
    
    # Display role cards
    with col1:
        st.markdown(role_descriptions[Role.INITIATOR.value])
        if st.button("Select Initiator Role"):
            st.session_state.role = Role.INITIATOR.value
            st.session_state.authenticated = True
            st.experimental_rerun()
            
    with col2:
        st.markdown(role_descriptions[Role.COORDINATOR.value])
        if st.button("Select Coordinator Role"):
            st.session_state.role = Role.COORDINATOR.value
            st.session_state.authenticated = True
            st.experimental_rerun()
            
    with col3:
        st.markdown(role_descriptions[Role.CONTRIBUTOR.value])
        if st.button("Select Contributor Role"):
            st.session_state.role = Role.CONTRIBUTOR.value
            st.session_state.authenticated = True
            st.experimental_rerun()
    
    # Show currently selected role if any
    if "role" in st.session_state:
        st.success(f"Selected Role: {st.session_state.role}")

# === Role-based Access Control ===
def role_required(*roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not st.session_state.authenticated:
                st.error("Please select a role first.")
                return None
            if st.session_state.role in [r.value for r in roles]:
                return func(*args, **kwargs)
            else:
                st.warning(f"Access denied. Required role(s): {', '.join(r.value for r in roles)}")
                return None
        return wrapper
    return decorator

# === Persistence Helpers ===
DATA_FILE = "change_data.json"

def save_state():
    try:
        state_dict = {
            key: value for key, value in st.session_state.items()
            if not key.startswith('_') and key not in ['authenticated']
        }
        with open(DATA_FILE, "w") as f:
            json.dump(state_dict, f)
    except Exception as e:
        st.error(f"Failed to save state: {str(e)}")

def load_state():
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                data = json.load(f)
            for key, value in data.items():
                if key not in ['authenticated']:
                    st.session_state[key] = value
    except Exception as e:
        st.error(f"Failed to load state: {str(e)}")

# === Main Application ===
def main_app():
    st.title("🔧 Change Management Workflow")
    
    # Show current role and logout option in sidebar
    with st.sidebar:
        st.header("Current Session")
        st.info(f"Role: {st.session_state.role}")
        st.info(f"User: {st.session_state.user}")
        if st.button("Change Role"):
            st.session_state.authenticated = False
            st.experimental_rerun()
    
    # === Phase 1: Issue Initialization ===
    @role_required(Role.INITIATOR)
    def phase_issue():
        st.header("1️⃣ Change Identification / Initialization (Issue)")
        title = st.text_input("Issue Title", key="issue_title")
        if st.button("Initialize Issue", key="init_issue"):
            st.session_state.issue = {"title": title, "status": Status.OPEN.name}
            save_state()
        if st.session_state.get("issue"):
            st.write(f"Issue: {st.session_state.issue['title']} - Status: {st.session_state.issue['status']}")
            if st.button("Analyze Issue", key="analyze_issue"):
                st.info("Issue analyzed.")
            if st.button("Issue Disposition", key="issue_disposition"):
                st.success("Issue disposition complete.")
            if st.button("Proceed to CR", key="proceed_cr"):
                st.session_state.cr = {"status": Status.OPEN.name}
                save_state()

    # === Phase 2: Change Request ===
    @role_required(Role.COORDINATOR)
    def phase_cr():
        st.header("2️⃣ Change Evaluation (CR)")
        if st.session_state.get("cr"):
            st.write(f"CR Status: {st.session_state.cr['status']}")
            if st.button("Analyze CR Impacts", key="analyze_cr"):
                st.info("Impacts analyzed.")
            if st.button("Refine to Functional Level", key="refine_cr"):
                st.info("Refinement complete.")
            if st.button("Stakeholder Approval", key="approve_cr"):
                st.session_state.cr['status'] = Status.APPROVED.name
                st.session_state.co = {"status": Status.OPEN.name, "actions": []}
                save_state()

    # === Phase 3: Change Order ===
    @role_required(Role.COORDINATOR)
    def phase_co():
        st.header("3️⃣ Change Steering and Orchestration/Planning (CO)")
        if st.session_state.get("co"):
            actions_text = st.text_area("Actions (comma separated)", key="co_actions")
            if st.button("Assign Actions", key="assign_actions"):
                actions = [a.strip() for a in actions_text.split(",") if a.strip()]
                st.session_state.co['actions'] = [{"desc": a, "status": Status.PENDING.name} for a in actions]
                save_state()
            if st.session_state.co.get('actions'):
                for i, action in enumerate(st.session_state.co['actions']):
                    st.write(f"Action {i+1}: {action['desc']} - {action['status']}")

    # === Phase 4: Change Actions ===
    @role_required(Role.CONTRIBUTOR)
    def phase_ca():
        st.header("4️⃣ Change Implementation (CA)")
        if st.session_state.get("co") and st.session_state.co.get("actions"):
            for i, action in enumerate(st.session_state.co['actions']):
                st.write(f"CA {i+1}: {action['desc']} - {action['status']}")
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"Implement {i}", key=f"implement_{i}"):
                        action['status'] = Status.COMPLETED.name
                        save_state()
                with col2:
                    if st.button(f"Validate {i}", key=f"validate_{i}"):
                        st.info("Validated.")
                with col3:
                    if st.button(f"Approve {i}", key=f"approve_{i}"):
                        action['status'] = Status.APPROVED.name
                        save_state()

            if all(a['status'] == Status.APPROVED.name for a in st.session_state.co['actions']):
                st.success("All CAs approved.")
                st.session_state.co['status'] = Status.CLOSED.name
                st.session_state.cr['status'] = Status.CLOSED.name
                st.session_state.issue['status'] = Status.CLOSED.name
                save_state()

    # Run phases
    phase_issue()
    phase_cr()
    phase_co()
    phase_ca()
    
    # === Final Status ===
    with st.expander("📦 Final Status"):
        if st.session_state.get("issue"):
            st.write(f"Issue: {st.session_state.issue['title']} - {st.session_state.issue['status']}")
        if st.session_state.get("cr"):
            st.write(f"CR: {st.session_state.cr['status']}")
        if st.session_state.get("co"):
            st.write(f"CO: {st.session_state.co['status']}")
            for a in st.session_state.co.get("actions", []):
                st.write(f"→ CA: {a['desc']} - {a['status']}")

# === Main Application Flow ===
def main():
    init_session_state()
    
    if not st.session_state.authenticated:
        show_auth_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
