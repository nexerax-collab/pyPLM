import streamlit as st
import pandas as pd
import os
from PIL import Image
from pyPLM import (
st.set_page_config(page_title="PyPLM", layout="centered", initial_sidebar_state="collapsed")
st.set_page_config(page_title="PyPLM", layout="centered", initial_sidebar_state="collapsed")

logo = Image.open("logo.png")
st.image(logo, use_column_width=False, width=200)

    create_database, get_db_connection, Item, BOM, ChangeRequest,
    add_item_to_db, add_change_request_to_db, get_document_from_db,
    add_document_to_db
)

# ---------- PAGE CONFIG ----------

# ---------- STYLES ----------
def apply_custom_styles(dark=False):
    primary = "#e8eaed" if not dark else "#202124"
    secondary = "#f1f3f4" if not dark else "#303134"
    text = "#202124" if not dark else "#ffffff"

    st.markdown(f"""
        <style>
        body {{
            background-color: {primary};
            color: {text};
        }}

        .stApp {{
            background-color: {primary};
        }}

        h1, h2, h3, label, .stTextInput label, .stRadio label {{
            color: {text} !important;
        }}

        .stButton > button {{
            background-color: {secondary};
            color: {text};
            border-radius: 24px;
            border: 1px solid #dadce0;
            padding: 0.5rem 1.5rem;
            font-size: 16px;
            transition: 0.3s ease;
        }}

        .stButton > button:hover {{
            background-color: #c6c6c6;
        }}

        .stTextInput input {{
            border-radius: 24px;
            padding: 0.6rem 1.2rem;
        }}

        .stFileUploader {{
            border: 1px dashed #dadce0;
            padding: 1rem;
            border-radius: 12px;
            background-color: #f8f9fa;
        }}

        #MainMenu, footer, header {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

# ---------- INIT ----------
create_database()
bom = BOM()

# Load existing items
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM items")
for row in cursor.fetchall():
    item = Item()
    item.item_number = row[0]
    item.revision = row[1]
    bom.add_item(item)

# Load change requests
cursor.execute("SELECT * FROM change_requests")
change_requests = []
for row in cursor.fetchall():
    item = bom.get_item(row[1])
    if item:
        cr = ChangeRequest(item, row[2], row[3], row[4])
        cr.change_request_number = row[0]
        cr.status = row[5]
        change_requests.append(cr)

# ---------- SETTINGS ----------
st.title("📦 PyPLM")
st.markdown("##### Minimal Product Lifecycle Management Tool")

dark_mode = st.toggle("🌙 Dark Mode", value=False)
apply_custom_styles(dark=dark_mode)

tab1, tab2, tab3, tab4 = st.tabs(["➕ Create", "🔄 Change Request", "📑 Documents", "📊 Overview"])

# ---------- TAB 1: CREATE ITEM ----------
with tab1:
    st.subheader("Create New Item")
    if st.button("➕ Generate New Item"):
        new_item = Item()
        bom.add_item(new_item)
        add_item_to_db(new_item)
        st.success(f"Item `{new_item.item_number}` (Rev `{new_item.revision}`) added.")

    st.markdown("---")
    st.subheader("Link Items")
    parent = st.text_input("Parent Item")
    child = st.text_input("Child Item")
    if st.button("🔗 Link Items"):
        bom.link_items(parent, child)
        st.success(f"Linked {child} under {parent}")

# ---------- TAB 2: CHANGE REQUEST ----------
with tab2:
    st.subheader("Create Change Request")
    item_id = st.text_input("Item Number for CR")
    reason = st.selectbox("Reason", ["A - Client", "B - Internal", "C - Bug Fix", "D - Admin"])
    cost = st.text_input("Cost Impact (in k€)", value="0")

    if st.button("🚀 Submit Change Request"):
        item = bom.get_item(item_id)
        if item:
            timeline_map = {"A": "< 2 weeks", "B": "< 1 month", "C": "< 3 months", "D": "< 6 months"}
            cr = item.create_change_request(reason[0], cost, timeline_map[reason[0]])
            add_change_request_to_db(cr)
            st.success(f"Change Request `{cr.change_request_number}` created.")
        else:
            st.error("Item not found.")

# ---------- TAB 3: DOCUMENT ATTACH ----------
with tab3:
    st.subheader("Attach PDF Document")
    attach_to = st.radio("Attach to", ["Item", "Change Request"], horizontal=True)
    target_id = st.text_input("Target ID")
    doc_type = st.text_input("Document Type")
    doc_file = st.file_uploader("Upload PDF", type=["pdf"])

    if st.button("📎 Attach Document"):
        if doc_file and target_id:
            path = f"temp_{doc_file.name}"
            with open(path, "wb") as f:
                f.write(doc_file.read())

            doc = Document(doc_type, file_path=path)
            doc.load_from_pdf(path)
            add_document_to_db(doc)

            if attach_to == "Item":
                item = bom.get_item(target_id)
                if item:
                    item.documents.append(doc.document_number)
                    st.success(f"📄 Document `{doc.document_number}` attached to Item `{item.item_number}`.")
                else:
                    st.error("Item not found.")
            else:
                st.warning("CR attachment not implemented yet.")
        else:
            st.warning("Please provide all required inputs.")

# ---------- TAB 4: OVERVIEW ----------
with tab4:
    st.subheader("📋 All Items")
    items_data = [{
        "Item Number": i.item_number,
        "Revision": i.revision,
        "Upper Level": i.upper_level.item_number if i.upper_level else "None"
    } for i in bom.items.values()]
    item_df = pd.DataFrame(items_data)

    item_filter = st.text_input("🔍 Filter Items")
    if item_filter:
        item_df = item_df[item_df.apply(lambda row: item_filter.lower() in str(row).lower(), axis=1)]
    st.dataframe(item_df, use_container_width=True)

    st.subheader("📋 All Change Requests")
    cr_data = [{
        "CR Number": cr.change_request_number,
        "Item": cr.item.item_number,
        "Reason": cr.reason,
        "Cost Impact": cr.cost_impact,
        "Timeline": cr.timeline_impact,
        "Type": cr.change_request_type,
        "Status": cr.status
    } for cr in change_requests]
    cr_df = pd.DataFrame(cr_data)

    cr_filter = st.text_input("🔍 Filter Change Requests")
    if cr_filter:
        cr_df = cr_df[cr_df.apply(lambda row: cr_filter.lower() in str(row).lower(), axis=1)]
    st.dataframe(cr_df, use_container_width=True)
