import streamlit as st
import pandas as pd
import json

# Set page configuration
st.set_page_config(
    page_title="Software FCA & PCA Audit Form",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar navigation
st.sidebar.title("Navigation")
pages = ["Introduction", "Project Details", "Functional Configuration Audit (FCA)", "Physical Configuration Audit (PCA)", "Audit Summary"]
selected_page = st.sidebar.radio("Go to", pages)

# Common UI elements
rating_options = ["Yes", "Partial", "No"]
rating_weights = {"Yes": 2, "Partial": 1, "No": 0}

def audit_section(title, questions_with_examples):
    """
    Helper function to generate audit questions with examples and capture responses.
    """
    st.subheader(title)
    responses = []
    for idx, (q, example) in enumerate(questions_with_examples, 1):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{idx}. {q}**")
            st.caption(f"Example: {example}")
            response = st.radio("Select your answer:", rating_options, key=f"{title}_{idx}")
        with col2:
            comment = st.text_area("Comments / Evidence:", key=f"{title}_comment_{idx}")
        responses.append({"Question": q, "Rating": response, "Comment": comment, "Weight": rating_weights[response]})
    return responses

def calculate_result(score, total):
    """
    Calculate the result based on the total score and assign a color.
    """
    percentage = (score / total) * 100
    if percentage >= 80:
        return "Green", "Pass", "No follow-up needed"
    elif 50 <= percentage < 80:
        return "Yellow", "Conditional", "Recommend review and partial corrections"
    else:
        return "Red", "Fail", "Immediate action required to address major issues"

# Page: Introduction
if selected_page == "Introduction":
    st.title("🚗 ECU Software FCA & PCA Audit Form")
    st.markdown("""
    This form supports internal CM audits software during development and release. 
    It follows configuration management standards such as ISO 10007, EIA-649C, and IEEE 828.

    ### Functional Configuration Audit (FCA)
    Verifies the specified software meets approved functional and performance requirements through traceability, 
    test results, and adherence to development processes.

    ### Physical Configuration Audit (PCA)
    Confirms the released software and its documentation match the approved baseline, including version control, 
    approved changes, and license compliance.
    """)

# Page: Project Details
elif selected_page == "Project Details":
    st.title("Project Details")
    st.markdown("### Provide the details of the project being audited.")
    project_name = st.text_input("Project Name")
    audit_date = st.date_input("Audit Date")
    auditor = st.text_input("Auditor(s)")

# Page: FCA
elif selected_page == "Functional Configuration Audit (FCA)":
    st.title("Functional Configuration Audit (FCA)")
    fca_questions_with_examples = [
        (
            "Is the software’s functional baseline clearly documented and under change control?",
            "Requirements baselines from DOORS, versioned functional specifications."
        ),
        (
            "Does the software implement all and only the approved functional requirements?",
            "Cross-check functional specifications with requirements traceability matrix."
        ),
        (
            "Is there full bi-directional traceability between requirements, design, implementation, and tests (e.g., in DOORS)?",
            "Traceability reports showing links between requirements, design documents, and test cases."
        ),
        (
            "Are all test results complete and reviewed, with no open issues or unapproved deviations?",
            "Reviewed test plans, execution reports, and issue resolution logs."
        ),
        (
            "Have defined development and CM processes been followed (e.g., reviews, approvals, versioning)?",
            "Evidence of code reviews, configuration management logs, and version-controlled repositories."
        )
    ]
    fca_responses = audit_section("Functional Configuration Audit (FCA)", fca_questions_with_examples)

# Page: PCA
elif selected_page == "Physical Configuration Audit (PCA)":
    st.title("Physical Configuration Audit (PCA)")
    pca_questions_with_examples = [
        (
            "Is the final product baseline established and complete, with all configuration items identified and versioned?",
            "Baseline configuration items, version control repository snapshots."
        ),
        (
            "Can the delivered binary be traced to a specific, immutable repository state (e.g., Git tag/SVN label)?",
            "Git repository tags or SVN labels linked to the binary file."
        ),
        (
            "Are all changes included in the release documented and approved (e.g., via CCB or change requests)?",
            "Change control board (CCB) meeting minutes, approved change requests."
        ),
        (
            "Are supporting documents (design, ICDs, manuals) updated and consistent with the delivered software?",
            "Updated design documents, interface control documents (ICDs), and user manuals."
        ),
        (
            "Are regulatory, licensing, and third-party software obligations satisfied and documented?",
            "License compliance reports, evidence of regulatory approvals."
        )
    ]
    pca_responses = audit_section("Physical Configuration Audit (PCA)", pca_questions_with_examples)

# Page: Audit Summary
elif selected_page == "Audit Summary":
    st.title("Audit Summary")
    st.markdown("### 📝 Summary of Audit Findings")

    # Convert responses to DataFrames for display and calculations
    fca_df = pd.DataFrame(fca_responses) if 'fca_responses' in locals() else pd.DataFrame()
    pca_df = pd.DataFrame(pca_responses) if 'pca_responses' in locals() else pd.DataFrame()

    # Calculate scores
    fca_score = fca_df["Weight"].sum() if not fca_df.empty else 0
    pca_score = pca_df["Weight"].sum() if not pca_df.empty else 0
    total_score = len(fca_df) * 2 + len(pca_df) * 2
    color, recommendation, follow_up = calculate_result(fca_score + pca_score, total_score)

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
    st.write(f"**Follow-up Recommendations:** {follow_up}")

    # Export Options
    st.markdown("### Export Options")
    fca_json = fca_df.to_json(orient="records")
    pca_json = pca_df.to_json(orient="records")

    st.download_button(
        label="Download FCA as JSON",
        data=fca_json,
        file_name="FCA_Responses.json",
        mime="application/json"
    )

    st.download_button(
        label="Download PCA as JSON",
        data=pca_json,
        file_name="PCA_Responses.json",
        mime="application/json"
    )

    combined_csv = fca_df.append(pca_df).to_csv(index=False)
    st.download_button(
        label="Download Combined Report as CSV",
        data=combined_csv,
        file_name="Audit_Report.csv",
        mime="text/csv"
    )
