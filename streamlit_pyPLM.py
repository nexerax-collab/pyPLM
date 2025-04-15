# streamlit_pyPLM.py
# Last Updated: 2025-04-15 08:49:18 UTC
# Author: nexerax-collab

[previous imports and logo remain the same...]

# Main menu with workflow first and hint
st.sidebar.info("👋 New to PyPLM? Start with the Workflow Simulator to learn the basics!")

main_menu = st.sidebar.selectbox("Menu", [
    "Workflow Simulator",  # Moved to top
    "Module Registry",
    "Patch Management", 
    "Dependency Viewer",
    "System Status", 
    "Module Roadmap",
    "Glossary",
    "Purge DB"
])

# Add context helper in sidebar
with st.sidebar:
    st.markdown("### 📋 Current Context")
    if main_menu == "Workflow Simulator":
        if 'workflow_step' in st.session_state:
            st.markdown(f"""
            - **Current Step:** Step {st.session_state.workflow_step} of 3
            - **Module ID:** `{st.session_state.created_module if st.session_state.created_module else 'Not created yet'}`
            - **Patch Status:** {'✅ Submitted' if st.session_state.patch_submitted else '⏳ Pending'}
            """)
    else:
        st.markdown(f"""
        - **Current View:** {main_menu}
        - **Total Modules:** {len(bom.items) if hasattr(bom, 'items') else 0}
        - **Session Start:** {time.strftime('%H:%M:%S')}
        """)

[Workflow Simulator section remains as in previous response...]

# --- Module Registry ---
if main_menu == "Module Registry":
    st.header("📦 Module Registry")
    st.markdown("""
    > The Module Registry is where you manage your software components.
    > Think of it as your package repository or service catalog.
    """)

    col1, col2 = st.columns([2,1])
    with col1:
        st.subheader("🆕 Register New Module")
        with st.form("module_form"):
            module_type = st.selectbox(
                "Module Type",
                ["Backend Service", "Frontend Component", "Data Model", "API Interface", "Utility Library"]
            )
            module_desc = st.text_area("Module Description")
            submit_module = st.form_submit_button("🏗️ Register Module")
            if submit_module:
                new_item = Item()
                bom.add_item(new_item)
                add_item_to_db(new_item)
                st.success(f"✅ Module `{new_item.item_number}` registered successfully!")
    
    with col2:
        st.info("""
        📝 **Tips:**
        - Give clear descriptions
        - Consider dependencies
        - Use consistent naming
        """)

    st.subheader("🔗 Module Dependencies")
    with st.form("dependency_form"):
        col1, col2, col3 = st.columns([2,2,1])
        with col1:
            parent = st.text_input("Parent Module ID", help="The module that needs a dependency")
        with col2:
            child = st.text_input("Dependency Module ID", help="The module being added as a dependency")
        with col3:
            quantity = st.number_input("Instances", min_value=1, value=1)
        
        submit_dep = st.form_submit_button("Declare Dependency")
        if submit_dep:
            p = bom.get_item(parent)
            c = bom.get_item(child)
            if p and c:
                p.add_lower_level_item(c, quantity)
                st.success(f"🔗 Dependency declared: `{parent}` → `{child}` (x{quantity})")
            else:
                st.error("❌ One or both modules not found")

# --- Patch Management ---
if main_menu == "Patch Management":
    st.header("🔄 Patch Management")
    st.markdown("""
    > Manage changes to your modules through a structured process.
    > Similar to Pull Requests in Git or Change Requests in PLM systems.
    """)

    col1, col2 = st.columns([2,1])
    with col1:
        with st.form("patch_form"):
            st.subheader("📝 Submit New Patch")
            module_id = st.text_input("Module ID", help="Target module for the patch")
            patch_type = st.selectbox(
                "Patch Type",
                [
                    "✨ Feature: Add new capability",
                    "🐛 Fix: Resolve an issue",
                    "🚀 Performance: Optimize code",
                    "📚 Docs: Improve documentation"
                ]
            )
            impact = st.select_slider(
                "Impact Level",
                options=["Minimal", "Moderate", "Significant"]
            )
            details = st.text_area("Patch Details")
            submit_patch = st.form_submit_button("📤 Submit Patch")
            
            if submit_patch:
                item = bom.get_item(module_id)
                if item:
                    cr = item.create_change_request(
                        reason=patch_type[0],
                        cost_impact=impact,
                        timeline_impact="< 1 week"
                    )
                    add_change_request_to_db(cr)
                    st.success(f"✅ Patch #{cr.change_request_number} submitted for `{module_id}`")
                else:
                    st.error("❌ Module not found")

    with col2:
        st.info("""
        🔍 **Review Checklist:**
        - Tests included?
        - Docs updated?
        - Dependencies checked?
        - Impact assessed?
        """)

[Continue with similar instructional layouts for other sections...]
