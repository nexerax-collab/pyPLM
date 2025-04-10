import streamlit as st
import sqlite3
import hashlib
from pyPLM import (
    create_database, get_db_connection, Item, BOM, ChangeRequest,
    add_item_to_db, add_change_request_to_db, get_document_from_db,
    add_document_to_db
)

st.set_page_config(page_title="PyPLM", layout="wide")

# Authentication + init logic (same as before)...
# [KEEP YOUR USER LOGIN CODE FROM ABOVE UNCHANGED HERE]

# --- Sidebar Navigation ---
main_menu = st.sidebar.selectbox("Main Menu", [
    "Item Management", "Change Management", "Document Management", "BOM Management"] +
    (["User Management", "Purge Database"] if st.session_state.role == "admin" else [])
)

# --- Item Management ---
if main_menu == "Item Management":
    item_action = st.radio("Item Options", ["Create Item", "Link Items", "Show BOM"])

    if item_action == "Create Item":
        if st.button("Create New Item"):
            new_item = Item()
            bom.add_item(new_item)
            add_item_to_db(new_item)
            st.success(f"Created Item {new_item.item_number} (Rev {new_item.revision})")

    elif item_action == "Link Items":
        parent = st.text_input("Parent Item Number")
        child = st.text_input("Child Item Number")
        if st.button("Link"):
            parent_item = bom.get_item(parent)
            child_item = bom.get_item(child)
            if parent_item and child_item:
                parent_item.add_lower_level_item(child_item)
                st.success(f"Linked {child} as child of {parent}")
            else:
                st.error("One or both items not found")

    elif item_action == "Show BOM":
        item_number = st.text_input("Enter Item Number to Show BOM")
        item = bom.get_item(item_number)
        if item:
            st.subheader(f"BOM for {item.item_number} (Rev {item.revision})")
            if item.bom.items:
                for i_num in item.bom.items:
                    st.text(f"- {i_num}")
            else:
                st.info("No items in BOM.")
        else:
            st.warning("Item not found")

# --- Change Management ---
elif main_menu == "Change Management":
    cr_action = st.radio("Change Options", ["Create CR", "Update CR Status", "View by Item", "View All"])

    if cr_action == "Create CR":
        item_number = st.text_input("Item Number")
        item = bom.get_item(item_number)
        if item:
            reason = st.selectbox("Reason", ["A - Client Request", "B - Internal Request", "C - Bug Fix", "D - Admin Fix"])
            cost = st.text_input("Cost Impact (in k€)", "0")
            cr = item.create_change_request(reason[0], cost, timeline_impact="< 2 weeks")
            add_change_request_to_db(cr)
            st.success(f"Created CR#{cr.change_request_number} for {item.item_number}")

    elif cr_action == "Update CR Status":
        cr_num = st.text_input("Enter CR Number")
        new_status = st.selectbox("New Status", ["Created", "In Progress", "Accepted", "Declined"])
        cursor = get_db_connection().cursor()
        cursor.execute("UPDATE change_requests SET status = ? WHERE change_request_number = ?", (new_status, cr_num))
        get_db_connection().commit()
        st.success(f"CR#{cr_num} updated to {new_status}")

    elif cr_action == "View by Item":
        item_number = st.text_input("Enter Item Number")
        cursor = get_db_connection().cursor()
        cursor.execute("SELECT * FROM change_requests WHERE item_number = ?", (item_number,))
        for row in cursor.fetchall():
            st.markdown(f"**CR#{row[0]}** — Reason: {row[2]} | Cost: {row[3]} | Status: {row[5]}")

    elif cr_action == "View All":
        cursor = get_db_connection().cursor()
        cursor.execute("SELECT * FROM change_requests")
        for row in cursor.fetchall():
            st.markdown(f"**CR#{row[0]}** — Item: {row[1]} | Reason: {row[2]} | Cost: {row[3]} | Status: {row[5]}")

# --- Document Management ---
elif main_menu == "Document Management":
    doc_action = st.radio("Document Options", ["Show Document", "Attach to Item (todo)", "Attach to CR (todo)"])

    if doc_action == "Show Document":
        doc_number = st.text_input("Enter Document Number")
        doc = get_document_from_db(doc_number)
        if doc:
            st.markdown(f"**Document {doc.document_number}** (v{doc.version})")
            st.code(doc.content[:1000])
        else:
            st.warning("Not found")

# --- BOM Management ---
elif main_menu == "BOM Management":
    st.subheader("(To be implemented)")

# --- Admin Tools ---
elif main_menu == "Purge Database" and st.session_state.role == "admin":
    st.header("⚠️ Purge Entire Database")
    if st.checkbox("I understand this will permanently delete all records."):
        if st.button("Delete ALL Data"):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM items")
            cursor.execute("DELETE FROM change_requests")
            cursor.execute("DELETE FROM documents")
            conn.commit()
            st.success("Database purged")

elif main_menu == "User Management" and st.session_state.role == "admin":
    st.header("Create New User")
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    r = st.selectbox("Role", ["admin", "user"])
    if st.button("Create"):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                       (u, hash_password(p), r))
        conn.commit()
        st.success("User created")

st.markdown("---")
st.caption("Built with ❤️ for developers and config managers")
