import streamlit as st
import sqlite3
import hashlib
from pyPLM import (
    create_database, get_db_connection, Item, BOM, ChangeRequest,
    add_item_to_db, add_change_request_to_db, get_document_from_db,
    add_document_to_db
)

# Configure the page
st.set_page_config(page_title="PyPLM", layout="centered", initial_sidebar_state="expanded")

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to verify passwords
def verify_password(input_password, stored_hash):
    return hash_password(input_password) == stored_hash

# User session and authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.role = None

# Initialize user table if not exists
def init_user_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )''')
    conn.commit()
    # Add default admin user
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       ('admin', hash_password('admin'), 'admin'))
        conn.commit()

init_user_db()

# Authentication form
if not st.session_state.authenticated:
    with st.form("Login"):
        st.subheader("🔐 Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login = st.form_submit_button("Login")

    if login:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password, role FROM users WHERE username=?", (username,))
        row = cursor.fetchone()
        if row and verify_password(password, row[0]):
            st.session_state.authenticated = True
            st.session_state.role = row[1]
            st.success("Logged in successfully!")
            st.rerun()
        else:
            st.error("Invalid credentials")
    st.stop()

# Sidebar navigation
menu = ["Create Item", "Manage BOM", "Create Change Request", "View Change Requests", "View Documents"]
if st.session_state.role == "admin":
    menu += ["User Management", "Purge Database"]

menu_choice = st.sidebar.radio("🚀 Navigate", menu)

# Admin: Purge Database
if menu_choice == "Purge Database" and st.session_state.role == "admin":
    st.header("⚠️ Purge Entire Database")
    confirm = st.checkbox("I understand this will permanently delete all records.")
    if confirm and st.button("Delete ALL Data"):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM items")
        cursor.execute("DELETE FROM change_requests")
        cursor.execute("DELETE FROM documents")
        conn.commit()
        st.success("Database purged successfully.")

# Admin: User Management
elif menu_choice == "User Management" and st.session_state.role == "admin":
    st.header("👥 User Management")
    new_user = st.text_input("New Username")
    new_pass = st.text_input("New Password", type="password")
    new_role = st.selectbox("Role", ["user", "admin"])
    if st.button("Create User"):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                           (new_user, hash_password(new_pass), new_role))
            conn.commit()
            st.success(f"User '{new_user}' created.")
        except sqlite3.IntegrityError:
            st.error("User already exists.")

# Code-based logo header
st.markdown("""
    <h1 style='font-family: Google Sans, sans-serif; color: #34a853; font-size: 2.2rem; margin-bottom: 0;'>PyPLM</h1>
    <p style='font-family: Google Sans, sans-serif; color: #5f6368; font-size: 1.1rem; margin-top: 0;'>Product Lifecycle Management</p>
""", unsafe_allow_html=True)

# CSS styling for Google-like theme
st.markdown("""
    <style>
    html, body, [class*='css'] {
        font-family: 'Google Sans', sans-serif;
        background-color: #f8f9fa;
        color: #202124;
    }
    .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 900px; }
    .stButton>button {
        background-color: #34a853;
        color: white;
        font-size: 1rem;
        border-radius: 1.5rem;
        padding: 0.4rem 1.5rem;
        margin-bottom: 10px;
    }
    .stButton>button:hover { background-color: #0f9d58; }
    .stSidebar nav { font-size: 1rem; }
    </style>
""", unsafe_allow_html=True)

# Initialize database
create_database()
bom = BOM()

# Load existing items
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

# Functional sections for PLM
if menu_choice == "Create Item":
    st.header("Create New Item")
    new_item = Item()
    bom.add_item(new_item)
    add_item_to_db(new_item)
    st.success(f"Created Item {new_item.item_number} (Rev {new_item.revision})")

elif menu_choice == "Manage BOM":
    st.header("BOM Management")
    item_number = st.text_input("Enter Item Number to Show BOM")
    if item_number:
        item = bom.get_item(item_number)
        if item:
            st.subheader(f"BOM for {item.item_number} (Rev {item.revision})")
            if item.bom.items:
                for i_num in item.bom.items:
                    st.text(f"- {i_num}")
            else:
                st.info("No items in BOM.")
        else:
            st.error("Item not found.")

elif menu_choice == "Create Change Request":
    st.header("Create Change Request")
    item_number = st.text_input("Enter Item Number")
    if item_number:
        item = bom.get_item(item_number)
        if item:
            reason = st.selectbox("Reason", ["A - Client Request", "B - Internal Request", "C - Bug Fix", "D - Admin Fix"])
            cost_impact = st.text_input("Cost Impact (in k€)", "0")
            cr = item.create_change_request(reason[0], cost_impact, timeline_impact="< 2 weeks")
            add_change_request_to_db(cr)
            st.success(f"Change Request {cr.change_request_number} created.")
        else:
            st.error("Item not found.")

elif menu_choice == "View Change Requests":
    st.header("Change Requests")
    status_filter = st.selectbox("Filter by status", ["All", "Created", "In Progress", "Accepted", "Declined"])
    cursor = get_db_connection().cursor()
    query = "SELECT * FROM change_requests"
    if status_filter != "All":
        query += f" WHERE status = '{status_filter}'"
    cursor.execute(query)
    rows = cursor.fetchall()
    for row in rows:
        st.markdown(f"**CR#{row[0]}** — Item: `{row[1]}` | Reason: {row[2]} | Cost: {row[3]} | Timeline: {row[4]} | Status: `{row[5]}`")

elif menu_choice == "View Documents":
    st.header("Documents")
    doc_number = st.text_input("Enter Document Number")
    if doc_number:
        doc = get_document_from_db(doc_number)
        if doc:
            st.markdown(f"**Document {doc.document_number}** (v{doc.version})")
            st.code(doc.content[:1000])
        else:
            st.warning("Document not found.")

st.markdown("---")
st.caption("Built with ❤️ for developers and config managers")
