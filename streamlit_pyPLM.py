import streamlit as st
import sqlite3
import hashlib
from pyPLM import (
    create_database, get_db_connection, Item, BOM, ChangeRequest,
    add_item_to_db, add_change_request_to_db, get_document_from_db,
    add_document_to_db
)

st.set_page_config(page_title="PyPLM", layout="wide")

# Init DB and BOM
create_database()
bom = BOM()

# Load items from DB
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

# Dev override for login
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = True
    st.session_state.role = 'admin'

main_menu = st.sidebar.selectbox("Main Menu", [
    "Item Management", "Change Management", "Document Management", "BOM Management"] +
    (["User Management", "Purge Database"] if st.session_state.role == "admin" else [])
)

# ---------- ITEM MANAGEMENT ----------
if main_menu == "Item Management":
    action = st.radio("Item Options", ["Create Item", "Link Items", "Show BOM"])

    if action == "Create Item":
        if st.button("Create New Item"):
            item = Item()
            bom.add_item(item)
            add_item_to_db(item)
            st.success(f"Created Item {item.item_number} (Rev {item.revision})")

    elif action == "Link Items":
        p = st.text_input("Parent Item")
        c = st.text_input("Child Item")
        if st.button("Link"):
            parent = bom.get_item(p)
            child = bom.get_item(c)
            if parent and child:
                parent.add_lower_level_item(child)
                st.success(f"Linked {c} under {p}")
            else:
                st.error("One or both items not found")

    elif action == "Show BOM":
        target = st.text_input("Item to show BOM")
        item = bom.get_item(target)
        if item:
            st.write(f"BOM for {item.item_number}")
            for child in item.lower_level:
                st.markdown(f"- {child.item_number} (Rev {child.revision})")
        else:
            st.warning("Item not found")

# ---------- CHANGE MANAGEMENT ----------
elif main_menu == "Change Management":
    act = st.radio("Change Options", ["Create CR", "Update Status", "Show by Item", "Show All"])

    if act == "Create CR":
        item_number = st.text_input("Item Number")
        item = bom.get_item(item_number)
        if item:
            reason = st.selectbox("Reason", ["A", "B", "C", "D"])
            cost = st.text_input("Cost (€k)", "0")
            cr = item.create_change_request(reason, cost, timeline_impact="< 2 weeks")
            add_change_request_to_db(cr)
            st.success(f"CR#{cr.change_request_number} created")
        else:
            st.warning("Item not found")

    elif act == "Update Status":
        cr_num = st.text_input("CR Number")
        new = st.selectbox("New Status", ["Created", "In Progress", "Accepted", "Declined"])
        conn = get_db_connection()
        conn.execute("UPDATE change_requests SET status = ? WHERE change_request_number = ?", (new, cr_num))
        conn.commit()
        st.success(f"CR#{cr_num} updated")

    elif act == "Show by Item":
        item_number = st.text_input("Item Number")
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM change_requests WHERE item_number = ?", (item_number,))
        for row in rows.fetchall():
            st.markdown(f"**CR#{row[0]}** — Reason: {row[2]} | Status: {row[5]}")

    elif act == "Show All":
        rows = get_db_connection().execute("SELECT * FROM change_requests")
        for row in rows.fetchall():
            st.markdown(f"**CR#{row[0]}** — Item: {row[1]} | Reason: {row[2]} | Status: {row[5]}")

# ---------- DOCUMENT MANAGEMENT ----------
elif main_menu == "Document Management":
    doc = st.radio("Doc Options", ["Show Doc"])
    if doc == "Show Doc":
        num = st.text_input("Document Number")
        d = get_document_from_db(num)
        if d:
            st.code(d.content[:1000])
        else:
            st.warning("Not found")

# ---------- BOM MANAGEMENT ----------
elif main_menu == "BOM Management":
    st.subheader("BOM Management")

    bom_action = st.radio("Select Action", ["Show BOM", "Link Items", "Remove Item", "Change Quantity", "Increment BOM Revision"])

    if bom_action == "Show BOM":
        item_number = st.text_input("Enter Item Number")
        item = bom.get_item(item_number)
        if item:
            st.write(f"BOM for {item.item_number}")
            for child in item.lower_level:
                qty = item.bom.quantities.get(child.item_number, 1)
                st.markdown(f"- {child.item_number} (Qty: {qty})")
        else:
            st.warning("Item not found")

    elif bom_action == "Link Items":
        parent = st.text_input("Parent Item Number")
        child = st.text_input("Child Item Number")
        quantity = st.number_input("Quantity", min_value=1, value=1)
        if st.button("Link Child"):
            parent_item = bom.get_item(parent)
            child_item = bom.get_item(child)
            if parent_item and child_item:
                parent_item.add_lower_level_item(child_item)
                parent_item.bom.quantities[child_item.item_number] = quantity
                st.success(f"Linked {child_item.item_number} to {parent_item.item_number} with qty {quantity}")
            else:
                st.error("One or both items not found")

    elif bom_action == "Remove Item":
        parent = st.text_input("Parent Item Number")
        child = st.text_input("Child Item Number to Remove")
        if st.button("Remove Child"):
            parent_item = bom.get_item(parent)
            if parent_item and child in [c.item_number for c in parent_item.lower_level]:
                parent_item.lower_level = [c for c in parent_item.lower_level if c.item_number != child]
                parent_item.bom.quantities.pop(child, None)
                st.success(f"Removed {child} from {parent}")
            else:
                st.warning("Link not found")

    elif bom_action == "Change Quantity":
        parent = st.text_input("Parent Item")
        child = st.text_input("Child Item")
        quantity = st.number_input("New Quantity", min_value=1, value=1)
        if st.button("Update Quantity"):
            parent_item = bom.get_item(parent)
            if parent_item and child in parent_item.bom.quantities:
                parent_item.bom.quantities[child] = quantity
                st.success(f"Updated quantity of {child} in {parent} BOM to {quantity}")
            else:
                st.warning("Item not found in BOM")

    elif bom_action == "Increment BOM Revision":
        item_number = st.text_input("Enter Item to Revise")
        item = bom.get_item(item_number)
        if item:
            item.bom.increment_revision()
            st.success(f"BOM revision incremented to {item.bom.revision}")
        else:
            st.warning("Item not found")

# ---------- ADMIN TOOLS ----------
elif main_menu == "Purge Database":
    if st.session_state.role == "admin":
        if st.checkbox("Yes, I understand"):
            if st.button("Purge"):
                conn = get_db_connection()
                for table in ["items", "change_requests", "documents"]:
                    conn.execute(f"DELETE FROM {table}")
                conn.commit()
                st.success("Database purged.")

elif main_menu == "User Management":
    st.subheader("Add new user (not yet functional)")
    st.text_input("Username")
    st.text_input("Password", type="password")

st.caption("Built with ❤️ for developers and config managers")
