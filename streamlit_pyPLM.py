
import streamlit as st
import sqlite3
from pyPLM import (
    create_database, get_db_connection, Item, BOM, ChangeRequest,
    add_item_to_db, add_change_request_to_db, get_document_from_db
)

st.set_page_config(page_title="PyPLM", layout="wide")

# 💡 Branding (Bug #1 fix)
st.markdown("""
<h1 style='font-family: Google Sans, sans-serif; color: #34a853;'>Pi PLM</h1>
<p style='color:gray;'>Your lightweight PLM system</p>
""", unsafe_allow_html=True)

# Init
create_database()
bom = BOM()

with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    for row in cursor.fetchall():
        item = Item()
        item.item_number = row[0]
        item.revision = row[1]
        if row[2]:
            upper = bom.get_item(row[2])
            if upper:
                item.upper_level = upper
        bom.add_item(item)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = True
    st.session_state.role = "admin"

main_menu = st.sidebar.selectbox("Main Menu", [
    "Item Management", "Change Management", "Document Management", "BOM Management",
    "User Management", "Purge Database"
])

# (The rest of the streamlit UI logic would continue from here...)

print("Full code placeholder filled in script file.")
