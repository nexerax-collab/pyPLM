import streamlit as st
import pandas as pd
import json
from datetime import datetime
from typing import List, Dict, Tuple, Optional
import uuid
from dataclasses import dataclass
from enum import Enum

# Custom types and data structures
class AuditStatus(Enum):
    PASS = "Pass"
    CONDITIONAL = "Conditional"
    FAIL = "Fail"
    NOT_APPLICABLE = "Not Applicable"

@dataclass
class AuditQuestion:
    id: str
    question: str
    example: str
    category: str

@dataclass
class AuditResponse:
    question_id: str
    rating: str
    comment: str
    timestamp: str
    auditor: str

class AuditConfiguration:
    def __init__(self):
        self.rating_options = ["Yes", "Partial", "No"]
        self.rating_weights = {"Yes": 2, "Partial": 1, "No": 0}
        self.success_threshold = 80
        self.warning_threshold = 50

class AuditManager:
    def __init__(self):
        self.config = AuditConfiguration()
        
    def calculate_score(self, responses: List[Dict]) -> Tuple[float, AuditStatus, str]:
        if not responses:
            return 0, AuditStatus.NOT_APPLICABLE, "No questions answered"
            
        total_possible = len(responses) * 2  # Maximum score possible
        actual_score = sum(self.config.rating_weights[r["Rating"]] for r in responses)
        
        if total_possible == 0:
            return 0, AuditStatus.NOT_APPLICABLE, "No questions answered"
            
        percentage = (actual_score / total_possible) * 100
        
        if percentage >= self.config.success_threshold:
            return percentage, AuditStatus.PASS, "No follow-up needed"
        elif percentage >= self.config.warning_threshold:
            return percentage, AuditStatus.CONDITIONAL, "Review and corrections recommended"
        else:
            return percentage, AuditStatus.FAIL, "Immediate action required"

def init_session_state():
    """Initialize session state variables"""
    if 'project_details' not in st.session_state:
        st.session_state.project_details = {
            'project_name': '',
            'audit_date': datetime.now().date(),
            'auditor': '',
            'scope': '',
            'version': ''
        }
    if 'audit_responses' not in st.session_state:
        st.session_state.audit_responses = {'fca': [], 'pca': []}

def set_page_config():
    """Configure the Streamlit page"""
    st.set_page_config(
        page_title="Software Configuration Audit Tool",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Add custom CSS
    st.markdown("""
        <style>
        .main {max-width: 1200px; padding: 2rem;}
        .stButton button {width: 100%;}
        .audit-header {background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;}
        .status-pass {color: green; font-weight: bold;}
        .status-conditional {color: orange; font-weight: bold;}
        .status-fail {color: red; font-weight: bold;}
        </style>
    """, unsafe_allow_html=True)

def create_sidebar():
    """Create and handle sidebar navigation"""
    st.sidebar.title("Audit Navigation")
    pages = {
        "Introduction": "📚",
        "Project Details": "📋",
        "Functional Configuration Audit": "⚙️",
        "Physical Configuration Audit": "📦",
        "Audit Summary": "📊"
    }
    
    selected_page = st.sidebar.radio(
        "Select Section",
        list(pages.keys()),
        format_func=lambda x: f"{pages[x]} {x}"
    )
    
    return selected_page

def render_introduction():
    """Render the introduction page"""
    st.title("Software Configuration Audit Tool")
    st.markdown("""
    ### Purpose
    This tool supports comprehensive software configuration audits during development 
    and release phases. It follows industry standards including:
    - ISO 10007
    - IEEE 828
    - CMMI Configuration Management
    
    ### Audit Types
    
    #### 🔍 Functional Configuration Audit (FCA)
    Verifies that:
    - Software meets approved requirements
    - Test results demonstrate compliance
    - Development processes were followed
    
    #### 📦 Physical Configuration Audit (PCA)
    Confirms that:
    - Released software matches approved baseline
    - Documentation is complete and accurate
    - All changes are properly tracked and approved
    
    ### How to Use
    1. Complete the Project Details section
    2. Answer all questions in both FCA and PCA sections
    3. Review the summary and export results as needed
    """)

def render_project_details():
    """Render and handle project details form"""
    st.title("Project Details")
    
    with st.form("project_details_form"):
        st.session_state.project_details['project_name'] = st.text_input(
            "Project Name",
            value=st.session_state.project_details.get('project_name', '')
        )
        
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.project_details['audit_date'] = st.date_input(
                "Audit Date",
                value=st.session_state.project_details.get('audit_date', datetime.now().date())
            )
            st.session_state.project_details['version'] = st.text_input(
                "Software Version",
                value=st.session_state.project_details.get('version', '')
            )
        
        with col2:
            st.session_state.project_details['auditor'] = st.text_input(
                "Auditor Name",
                value=st.session_state.project_details.get('auditor', '')
            )
            st.session_state.project_details['scope'] = st.text_area(
                "Audit Scope",
                value=st.session_state.project_details.get('scope', '')
            )
        
        if st.form_submit_button("Save Project Details"):
            st.success("Project details saved successfully!")

def get_fca_questions() -> List[AuditQuestion]:
    """Define FCA questions"""
    return [
        AuditQuestion(
            id=str(uuid.uuid4()),
            question="Is the software's functional baseline documented and under change control?",
            example="Requirements baseline in issue tracking system, versioned specifications",
            category="Requirements"
        ),
        AuditQuestion(
            id=str(uuid.uuid4()),
            question="Is there complete traceability between requirements, code, and tests?",
            example="Traceability matrix showing links between requirements and test cases",
            category="Traceability"
        ),
        AuditQuestion(
            id=str(uuid.uuid4()),
            question="Are all test results complete and reviewed?",
            example="Test execution reports, issue resolution documentation",
            category="Testing"
        ),
        AuditQuestion(
            id=str(uuid.uuid4()),
            question="Have all required reviews and approvals been completed?",
            example="Code review records, approval documentation",
            category="Process"
        ),
        AuditQuestion(
            id=str(uuid.uuid4()),
            question="Is the development environment properly configured and documented?",
            example="Build configuration files, deployment scripts",
            category="Environment"
        )
    ]

def get_pca_questions() -> List[AuditQuestion]:
    """Define PCA questions"""
    return [
        AuditQuestion(
            id=str(uuid.uuid4()),
            question="Is the software baseline complete and properly versioned?",
            example="Tagged release in version control, complete artifact list",
            category="Baseline"
        ),
        AuditQuestion(
            id=str(uuid.uuid4()),
            question="Are all changes properly documented and approved?",
            example="Change request records, approval documentation",
            category="Changes"
        ),
        AuditQuestion(
            id=str(uuid.uuid4()),
            question="Is the documentation current and consistent?",
            example="Updated technical documentation, release notes",
            category="Documentation"
        ),
        AuditQuestion(
            id=str(uuid.uuid4()),
            question="Are all third-party components properly licensed and documented?",
            example="License inventory, compliance documentation",
            category="Licensing"
        ),
        AuditQuestion(
            id=str(uuid.uuid4()),
            question="Is the build and release process documented and repeatable?",
            example="Build instructions, release procedure documentation",
            category="Build"
        )
    ]

def render_audit_section(title: str, questions: List[AuditQuestion], audit_type: str):
    """Render an audit section with questions and capture responses"""
    st.title(title)
    
    responses = []
    for question in questions:
        with st.expander(f"{question.category}: {question.question}"):
            st.caption(f"Example: {question.example}")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                response = st.radio(
                    "Rating:",
                    AuditConfiguration().rating_options,
                    key=f"{question.id}_rating"
                )
            
            with col2:
                comment = st.text_area(
                    "Evidence and Comments:",
                    key=f"{question.id}_comment"
                )
            
            responses.append({
                "Question_ID": question.id,
                "Category": question.category,
                "Question": question.question,
                "Rating": response,
                "Comment": comment,
                "Timestamp": datetime.now().isoformat(),
                "Auditor": st.session_state.project_details.get('auditor', '')
            })
    
    if st.button(f"Save {audit_type} Responses"):
        st.session_state.audit_responses[audit_type.lower()] = responses
        st.success(f"{audit_type} responses saved successfully!")

def render_summary():
    """Render the audit summary page"""
    st.title("Audit Summary")
    
    # Project Information
    st.markdown("### Project Information")
    project_df = pd.DataFrame([st.session_state.project_details])
    st.dataframe(project_df)
    
    # Calculate and display results
    audit_manager = AuditManager()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### FCA Results")
        if st.session_state.audit_responses['fca']:
            fca_score, fca_status, fca_message = audit_manager.calculate_score(
                st.session_state.audit_responses['fca']
            )
            st.metric("FCA Score", f"{fca_score:.1f}%")
            st.markdown(f"Status: **{fca_status.value}**")
            st.info(fca_message)
    
    with col2:
        st.markdown("### PCA Results")
        if st.session_state.audit_responses['pca']:
            pca_score, pca_status, pca_message = audit_manager.calculate_score(
                st.session_state.audit_responses['pca']
            )
            st.metric("PCA Score", f"{pca_score:.1f}%")
            st.markdown(f"Status: **{pca_status.value}**")
            st.info(pca_message)
    
    # Export options
    st.markdown("### Export Options")
    
    col3, col4, col5 = st.columns(3)
    
    with col3:
        if st.button("Export as JSON"):
            export_data = {
                "project_details": st.session_state.project_details,
                "audit_responses": st.session_state.audit_responses,
                "export_date": datetime.now().isoformat()
            }
            st.download_button(
                "Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"audit_report_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    with col4:
        if st.button("Export as CSV"):
            # Combine FCA and PCA responses
            all_responses = (
                pd.DataFrame(st.session_state.audit_responses['fca'] +
                           st.session_state.audit_responses['pca'])
            )
            st.download_button(
                "Download CSV",
                data=all_responses.to_csv(index=False),
                file_name=f"audit_report_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col5:
        if st.button("Export as HTML"):
            # Generate HTML report
            html_content = generate_html_report(
                st.session_state.project_details,
                st.session_state.audit_responses
            )
            st.download_button(
                "Download HTML",
                data=html_content,
                file_name=f"audit_report_{datetime.now().strftime('%Y%m%d')}.html",
                mime="text/html"
            )

def generate_html_report(project_details: Dict, audit_responses: Dict) -> str:
    """Generate an HTML report from the audit data"""
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Software Configuration Audit Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 2rem; }
            .header { background-color: #f8f9fa; padding: 1rem; margin-bottom: 2rem; }
            .section { margin-bottom: 2rem; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 1rem; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f8f9fa; }
            .pass { color: green; }
            .fail { color: red; }
            .conditional { color: orange; }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Software Configuration Audit Report</h1>
            <p>Generated: {date}</p>
        </div>
        
        <div class="section">
            <h2>Project Details</h2>
            {project_details_table}
        </div>
        
        <div class="section">
            <h2>Functional Configuration Audit</h2>
            {fca_table}
        </div>
        
        <div class="section">
            <h2>Physical Configuration Audit</h2>
            {pca_table}
        </div>
    </body>
    </html>
    """
    
    # Convert data to HTML tables
    project_df = pd.DataFrame([project_details])
    fca_df = pd.DataFrame(audit_responses['fca'])
    pca_df = pd.DataFrame(audit_responses['pca'])
    
    return html_template.format(
        date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        project_details_table=project_df.to_html(index=False),
        fca_table=fca_df.to_html(index=False),
        pca_table=pca_df.to_html(index=False)
    )

def main():
    """Main application entry point"""
    init_session_state()
    set_page_config()
    
    selected_page = create_sidebar()
    
    if selected_page == "Introduction":
        render_introduction()
    elif selected_page == "Project Details":
        render_project_details()
    elif selected_page == "Functional Configuration Audit":
        render_audit_section(
            "Functional Configuration Audit (FCA)",
            get_fca_questions(),
            "FCA"
        )
    elif selected_page == "Physical Configuration Audit":
        render_audit_section(
            "Physical Configuration Audit (PCA)",
            get_pca_questions(),
            "PCA"
        )
    else:  # Audit Summary
        render_summary()

if __name__ == "__main__":
    main()
