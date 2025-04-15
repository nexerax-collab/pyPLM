# ... (keep existing imports and initialization) ...

CURRENT_UTC = "2025-04-15 13:16:39"
CURRENT_USER = "nexerax-collab"

def show_interactive_intro():
    st.markdown(f"""
    <div style='background-color: #f0f2f6; padding: 1em; border-radius: 5px; margin-bottom: 1em;'>
        <h1 style='margin:0'>Welcome to PyPLM</h1>
        <p style='color: #666;'>Your Software Product Lifecycle Management Hub</p>
        <small style='font-family: monospace;'>
            🕒 {CURRENT_UTC} UTC • 👤 {CURRENT_USER}
        </small>
    </div>
    """, unsafe_allow_html=True)

    # Initialize intro state if needed
    if 'intro_state' not in st.session_state:
        st.session_state.intro_state = {
            'step': 0,
            'completed_steps': set(),
            'module_created': False,
            'change_submitted': False,
            'tutorial_completed': False
        }

    # Interactive Workflow
    steps = [
        {
            'title': "🎯 Define Your Goal",
            'content': show_goal_selector
        },
        {
            'title': "📚 Understanding PLM",
            'content': show_plm_basics
        },
        {
            'title': "🛠️ First Steps",
            'content': show_first_steps
        },
        {
            'title': "🎮 Hands-on Practice",
            'content': show_practice_area
        }
    ]

    # Progress bar
    progress = len(st.session_state.intro_state['completed_steps']) / len(steps)
    st.progress(progress, f"Progress: {int(progress * 100)}%")

    # Show current step
    current_step = steps[st.session_state.intro_state['step']]
    st.subheader(current_step['title'])
    current_step['content']()

def show_goal_selector():
    st.markdown("### What brings you to PyPLM today?")
    
    goal = st.selectbox(
        "Select your primary goal:",
        [
            "Choose a goal...",
            "🏗️ Start a new software project",
            "📈 Improve existing project management",
            "🔄 Learn about change management",
            "📚 Understand PLM concepts"
        ]
    )
    
    if goal != "Choose a goal...":
        st.session_state.intro_state['user_goal'] = goal
        st.session_state.intro_state['completed_steps'].add(0)
        
        # Show personalized next steps
        st.markdown("### Recommended Path")
        if goal == "🏗️ Start a new software project":
            st.info("""
            Great! Let's help you:
            1. Set up your first module
            2. Learn about version control
            3. Establish change management processes
            """)
        elif goal == "📈 Improve existing project management":
            st.info("""
            Perfect! We'll focus on:
            1. Analyzing your current setup
            2. Implementing best practices
            3. Optimizing workflows
            """)
        
        if st.button("Continue to Next Step ➡️"):
            st.session_state.intro_state['step'] = 1
            st.rerun()

def show_plm_basics():
    st.markdown("### Quick PLM Overview")
    
    # Interactive PLM concepts
    concept = st.selectbox(
        "Choose a concept to learn about:",
        [
            "What is PLM?",
            "Modules & Components",
            "Change Management",
            "Version Control",
            "Configuration Management"
        ]
    )
    
    # Show concept details
    if concept == "What is PLM?":
        st.info("""
        Product Lifecycle Management (PLM) in software:
        - Manages the entire lifecycle of your software
        - Tracks changes and versions
        - Ensures quality and compliance
        - Facilitates collaboration
        """)
    elif concept == "Modules & Components":
        st.info("""
        In software PLM:
        - Modules = Parts in traditional PLM
        - Components = Assemblies
        - Dependencies = Bill of Materials
        """)
    
    # Knowledge check
    if st.checkbox("Take Quick Knowledge Check"):
        with st.form("plm_check"):
            st.radio(
                "What's the software equivalent of a Bill of Materials?",
                ["Source code", "Dependencies", "Documentation"]
            )
            if st.form_submit_button("Check Answer"):
                st.success("Correct! Dependencies list is like a Bill of Materials")
                st.session_state.intro_state['completed_steps'].add(1)
                if st.button("Continue to First Steps ➡️"):
                    st.session_state.intro_state['step'] = 2
                    st.rerun()

def show_first_steps():
    st.markdown("### Let's Get Started")
    
    # Quick start actions
    action = st.selectbox(
        "Choose your first action:",
        [
            "Create a Module",
            "Submit a Change",
            "Explore Documentation",
            "Take the Tutorial"
        ]
    )
    
    if action == "Create a Module":
        with st.form("quick_module"):
            st.text_input("Module Name", placeholder="my-first-module")
            st.selectbox("Module Type", ["Service", "Library", "Plugin"])
            if st.form_submit_button("Create"):
                st.success("🎉 Congratulations! You've created your first module!")
                st.session_state.intro_state['module_created'] = True
                st.session_state.intro_state['completed_steps'].add(2)
                if st.button("Continue to Practice ➡️"):
                    st.session_state.intro_state['step'] = 3
                    st.rerun()

def show_practice_area():
    st.markdown("### Hands-on Practice Area")
    
    # Practice scenarios
    scenario = st.selectbox(
        "Choose a scenario to practice:",
        [
            "Module Management",
            "Change Control",
            "Version Management",
            "Impact Analysis"
        ]
    )
    
    if scenario == "Module Management":
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            ### Practice Task
            Create a new module with:
            1. Clear description
            2. Proper categorization
            3. Initial version
            """)
        with col2:
            with st.form("practice_module"):
                st.text_input("Module Name")
                st.text_area("Description")
                st.selectbox("Category", ["Backend", "Frontend", "Data"])
                if st.form_submit_button("Submit"):
                    st.success("Great job! You've completed the practice task!")
                    st.session_state.intro_state['tutorial_completed'] = True
                    st.session_state.intro_state['completed_steps'].add(3)
    
    # Show completion message when all steps are done
    if len(st.session_state.intro_state['completed_steps']) == 4:
        st.balloons()
        st.success("""
        🎉 Congratulations! You've completed the introduction to PyPLM!
        
        Next Steps:
        1. Explore the Module Management section
        2. Try out Change Control
        3. Check the Analytics dashboard
        """)

# Update main content router
if main_menu == "🏠 Introduction":
    show_interactive_intro()

# ... (rest of the code remains the same)
