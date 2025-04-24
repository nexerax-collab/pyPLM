import streamlit as st
import base64
from datetime import datetime
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from docx import Document
import json

# Initialize session state if not exists
if 'generated_plan' not in st.session_state:
    st.session_state.generated_plan = ""

def init_styles():
    st.set_page_config(
        page_title="CM Plan Generator",
        page_icon="🔧",
        layout="wide"
    )
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
        }
        .stSelectbox, .stMultiSelect {
            margin-bottom: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

def generate_pdf(content):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    y = 750  # Starting y position
    
    for line in content.split('\n'):
        if y < 50:  # Check if we need a new page
            c.showPage()
            y = 750
        c.drawString(50, y, line)
        y -= 15
    
    c.save()
    return buffer

def generate_docx(content):
    doc = Document()
    doc.add_heading('Configuration Management Plan', 0)
    
    for paragraph in content.split('\n\n'):
        if paragraph.strip():
            doc.add_paragraph(paragraph)
    
    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer

def generate_confluence_text(content):
    # Convert the content to Confluence wiki markup
    confluence_content = f"h1. Configuration Management Plan\n\n{content}"
    return confluence_content

def get_download_link(buffer, filename, display_text):
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{display_text}</a>'

def main():
    init_styles()
    st.title("Configuration Management Plan Generator")
    
    with st.container():
        st.subheader("1. Project & General Info")
        col1, col2 = st.columns(2)
        
        with col1:
            project_name = st.text_input("Project Name")
            ecu_type = st.selectbox(
                "ECU Type / Domain",
                ["Powertrain", "Chassis", "Infotainment", "Body Electronics", "ADAS", "Other"]
            )
            dev_lifecycle = st.selectbox(
                "Development Lifecycle",
                ["V-model", "Agile", "ASPICE", "Hybrid"]
            )
        
        with col2:
            compliance_target = st.multiselect(
                "Compliance Target",
                ["ISO 10007", "EIA-649C", "ASPICE", "ISO 26262", "Other"]
            )
            cm_tools = st.multiselect(
                "CM Tools Used",
                ["Git", "SVN", "DOORS", "Polarion", "Jira", "Jenkins", "Other"]
            )
            release_type = st.selectbox(
                "Release Type",
                ["Internal", "Customer Delivery", "Production"]
            )

    st.subheader("2. Roles & Responsibilities")
    col3, col4 = st.columns(2)
    
    with col3:
        cm_manager = st.text_input("Configuration Manager")
        project_manager = st.text_input("Project Manager")
        dev_qa_leads = st.text_input("Dev/QA Leads")
    
    with col4:
        use_ccb = st.checkbox("Is a CCB Used?")
        if use_ccb:
            ccb_description = st.text_area("CCB Description")

    st.subheader("3. CM Domains")
    col5, col6 = st.columns(2)
    
    with col5:
        config_id = st.checkbox("Configuration Identification")
        if config_id:
            config_id_details = st.text_area("Configuration Identification Details")
        
        change_control = st.checkbox("Change Control")
        if change_control:
            change_control_type = st.selectbox(
                "Change Control Process",
                ["Agile (Backlog/Grooming)", "V-model (CCB forms)", "Custom"]
            )
        
        status_accounting = st.checkbox("Status Accounting")
        if status_accounting:
            reporting_cadence = st.selectbox(
                "Reporting Cadence",
                ["Weekly", "Bi-weekly", "Monthly", "Sprint-based"]
            )
    
    with col6:
        version_control = st.checkbox("Version Control")
        if version_control:
            vcs_system = st.selectbox("Version Control System", ["Git", "SVN"])
            branch_strategy = st.text_area("Branching Strategy")
        
        baseline_strategy = st.radio(
            "Baseline Strategy",
            ["Sprint-based", "Milestone-based", "Product-based"]
        )

    st.subheader("4. Output Options")
    col7, col8 = st.columns(2)
    
    with col7:
        include_glossary = st.checkbox("Include Glossary")
        output_format = st.selectbox(
            "Document Format",
            ["PDF", "Word (DOCX)", "Confluence", "Plain Text"]
        )
    
    with col8:
        output_language = st.selectbox(
            "Output Language",
            ["English", "German"]
        )

    if st.button("Generate CM Plan"):
        # Generate plan content based on inputs
        plan_content = f"""
Configuration Management Plan
Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

1. Project Information
Project Name: {project_name}
ECU Type/Domain: {ecu_type}
Development Lifecycle: {dev_lifecycle}
Compliance Targets: {', '.join(compliance_target)}
CM Tools: {', '.join(cm_tools)}
Release Type: {release_type}

2. Roles and Responsibilities
Configuration Manager: {cm_manager}
Project Manager: {project_manager}
Dev/QA Leads: {dev_qa_leads}
{"CCB Information: " + ccb_description if use_ccb else "No CCB Used"}

3. CM Domains
{"Configuration Identification: " + config_id_details if config_id else ""}
{"Change Control Process: " + change_control_type if change_control else ""}
{"Status Accounting - Reporting Cadence: " + reporting_cadence if status_accounting else ""}
{"Version Control System: " + vcs_system if version_control else ""}
Baseline Strategy: {baseline_strategy}
        """
        
        st.session_state.generated_plan = plan_content
        st.text_area("Generated Plan", plan_content, height=300)
        
        # Generate download options based on selected format
        if output_format == "PDF":
            pdf_buffer = generate_pdf(plan_content)
            st.markdown(
                get_download_link(pdf_buffer, "cm_plan.pdf", "Download PDF"),
                unsafe_allow_html=True
            )
        elif output_format == "Word (DOCX)":
            docx_buffer = generate_docx(plan_content)
            st.markdown(
                get_download_link(docx_buffer, "cm_plan.docx", "Download DOCX"),
                unsafe_allow_html=True
            )
        elif output_format == "Confluence":
            confluence_content = generate_confluence_text(plan_content)
            st.text_area("Confluence Format", confluence_content, height=300)
        else:  # Plain Text
            st.download_button(
                "Download TXT",
                plan_content,
                file_name="cm_plan.txt",
                mime="text/plain"
            )

if __name__ == "__main__":
    main()
