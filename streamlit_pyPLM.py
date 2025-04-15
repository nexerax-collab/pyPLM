def show_enhanced_feature_discovery():
    current_utc = "2025-04-15 09:33:47"
    current_user = "nexerax-collab"

    st.markdown(f"""
    <div style='background-color: #f0f2f6; padding: 0.5em; border-radius: 5px; margin-bottom: 1em;'>
        <small style='font-family: monospace;'>
        🕒 {current_utc} UTC • 👤 {current_user} • 🔍 Feature Discovery Tour
        </small>
    </div>
    """, unsafe_allow_html=True)

    st.header("🎯 Interactive Feature Discovery")

    # Feature Categories with detailed tours
    feature_category = st.selectbox(
        "Select a feature category to explore",
        [
            "Choose a category...",
            "📦 Module Management Suite",
            "🔄 Change Control System",
            "🔗 Dependency Management",
            "📊 Analytics & Reporting",
            "🔍 Impact Analysis Tools",
            "📚 Documentation Center"
        ]
    )

    if feature_category != "Choose a category...":
        # Initialize feature tour state
        if 'feature_tour' not in st.session_state:
            st.session_state.feature_tour = {
                'current_step': 0,
                'completed_tours': set(),
                'current_category': None
            }

        # Reset tour if category changed
        if st.session_state.feature_tour['current_category'] != feature_category:
            st.session_state.feature_tour['current_step'] = 0
            st.session_state.feature_tour['current_category'] = feature_category

        # Feature Tours Content
        tours = {
            "📦 Module Management Suite": {
                'steps': [
                    {
                        'title': "Module Creation Wizard",
                        'description': """
                        Create new software modules with our intuitive wizard:
                        - Define module properties
                        - Set up dependencies
                        - Configure build settings
                        """,
                        'demo': show_module_creation_demo
                    },
                    {
                        'title': "Module Templates",
                        'description': """
                        Start with pre-configured templates:
                        - Microservice template
                        - Library template
                        - API template
                        """,
                        'demo': show_template_demo
                    },
                    {
                        'title': "Version Control",
                        'description': """
                        Manage module versions effectively:
                        - Version tagging
                        - Release management
                        - Changelog generation
                        """,
                        'demo': show_version_control_demo
                    }
                ],
                'interactive_demo': True
            },
            "🔄 Change Control System": {
                'steps': [
                    {
                        'title': "Change Request Creation",
                        'description': """
                        Submit and track changes:
                        - Define change scope
                        - Set priority levels
                        - Assign reviewers
                        """,
                        'demo': show_change_request_demo
                    },
                    {
                        'title': "Review Workflow",
                        'description': """
                        Streamlined review process:
                        - Multi-stage reviews
                        - Automated checks
                        - Approval tracking
                        """,
                        'demo': show_review_workflow_demo
                    }
                ],
                'interactive_demo': True
            }
        }

        if feature_category in tours:
            tour_data = tours[feature_category]
            current_step = st.session_state.feature_tour['current_step']
            total_steps = len(tour_data['steps'])

            # Show tour progress
            st.progress(current_step / total_steps, 
                       f"Tour Progress: Step {current_step + 1}/{total_steps}")

            # Display current step
            step = tour_data['steps'][current_step]
            
            col1, col2 = st.columns([2,1])
            with col1:
                st.subheader(step['title'])
                st.markdown(step['description'])
                
                # Interactive elements based on step
                if 'demo' in step:
                    step['demo']()

            with col2:
                st.markdown("### Try it out")
                if tour_data['interactive_demo']:
                    show_interactive_feature_demo(feature_category, step['title'])

            # Navigation buttons
            col1, col2, col3 = st.columns([1,2,1])
            with col1:
                if current_step > 0:
                    if st.button("⬅️ Previous Step"):
                        st.session_state.feature_tour['current_step'] -= 1
                        st.rerun()
            
            with col3:
                if current_step < total_steps - 1:
                    if st.button("Next Step ➡️"):
                        st.session_state.feature_tour['current_step'] += 1
                        st.rerun()
                elif current_step == total_steps - 1:
                    if st.button("✅ Complete Tour"):
                        st.session_state.feature_tour['completed_tours'].add(feature_category)
                        show_tour_completion()

        # Show tour completion status
        if st.session_state.feature_tour['completed_tours']:
            st.sidebar.markdown("### 🏆 Completed Tours")
            for completed in st.session_state.feature_tour['completed_tours']:
                st.sidebar.success(f"✅ {completed}")

def show_interactive_feature_demo(category, feature):
    """Show interactive demo for specific feature"""
    st.markdown("### 🎮 Interactive Demo")
    
    if category == "📦 Module Management Suite":
        if feature == "Module Creation Wizard":
            with st.form("demo_module_creation"):
                st.text_input("Module Name", placeholder="my-awesome-module")
                st.selectbox("Module Type", ["Service", "Library", "API"])
                st.text_area("Description", placeholder="Describe your module...")
                st.button("Create Demo Module")
    
    elif category == "🔄 Change Control System":
        if feature == "Change Request Creation":
            with st.form("demo_change_request"):
                st.selectbox("Change Type", ["Feature", "Bug Fix", "Enhancement"])
                st.text_area("Change Description", placeholder="Describe the change...")
                st.button("Submit Demo Change")

def show_guided_tour():
    """Show comprehensive guided tour"""
    st.markdown("### 🎯 Guided Tour")
    
    if 'guided_tour' not in st.session_state:
        st.session_state.guided_tour = {
            'started': False,
            'current_step': 0,
            'completed_steps': set()
        }

    if not st.session_state.guided_tour['started']:
        st.markdown("""
        Welcome to the PyPLM Guided Tour! 
        This tour will walk you through all major features and best practices.
        
        **Duration:** ~30 minutes
        **Topics Covered:**
        - Module Management
        - Change Control
        - Dependencies
        - Analytics
        """)
        
        if st.button("🚀 Start Guided Tour"):
            st.session_state.guided_tour['started'] = True
            st.rerun()
    else:
        tour_steps = [
            {
                'title': "Module Creation",
                'content': show_module_tour,
                'duration': "5 min"
            },
            {
                'title': "Change Management",
                'content': show_change_tour,
                'duration': "8 min"
            },
            {
                'title': "Dependency Analysis",
                'content': show_dependency_tour,
                'duration': "7 min"
            },
            {
                'title': "Reporting & Analytics",
                'content': show_analytics_tour,
                'duration': "10 min"
            }
        ]

        current_step = tour_steps[st.session_state.guided_tour['current_step']]
        
        # Show tour progress
        st.progress(len(st.session_state.guided_tour['completed_steps']) / len(tour_steps),
                   f"Tour Progress: {len(st.session_state.guided_tour['completed_steps'])}/{len(tour_steps)} completed")
        
        st.subheader(f"Step {st.session_state.guided_tour['current_step'] + 1}: {current_step['title']}")
        st.markdown(f"⏱️ Duration: {current_step['duration']}")
        
        current_step['content']()

# Add these to your main navigation
if main_menu == "🎯 Feature Discovery":
    show_enhanced_feature_discovery()
elif main_menu == "🎮 Guided Tour":
    show_guided_tour()
