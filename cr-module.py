import streamlit as st
from enum import Enum

# === Enums and Classes ===

class Status(Enum):
    OPEN = "Open"
    CLOSED = "Closed"
    APPROVED = "Approved"
    PENDING = "Pending"
    COMPLETED = "Completed"

class ChangeIssue:
    def __init__(self, title):
        self.title = title
        self.status = Status.OPEN

class ChangeRequest:
    def __init__(self, issue):
        self.issue = issue
        self.status = Status.OPEN

class ChangeOrder:
    def __init__(self, cr):
        self.cr = cr
        self.status = Status.OPEN
        self.actions = []

    def assign_actions(self, actions):
        self.actions = [ChangeAction(desc, self) for desc in actions]

    def check_all_actions_closed(self):
        return all(action.status == Status.APPROVED for action in self.actions)

    def complete_and_close(self):
        if self.check_all_actions_closed():
            self.status = Status.CLOSED
            self.cr.status = Status.CLOSED
            self.cr.issue.status = Status.CLOSED

class ChangeAction:
    def __init__(self, description, change_order):
        self.description = description
        self.status = Status.PENDING
        self.change_order = change_order

# === Streamlit UI ===

st.title("🔧 Change Management Workflow")

# Initialize session state
if 'issue' not in st.session_state:
    st.session_state.issue = None
if 'cr' not in st.session_state:
    st.session_state.cr = None
if 'co' not in st.session_state:
    st.session_state.co = None

# Phase 1: Issue Management
with st.expander("1️⃣ Change Identification / Initialization"):
    title = st.text_input("Issue Title", key="issue_title")
    if st.button("Initialize Issue"):
        st.session_state.issue = ChangeIssue(title)
        st.success(f"Issue '{title}' initialized.")

    if st.session_state.issue:
        st.write(f"Issue Status: {st.session_state.issue.status.value}")
        if st.button("Dispose Issue"):
            st.success("Issue dispositioned.")
        if st.button("Proceed to Change Request"):
            st.session_state.cr = ChangeRequest(st.session_state.issue)

# Phase 2: Change Request
with st.expander("2️⃣ Change Request (CR)"):
    if st.session_state.cr:
        st.write("CR is active.")
        if st.button("Approve Stakeholder"):
            st.session_state.cr.status = Status.APPROVED
            st.session_state.co = ChangeOrder(st.session_state.cr)
            st.success("Stakeholder approved. CO initialized.")

# Phase 3: Change Order
with st.expander("3️⃣ Change Order (CO)"):
    if st.session_state.co:
        actions_input = st.text_area("Enter action descriptions (comma separated)", key="actions_text")
        if st.button("Assign Actions"):
            actions = [a.strip() for a in actions_input.split(",") if a.strip()]
            st.session_state.co.assign_actions(actions)
            st.success("Actions assigned.")

        for i, action in enumerate(st.session_state.co.actions):
            st.markdown(f"**Action {i+1}: {action.description}** - {action.status.value}")
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("Implement", key=f"impl_{i}"):
                    action.status = Status.COMPLETED
            with col2:
                if st.button("Validate", key=f"val_{i}"):
                    st.info("Validated.")
            with col3:
                if st.button("Approve", key=f"app_{i}"):
                    action.status = Status.APPROVED
                    if st.session_state.co.check_all_actions_closed():
                        st.session_state.co.complete_and_close()
                        st.success("All actions approved. CO, CR, and Issue closed.")

# Final Status
with st.expander("📦 Final Status"):
    if st.session_state.issue:
        st.write(f"Issue: {st.session_state.issue.status.value}")
    if st.session_state.cr:
        st.write(f"CR: {st.session_state.cr.status.value}")
    if st.session_state.co:
        st.write(f"CO: {st.session_state.co.status.value}")
        for action in st.session_state.co.actions:
            st.write(f"→ CA: {action.description} - {action.status.value}")
