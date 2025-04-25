import streamlit as st
import pandas as pd
import time
from datetime import datetime
import uuid
from typing import Dict, List, Optional

# Initialize page config first
st.set_page_config(
    page_title="PyPLM - Product Lifecycle Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
CURRENT_UTC = "2025-04-25 11:38:11"
CURRENT_USER = "nexerax-collab"

# Risk Areas for Change Management
RISK_AREAS = {
    "Performance Impact": 3,
    "Security Impact": 4,
    "Data Impact": 3,
    "UI Impact": 2,
    "API Impact": 3,
    "Documentation Impact": 1,
    "Testing Impact": 2
}

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

def show_module_creation():
    """Show module creation form and handling"""
    st.markdown("### Create New Module")
    
    with st.form("module_creation_form"):
        module_name = st.text_input(
            "Module Name",
            placeholder="e.g., authentication-service"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            module_type = st.selectbox(
                "Module Type",
                [
                    "🌐 Microservice",
                    "📚 Library",
                    "🧩 Plugin",
                    "🔧 Utility",
                    "🎨 UI Component",
                    "🗄️ Data Service",
                    "🔒 Security Module",
                    "📡 API Gateway",
                    "⚙️ Infrastructure",
                    "📊 Analytics Module"
                ]
            )
            
            version = st.text_input(
                "Initial Version",
                placeholder="e.g., 1.0.0",
                value="0.1.0"
            )
        
        with col2:
            status = st.selectbox(
                "Status",
                ["Planning", "Development", "Testing", "Production", "Maintenance"]
            )
            
            priority = st.select_slider(
                "Priority",
                ["Low", "Medium", "High", "Critical"],
                value="Medium"
            )
        
        description = st.text_area(
            "Description",
            placeholder="Describe the purpose and functionality of this module"
        )
        
        dependencies = st.multiselect(
            "Dependencies",
            ["None"] + [m.get('name', '') for m in st.session_state.get('modules', [])]
        )
        
        col3, col4 = st.columns(2)
        with col3:
            owner = st.text_input(
                "Module Owner",
                value=CURRENT_USER
            )
        with col4:
            team = st.text_input(
                "Team",
                placeholder="e.g., Backend Team"
            )
        
        submit_button = st.form_submit_button("Create Module")
        
        if submit_button and module_name:
            new_module = {
                'id': str(uuid.uuid4()),
                'name': module_name,
                'type': module_type,
                'version': version,
                'status': status,
                'priority': priority,
                'description': description,
                'dependencies': dependencies if dependencies != ["None"] else [],
                'owner': owner,
                'team': team,
                'created_at': CURRENT_UTC,
                'created_by': CURRENT_USER,
                'last_updated': CURRENT_UTC
            }
            
            if 'modules' not in st.session_state:
                st.session_state.modules = []
            
            st.session_state.modules.append(new_module)
            st.success(f"Module '{module_name}' created successfully!")
            return True
    
    return False

def show_module_browser():
    """Show module browsing interface"""
    st.markdown("### Browse Modules")
    
    # Filtering options
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.multiselect(
            "Filter by Type",
            list(set(m.get('type', '') for m in st.session_state.get('modules', [])))
        )
    with col2:
        status_filter = st.multiselect(
            "Filter by Status",
            ["Planning", "Development", "Testing", "Production", "Maintenance"]
        )
    with col3:
        search = st.text_input("Search Modules", placeholder="Enter keywords...")
    
    # Get filtered modules
    modules = st.session_state.get('modules', [])
    if type_filter:
        modules = [m for m in modules if m.get('type', '') in type_filter]
    if status_filter:
        modules = [m for m in modules if m.get('status', '') in status_filter]
    if search:
        search_lower = search.lower()
        modules = [m for m in modules if (
            search_lower in m.get('name', '').lower() or
            search_lower in m.get('description', '').lower()
        )]
    
    # Display modules
    if not modules:
        st.info("No modules found. Create your first module using the form above.")
    else:
        for module in modules:
            with st.expander(f"📦 {module['name']} - {module['type']}"):
                col1, col2 = st.columns([2,1])
                
                with col1:
                    st.markdown(f"**Description:** {module['description']}")
                    st.markdown(f"**Version:** {module['version']}")
                    st.markdown(f"**Dependencies:** {', '.join(module['dependencies']) if module['dependencies'] else 'None'}")
                
                with col2:
                    st.markdown(f"**Status:** {module['status']}")
                    st.markdown(f"**Priority:** {module['priority']}")
                    st.markdown(f"**Owner:** {module['owner']}")
                    st.markdown(f"**Team:** {module['team']}")
                
                st.markdown(f"**Created:** {module['created_at']} by {module['created_by']}")
                st.markdown(f"**Last Updated:** {module['last_updated']}")

def show_module_learning():
    """Show module management learning resources"""
    st.markdown("### Learn about Module Management")
    
    with st.expander("📚 What is a Module?"):
        st.markdown("""
        In software PLM, a module is a self-contained unit of software that serves a specific purpose.
        It could be:
        - A microservice
        - A library
        - A plugin
        - A UI component
        - An infrastructure component
        
        Good modules are:
        - Well-defined in scope
        - Loosely coupled
        - Highly cohesive
        - Properly documented
        - Version controlled
        """)
    
    with st.expander("🔍 Module Best Practices"):
        st.markdown("""
        1. **Naming Conventions**
           - Use clear, descriptive names
           - Follow team/organization standards
           - Include version information
        
        2. **Documentation**
           - Clear purpose and functionality
           - Setup and usage instructions
           - Dependencies and requirements
           - API documentation if applicable
        
        3. **Version Control**
           - Use semantic versioning
           - Maintain a changelog
           - Tag releases properly
        
        4. **Dependencies**
           - Minimize external dependencies
           - Use dependency management
           - Keep dependencies updated
        
        5. **Testing**
           - Unit tests
           - Integration tests
           - Performance tests
           - Security tests
        """)
    
    with st.expander("📊 Module Metrics"):
        st.markdown("""
        Key metrics to track:
        1. **Quality Metrics**
           - Code coverage
           - Technical debt
           - Complexity
        
        2. **Performance Metrics**
           - Response time
           - Resource usage
           - Error rates
        
        3. **Development Metrics**
           - Change frequency
           - Lead time
           - MTTR (Mean Time To Recovery)
        """)

def show_change_submission():
    """Show change submission form"""
    st.markdown("### Submit New Change")
    
    with st.form("change_submission_form"):
        title = st.text_input(
            "Change Title",
            placeholder="Brief description of the change"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            change_type = st.selectbox(
                "Change Type",
                [
                    "Feature Request",
                    "Bug Fix",
                    "Enhancement",
                    "Documentation",
                    "Refactoring",
                    "Security Fix",
                    "Performance Improvement",
                    "Dependency Update",
                    "Configuration Change",
                    "Other"
                ]
            )
            
            priority = st.select_slider(
                "Priority",
                ["Low", "Medium", "High", "Critical"],
                value="Medium"
            )
        
        with col2:
            affected_modules = st.multiselect(
                "Affected Modules",
                [m.get('name', '') for m in st.session_state.get('modules', [])]
            )
            
            risk_areas = st.multiselect(
                "Risk Areas",
                list(RISK_AREAS.keys())
            )
        
        description = st.text_area(
            "Detailed Description",
            placeholder="Provide detailed information about the change"
        )
        
        impact_analysis = st.text_area(
            "Impact Analysis",
            placeholder="Describe potential impacts on system, performance, security, etc."
        )
        
        testing_requirements = st.text_area(
            "Testing Requirements",
            placeholder="Specify testing needs for this change"
        )
        
        submit_button = st.form_submit_button("Submit Change")
        
        if submit_button and title and description:
            risk_score = sum(RISK_AREAS[risk] for risk in risk_areas)
            
            new_change = {
                'id': str(uuid.uuid4()),
                'title': title,
                'type': change_type,
                'priority': priority,
                'affected_modules': affected_modules,
                'risk_areas': risk_areas,
                'risk_score': risk_score,
                'description': description,
                'impact_analysis': impact_analysis,
                'testing_requirements': testing_requirements,
                'status': 'Pending Review',
                'created_at': CURRENT_UTC,
                'created_by': CURRENT_USER,
                'last_updated': CURRENT_UTC
            }
            
            if 'changes' not in st.session_state:
                st.session_state.changes = []
            
            st.session_state.changes.append(new_change)
            st.success(f"Change request '{title}' submitted successfully!")
            return True
    
    return False

def show_change_review():
    """Show change review interface"""
    st.markdown("### Review Changes")
    
    # Filtering options
    col1, col2, col3 = st.columns(3)
    with col1:
        type_filter = st.multiselect(
            "Filter by Type",
            list(set(c.get('type', '') for c in st.session_state.get('changes', [])))
        )
    with col2:
        status_filter = st.multiselect(
            "Filter by Status",
            ["Pending Review", "In Review", "Approved", "Rejected", "Implemented"]
        )
    with col3:
        search = st.text_input("Search Changes", placeholder="Enter keywords...")
    
    # Get filtered changes
    changes = st.session_state.get('changes', [])
    if type_filter:
        changes = [c for c in changes if c.get('type', '') in type_filter]
    if status_filter:
        changes = [c for c in changes if c.get('status', '') in status_filter]
    if search:
        search_lower = search.lower()
        changes = [c for c in changes if (
            search_lower in c.get('title', '').lower() or
            search_lower in c.get('description', '').lower()
        )]
    
    # Display changes
    if not changes:
        st.info("No changes found. Submit a new change using the form above.")
    else:
        for change in changes:
            with st.expander(f"🔄 {change['title']} ({change['type']})"):
                col1, col2 = st.columns([2,1])
                
                with col1:
                    st.markdown(f"**Description:** {change['description']}")
                    st.markdown(f"**Affected Modules:** {', '.join(change['affected_modules'])}")
                    st.markdown(f"**Impact Analysis:** {change['impact_analysis']}")
                    st.markdown(f"**Testing Requirements:** {change['testing_requirements']}")
                
                with col2:
                    st.markdown(f"**Status:** {change['status']}")
                    st.markdown(f"**Priority:** {change['priority']}")
                    st.markdown(f"**Risk Score:** {change['risk_score']}")
                    st.markdown(f"**Risk Areas:** {', '.join(change['risk_areas'])}")
                
                st.markdown(f"**Created:** {change['created_at']} by {change['created_by']}")
                st.markdown(f"**Last Updated:** {change['last_updated']}")
                
                # Add review actions if pending
                if change['status'] == 'Pending Review':
                    col3, col4, col5 = st.columns(3)
                    with col3:
                        if st.button("✅ Approve", key=f"approve_{change['id']}"):
                            change['status'] = 'Approved'
                            change['last_updated'] = CURRENT_UTC
                            st.rerun()
                    with col4:
                        if st.button("❌ Reject", key=f"reject_{change['id']}"):
                            change['status'] = 'Rejected'
                            change['last_updated'] = CURRENT_UTC
                            st.rerun()
                    with col5:
                        if st.button("📝 Request Changes", key=f"request_{change['id']}"):
                            change['status'] = 'In Review'
                            change['last_updated'] = CURRENT_UTC
                            st.rerun()

def show_change_learning():
    """Show change management learning resources"""
    st.markdown("### Learn about Change Management")
    
    with st.expander("📚 Understanding Change Management"):
        st.markdown("""
        Change management in software development ensures that:
        - Changes are properly tracked
        - Risks are assessed
        - Impact is understood
        - Proper approvals are obtained
        - Implementation is controlled
        
        Good change management leads to:
        - Reduced risks
        - Better quality
        - Traceable modifications
        - Coordinated updates
        """)
    
    with st.expander("🔍 Change Management Best Practices"):
        st.markdown("""
        1. **Change Request Process**
           - Clear description
           - Impact analysis
           - Risk assessment
           - Testing requirements
        
        2. **Review and Approval**
           - Proper stakeholder review
           - Technical assessment
           - Risk evaluation
           - Documentation review
        
        3. **Implementation**
           - Controlled deployment
           - Proper testing
           - Rollback plans
           - Monitoring
        
        4. **Documentation**
           - Change records
           - Implementation details
           - Test results
           - Sign-offs
        """)
    
    with st.expander("⚖️ Risk Assessment"):
        st.markdown("""
        Consider these factors when assessing change risks:
        
        1. **Impact Areas**
           - Performance
           - Security
           - Data integrity
           - User experience
           - System stability
        
        2. **Risk Levels**
           - Critical: System-wide impact
           - High: Major feature impact
           - Medium: Limited feature impact
           - Low: Minimal impact
        
        3. **Mitigation Strategies**
           - Proper testing
           - Phased rollout
           - Monitoring
           - Rollback procedures
        """)

# Main navigation
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

# Main content router
if main_menu == "🏠 Introduction":
    st.title("Welcome to PyPLM")
    st.markdown("""
    ### Modern Software PLM
    
    Product Lifecycle Management (PLM) helps track the entire lifecycle of your software products,
    from initial concept through development, deployment, and maintenance.
    
    This tool helps you:
    - Manage software modules and components
    - Track changes and their impacts
    - Ensure quality and compliance
    - Monitor project progress
    """)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 Create New Module"):
            main_menu = "📦 Module Management"
            st.rerun()
    with col2:
        if st.button("🔄 Submit Change"):
            main_menu = "🔄 Change Control"
            st.rerun()

elif main_menu == "📦 Module Management":
    tabs = st.tabs(["Create", "Browse", "Learn"])
    
    with tabs[0]:
        show_module_creation()
    
    with tabs[1]:
        show_module_browser()
    
    with tabs[2]:
        show_module_learning()

elif main_menu == "🔄 Change Control":
    tabs = st.tabs(["Submit", "Review", "Learn"])
    
    with tabs[0]:
        show_change_submission()
    
    with tabs[1]:
        show_change_review()
    
    with tabs[2]:
        show_change_learning()

elif main_menu == "📊 Analytics":
    st.title("Analytics Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Module Statistics")
        modules = st.session_state.get('modules', [])
        if modules:
            df_modules = pd.DataFrame(modules)
            st.bar_chart(df_modules['type'].value_counts())
        else:
            st.info("No modules data available")
    
    with col2:
        st.subheader("Change Statistics")
        changes = st.session_state.get('changes', [])
        if changes:
            df_changes = pd.DataFrame(changes)
            st.bar_chart(df_changes['type'].value_counts())
        else:
            st.info("No changes data available")
    
    # Risk Analysis
    st.subheader("Risk Analysis")
    if changes:
        high_risk = len([c for c in changes if c.get('risk_score', 0) > 7])
        medium_risk = len([c for c in changes if 4 <= c.get('risk_score', 0) <= 7])
        low_risk = len([c for c in changes if c.get('risk_score', 0) < 4])
        
        col3, col4, col5 = st.columns(3)
        col3.metric("High Risk Changes", high_risk)
        col4.metric("Medium Risk Changes", medium_risk)
        col5.metric("Low Risk Changes", low_risk)
    else:
        st.info("No risk data available")

elif main_menu == "📚 Learning Resources":
    st.title("Learning Resources")
    
    with st.expander("🎓 PLM Fundamentals"):
        st.markdown("""
        ### Product Lifecycle Management (PLM)
        
        PLM in software development helps manage:
        - Product planning and conception
        - Development and implementation
        - Testing and validation
        - Deployment and maintenance
        - End-of-life and archival
        """)
    
    with st.expander("🔄 Change Management"):
        st.markdown("""
        ### Change Management Best Practices
        
        1. Clear Process Definition
        2. Risk Assessment
        3. Impact Analysis
        4. Review and Approval
        5. Implementation Control
        6. Documentation
        7. Post-implementation Review
        """)
    
    with st.expander("📈 Metrics and KPIs"):
        st.markdown("""
        ### Key Performance Indicators
        
        1. Product Quality Metrics
        2. Development Efficiency
        3. Change Success Rate
        4. Risk Management
        5. Compliance Metrics
        """)

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
