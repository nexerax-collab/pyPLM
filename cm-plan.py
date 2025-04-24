import streamlit as st
import json
from datetime import datetime
import io
from dataclasses import dataclass
from enum import Enum
import base64
from typing import Dict, List, Optional
import yaml

# Constants and Configurations
PROJECT_TYPES = [
    "Web Application",
    "Mobile Application",
    "Desktop Application",
    "Cloud Service",
    "API Service",
    "Library/Framework",
    "Data Pipeline",
    "ML/AI System",
    "DevOps Tool",
    "Enterprise System",
    "Microservices",
    "Other"
]

METHODOLOGIES = [
    "Agile/Scrum",
    "Kanban",
    "DevOps",
    "GitFlow",
    "Trunk Based Development",
    "Feature Branch",
    "Environment Branch",
    "Custom"
]

STANDARDS = [
    "ISO 9001",
    "ISO/IEC 27001",
    "GDPR",
    "SOC 2",
    "HIPAA",
    "PCI DSS",
    "CMMI",
    "IEEE",
    "Custom"
]

TOOLS = {
    "Version Control": ["Git", "GitHub", "GitLab", "Bitbucket", "Azure Repos"],
    "CI/CD": ["Jenkins", "GitHub Actions", "GitLab CI", "CircleCI", "Azure Pipelines"],
    "Issue Tracking": ["Jira", "GitHub Issues", "GitLab Issues", "Azure Boards"],
    "Documentation": ["Confluence", "GitHub Wiki", "GitLab Wiki", "ReadTheDocs"],
    "Artifacts": ["Artifactory", "Nexus", "GitHub Packages", "Azure Artifacts"],
    "Monitoring": ["Prometheus", "Grafana", "ELK Stack", "Azure Monitor"],
    "Testing": ["JUnit", "pytest", "Selenium", "Cypress", "k6"],
    "Security": ["SonarQube", "Snyk", "Dependabot", "OWASP ZAP"]
}

class CMSection(Enum):
    OVERVIEW = "Overview"
    ROLES = "Roles and Responsibilities"
    PROCESS = "CM Process"
    TOOLS = "Tools and Infrastructure"
    BASELINE = "Baseline Management"
    RELEASE = "Release Management"
    AUDIT = "Audit and Compliance"

@dataclass
class CMPlanTemplate:
    """Template for generating CM Plan sections"""
    sections: Dict[CMSection, str]
    
    @staticmethod
    def create_default():
        return CMPlanTemplate({
            CMSection.OVERVIEW: """
# Configuration Management Plan
## {project_name}
Generated: {date}

## Overview
This Configuration Management Plan defines the CM activities and controls for {project_name}. 
The plan ensures consistent management of all configuration items throughout the project lifecycle.

### Scope
This plan covers all configuration management activities for {project_name}, including:
- Version control
- Change management
- Build and release processes
- Configuration identification
- Status accounting
- Auditing

### Project Information
- Project Type: {project_type}
- Development Methodology: {methodology}
- Compliance Standards: {standards}
- Start Date: {start_date}
""",
            CMSection.ROLES: """
## Roles and Responsibilities

### Key Roles
- Configuration Manager: {cm_manager}
  - Oversees CM implementation
  - Manages CM infrastructure
  - Ensures compliance with CM procedures

- Technical Lead: {tech_lead}
  - Reviews technical changes
  - Approves architectural decisions
  - Ensures technical standards

- Development Team: {dev_team}
  - Follows CM procedures
  - Implements version control practices
  - Participates in code reviews

### Additional Responsibilities
- QA Lead: {qa_lead}
  - Ensures test artifact management
  - Verifies release quality
  - Maintains test environments

- Release Manager: {release_manager}
  - Coordinates releases
  - Manages release documentation
  - Oversees deployment process
""",
            CMSection.PROCESS: """
## CM Process

### Version Control
- Repository Structure: {repo_structure}
- Branching Strategy: {branch_strategy}
- Commit Guidelines: {commit_guidelines}

### Change Management
- Change Request Process: {cr_process}
- Review Requirements: {review_requirements}
- Approval Workflow: {approval_workflow}

### Build Process
- Build Environment: {build_env}
- Continuous Integration: {ci_process}
- Artifact Management: {artifact_mgmt}
""",
            CMSection.TOOLS: """
## Tools and Infrastructure

### Development Tools
{dev_tools}

### CI/CD Pipeline
{cicd_tools}

### Monitoring and Tracking
{monitoring_tools}

### Documentation and Communication
{doc_tools}
""",
            CMSection.BASELINE: """
## Baseline Management

### Baseline Types
- Development Baselines: {dev_baseline}
- Release Baselines: {release_baseline}
- Production Baselines: {prod_baseline}

### Baseline Control
- Identification: {baseline_id}
- Storage: {baseline_storage}
- Access Control: {access_control}
""",
            CMSection.RELEASE: """
## Release Management

### Release Process
- Release Planning: {release_planning}
- Build Verification: {build_verification}
- Release Approval: {release_approval}
- Distribution: {distribution}

### Version Numbering
{version_scheme}

### Release Documentation
{release_docs}

### Emergency Release Procedure
{emergency_procedure}
""",
            CMSection.AUDIT: """
## Audit and Compliance

### Audit Types
- Internal Audits: {internal_audit}
- External Audits: {external_audit}
- Compliance Checks: {compliance_checks}

### Metrics and Reporting
{metrics}

### Documentation Requirements
{doc_requirements}
"""
        })

class CMPlanGenerator:
    def __init__(self):
        self.template = CMPlanTemplate.create_default()
        self.initialize_session_state()
        self.setup_page()

    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'plan_data' not in st.session_state:
            st.session_state.plan_data = {
                'overview': {},
                'roles': {},
                'process': {},
                'tools': {},
                'baseline': {},
                'release': {},
                'audit': {}
            }
        if 'generated_plan' not in st.session_state:
            st.session_state.generated_plan = None

    def setup_page(self):
        """Configure page layout and styling"""
        st.set_page_config(
            page_title="CM Plan Generator",
            page_icon="📋",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        st.markdown("""
            <style>
            .main { max-width: 1200px; padding: 2rem; }
            .stButton button { width: 100%; }
            .section-header {
                background-color: #f0f2f6;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
            }
            .info-box {
                background-color: #e1f5fe;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
            }
            </style>
        """, unsafe_allow_html=True)

    def render_overview_section(self):
        """Render project overview section"""
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("📌 Project Overview")
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            overview = {
                'project_name': st.text_input("Project Name", key="project_name"),
                'project_type': st.selectbox("Project Type", PROJECT_TYPES, key="project_type"),
                'methodology': st.selectbox("Development Methodology", METHODOLOGIES, key="methodology")
            }
        
        with col2:
            overview.update({
                'standards': st.multiselect("Compliance Standards", STANDARDS, key="standards"),
                'start_date': str(st.date_input("Project Start Date", key="start_date")),
                'description': st.text_area("Project Description", key="description")
            })
        
        st.session_state.plan_data['overview'] = overview

    def render_roles_section(self):
        """Render roles and responsibilities section"""
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("👥 Roles and Responsibilities")
        st.markdown("</div>", unsafe_allow_html=True)
        
        roles = {}
        
        col1, col2 = st.columns(2)
        with col1:
            roles.update({
                'cm_manager': st.text_input("Configuration Manager", key="cm_manager"),
                'tech_lead': st.text_input("Technical Lead", key="tech_lead"),
                'dev_team': st.text_area("Development Team", key="dev_team")
            })
        
        with col2:
            roles.update({
                'qa_lead': st.text_input("QA Lead", key="qa_lead"),
                'release_manager': st.text_input("Release Manager", key="release_manager"),
                'stakeholders': st.text_area("Key Stakeholders", key="stakeholders")
            })
        
        st.session_state.plan_data['roles'] = roles

    def render_process_section(self):
        """Render CM process section"""
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("⚙️ CM Process")
        st.markdown("</div>", unsafe_allow_html=True)
        
        process = {}
        
        # Version Control
        st.markdown("#### Version Control")
        process['version_control'] = {
            'repo_structure': st.text_area(
                "Repository Structure",
                placeholder="Describe your repository organization",
                key="repo_structure"
            ),
            'branch_strategy': st.selectbox(
                "Branching Strategy",
                ["GitFlow", "Trunk Based", "Feature Branch", "Custom"],
                key="branch_strategy"
            ),
            'commit_guidelines': st.text_area(
                "Commit Guidelines",
                placeholder="Describe commit message format and rules",
                key="commit_guidelines"
            )
        }
        
        # Change Management
        st.markdown("#### Change Management")
        process['change_management'] = {
            'cr_process': st.text_area(
                "Change Request Process",
                placeholder="Describe your CR workflow",
                key="cr_process"
            ),
            'review_requirements': st.text_area(
                "Review Requirements",
                placeholder="Describe review criteria",
                key="review_requirements"
            )
        }
        
        st.session_state.plan_data['process'] = process

    def render_tools_section(self):
        """Render tools section"""
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("🔧 Tools and Infrastructure")
        st.markdown("</div>", unsafe_allow_html=True)
        
        tools = {}
        
        for category, tool_list in TOOLS.items():
            st.markdown(f"#### {category}")
            tools[category.lower().replace(' ', '_')] = st.multiselect(
                f"Select {category} Tools",
                tool_list,
                key=f"tools_{category.lower().replace(' ', '_')}"
            )
        
        st.session_state.plan_data['tools'] = tools

    def generate_plan(self) -> str:
        """Generate the complete CM plan"""
        data = st.session_state.plan_data
        
        # Format each section using the template
        plan_sections = []
        for section in CMSection:
            formatted_section = self.template.sections[section].format(
                **data.get(section.name.lower(), {}),
                date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
            plan_sections.append(formatted_section)
        
        return "\n\n".join(plan_sections)

    def export_plan(self, plan_content: str, format: str):
        """Export the plan in various formats"""
        if format == "markdown":
            return plan_content
        elif format == "json":
            return json.dumps(st.session_state.plan_data, indent=2)
        elif format == "yaml":
            return yaml.dump(st.session_state.plan_data, default_flow_style=False)
        else:  # plain text
            return plan_content

    def render_export_section(self):
        """Render export options"""
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("📤 Export Options")
        st.markdown("</div>", unsafe_allow_html=True)
        
        export_format = st.selectbox(
            "Export Format",
            ["markdown", "json", "yaml", "text"],
            key="export_format"
        )
        
        if st.button("Generate Plan"):
            plan_content = self.generate_plan()
            exported_content = self.export_plan(plan_content, export_format)
            
            st.session_state.generated_plan = exported_content
            st.text_area("Preview", exported_content, height=400)
            
            # Create download button
            file_extension = {"markdown": "md", "json": "json", "yaml": "yaml", "text": "txt"}[export_format]
            st.download_button(
                f"Download {export_format.upper()}",
                exported_content,
                file_name=f"cm_plan_{datetime.now().strftime('%Y%m%d')}.{file_extension}",
                mime=f"text/{file_extension}"
            )

    def run(self):
        """Run the CM Plan Generator application"""
        st.title("📋 Configuration Management Plan Generator")
        
        st.markdown("""
        <div class='info-box'>
        Generate a comprehensive Configuration Management Plan for your software project.
        Fill out each section below to create your customized plan.
        </div>
        """, unsafe_allow_html=True)
        
        # Render all sections
        self.render_overview_section()
        self.render_roles_section()
        self.render_process_section()
        self.render_tools_section()
        self.render_export_section()

def main():
    generator = CMPlanGenerator()
    generator.run()

if __name__ == "__main__":
    main()
