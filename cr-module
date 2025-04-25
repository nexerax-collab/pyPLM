import streamlit as st
from enum import Enum


# Define Enums and Classes
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
        st.write(f"Issue initialized: {self.title}")

    def analyze(self):
        st.write("Analyzing issue...")

    def dispose(self):
        st.write("Disposing issue...")

    def close(self):
        st.write("Closing issue.")
        self.status = Status.CLOSED


class ChangeRequest:
    def __init__(self, issue):
        self.issue = issue
        self.status = Status.OPEN
        st.write("Change Request initialized.")

    def analyze_impacts(self):
        st.write("Analyzing CR impacts...")

    def refine_functional_level(self):
        st.write("Refining IA to functional level...")

    def approve_by_stakeholders(self):
        st.write("Stakeholder approved.")
        self.status = Status.APPROVED

    def close(self):
        st.write("Closing Change Request.")
        self.status = Status.CLOSED
        self.issue.close()


class ChangeOrder:
    def __init__(self, change_request):
        self.cr = change_request
        self.status = Status.OPEN
        self.actions = []
        st.write("Change Order initialized.")

    def assign_actions(self, action_descriptions):
        self.actions = [ChangeAction(desc, self) for desc in action_descriptions]
        st.write(f"Assigned actions: {action_descriptions}")

    def check_all_actions_closed(self):
        return all(action.status == Status.APPROVED for action in self.actions)

    def complete_and_close(self):
        if self.check_all_actions_closed():
            st.write("All CAs approved. Closing Change Order.")
            self.status = Status.CLOSED
            self.cr.close()
        else:
            st.write("Not all CAs are approved yet.")


class ChangeAction:
    def __init__(self, description, change_order):
        self.description = description
        self.status = Status.PENDING
        self.change_order = change_order
        st.write(f"Initialized CA: {description}")

    def implement(self):
        st.write(f"Implementing: {self.description}")
        self.status = Status.COMPLETED

    def validate(self):
        st.write(f"Validating: {self.description}")

    def approve(self):
        st.write(f"Approving: {self.description}")
        self.status = Status.APPROVED

        # Check if all actions are approved and close CO if so
        if self.change_order.check_all_actions_closed():
            self.change_order.complete_and_close()


# Streamlit App UI
def main():
    st.title("Change Management Workflow")
    st.sidebar.title("Workflow Steps")

    if st.sidebar.button("Initialize Issue"):
        issue = ChangeIssue("Upgrade obsolete connector")
        st.session_state['issue'] = issue

    if 'issue' in st.session_state:
        issue = st.session_state['issue']
        if st.sidebar.button("Analyze Issue"):
            issue.analyze()
        if st.sidebar.button("Dispose Issue"):
            issue.dispose()

        if st.sidebar.button("Proceed to Change Request"):
            cr = ChangeRequest(issue)
            st.session_state['cr'] = cr

    if 'cr' in st.session_state:
        cr = st.session_state['cr']
        if st.sidebar.button("Analyze Impacts"):
            cr.analyze_impacts()
        if st.sidebar.button("Refine Functional Level"):
            cr.refine_functional_level()
        if st.sidebar.button("Approve by Stakeholders"):
            cr.approve_by_stakeholders()

        if st.sidebar.button("Proceed to Change Order"):
            co = ChangeOrder(cr)
            st.session_state['co'] = co

    if 'co' in st.session_state:
        co = st.session_state['co']
        if st.sidebar.button("Assign Actions"):
            actions = ["Update connector specs", "Revise BOM", "Change documentation"]
            co.assign_actions(actions)

        for action in co.actions:
            if st.sidebar.button(f"Implement {action.description}"):
                action.implement()
            if st.sidebar.button(f"Validate {action.description}"):
                action.validate()
            if st.sidebar.button(f"Approve {action.description}"):
                action.approve()


if __name__ == "__main__":
    if "issue" not in st.session_state:
        st.session_state['issue'] = None
    if "cr" not in st.session_state:
        st.session_state['cr'] = None
    if "co" not in st.session_state:
        st.session_state['co'] = None

    main()
