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
        item.upper_level_number = row[2]
        item = Item()
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
