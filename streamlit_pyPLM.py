import streamlit as st
import pandas as pd
from datetime import datetime
import time
import json
from typing import Dict, List, Optional
import uuid

# Initialize page config first
st.set_page_config(
    page_title="PyPLM - Product Lifecycle Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
CURRENT_UTC = "2025-04-25 10:02:34"
CURRENT_USER = "nexerax-collab"

# PLM Module Types
MODULE_TYPES = [
    "Software Component",
    "Documentation",
    "Configuration",
    "API",
    "Test Suite",
    "Infrastructure",
    "Security",
    "UI Component",
    "Database",
    "Other"
]

# Change Types
CHANGE_TYPES = [
    "Feature Request",
    "Bug Fix",
    "Enhancement",
    "Documentation",
    "Refactoring",
    "Security Fix",
    "Performance Improvement",
    "Other"
]

# Risk Areas
RISK_AREAS = {
    "Performance Impact": 3,
    "Security Impact": 4,
    "Data Impact": 3,
    "UI Impact": 2,
    "API Impact": 3,
    "Documentation Impact": 1,
    "Testing Impact": 2
}

class PLMState:
    """Manages PLM application state"""
    def __init__(self):
        if 'plm_state' not in st.session_state:
            st.session_state.plm_state = {
                'login': CURRENT_USER,
                'session_id': f"SESSION_{int(time.time())}",
                'start_time': CURRENT_UTC,
                'intro_step': 0,
                'completed_steps': set(),
                'changes': [],
                'modules': [],
                'current_page': 'intro'
            }
    
    def get_state(self) -> dict:
        return st.session_state.plm_state
    
    def update_state(self, key: str, value: any):
        st.session_state.plm_state[key] = value
    
    def add_module(self, module: dict):
        if 'modules' not in st.session_state.plm_state:
            st.session_state.plm_state['modules'] = []
        st.session_state.plm_state['modules'].append(module)
    
    def add_change(self, change: dict):
        if 'changes' not in st.session_state.plm_state:
            st.session_state.plm_state['changes'] = []
        st.session_state.plm_state['changes'].append(change)
    
    def get_modules(self) -> List[dict]:
        return st.session_state.plm_state.get('modules', [])
    
    def get_changes(self) -> List[dict]:
        return st.session_state.plm_state.get('changes', [])

class PLMNavigation:
    """Handles navigation and page rendering"""
    def __init__(self, state: PLMState):
        self.state = state
        self.pages = {
            'intro': self.render_intro_page,
            'modules': self.render_modules_page,
            'changes': self.render_changes_page,
            'analytics': self.render_analytics_page
        }
    
    def render_header(self):
        st.markdown(f"""
            <div style='background-color: #f0f2f6; padding: 1em; border-radius: 5px; margin-bottom: 1em;'>
                <h1 style='margin:0'>PyPLM</h1>
                <p style='color: #666;'>Product Lifecycle Management</p>
                <small style='font-family: monospace;'>
                    🕒 {CURRENT_UTC} UTC • 👤 {CURRENT_USER}
                </small>
            </div>
        """, unsafe_allow_html=True)
    
    def render_navigation(self):
        st.sidebar.title("Navigation")
        current_page = st.sidebar.radio(
            "Go to",
            ['intro', 'modules', 'changes', 'analytics'],
            format_func=lambda x: x.capitalize()
        )
        self.state.update_state('current_page', current_page)
    
    def render_intro_page(self):
        st.title("Welcome to PyPLM")
        st.markdown("""
        ### Modern Software PLM
        
        Product Lifecycle Management (PLM) and Configuration Management (CM) are essential 
        for managing complex software projects effectively.
        
        This tool helps you:
        - Track software components and their relationships
        - Manage changes and their impacts
        - Monitor project progress and health
        - Ensure compliance and quality
        """)
        
        st.markdown("### Quick Start")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📦 Create New Module"):
                self.state.update_state('current_page', 'modules')
                st.rerun()
                
        with col2:
            if st.button("🔄 Submit Change"):
                self.state.update_state('current_page', 'changes')
                st.rerun()
    
    def render_modules_page(self):
        st.title("Module Management")
        
        # Add new module form
        with st.expander("➕ Add New Module", expanded=True):
            with st.form("new_module_form"):
                module_name = st.text_input("Module Name")
                module_type = st.selectbox("Module Type", MODULE_TYPES)
                description = st.text_area("Description")
                dependencies = st.multiselect(
                    "Dependencies",
                    [m['name'] for m in self.state.get_modules()]
                )
                
                if st.form_submit_button("Add Module"):
                    if module_name and module_type:
                        new_module = {
                            'id': str(uuid.uuid4()),
                            'name': module_name,
                            'type': module_type,
                            'description': description,
                            'dependencies': dependencies,
                            'created_at': CURRENT_UTC,
                            'created_by': CURRENT_USER,
                            'status': 'Active'
                        }
                        self.state.add_module(new_module)
                        st.success(f"Module '{module_name}' added successfully!")
        
        # Display existing modules
        st.markdown("### Existing Modules")
        modules = self.state.get_modules()
        if not modules:
            st.info("No modules created yet. Use the form above to add your first module.")
        else:
            for module in modules:
                with st.expander(f"📦 {module['name']} ({module['type']})"):
                    st.markdown(f"**Description:** {module['description']}")
                    st.markdown(f"**Dependencies:** {', '.join(module['dependencies']) if module['dependencies'] else 'None'}")
                    st.markdown(f"**Created:** {module['created_at']} by {module['created_by']}")
    
    def render_changes_page(self):
        st.title("Change Management")
        
        # Add new change form
        with st.expander("➕ Submit New Change", expanded=True):
            with st.form("new_change_form"):
                change_title = st.text_input("Change Title")
                change_type = st.selectbox("Change Type", CHANGE_TYPES)
                affected_modules = st.multiselect(
                    "Affected Modules",
                    [m['name'] for m in self.state.get_modules()]
                )
                description = st.text_area("Description")
                risk_areas = st.multiselect(
                    "Risk Areas",
                    list(RISK_AREAS.keys())
                )
                
                if st.form_submit_button("Submit Change"):
                    if change_title and change_type:
                        risk_score = sum(RISK_AREAS[risk] for risk in risk_areas)
                        new_change = {
                            'id': str(uuid.uuid4()),
                            'title': change_title,
                            'type': change_type,
                            'description': description,
                            'affected_modules': affected_modules,
                            'risk_areas': risk_areas,
                            'risk_score': risk_score,
                            'status': 'Pending',
                            'created_at': CURRENT_UTC,
                            'created_by': CURRENT_USER
                        }
                        self.state.add_change(new_change)
                        st.success(f"Change '{change_title}' submitted successfully!")
        
        # Display existing changes
        st.markdown("### Change Requests")
        changes = self.state.get_changes()
        if not changes:
            st.info("No changes submitted yet. Use the form above to submit your first change request.")
        else:
            for change in changes:
                with st.expander(f"🔄 {change['title']} ({change['type']})"):
                    st.markdown(f"**Description:** {change['description']}")
                    st.markdown(f"**Affected Modules:** {', '.join(change['affected_modules'])}")
                    st.markdown(f"**Risk Score:** {change['risk_score']}")
                    st.markdown(f"**Status:** {change['status']}")
                    st.markdown(f"**Created:** {change['created_at']} by {change['created_by']}")
    
    def render_analytics_page(self):
        st.title("Analytics & Insights")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Module Statistics")
            modules = self.state.get_modules()
            if modules:
                module_types = pd.DataFrame([{'type': m['type']} for m in modules])
                st.bar_chart(module_types['type'].value_counts())
            else:
                st.info("No modules data available")
        
        with col2:
            st.markdown("### Change Statistics")
            changes = self.state.get_changes()
            if changes:
                change_types = pd.DataFrame([{'type': c['type']} for c in changes])
                st.bar_chart(change_types['type'].value_counts())
            else:
                st.info("No changes data available")
        
        # Risk Analysis
        st.markdown("### Risk Analysis")
        if changes:
            risk_data = pd.DataFrame(changes)
            avg_risk = risk_data['risk_score'].mean()
            st.metric("Average Risk Score", f"{avg_risk:.2f}")
            
            high_risk_changes = risk_data[risk_data['risk_score'] > 7]
            st.warning(f"Number of high-risk changes: {len(high_risk_changes)}")
        else:
            st.info("No risk data available")
    
    def render(self):
        self.render_header()
        self.render_navigation()
        
        current_page = self.state.get_state()['current_page']
        self.pages[current_page]()

def main():
    """Main application entry point"""
    state = PLMState()
    navigation = PLMNavigation(state)
    navigation.render()

if __name__ == "__main__":
    main()
