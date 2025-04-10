import streamlit as st
from PIL import Image
from pyPLM import (
    create_database, get_db_connection, Item, BOM, ChangeRequest,
    add_item_to_db, add_change_request_to_db, get_document_from_db,
    add_document_to_db
)

# Configure the page
st.set_page_config(page_title="PyPLM", layout="centered", initial_sidebar_state="collapsed")

# Display logo
logo = Image.open("logo.png")
st.image(logo, width=100)

# Toggle dark mode
dark_mode = st.toggle("🌙 Dark Mode", value=False)

# CSS styling
if dark_mode:
    background = "#202124"
    text = "#ffffff"
else:
    background = "#f8f9fa"
    text = "#202124"

st.markdown(f"""
    <style>
    html, body, [class*='css'] {{
        font-family: 'Google Sans', sans-serif;
        background-color: {background};
        color: {text};
    }}
    .block-container {{ padding-top: 2rem; padding-bottom: 2rem; max-width: 900px; }}
    .stButton>button {{
        background-color: #34a853;
        color: white;
        font-size: 1rem;
        border-radius: 1.5rem;
        padding: 0.4rem 1.5rem;
        margin-bottom: 10px;
    }}
    .stButton>button:hover {{ background-color: #0f9d58; }}
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

# MENU
menu = st.sidebar.radio("Navigate", ["Create Item", "Manage BOM", "Create Change Request", "View Change Requests", "View Documents"])

if menu == "Create Item":
    st.header("Create New Item")
    new_item = Item()
    bom.add_item(new_item)
    add_item_to_db(new_item)
    st.success(f"Created Item {new_item.item_number} (Rev {new_item.revision})")

elif menu == "Manage BOM":
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

elif menu == "Create Change Request":
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

elif menu == "View Change Requests":
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

elif menu == "View Documents":
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
st.caption("Built with ❤️ for engineers")
