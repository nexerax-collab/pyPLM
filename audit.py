import streamlit as st
import pandas as pd
from io import BytesIO
import xlsxwriter
from fpdf import FPDF

# Set page configuration
st.set_page_config(
    page_title="ECU Software FCA & PCA Audit Form",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("Navigation")
pages = ["Project Details", "Functional Configuration Audit (FCA)", "Physical Configuration Audit (PCA)", "Audit Summary"]
selected_page = st.sidebar.radio("Go to", pages)

# Common UI elements
rating_options = ["Yes", "Partial", "No"]
rating_weights = {"Yes": 2, "Partial": 1, "No": 0}

def audit_section(title, questions):
    """
    Helper function to generate audit questions and capture responses.
    """
    st.subheader(title)
    responses = []
    for idx, q in enumerate(questions, 1):
        col1, col2 = st.columns([2, 1])
        with col1:
            response = st.radio(f"{idx}. {q}", rating_options, key=f"{title}_{idx}")
        with col2:
            comment = st.text_area("Comments / Evidence", key=f"{title}_comment_{idx}")
        responses.append({"Question": q, "Rating": response, "Comment": comment, "Weight": rating_weights[response]})
    return responses

def calculate_result(score, total):
    """
    Calculate the result based on the total score and assign a color.
    """
    percentage = (score / total) * 100
    if percentage >= 80:
        return "Green", "Pass"
    elif 50 <= percentage < 80:
        return "Yellow", "Conditional"
    else:
        return "Red", "Fail"

def save_to_excel(dataframes, sheet_names):
    """
    Save data to an Excel file in memory.
    """
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for df, sheet_name in zip(dataframes, sheet_names):
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    return output.getvalue()

def save_to_pdf(fca_df, pca_df, summary, overall_status):
    """
    Save data to a PDF file in memory.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="ECU Software FCA & PCA Audit Report", ln=True, align='C')
    pdf.ln(10)

    # FCA Section
    pdf.cell(200, 10, txt="Functional Configuration Audit (FCA)", ln=True, align='L')
    for index, row in fca_df.iterrows():
        pdf.cell(0, 10, txt=f"{row['Question']}: {row['Rating']} | {row['Comment']}", ln=True)

    pdf.ln(10)

    # PCA Section
    pdf.cell(200, 10, txt="Physical Configuration Audit (PCA)", ln=True, align='L')
    for index, row in pca_df.iterrows():
        pdf.cell(0, 10, txt=f"{row['Question']}: {row['Rating']} | {row['Comment']}", ln=True)

    pdf.ln(10)

    # Summary Section
    pdf.cell(200, 10, txt="Audit Summary", ln=True, align='L')
    pdf.cell(0, 10, txt=f"Overall Status: {overall_status}", ln=True)
    pdf.cell(0, 10, txt=summary, ln=True)

    output = BytesIO()
    pdf.output(output)
    return output.getvalue()

# Page: Project Details
if selected_page == "Project Details":
    st.title("🚗 ECU Software FCA & PCA Audit Form")
    st.markdown("### Project Details")
    project_name = st.text_input("Project Name")
    audit_date = st.date_input("Audit Date")
    auditor = st.text_input("Auditor(s)")

# Page: FCA
elif selected_page == "Functional Configuration Audit (FCA)":
    st.title("Functional Configuration Audit (FCA)")
    fca_questions = [
        "Is the software’s functional baseline clearly documented and under change control?",
        "Does the software implement all and only the approved functional requirements?",
        "Is there full bi-directional traceability between requirements, design, implementation, and tests (e.g., in DOORS)?",
        "Are all test results complete and reviewed, with no open issues or unapproved deviations?",
        "Have defined development and CM processes been followed (e.g., reviews, approvals, versioning)?"
    ]
    fca_responses = audit_section("Functional Configuration Audit (FCA)", fca_questions)

# Page: PCA
elif selected_page == "Physical Configuration Audit (PCA)":
    st.title("Physical Configuration Audit (PCA)")
    pca_questions = [
        "Is the final product baseline established and complete, with all configuration items identified and versioned?",
        "Can the delivered binary be traced to a specific, immutable repository state (e.g., Git tag/SVN label)?",
        "Are all changes included in the release documented and approved (e.g., via CCB or change requests)?",
        "Are supporting documents (design, ICDs, manuals) updated and consistent with the delivered software?",
        "Are regulatory, licensing, and third-party software obligations satisfied and documented?"
    ]
    pca_responses = audit_section("Physical Configuration Audit (PCA)", pca_questions)

# Page: Audit Summary
elif selected_page == "Audit Summary":
    st.title("Audit Summary")
    st.markdown("### 📝 Summary of Audit Findings")
    overall_status = st.selectbox("Overall Audit Status", ["Pass", "Conditional", "Fail"])
    summary = st.text_area("Summary of Issues and Actions")

    if st.button("Generate Report"):
        # Convert responses to DataFrames for display and calculations
        fca_df = pd.DataFrame(fca_responses) if 'fca_responses' in locals() else pd.DataFrame()
        pca_df = pd.DataFrame(pca_responses) if 'pca_responses' in locals() else pd.DataFrame()

        # Calculate scores
        fca_score = fca_df["Weight"].sum() if not fca_df.empty else 0
        pca_score = pca_df["Weight"].sum() if not pca_df.empty else 0
        total_score = len(fca_df) * 2 + len(pca_df) * 2
        color, recommendation = calculate_result(fca_score + pca_score, total_score)

        # Display FCA and PCA responses
        if not fca_df.empty:
            st.markdown("#### FCA Responses")
            st.dataframe(fca_df)
        if not pca_df.empty:
            st.markdown("#### PCA Responses")
            st.dataframe(pca_df)

        # Display summary
        st.markdown("#### Summary")
        st.write(f"**Overall Status:** {recommendation}")
        st.write(f"**Color Indicator:** {color}")
        st.write(summary)

        # Export Options
        st.markdown("### Export Options")
        excel_data = save_to_excel([fca_df, pca_df], ["FCA", "PCA"])
        st.download_button("Download Excel", data=excel_data, file_name="Audit_Report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        pdf_data = save_to_pdf(fca_df, pca_df, summary, recommendation)
        st.download_button("Download PDF", data=pdf_data, file_name="Audit_Report.pdf", mime="application/pdf")
