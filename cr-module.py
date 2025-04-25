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
            if st.session_state.get("role") in roles:
                return func(*args, **kwargs)
            else:
                st.warning("Access denied for your role.")
        return wrapper
    return decorator

# === Persistence Helpers ===
DATA_FILE = "change_data.json"

def save_state():
    with open(DATA_FILE, "w") as f:
        json.dump(st.session_state.to_dict(), f)

def load_state():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        for key, value in data.items():
            st.session_state[key] = value

# === Streamlit UI ===
st.set_page_config(page_title="Change Management Workflow", layout="wide")
st.title("🔧 Change Management Workflow")

roles = ["Change Initiator", "Change Coordinator/Manager", "Change Contributors"]

# === Role Selection ===
if "role" not in st.session_state:
    st.session_state.role = None

st.sidebar.header("User Role")
st.session_state.role = st.sidebar.selectbox("Select your role:", roles)
st.sidebar.success(f"Current role: {st.session_state.role}")

load_state()

# === Phase 1: Issue Initialization ===
@role_required("Change Initiator")
def phase_issue():
    st.header("1️⃣ Change Identification / Initialization (Issue)")
    title = st.text_input("Issue Title", key="issue_title")
    if st.button("Initialize Issue"):
        st.session_state.issue = {"title": title, "status": Status.OPEN.name}
        save_state()
    if st.session_state.get("issue"):
        st.write(f"Issue: {st.session_state.issue['title']} - Status: {st.session_state.issue['status']}")
        if st.button("Analyze Issue"):
            st.info("Issue analyzed.")
        if st.button("Issue Disposition"):
            st.success("Issue disposition complete.")
        if st.button("Proceed to CR"):
            st.session_state.cr = {"status": Status.OPEN.name}
            save_state()

# === Phase 2: Change Request ===
@role_required("Change Coordinator/Manager")
def phase_cr():
    st.header("2️⃣ Change Evaluation (CR)")
    if st.session_state.get("cr"):
        st.write(f"CR Status: {st.session_state.cr['status']}")
        if st.button("Analyze CR Impacts"):
            st.info("Impacts analyzed.")
        if st.button("Refine to Functional Level"):
            st.info("Refinement complete.")
        if st.button("Stakeholder Approval"):
            st.session_state.cr['status'] = Status.APPROVED.name
            st.session_state.co = {"status": Status.OPEN.name, "actions": []}
            save_state()

# === Phase 3: Change Order ===
@role_required("Change Coordinator/Manager")
def phase_co():
    st.header("3️⃣ Change Steering and Orchestration/Planning (CO)")
    if st.session_state.get("co"):
        actions_text = st.text_area("Actions (comma separated)", key="co_actions")
        if st.button("Assign Actions"):
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
                if st.button(f"Implement {i}"):
                    action['status'] = Status.COMPLETED.name
            with col2:
                if st.button(f"Validate {i}"):
                    st.info("Validated.")
            with col3:
                if st.button(f"Approve {i}"):
                    action['status'] = Status.APPROVED.name

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

# Run role-specific phases
phase_issue()
phase_cr()
phase_co()
phase_ca()
