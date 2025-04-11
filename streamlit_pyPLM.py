
import streamlit as st
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

# Branding/Header
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

# Item Management
if main_menu == "Item Management":
    st.header("Item Management")
    action = st.radio("Choose action", ["Create Item", "Link Items", "Show BOM"])
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
            for i_num, child in item.bom.items.items():
                qty = item.bom.quantities.get(i_num, 1)
                st.markdown(f"- {i_num} (Qty: {qty}, )")
                st.markdown(f"- {child.item_number} (Rev {child.revision})")
        else:
            st.warning("Item not found")

# Change Management
elif main_menu == "Change Management":
    st.header("Change Management")
    act = st.radio("Change Options", ["Create CR", "Update Status", "Show by Item", "Show All"])
    if act == "Create CR":
        conn = get_db_connection()
        items = [row[0] for row in conn.execute("SELECT item_number FROM items").fetchall()]
        item_number = st.selectbox("Choose item", items)  # dropdown suggestion
        item = bom.get_item(item_number)
        if item:
            reason = st.selectbox("Reason", ["", "A", "B", "C", "D"])
            cost = st.text_input("Cost (€k)", "0")
            if reason and cost.replace(".", "", 1).isdigit():
                cr = item.create_change_request(reason, cost, timeline_impact="< 2 weeks")
                add_change_request_to_db(cr)
                st.success(f"CR#{cr.change_request_number} created")
            else:
                st.warning("Reason and cost required.")
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
        conn = get_db_connection()
        items = [row[0] for row in conn.execute("SELECT item_number FROM items").fetchall()]
        item_number = st.selectbox("Choose item", items)  # dropdown suggestion
        conn = get_db_connection()
        rows = conn.execute("SELECT * FROM change_requests WHERE item_number = ?", (item_number,))
        for row in rows.fetchall():
            st.markdown(f"**CR#{row[0]}** — Reason: {row[2]} | Status: {row[5]}")
    elif act == "Show All":
        rows = get_db_connection().execute("SELECT * FROM change_requests")
        for row in rows.fetchall():
            st.markdown(f"**CR#{row[0]}** — Item: {row[1]} | Reason: {row[2]} | Status: {row[5]}")

# Document Management
elif main_menu == "Document Management":
    st.header("Document Viewer")
    num = st.text_input("Document Number")
    d = get_document_from_db(num)
    if d:
        st.code(d.content[:1000])
    else:
        st.warning("Document not found")

# BOM Management
elif main_menu == "BOM Management":
    st.header("BOM Management")
    bom_action = st.radio("Select Action", ["Show BOM", "Link Items", "Remove Item", "Change Quantity", "Increment BOM Revision"])
    if bom_action == "Show BOM":
        conn = get_db_connection()
        items = [row[0] for row in conn.execute("SELECT item_number FROM items").fetchall()]
        item_number = st.selectbox("Choose item", items)  # dropdown suggestion
        item = bom.get_item(item_number)
        if item:
            st.write(f"BOM for {item.item_number}")
            for i_num, child in item.bom.items.items():
                qty = item.bom.quantities.get(i_num, 1)
                st.markdown(f"- {i_num} (Qty: {qty}, )")
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
                if not hasattr(parent_item.bom, "quantities"):
                    parent_item.bom.quantities = {}
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
        conn = get_db_connection()
        items = [row[0] for row in conn.execute("SELECT item_number FROM items").fetchall()]
        item_number = st.selectbox("Choose item", items)  # dropdown suggestion
        item = bom.get_item(item_number)
        if item:
            item.bom.increment_revision()
            st.success(f"BOM revision incremented to {item.bom.revision}")
        else:
            st.warning("Item not found")

# Admin Sections
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
    st.subheader("Add new user (coming soon)")


elif main_menu == "System Status & Logs":
    st.header("🔍 System Status Overview")
    st.write("Current application health and database status:")

    # DB Status
    st.markdown("**Database:** 🟢 Initialized")

    # BOM
    st.markdown("**BOM:** 🟢 Initialized")

    # Check item count
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM items")
    item_count = cursor.fetchone()[0]
    if item_count == 0:
        st.markdown("**Items in DB:** 🟡 No items found")
    else:
        st.markdown(f"**Items in DB:** 🟢 {item_count} item(s)")
    
    st.subheader("📊 Database Statistics")

    # Total entries per table (ordered and clearly labeled)
    tables = [("items", "📦 Items"), ("change_requests", "🔁 Change Requests"), ("documents", "📄 Documents")]
    for table_name, label in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            st.markdown(f"**{label}**: {count} record(s)")


    # Check for errors in log file
    import os
    error_log = 'plm_tool.log'
    if os.path.exists(error_log):
        with open(error_log) as log_file:
            logs = log_file.read()
            if "ERROR" in logs:
                st.markdown("**Recent Errors:** 🔴 Found")
            else:
                st.markdown("**Recent Errors:** 🟢 None")
    else:
        st.markdown("**Log File:** 🟡 Not found")


st.caption("Built with ❤️ for developers and config managers")
