# --- Common Session Information Function ---
def show_session_header():
    st.markdown(f"""
    <div style='background-color: #f0f2f6; padding: 0.5em; border-radius: 5px; margin-bottom: 1em; font-family: monospace;'>
        <small>
        Session: {st.session_state.user_data['session_id']}
        • User: {st.session_state.user_data['login']}
        • UTC: 2025-04-15 09:15:14
        </small>
    </div>
    """, unsafe_allow_html=True)

# --- General App Introduction ---
def show_app_welcome():
    st.markdown("""
    <div style='text-align: center; padding: 2em 0;'>
        <h1>Welcome to PyPLM</h1>
        <p style='font-size: 1.2em; color: #666;'>Product Lifecycle Management for Modern Development</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    ### 🎯 What is PyPLM?
    
    PyPLM is a modern, developer-focused Product Lifecycle Management system that helps teams:
    - Manage software modules and components
    - Track changes and their impacts
    - Control configurations and dependencies
    - Ensure quality and compliance
    
    ### 🚀 Quick Start Guide
    
    1. **Try the Workflow Simulator**
       - Experience PLM concepts hands-on
       - Learn best practices
       - Understand the lifecycle
    
    2. **Manage Your Modules**
       - Create and organize components
       - Track dependencies
       - Monitor metrics
    
    3. **Control Changes**
       - Submit and review changes
       - Assess impacts
       - Track history
    
    ### 📚 Key Concepts
    
    ```mermaid
    graph LR
        A[Modules] --> B[Changes]
        B --> C[Lifecycle]
        C --> D[Release]
        A --> E[Dependencies]
        B --> F[Impact]
    ```
    
    ### 🎓 Learning Path
    
    1. **Beginner**
       - Start with Workflow Simulator
       - Create basic modules
       - Submit simple changes
    
    2. **Intermediate**
       - Manage dependencies
       - Analyze impacts
       - Track metrics
    
    3. **Advanced**
       - Configure workflows
       - Optimize processes
       - Generate reports
    """)

    # Quick access cards
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("🎮 **Start Learning**\nTry the interactive workflow simulator")
        if st.button("Launch Simulator"):
            st.session_state.menu = "🎮 Interactive Workflow"
            st.rerun()
    
    with col2:
        st.info("📦 **Start Building**\nCreate your first module")
        if st.button("Create Module"):
            st.session_state.menu = "📦 Module Management"
            st.rerun()
    
    with col3:
        st.info("📚 **Start Reading**\nExplore the knowledge base")
        if st.button("Browse Docs"):
            st.session_state.menu = "📚 Knowledge Base"
            st.rerun()

# --- Main App Structure ---
def main():
    # Initialize session state
    if 'user_data' not in st.session_state:
        st.session_state.user_data = {
            'login': 'nexerax-collab',
            'session_id': f"SESSION_{int(time.time())}",
            'start_time': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        }

    # Configure the page
    st.set_page_config(
        page_title="PyPLM - Developer's Guide to PLM",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Show logo and app header
    show_app_logo()

    # Main navigation
    main_menu = st.sidebar.selectbox("Navigation", [
        "🏠 Introduction",
        "🎮 Interactive Workflow",
        "📦 Module Management",
        "🔄 Change Control",
        "🔗 Dependencies & Impact",
        "📊 System Overview",
        "📚 Knowledge Base",
        "⚙️ Settings"
    ])

    # Show session info in sidebar
    with st.sidebar:
        st.markdown("### 🔍 Session Info")
        st.code(f"""
User: {st.session_state.user_data['login']}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC
Session: {st.session_state.user_data['session_id']}
        """)

    # Show context-aware help
    show_context_help(main_menu)

    # Display session header
    show_session_header()

    # Route to appropriate section
    if main_menu == "🏠 Introduction":
        show_app_welcome()
    elif main_menu == "🎮 Interactive Workflow":
        show_workflow_simulator()
    elif main_menu == "📦 Module Management":
        show_module_management()
    elif main_menu == "🔄 Change Control":
        show_change_control()
    # ... [other sections]

if __name__ == "__main__":
    main()
