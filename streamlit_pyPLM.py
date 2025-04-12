
import streamlit as st
import sqlite3
import os
from pyPLM import (
    create_database, get_db_connection, Item, BOM, ChangeRequest,
    add_item_to_db, add_change_request_to_db, load_bom_links
)

st.set_page_config(page_title="PyPLM - Dev Mode", layout="wide")
st.markdown("<h1 style='color:#34a853;'>PyPLM (Dev Mode)</h1><p>🛠️ A PLM tool reimagined for developers</p>", unsafe_allow_html=True)

create_database()
bom = BOM()

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM items")
for row in cursor.fetchall():
    item = Item()
    item.item_number = row["item_number"]
    bom.add_item(item)

# Load links
load_bom_links(bom)

main_menu = st.sidebar.selectbox("Menu", [
    "Module Registry", "Patch Management", "Dependency Viewer", "System Status", "Purge DB"
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
        st.markdown("### Dependency List (BOM View)")
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

            import pandas as pd
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

    st.markdown("### 📋 Recent System Logs")
    if os.path.exists("plm_tool.log"):
        with open("plm_tool.log", "r") as f:
            logs = f.readlines()[-10:]
            st.code("".join(logs), language="text")
    else:
        st.info("Log file not found.")

# --- Purge ---
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
        st.markdown(f"**{term}**: {desc}")

if main_menu == "Workflow Simulator":
    st.header("🚦 Module Lifecycle State")
    item_id = st.text_input("Enter Module ID", help="Check and update the state of a specific module")

    if item_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT item_number FROM items WHERE item_number = ?", (item_id,))
        exists = cursor.fetchone()
        if exists:
            state_key = f"{item_id}_state"
            if state_key not in st.session_state:
                st.session_state[state_key] = "Draft"

            st.markdown(f"**Current State of `{item_id}`:** `{st.session_state[state_key]}`")

            if st.session_state[state_key] == "Draft":
                if st.button("Submit for Review"):
                    st.session_state[state_key] = "Reviewed"
                    st.success("Moved to Reviewed state")

            elif st.session_state[state_key] == "Reviewed":
                if st.button("Approve & Release"):
                    st.session_state[state_key] = "Released"
                    st.success("Module is now Released ✅")

            elif st.session_state[state_key] == "Released":
                st.info("Module is fully released. 🎉")
        else:
            st.error("Module not found")
