import streamlit as st
import os
import sqlite3
from pyPLM import (
    create_database, get_db_connection, Item, BOM, ChangeRequest,
    add_item_to_db, add_change_request_to_db, get_document_from_db
)

st.set_page_config(page_title="PyPLM", layout="wide")

# Session state
if 'role' not in st.session_state:
    st.session_state['role'] = 'admin'
if 'username' not in st.session_state:
    st.session_state['username'] = 'admin'

# Header
st.markdown("""
<h1 style='font-family: Google Sans, sans-serif; color: #34a853;'>PyPLM</h1>
<p style='color:gray;'>Your lightweight PLM system</p>
""", unsafe_allow_html=True)

# Database and BOM setup
create_database()
bom = BOM()
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    for row in rows:
        item = Item()
        item.upper_level_number = row[2]
        item.item_number = row[0]
        if row[2]:
            upper = bom.get_item(row[2])
            if upper:
                item.upper_level = upper
        bom.add_item(item)

# Second pass: establish BOM relationships from upper_level
for item in list(bom.items.values()):
    if item.upper_level_number:
        parent = bom.get_item(item.upper_level_number)
        if parent:
            parent.bom.add_item(item)
            parent.add_lower_level_item(item)
            del item.upper_level_number

# System Status Menu
elif main_menu == "System Status":
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

        # Log preview
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
