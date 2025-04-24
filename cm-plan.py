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
CURRENT_USER = "nexerax-collab"
CURRENT_DATE = "2025-04-24 15:11:36"

PROJECT_TYPES = [
    "Web Application", "Mobile Application", "Desktop Application",
    "Cloud Service", "API Service", "Library/Framework",
    "Data Pipeline", "ML/AI System", "DevOps Tool",
    "Enterprise System", "Microservices", "Other"
]

METHODOLOGIES = [
    "Agile/Scrum", "Kanban", "DevOps", "GitFlow",
    "Trunk Based Development", "Feature Branch",
    "Environment Branch", "SAFe", "Hybrid/Custom"
]

CM_STANDARDS = [
    "ISO 10007:2017", 
    "ANSI/EIA-649C:2019",
    "IEEE Std 828-2012",
    "ISO/IEC 12207:2017",
    "ISO 9001:2015",
    "ISO/IEC 27001",
    "GDPR",
    "SOC 2",
    "HIPAA",
    "PCI DSS",
    "CMMI",
    "Other"
]

TOOLS = {
    "Version Control": [
        "Git", "GitHub", "GitLab", "Bitbucket", "Azure Repos",
        "Perforce", "SVN", "Other"
    ],
    "CI/CD": [
        "Jenkins", "GitHub Actions", "GitLab CI", "CircleCI",
        "Azure Pipelines", "TeamCity", "Bamboo", "Other"
    ],
    "Issue Tracking": [
        "Jira", "GitHub Issues", "GitLab Issues", "Azure Boards",
        "Linear", "YouTrack", "Other"
    ],
    "Documentation": [
        "Confluence", "GitHub Wiki", "GitLab Wiki", "ReadTheDocs",
        "Docusaurus", "MkDocs", "Other"
    ],
    "Requirements": [
        "Jira", "Azure DevOps", "PolarionALM", "DOORS NG",
        "Helix RM", "Other"
    ],
    "Build & Artifacts": [
        "Maven", "Gradle", "npm", "pip",
        "Artifactory", "Nexus", "GitHub Packages",
        "Docker Hub", "Other"
    ],
    "Testing": [
        "JUnit", "pytest", "Jest", "Cypress",
        "Selenium", "k6", "Postman", "Other"
    ],
    "Code Quality": [
        "SonarQube", "ESLint", "Checkstyle", "PMD",
        "CodeClimate", "Other"
    ],
    "Security": [
        "Snyk", "Dependabot", "OWASP ZAP", "Fortify",
        "BlackDuck", "Other"
    ]
}

BASELINE_TYPES = {
    "Development": "Internal working baselines created during development iterations",
    "Integration": "Baselines for system integration testing",
    "Release": "Formal baselines for customer or production delivery",
    "Production": "Final validated baseline for deployment"
}

CHANGE_TYPES = {
    "Emergency": "Critical fixes requiring immediate attention",
    "Standard": "Normal changes following standard process",
    "Major": "Significant changes requiring full CCB review"
}

class CMPlanSection:
    def __init__(self, title: str, key: str, icon: str):
        self.title = title
        self.key = key
        self.icon = icon

class CMPlanGenerator:
    def __init__(self):
        self.initialize_session_state()
        self.setup_page()

    def initialize_session_state(self):
        if 'plan_data' not in st.session_state:
            st.session_state.plan_data = {
                'metadata': {
                    'generated_date': CURRENT_DATE,
                    'generated_by': CURRENT_USER
                },
                'overview': {},
                'roles': {},
                'identification': {},
                'change_control': {},
                'status_accounting': {},
                'audit': {},
                'version_control': {},
                'release': {},
                'tools': {}
            }

    def setup_page(self):
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
            .warning-box {
                background-color: #fff3e0;
                padding: 1rem;
                border-radius: 0.5rem;
                margin: 1rem 0;
            }
            </style>
        """, unsafe_allow_html=True)

    def render_overview_section(self):
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("📌 Project Overview")
        st.markdown("</div>", unsafe_allow_html=True)
        
        overview = {}
        
        col1, col2 = st.columns(2)
        with col1:
            overview.update({
                'project_name': st.text_input("Project Name", key="project_name"),
                'project_type': st.selectbox("Project Type", PROJECT_TYPES, key="project_type"),
                'methodology': st.selectbox("Development Methodology", METHODOLOGIES, key="methodology"),
                'start_date': str(st.date_input("Project Start Date", key="start_date"))
            })
        
        with col2:
            overview.update({
                'standards': st.multiselect("Compliance Standards", CM_STANDARDS, key="standards"),
                'description': st.text_area("Project Description", key="description", height=100),
                'scope': st.text_area("Project Scope", key="scope", height=100)
            })
        
        st.session_state.plan_data['overview'] = overview

    def render_roles_section(self):
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("👥 Roles and Responsibilities")
        st.markdown("</div>", unsafe_allow_html=True)
        
        roles = {}
        
        col1, col2 = st.columns(2)
        with col1:
            roles.update({
                'cm_manager': st.text_input("Configuration Manager", key="cm_manager"),
                'tech_lead': st.text_input("Technical Lead", key="tech_lead"),
                'dev_team': st.text_area("Development Team", key="dev_team", height=100)
            })
        
        with col2:
            roles.update({
                'qa_lead': st.text_input("QA Lead", key="qa_lead"),
                'release_manager': st.text_input("Release Manager", key="release_manager"),
                'stakeholders': st.text_area("Key Stakeholders", key="stakeholders", height=100)
            })
        
        st.markdown("### CCB Structure")
        roles['ccb'] = st.text_area(
            "Configuration Control Board (CCB) Members and Responsibilities",
            key="ccb",
            height=150
        )
        
        st.session_state.plan_data['roles'] = roles

    def render_identification_section(self):
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("🏷️ Configuration Identification")
        st.markdown("</div>", unsafe_allow_html=True)
        
        identification = {}
        
        st.markdown("### Configuration Items")
        col1, col2 = st.columns(2)
        
        with col1:
            identification['naming_convention'] = st.text_area(
                "Naming Conventions",
                placeholder="Describe your naming conventions for different types of artifacts",
                key="naming_convention",
                height=100
            )
            identification['version_scheme'] = st.text_area(
                "Version Numbering Scheme",
                placeholder="Describe your versioning scheme (e.g., SemVer)",
                key="version_scheme",
                height=100
            )
        
        with col2:
            identification['baseline_types'] = st.multiselect(
                "Baseline Types",
                list(BASELINE_TYPES.keys()),
                key="baseline_types",
                help="\n".join([f"{k}: {v}" for k, v in BASELINE_TYPES.items()])
            )
        
        st.markdown("### CI Structure")
        identification['ci_structure'] = st.text_area(
            "Configuration Item Structure",
            placeholder="Describe how CIs are organized and related",
            key="ci_structure",
            height=150
        )
        
        st.session_state.plan_data['identification'] = identification

    def render_change_control_section(self):
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("🔄 Change Control")
        st.markdown("</div>", unsafe_allow_html=True)
        
        change_control = {}
        
        st.markdown("### Change Request Process")
        change_control['cr_process'] = st.text_area(
            "Change Request Workflow",
            placeholder="Describe your CR process from submission to implementation",
            key="cr_process",
            height=150
        )
        
        col1, col2 = st.columns(2)
        with col1:
            change_control['change_types'] = st.multiselect(
                "Change Types",
                list(CHANGE_TYPES.keys()),
                key="change_types",
                help="\n".join([f"{k}: {v}" for k, v in CHANGE_TYPES.items()])
            )
            
            change_control['emergency_process'] = st.text_area(
                "Emergency Change Process",
                placeholder="Describe your process for handling urgent changes",
                key="emergency_process",
                height=100
            )
        
        with col2:
            change_control['review_requirements'] = st.text_area(
                "Review Requirements",
                placeholder="Describe your review criteria and process",
                key="review_requirements",
                height=100
            )
            
            change_control['approval_workflow'] = st.text_area(
                "Approval Workflow",
                placeholder="Describe your change approval workflow",
                key="approval_workflow",
                height=100
            )
        
        st.session_state.plan_data['change_control'] = change_control

    def render_tools_section(self):
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("🔧 Tools and Infrastructure")
        st.markdown("</div>", unsafe_allow_html=True)
        
        tools = {}
        
        for category, tool_list in TOOLS.items():
            st.markdown(f"#### {category}")
            selected_tools = st.multiselect(
                f"Select {category} Tools",
                tool_list,
                key=f"tools_{category.lower().replace(' ', '_')}"
            )
            
            if "Other" in selected_tools:
                other_tools = st.text_input(
                    f"Other {category} Tools",
                    key=f"other_tools_{category.lower().replace(' ', '_')}"
                )
                if other_tools:
                    selected_tools.remove("Other")
                    selected_tools.extend([tool.strip() for tool in other_tools.split(",")])
            
            tools[category] = selected_tools
        
        st.session_state.plan_data['tools'] = tools

    def render_release_section(self):
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("📦 Release Management")
        st.markdown("</div>", unsafe_allow_html=True)
        
        release = {}
        
        col1, col2 = st.columns(2)
        with col1:
            release['release_types'] = st.text_area(
                "Release Types",
                placeholder="Describe your different types of releases",
                key="release_types",
                height=100
            )
            
            release['release_schedule'] = st.text_area(
                "Release Schedule",
                placeholder="Describe your release cadence and planning",
                key="release_schedule",
                height=100
            )
        
        with col2:
            release['release_process'] = st.text_area(
                "Release Process",
                placeholder="Describe your release workflow",
                key="release_process",
                height=100
            )
            
            release['deployment_process'] = st.text_area(
                "Deployment Process",
                placeholder="Describe your deployment strategy",
                key="deployment_process",
                height=100
            )
        
        st.markdown("### Release Documentation")
        release['documentation'] = st.text_area(
            "Documentation Requirements",
            placeholder="Describe required documentation for releases",
            key="release_documentation",
            height=150
        )
        
        st.session_state.plan_data['release'] = release

    def generate_plan(self) -> str:
        data = st.session_state.plan_data
        
        # Create the complete plan
        plan = f"""# Configuration Management Plan
## {data['overview'].get('project_name', '[Project Name]')}

Generated on: {data['metadata']['generated_date']}
Generated by: {data['metadata']['generated_by']}

## 1. Introduction

This Configuration Management Plan defines how configuration management activities are conducted for {data['overview'].get('project_name', '[Project Name]')}.

### Scope
{data['overview'].get('scope', '')}

### Project Overview
- Project Type: {data['overview'].get('project_type', '')}
- Development Methodology: {data['overview'].get('methodology', '')}
- Start Date: {data['overview'].get('start_date', '')}

### Compliance Standards
{', '.join(data['overview'].get('standards', []))}

## 2. Roles and Responsibilities

### Key Roles
- Configuration Manager: {data['roles'].get('cm_manager', '')}
- Technical Lead: {data['roles'].get('tech_lead', '')}
- QA Lead: {data['roles'].get('qa_lead', '')}
- Release Manager: {data['roles'].get('release_manager', '')}

### Teams
Development Team:
{data['roles'].get('dev_team', '')}

Stakeholders:
{data['roles'].get('stakeholders', '')}

### CCB Structure
{data['roles'].get('ccb', '')}

## 3. Configuration Identification

### Naming Conventions
{data['identification'].get('naming_convention', '')}

### Version Numbering
{data['identification'].get('version_scheme', '')}

### Baseline Types
{', '.join(data['identification'].get('baseline_types', []))}

### CI Structure
{data['identification'].get('ci_structure', '')}

## 4. Change Control

### Change Request Process
{data['change_control'].get('cr_process', '')}

### Change Types
{', '.join(data['change_control'].get('change_types', []))}

### Emergency Process
{data['change_control'].get('emergency_process', '')}

### Review Requirements
{data['change_control'].get('review_requirements', '')}

## 5. Tools and Infrastructure

"""
        # Add tools section
        for category, tools in data['tools'].items():
            if tools:
                plan += f"\n### {category}\n"
                for tool in tools:
                    plan += f"- {tool}\n"

        plan += f"""
## 6. Release Management

### Release Types
{data['release'].get('release_types', '')}

### Release Schedule
{data['release'].get('release_schedule', '')}

### Release Process
{data['release'].get('release_process', '')}

### Deployment Process
{data['release'].get('deployment_process', '')}

### Documentation Requirements
{data['release'].get('documentation', '')}
"""
        
        return plan

    def export_plan(self, format: str) -> tuple[str, str]:
        """Generate the plan in the specified format"""
        if format == "markdown":
            content = self.generate_plan()
            filename = f"cm_plan_{datetime.now().strftime('%Y%m%d')}.md"
        elif format == "json":
            content = json.dumps(st.session_state.plan_data, indent=2)
            filename = f"cm_plan_{datetime.now().strftime('%Y%m%d')}.json"
        elif format == "yaml":
            content = yaml.dump(st.session_state.plan_data, default_flow_style=False)
            filename = f"cm_plan_{datetime.now().strftime('%Y%m%d')}.yaml"
        else:  # plain text
            content = self.generate_plan()
            filename = f"cm_plan_{datetime.now().strftime('%Y%m%d')}.txt"
        
        return content, filename

    def render_export_section(self):
        st.markdown("<div class='section-header'>", unsafe_allow_html=True)
        st.subheader("📤 Export Options")
        st.markdown("</div>", unsafe_allow_html=True)
        
        export_format = st.selectbox(
            "Export Format",
            ["markdown", "json", "yaml", "text"],
            key="export_format"
        )
        
        if st.button("Generate Plan"):
            content, filename = self.export_plan(export_format)
            
            st.session_state.generated_plan = content
            st.text_area("Preview", content, height=400)
            
            st.download_button(
                f"Download {export_format.upper()}",
                content,
                file_name=filename,
                mime=f"text/{export_format}"
            )

    def run(self):
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
        self.render_identification_section()
        self.render_change_control_section()
        self.render_tools_section()
        self.render_release_section()
        self.render_export_section()

def main():
    generator = CMPlanGenerator()
    generator.run()

if __name__ == "__main__":
    main()
