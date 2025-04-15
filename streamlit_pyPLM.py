# streamlit_pyPLM.py
# Last Updated: 2025-04-15 08:38:16 UTC
# Author: nexerax-collab

from pyPLM import (
    create_database, get_db_connection, Item, BOM, ChangeRequest,
    add_item_to_db, add_change_request_to_db, load_bom_links,
    get_item_state, update_item_state
)
import os
import sqlite3
import streamlit as st
import time
import pandas as pd
from collections import defaultdict

# Configure the Streamlit page
st.set_page_config(page_title="PyPLM - Dev Mode", layout="wide")

# Show logo and header
col1, col2 = st.columns([1, 10])
with col1:
    st.image("pyplm_cat_logo_small.gif", width=50)
with col2:
    st.markdown("### PyPLM\n*Lightweight PLM for developers*", unsafe_allow_html=True)

# Show splash screen on first load
if "splash_shown" not in st.session_state:
    splash = st.empty()
    with splash.container():
        st.image("pyplm_splash_cat.gif", use_column_width=True)
        st.info("🐱 Booting PyPLM… preparing your dev toolkit.")
        time.sleep(5)
    splash.empty()
    st.session_state["splash_shown"] = True

# Initialize database and BOM
create_database()
bom = BOM()

# Load existing items
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM items")
for row in cursor.fetchall():
    item = Item()
    item.item_number = row["item_number"]
    bom.add_item(item)

# Load links
load_bom_links(bom)

# Main menu
main_menu = st.sidebar.selectbox("Menu", [
    "Module Registry", "Patch Management", "Dependency Viewer", 
    "System Status", "Workflow Simulator", "Module Roadmap", 
    "Glossary", "Purge DB"
])

# --- Module Registry ---
if main_menu == "Module Registry":
    st.header("Module Registry")
    if st.button("🧱 Commit New Module"):
        new_item = Item()
        bom.add_item(new_item)
        add_item_to_db(new_item)
        st.success(f"✅ Committed module `{new_item.item_number}` to registry")

    with st.form("link_form"):
        st.subheader("🔗 Declare Dependency")
        parent = st.text_input("Parent Module ID", help="This is the module that will depend on another")
        child = st.text_input("Child Module ID", help="This is the required module being linked")
        quantity = st.number_input("Instances Required", min_value=1, value=1, help="How many units of this module are needed?")
        submitted = st.form_submit_button("Declare Link")
        if submitted:
            p = bom.get_item(parent)
            c = bom.get_item(child)
            if p and c:
                p.add_lower_level_item(c, quantity)
                st.success(f"🔗 `{child}` linked as dependency to `{parent}` (Qty: {quantity})")
            else:
                st.error("❌ One or both modules not found in registry")

# --- Patch Management ---
if main_menu == "Patch Management":
    st.header("Pull Request (Patch) Tracker")
    with st.form("cr_form"):
        item_number = st.text_input("Module ID", help="Enter the module you're applying the patch to (e.g., P0003)")
        reason = st.selectbox("Patch Type", [
            "A - Feature Request",
            "B - Refactor",
            "C - Bugfix",
            "D - Hotfix"
        ], help="What type of change are you introducing?")
        cost = st.selectbox("Complexity Level", ["<1k", "<5k", "<10k", ">10k"], help="Estimated cost or size of the patch")
        submit_cr = st.form_submit_button("Submit Pull Request")
        if submit_cr:
            item = bom.get_item(item_number)
            if item:
                cr = item.create_change_request(reason[0], cost, "< 2 weeks")
                add_change_request_to_db(cr)
                st.success(f"✅ Pull Request #{cr.change_request_number} created for `{item.item_number}`")
            else:
                st.error("❌ Module not found")

# --- Dependency Viewer ---
if main_menu == "Dependency Viewer":
    st.header("📦 View Dependencies")
    selected_item = st.text_input("Enter Module ID", help="View linked dependencies for this module")
    item = bom.get_item(selected_item)

    if item:
        data = []
        data.append({
            "Module ID": item.item_number,
            "Role": "Top-level Module",
            "Quantity": 1
        })

        if item.bom.items:
            for child_id, child in item.bom.items.items():
                qty = item.bom.quantities.get(child_id, 1)
                data.append({
                    "Module ID": child_id,
                    "Role": "Dependency",
                    "Quantity": qty
                })

            df = pd.DataFrame(data)
            st.dataframe(df, use_container_width=True)

            # Export button
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📤 Export as CSV",
                data=csv,
                file_name=f"{item.item_number}_dependencies.csv",
                mime='text/csv'
            )
        else:
            st.info("No dependencies declared for this module.")
    else:
        st.warning("Module not found in registry.")

# --- System Status ---
if main_menu == "System Status":
    st.header("🧭 System Dashboard")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM items")
    items_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM change_requests")
    cr_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM documents")
    doc_count = cursor.fetchone()[0]

    st.metric("Modules Committed", items_count)
    st.metric("Patches Submitted", cr_count)
    st.metric("Documents Attached", doc_count)

    if os.path.exists("plm_tool.log"):
        with open("plm_tool.log", "r") as f:
            logs = f.readlines()[-10:]
            st.code("".join(logs), language="text")
    else:
        st.info("Log file not found.")

# --- Workflow Simulator ---
if main_menu == "Workflow Simulator":
    st.header("🚦 Module Lifecycle Simulator")
    
    # Initialize session state for workflow steps
    if 'workflow_step' not in st.session_state:
        st.session_state.workflow_step = 1
    if 'created_module' not in st.session_state:
        st.session_state.created_module = None
    if 'patch_submitted' not in st.session_state:
        st.session_state.patch_submitted = False

    # Display workflow progress
    progress_text = ["1. Create Module", "2. Submit Patch", "3. Progress Lifecycle"]
    progress_value = (st.session_state.workflow_step - 1) / 3
    st.progress(progress_value, text=f"Step {st.session_state.workflow_step} of 3")

    # Step 1: Create Module
    if st.session_state.workflow_step == 1:
        st.subheader("🎯 Step 1: Create New Module")
        st.markdown("""
        > In this step, you'll create a new module in the system. Think of this as:
        > - Creating a new microservice
        > - Starting a new package
        > - Initializing a new component
        """)

        col1, col2 = st.columns([2,1])
        with col1:
            module_type = st.selectbox(
                "Module Type",
                ["Backend Service", "Frontend Component", "Data Model", "API Interface", "Utility Library"]
            )
            module_desc = st.text_area("Module Description", placeholder="Describe the purpose of this module...")
        with col2:
            st.info("📝 Tips:\n- Be specific\n- Consider dependencies\n- Think about scaling")

        if st.button("🏗️ Create Module"):
            new_item = Item()
            bom.add_item(new_item)
            add_item_to_db(new_item)
            st.session_state.created_module = new_item.item_number
            st.session_state.workflow_step = 2
            st.success(f"✨ Module `{new_item.item_number}` created successfully!")
            st.rerun()

    # Step 2: Submit Patch
    elif st.session_state.workflow_step == 2:
        st.subheader("🔄 Step 2: Submit Module Patch")
        st.markdown(f"""
        > Current Module: `{st.session_state.created_module}`
        > 
        > Time to improve your module! Submit a patch (like a Pull Request) to:
        > - Add features
        > - Fix issues
        > - Improve performance
        """)

        col1, col2 = st.columns([2,1])
        with col1:
            patch_type = st.selectbox(
                "Patch Type",
                [
                    "✨ Feature: Add new capability",
                    "🐛 Fix: Resolve an issue",
                    "🚀 Performance: Optimize code",
                    "📚 Docs: Improve documentation"
                ]
            )
            patch_desc = st.text_area("Patch Details", placeholder="Describe your changes...")
            patch_impact = st.select_slider(
                "Impact Assessment",
                options=["Minimal", "Moderate", "Significant"],
                value="Moderate"
            )
        with col2:
            st.info("🔍 Review Checklist:\n- Tests included?\n- Docs updated?\n- Dependencies checked?")

        if st.button("📤 Submit Patch"):
            item = bom.get_item(st.session_state.created_module)
            if item:
                cr = item.create_change_request(
                    reason=patch_type[0],
                    cost_impact=patch_impact,
                    timeline_impact="< 1 week"
                )
                add_change_request_to_db(cr)
                st.session_state.patch_submitted = True
                st.session_state.workflow_step = 3
                st.success(f"🎉 Patch #{cr.change_request_number} submitted successfully!")
                st.rerun()

    # Step 3: Lifecycle Management
    elif st.session_state.workflow_step == 3:
        st.subheader("📈 Step 3: Progress Module Lifecycle")
        st.markdown(f"""
        > Module `{st.session_state.created_module}` Lifecycle Management
        >
        > Guide your module through its lifecycle stages:
        > 1. 📝 Draft: Initial development
        > 2. 🔍 Reviewed: Peer review complete
        > 3. ✅ Released: Production-ready
        """)

        current_state = get_item_state(st.session_state.created_module)
        
        col1, col2 = st.columns([2,1])
        with col1:
            st.info(f"Current State: {current_state}")
            
            lifecycle_chart_data = pd.DataFrame({
                'Stage': ['Draft', 'Reviewed', 'Released'],
                'Value': [100 if s == current_state else 30 for s in ['Draft', 'Reviewed', 'Released']]
            })
            st.bar_chart(lifecycle_chart_data.set_index('Stage'))

        with col2:
            st.success("Patch Status: ✅ Submitted")
            if current_state == "Draft":
                if st.button("🔍 Submit for Review"):
                    update_item_state(st.session_state.created_module, "Reviewed")
                    st.rerun()
            elif current_state == "Reviewed":
                if st.button("✨ Release to Production"):
                    update_item_state(st.session_state.created_module, "Released")
                    st.rerun()
            elif current_state == "Released":
                st.success("🎉 Module Successfully Released!")
                if st.button("🔄 Start New Workflow"):
                    st.session_state.workflow_step = 1
                    st.session_state.created_module = None
                    st.session_state.patch_submitted = False
                    st.rerun()

    # Display current workflow context
    with st.sidebar:
        st.markdown("### 📋 Workflow Context")
        st.markdown(f"""
        - **Current Step:** {progress_text[st.session_state.workflow_step - 1]}
        - **Module ID:** `{st.session_state.created_module if st.session_state.created_module else 'Not created yet'}`
        - **Patch Status:** {'✅ Submitted' if st.session_state.patch_submitted else '⏳ Pending'}
        """)


# --- Module Roadmap ---
if main_menu == "Module Roadmap":
    st.header("🗺️ Module Roadmap by State")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_number, state FROM items")
    rows = cursor.fetchall()

    state_map = defaultdict(list)
    for row in rows:
        state = row["state"] or "Draft"
        state_map[state].append(row["item_number"])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("📥 Draft")
        for item in state_map.get("Draft", []):
            st.write(f"- {item}")

    with col2:
        st.subheader("🔍 Reviewed")
        for item in state_map.get("Reviewed", []):
            st.write(f"- {item}")

    with col3:
        st.subheader("✅ Released")
        for item in state_map.get("Released", []):
            st.write(f"- {item}")

# --- Glossary ---
if main_menu == "Glossary":
    st.header("📖 PLM Glossary for Developers")
    glossary = {
        "Module (Item)": "A reusable unit or part in a system, like a class, package, or microservice.",
        "Dependency (BOM)": "Other modules this one depends on — like imports or library references.",
        "Pull Request (Change Request)": "A request to make a change to a module — reviewed and approved.",
        "Lifecycle / Workflow": "The stages a module goes through: Draft → Reviewed → Released.",
        "Document": "A spec, diagram, or PDF linked to a module or request — like a README or architecture doc.",
        "Quantity": "How many units of a module are used — think of this like container scaling or replicas.",
    }
    for term, desc in glossary.items():
        st.subheader(term)
        st.write(desc)

# --- Purge DB ---
if main_menu == "Purge DB":
    st.warning("This will delete all project data.")
    if st.button("⚠️ Confirm Project Reset"):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM items")
        c.execute("DELETE FROM change_requests")
        c.execute("DELETE FROM documents")
        c.execute("DELETE FROM bom_links")
        conn.commit()
        st.success("🗑️ Project reset complete.")
