import streamlit as st
import json
from datetime import datetime
import base64
import io
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class PlanSection(Enum):
    PROJECT_INFO = "Project Information"
    ROLES = "Roles and Responsibilities"
    CM_PROCESSES = "CM Processes"
    TOOLS = "Tools and Infrastructure"
    METRICS = "Metrics and Reporting"

@dataclass
class CMPlanConfig:
    """Configuration for CM Plan generation"""
    project_types = [
        "Web Application", "Mobile App", "Desktop Application",
        "Microservices", "API", "Library/Framework", "Enterprise System",
        "Data Pipeline", "ML/AI System", "Other"
    ]
    
    development_methodologies = [
        "Agile/Scrum", "Kanban", "DevOps", "GitFlow",
        "Trunk Based Development", "Feature Branch Workflow",
        "Environment Branch Strategy", "Custom"
    ]
    
    compliance_standards = [
        "ISO 9001", "ISO/IEC 27001", "GDPR", "SOC 2",
        "HIPAA", "PCI DSS", "CMMI", "Other"
    ]
    
    common_tools = [
        "Git", "GitHub", "GitLab", "Bitbucket", "Jenkins", "CircleCI",
        "Travis CI", "Docker", "Kubernetes", "Jira", "Confluence",
        "Azure DevOps", "AWS CodeCommit", "Other"
    ]

class CMPlanGenerator:
    def __init__(self):
        self.config = CMPlanConfig()
        self.initialize_session_state()
        self.setup_page()

    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'plan_data' not in st.session_state:
            st.session_state.plan_data = {
                'project_info': {},
                'roles': {},
                'processes': {},
                'tools': {},
                'metrics': {}
            }
        if 'generated_plan' not in st.session_state:
            st.session_state.generated_plan = None

    def setup_page(self):
        """Configure page layout and styling"""
        st.set_page_config(
            page_title="Software CM Plan Generator",
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

    def render_project_info(self):
        """Render project information section"""
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("📌 Project Information")
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            project_info = {
                'name': st.text_input("Project Name", key="project_name"),
                'type': st.selectbox("Project Type", self.config.project_types, key="project_type"),
                'version': st.text_input("Version/Release", key="version"),
                'methodology': st.selectbox(
                    "Development Methodology",
                    self.config.development_methodologies,
                    key="methodology"
                )
            }
        
        with col2:
            project_info.update({
                'compliance': st.multiselect(
                    "Compliance Requirements",
                    self.config.compliance_standards,
                    key="compliance"
                ),
                'scope': st.text_area("Project Scope", key="scope"),
                'start_date': str(st.date_input("Start Date", key="start_date"))
            })
        
        st.session_state.plan_data['project_info'] = project_info

    def render_roles_section(self):
        """Render roles and responsibilities section"""
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("👥 Roles and Responsibilities")
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            roles = {
                'cm_manager': st.text_input("Configuration Manager", key="cm_manager"),
                'tech_lead': st.text_input("Technical Lead", key="tech_lead"),
                'dev_team': st.text_area("Development Team", key="dev_team")
            }
        
        with col2:
            roles.update({
                'qa_lead': st.text_input("QA Lead", key="qa_lead"),
                'release_manager': st.text_input("Release Manager", key="release_manager"),
                'stakeholders': st.text_area("Key Stakeholders", key="stakeholders")
            })
        
        st.session_state.plan_data['roles'] = roles

    def render_processes_section(self):
        """Render CM processes section"""
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("⚙️ CM Processes")
        st.markdown("</div>", unsafe_allow_html=True)
        
        processes = {}
        
        # Version Control
        st.markdown("#### Version Control")
        processes['version_control'] = {
            'branching_strategy': st.selectbox(
                "Branching Strategy",
                ["GitFlow", "Trunk Based", "Feature Branch", "Custom"],
                key="branch_strategy"
            ),
            'commit_convention': st.text_input(
                "Commit Message Convention",
                key="commit_convention"
            )
        }
        
        # Change Control
        st.markdown("#### Change Control")
        processes['change_control'] = {
            'pr_process': st.checkbox("Pull Request Process", key="pr_process"),
            'review_requirements': st.text_area(
                "Review Requirements",
                key="review_requirements"
            )
        }
        
        # Build and Release
        st.markdown("#### Build and Release")
        processes['build_release'] = {
            'release_cycle': st.selectbox(
                "Release Cycle",
                ["Continuous", "Weekly", "Bi-weekly", "Monthly", "Custom"],
                key="release_cycle"
            ),
            'versioning_scheme': st.text_input(
                "Versioning Scheme",
                key="versioning_scheme"
            )
        }
        
        st.session_state.plan_data['processes'] = processes

    def render_tools_section(self):
        """Render tools and infrastructure section"""
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("🔧 Tools and Infrastructure")
        st.markdown("</div>", unsafe_allow_html=True)
        
        tools = {
            'selected_tools': st.multiselect(
                "Selected Tools",
                self.config.common_tools,
                key="tools"
            ),
            'custom_tools': st.text_area(
                "Custom Tools and Infrastructure",
                key="custom_tools"
            ),
            'automation': st.text_area(
                "Automation and CI/CD",
                key="automation"
            )
        }
        
        st.session_state.plan_data['tools'] = tools

    def generate_markdown_plan(self) -> str:
        """Generate the CM plan in Markdown format"""
        data = st.session_state.plan_data
        
        plan = f"""# Software Configuration Management Plan
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 1. Project Information
- **Project Name:** {data['project_info'].get('name', '')}
- **Project Type:** {data['project_info'].get('type', '')}
- **Version/Release:** {data['project_info'].get('version', '')}
- **Development Methodology:** {data['project_info'].get('methodology', '')}
- **Compliance Requirements:** {', '.join(data['project_info'].get('compliance', []))}
- **Project Scope:** {data['project_info'].get('scope', '')}
- **Start Date:** {data['project_info'].get('start_date', '')}

## 2. Roles and Responsibilities
### Key Personnel
- Configuration Manager: {data['roles'].get('cm_manager', '')}
- Technical Lead: {data['roles'].get('tech_lead', '')}
- QA Lead: {data['roles'].get('qa_lead', '')}
- Release Manager: {data['roles'].get('release_manager', '')}

### Teams
- Development Team: {data['roles'].get('dev_team', '')}
- Stakeholders: {data['roles'].get('stakeholders', '')}

## 3. CM Processes
### Version Control
- Branching Strategy: {data['processes'].get('version_control', {}).get('branching_strategy', '')}
- Commit Convention: {data['processes'].get('version_control', {}).get('commit_convention', '')}

### Change Control
- Pull Request Process: {'Required' if data['processes'].get('change_control', {}).get('pr_process', False) else 'Not Required'}
- Review Requirements: {data['processes'].get('change_control', {}).get('review_requirements', '')}

### Build and Release
- Release Cycle: {data['processes'].get('build_release', {}).get('release_cycle', '')}
- Versioning Scheme: {data['processes'].get('build_release', {}).get('versioning_scheme', '')}

## 4. Tools and Infrastructure
### Selected Tools
{chr(10).join(['- ' + tool for tool in data['tools'].get('selected_tools', [])])}

### Custom Tools and Infrastructure
{data['tools'].get('custom_tools', '')}

### Automation and CI/CD
{data['tools'].get('automation', '')}
"""
        return plan

    def render_export_options(self):
        """Render export options for the generated plan"""
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("📤 Export Options")
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            export_format = st.selectbox(
                "Export Format",
                ["Markdown", "Plain Text", "JSON"],
                key="export_format"
            )
        
        if st.button("Generate and Export Plan"):
            plan_content = self.generate_markdown_plan()
            st.session_state.generated_plan = plan_content
            
            if export_format == "Markdown":
                st.download_button(
                    "Download Markdown",
                    plan_content,
                    file_name=f"cm_plan_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
            elif export_format == "JSON":
                json_content = json.dumps(st.session_state.plan_data, indent=2)
                st.download_button(
                    "Download JSON",
                    json_content,
                    file_name=f"cm_plan_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json"
                )
            else:  # Plain Text
                st.download_button(
                    "Download Text",
                    plan_content,
                    file_name=f"cm_plan_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain"
                )
        
        if st.session_state.generated_plan:
            st.markdown("### Preview")
            st.markdown(st.session_state.generated_plan)

    def run(self):
        """Run the CM Plan Generator application"""
        st.title("📋 Software Configuration Management Plan Generator")
        
        st.markdown("""
        <div class='info-box'>
        This tool helps you generate a comprehensive Configuration Management Plan for your software project.
        Fill out each section below to create your customized CM plan.
        </div>
        """, unsafe_allow_html=True)
        
        # Render all sections
        self.render_project_info()
        self.render_roles_section()
        self.render_processes_section()
        self.render_tools_section()
        self.render_export_options()

def main():
    generator = CMPlanGenerator()
    generator.run()

if __name__ == "__main__":
    main()
