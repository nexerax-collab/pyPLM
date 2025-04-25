import streamlit as st
import json
import os
from enum import Enum

# === Enums and Classes ===

class Status(Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    APPROVED = "Approved"
    PENDING = "Pending"
    COMPLETED = "Completed"

# === Role-based wrapper ===
def role_required(*roles):
    def decorator(func):
        def wrapper(*args, **kwargs):
            current_role = st.session_state.get("role")
            if current_role in roles:
                return func(*args, **kwargs)
            else:
                st.warning(f"Access denied. Required role(s): {', '.join(roles)}. Current role: {current_role}")
        return wrapper
    return decorator

# === Persistence Helpers ===
DATA_FILE = "change_data.json"

def save_state():
    try:
        state_dict = {
            key: value for key, value in st.session_state.items()
            if not key.startswith('_')
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
                st.session_state[key] = value
    except Exception as e:
        st.error(f"Failed to load state: {str(e)}")

# === Streamlit UI ===
st.set_page_config(page_title="Change Management Workflow", layout="wide")
st.title("🔧 Change Management Workflow")

# === Role Selection - MOVED TO TOP AND IMPROVED ===
roles = ["Change Initiator", "Change Coordinator/Manager", "Change Contributors"]

# Initialize role if not present
if "role" not in st.session_state:
    st.session_state["role"] = roles[0]  # Default to first role

# Role selection in sidebar
with st.sidebar:
    st.header("User Role")
    selected_role = st.selectbox(
        "Select your role:",
        options=roles,
        key="role_selector",
        index=roles.index(st.session_state["role"])
    )
    # Update session state role
    st.session_state["role"] = selected_role
    st.success(f"Current role: {selected_role}")

# Load saved state after role initialization
load_state()

# === Phase 1: Issue Initialization ===
@role_required("Change Initiator")
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
@role_required("Change Coordinator/Manager")
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
@role_required("Change Coordinator/Manager")
def phase_co():
    st.header("3️⃣ Change Steering and Orchestration/Planning (CO)")
    if st.session_state.get("co"):
        actions_text = st.text_area("Actions (comma separated)", key="co_actions")
        if st.button("Assign Actions", key="assign_actions"):
            actions = [a.strip() for a in actions_text.split(",") if a.strip()]
            st.session_state.co['actions'] = [{"desc": a, "status": Status.PENDING.name} for a in actions]
            save_state()
        for i, action in enumerate(st.session_state.co['actions']):
            st.write(f"Action {i+1}: {action['desc']} - {action['status']}")

# === Phase 4: Change Actions ===
@role_required("Change Contributors")
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

        # Auto-close CO/CR/Issue if all actions approved
        if all(a['status'] == Status.APPROVED.name for a in st.session_state.co['actions']):
            st.success("All CAs approved.")
            st.session_state.co['status'] = Status.CLOSED.name
            st.session_state.cr['status'] = Status.CLOSED.name
            st.session_state.issue['status'] = Status.CLOSED.name
            save_state()

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

# Debug information
with st.expander("🔍 Debug Information"):
    st.write("Session State:", {k: v for k, v in st.session_state.items() if not k.startswith('_')})
    st.write("Current Role:", st.session_state.get("role"))

# Run role-specific phases
phase_issue()
phase_cr()
phase_co()
phase_ca()
