
import streamlit as st
import sqlite3
from pyPLM import (
    create_database, get_db_connection, Item, BOM, ChangeRequest,
    add_item_to_db, add_change_request_to_db
)

st.set_page_config(page_title="PyPLM", layout="wide")
st.markdown("<h1 style='color:#34a853;'>PyPLM</h1>", unsafe_allow_html=True)

create_database()
bom = BOM()

# Load items from DB
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM items")
for row in cursor.fetchall():
    item = Item()
    item.item_number = row["item_number"]
    if row["upper_level"]:
        item.upper_level_number = row["upper_level"]
        parent = bom.get_item(item.upper_level_number)
        if parent:
            item.upper_level = parent
            parent.bom.add_item(item)
            parent.add_lower_level_item(item)
    bom.add_item(item)

# Menu
main_menu = st.sidebar.selectbox("Menu", ["Item Management", "Change Requests", "BOM Management", "System Status", "Purge DB"])

if main_menu == "Item Management":
    st.header("Item Management")
    if st.button("Create New Item"):
        new_item = Item()
        bom.add_item(new_item)
        add_item_to_db(new_item)
        st.success(f"Created {new_item.item_number}")

    with st.form("link_form"):
        st.subheader("Link Items")
        parent = st.text_input("Parent Item")
        child = st.text_input("Child Item")
        submitted = st.form_submit_button("Link")
        if submitted:
            p = bom.get_item(parent)
            c = bom.get_item(child)
            if p and c:
                p.add_lower_level_item(c)
                st.success(f"Linked {child} under {parent}")
            else:
                st.error("One or both items not found")

if main_menu == "Change Requests":
    st.header("Create Change Request")
    with st.form("cr_form"):
        item_number = st.text_input("Item Number")
        reason = st.selectbox("Reason", ["A - Client", "B - Internal", "C - Bug", "D - Admin"])
        cost = st.selectbox("Cost Impact", ["<1k", "<5k", "<10k", ">10k"])
        submit_cr = st.form_submit_button("Create CR")
        if submit_cr:
            item = bom.get_item(item_number)
            if item:
                cr = item.create_change_request(reason[0], cost, "< 2 weeks")
                add_change_request_to_db(cr)
                st.success(f"Created CR#{cr.change_request_number}")
            else:
                st.error("Item not found")

if main_menu == "BOM Management":
    st.header("Show BOM")
    selected_item = st.text_input("Enter Item Number")
    item = bom.get_item(selected_item)
    if item:
        st.subheader(f"BOM for {item.item_number}")
        if item.bom.items:
            for i_num in item.bom.items:
                st.write(f"- {i_num}")
        else:
            st.info("No items in BOM.")

if main_menu == "System Status":
    st.header("System Status")
    try:
        with open("plm_tool.log", "r") as log:
            lines = log.readlines()
            st.code("".join(lines[-10:]), language="text")
    except FileNotFoundError:
        st.info("No recent log entries.")

if main_menu == "Purge DB":
    st.warning("This will delete all data.")
    if st.button("Confirm Purge"):
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM items")
        c.execute("DELETE FROM change_requests")
        c.execute("DELETE FROM documents")
        conn.commit()
        st.success("Database purged.")
