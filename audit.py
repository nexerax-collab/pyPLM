import streamlit as st
import pandas as pd

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
        responses.append({"Question": q, "Rating": response, "Comment": comment})
    return responses

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
        # Convert responses to DataFrames for display
        fca_df = pd.DataFrame(fca_responses) if 'fca_responses' in locals() else pd.DataFrame()
        pca_df = pd.DataFrame(pca_responses) if 'pca_responses' in locals() else pd.DataFrame()

        # Display FCA and PCA responses
        if not fca_df.empty:
            st.markdown("#### FCA Responses")
            st.dataframe(fca_df)
        if not pca_df.empty:
            st.markdown("#### PCA Responses")
            st.dataframe(pca_df)

        # Display summary
        st.markdown("#### Summary")
        st.write(f"**Overall Status:** {overall_status}")
        st.write(summary)

        # Optional: Add export functionality (e.g., to CSV or Excel)
        if st.button("Export to CSV"):
            fca_df.to_csv("FCA_Responses.csv", index=False)
            pca_df.to_csv("PCA_Responses.csv", index=False)
            st.success("Responses exported as CSV files!")
