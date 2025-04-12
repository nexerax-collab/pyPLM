import streamlit as st
import sqlite3
import os
from pyPLM import (
    create_database, get_db_connection, Item, BOM, ChangeRequest,
    add_item_to_db, add_change_request_to_db, load_bom_links
)

st.set_page_config(page_title="PyPLM - Dev Mode", layout="wide")

if "tutorial_xp" not in st.session_state:
    st.session_state["tutorial_xp"] = 0
if "badge" not in st.session_state:
    st.session_state["badge"] = " Newbie Engineer"

# Badge logic
if st.session_state["tutorial_xp"] >= 3:
    st.session_state["badge"] = " PLM Practitioner"
if st.session_state["tutorial_xp"] >= 5:
    st.session_state["badge"] = " PLM Pro"

st.sidebar.markdown("### Progress")
st.sidebar.markdown(f"**Badge:** {st.session_state['badge']}")
st.sidebar.progress(st.session_state["tutorial_xp"] / 5)
st.markdown("<h1 style='color:#34a853;'>PyPLM (Dev Mode)</h1><p> A PLM tool reimagined for developers</p>", unsafe_allow_html=True)

create_database()
bom = BOM()

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT item_number FROM items")
available_item_ids = [row["item_number"] for row in cursor.fetchall()]

conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM items")
for row in cursor.fetchall():
    item = Item()
    item.item_number = row["item_number"]
    bom.add_item(item)

# Load links
load_bom_links(bom)

main_menu = st.sidebar.selectbox("Menu", [
    "Module Registry", "Patch Management", "Dependency Viewer", "System Status", "Purge DB",
    "Glossary", "Workflow Simulator", "Module Roadmap", "PLM Resources", "Interactive Tutorial"
])

# --- Module Registry ---
if main_menu == "Module Registry":
    st.header("Module Registry")
    if st.button(" Commit New Module"):
        new_item = Item()
        bom.add_item(new_item)
        add_item_to_db(new_item)
        st.success(f" Committed module `{new_item.item_number}` to registry")

    with st.form("link_form"):
        st.subheader(" Declare Dependency")
        parent = st.selectbox("Parent Module", options=available_item_ids)
        child = st.selectbox("Child Module", options=available_item_ids)
        quantity = st.number_input("Instances Required", min_value=1, value=1, help="How many units of this module are needed?")
        submitted = st.form_submit_button("Declare Link")
        if submitted:
            if parent and child:
                p = bom.get_item(parent)
                c = bom.get_item(child)
                if p and c:
                    p.add_lower_level_item(c, quantity)
                    st.success(f" `{child}` linked as dependency to `{parent}` (Qty: {quantity})")
                else:
                    st.error(" One or both modules not found in registry")

# --- Patch Management ---
if main_menu == "Patch Management":
    st.header("Pull Request (Patch) Tracker")
    with st.form("cr_form"):
        reason = st.selectbox("Patch Type", [
            "A - Feature Request",
            "B - Refactor",
            "C - Bugfix",
            "D - Hotfix"
        ], help="What type of change are you introducing?")
        cost = st.selectbox("Complexity Level", ["<1k", "<5k", "<10k", ">10k"], help="Estimated cost or size of the patch")
        item_number = st.selectbox("Module", options=available_item_ids)
        submit_cr = st.form_submit_button("Submit Pull Request")
        if submit_cr:
            item = bom.get_item(item_number)
            if item:
                cr = item.create_change_request(reason[0], cost, "< 2 weeks")
                add_change_request_to_db(cr)
                st.success(f" Pull Request #{cr.change_request_number} created for `{item.item_number}`")
            else:
                st.error(" Module not found")

# --- Dependency Viewer ---
if main_menu == "Dependency Viewer":
    st.header(" View Dependencies")
    selected_item = st.selectbox("Select Module to View", options=available_item_ids, index=0 if available_item_ids else None, help="View linked dependencies for this module")
    item = bom.get_item(selected_item)

    if item:
        st.markdown("### Dependency List (BOM View)")
        data = []
        data.append({
            "Module ID": item.item_number,
            "Role": "Top-level Module",
            "Quantity": 1
        })

        if item.bom.items:
            for child_id, child in item
