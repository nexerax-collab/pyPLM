# In the main content router section, replace the introduction page code with:

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
    
    # Add navigation state to session state if not present
    if 'navigation' not in st.session_state:
        st.session_state.navigation = "🏠 Introduction"
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📦 Create New Module"):
            st.session_state.navigation = "📦 Module Management"
            st.rerun()
    with col2:
        if st.button("🔄 Submit Change"):
            st.session_state.navigation = "🔄 Change Control"
            st.rerun()

# And update the main navigation code to use the session state:

# Main navigation (replace the existing main_menu definition)
if 'navigation' not in st.session_state:
    st.session_state.navigation = "🏠 Introduction"

main_menu = st.sidebar.selectbox(
    "Navigation",
    [
        "🏠 Introduction",
        "📦 Module Management",
        "🔄 Change Control",
        "📊 Analytics",
        "📚 Learning Resources"
    ],
    key="navigation"
)
