import streamlit as st
import os
import sqlite3
from pyPLM import (
    create_database, get_db_connection, Item, BOM, ChangeRequest,
    add_item_to_db, add_change_request_to_db, get_document_from_db
)

st.set_page_config(page_title="PyPLM", layout="wide")

if 'role' not in st.session_state:
    st.session_state['role'] = 'admin'
if 'username' not in st.session_state:
    st.session_state['username'] = 'admin'

st.markdown("""
<h1 style='font-family: Google Sans, sans-serif; color: #34a853;'>PyPLM</h1>
<p style='color:gray;'>Your lightweight PLM system</p>
""", unsafe_allow_html=True)

create_database()
bom = BOM()
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    for row in rows:
        item = Item()
        item.item_number = row[0]
        item.upper_level_number = row[2]
        bom.add_item(item)

# Second pass to build relationships
for item in list(bom.items.values()):
    if item.upper_level_number:
        parent = bom.get_item(item.upper_level_number)
        if parent:
            parent.bom.add_item(item)
            parent.add_lower_level_item(item)
        del item.upper_level_number

main_menu = st.sidebar.selectbox("Main Menu", [
    "Item Management", "BOM Management", "Change Management", "Document Management", "System Status", "Purge Database"
])

# --- Item Management ---
if main_menu == "Item Management":
    st.header("Item Management")
    action = st.radio("Choose action", ["Create Item"])
    if action == "Create Item":
        if st.button("Create New Item"):
            new_item = Item()
            bom.add_item(new_item)
            add_item_to_db(new_item)
            st.success(f"Created Item {new_item.item_number}")

# --- BOM Management ---
if main_menu == "BOM Management":
    st.header("BOM Management")
    bom_action = st.radio("BOM Options", ["Link Items", "Show BOM"])

    if bom_action == "Link Items":
        parent = st.text_input("Parent Item Number")
        child = st.text_input("Child Item Number")
        if st.button("Link"):
            parent_item = bom.get_item(parent)
            child_item = bom.get_item(child)
            if parent_item and child_item:
                parent_item.add_lower_level_item(child_item)
                parent_item.bom.add_item(child_item)
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM items WHERE item_number = ?", (child_item.item_number,))
                if cursor.fetchone()[0] == 0:
                    add_item_to_db(child_item)
                cursor.execute("UPDATE items SET upper_level = ? WHERE item_number = ?", (parent_item.item_number, child_item.item_number))
                conn.commit()
                st.success(f"Linked {child} as child of {parent}")
            else:
                st.error("One or both items not found")

    elif bom_action == "Show BOM":
        item_number = st.text_input("Enter Item Number to Show BOM")
        item = bom.get_item(item_number)
        if item:
            st.subheader(f"BOM for {item.item_number}")
            st.markdown(f"**(Top Level)**: {item.item_number}")
            st.markdown(f"**BOM Revision:** {item.bom.revision}")
            if item.bom.items:
                import pandas as pd
                conn = get_db_connection()
                cursor = conn.cursor()
                bom_data = []
                for idx, i_num in enumerate(item.bom.items, start=1):
                    cursor.execute("SELECT COUNT(*) FROM items WHERE item_number = ?", (i_num,))
                    if cursor.fetchone()[0] == 0:
                        continue
                    quantity = item.bom.quantities.get(i_num, 1)
                    bom_data.append({
                        "Position": idx,
                        "Item Number": i_num,
                        "Quantity": quantity
                    })
                if bom_data:
                    bom_df = pd.DataFrame(bom_data)
                    st.dataframe(bom_df)
                else:
                    st.warning("All BOM items filtered out (not found in DB).")
            else:
                st.info("No items in BOM.")
        else:
            st.warning("Item not found")

# --- Change Management ---
if main_menu == "Change Management":
    st.header("Change Management")
    act = st.radio("Change Options", ["Create CR", "Update Status", "Show by Item", "Show All"])
    if act == "Create CR":
        item_number = st.selectbox("Choose Item", [row[0] for row in cursor.execute("SELECT item_number FROM items").fetchall()])
        item = bom.get_item(item_number)
        if item:
            reason = st.selectbox("Reason", [
                "A - Client Request",
                "B - Internal Request",
                "C - Bug Fix",
                "D - Admin Fix"
            ])
            cost = st.selectbox("Cost Impact", ["A - < 1k", "B - < 5k", "C - < 10k", "D - > 10k"])
            cost_value = {"A": "1", "B": "5", "C": "10", "D": "15"}[cost[0]]
            if st.button("Create Change Request"):
                cr = item.create_change_request(reason[0], cost_value, timeline_impact="< 2 weeks")
                add_change_request_to_db(cr)
                st.success(f"Created CR#{cr.change_request_number} for {item.item_number}")

# --- Document Management ---
if main_menu == "Document Management":
    st.header("Document Management")
    st.info("Document features coming soon.")

# --- System Status ---
if main_menu == "System Status":
    st.header("📊 System Status")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM items")
        item_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM change_requests")
        cr_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM documents")
        doc_count = cursor.fetchone()[0]
        st.metric("Total Items", item_count)
        st.metric("Change Requests", cr_count)
        st.metric("Documents", doc_count)
        error_log = 'plm_tool.log'
        if os.path.exists(error_log):
            with open(error_log, "r") as log_file:
                lines = log_file.readlines()
                errors = [line for line in lines if "ERROR" in line]
                recent_errors = errors[-3:] if errors else []
                st.markdown("### Recent Errors:")
                if recent_errors:
                    for err in recent_errors:
                        st.error(err.strip())
                else:
                    st.success("🟢 No recent errors found.")
        else:
            st.warning("Log file not found.")
    except Exception as e:
        st.error(f"Status check failed: {e}")

# --- Purge Database ---
if main_menu == "Purge Database":
    st.header("⚠️ Purge Entire Database")
    if st.checkbox("Yes, I understand this will delete all data."):
        if st.button("Purge"):
            conn = get_db_connection()
            for table in ["items", "change_requests", "documents"]:
                conn.execute(f"DELETE FROM {table}")
            conn.commit()
            bom = BOM()
            st.success("✅ Database has been purged.")
