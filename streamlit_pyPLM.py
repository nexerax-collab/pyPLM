
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

# Database + BOM
create_database()
bom = BOM()
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    for row in rows:
        item = Item()
        item.item_number = row[0]
        if row[2]:
            upper = bom.get_item(row[2])
            if upper:
                item.upper_level = upper
        bom.add_item(item)

main_menu = st.sidebar.selectbox("Main Menu", [
    "Item Management", "Change Management", "Document Management", "BOM Management",
    "User Management", "Purge Database", "System Status & Logs"
])

# Change Management
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
            cost = st.selectbox("Cost Impact", [
                "A - < 1k", "B - < 5k", "C - < 10k", "D - > 10k"
            ])
            if reason and cost:
                cost_value = {"A": "1", "B": "5", "C": "10", "D": "15"}[cost[0]]
                cr = item.create_change_request(reason[0], cost_value, timeline_impact="< 2 weeks")
                add_change_request_to_db(cr)
                st.success(f"Created CR#{cr.change_request_number} for {item.item_number}")
            else:
                st.warning("Please select a valid reason and cost impact.")

# (Other menus omitted for brevity - this focuses on the CR patch)

