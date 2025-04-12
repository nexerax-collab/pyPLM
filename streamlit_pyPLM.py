import streamlit as st
import time
import sqlite3
from pyPLM_with_states import create_database, get_db_connection, Item, BOM, ChangeRequest, add_item_to_db, add_change_request_to_db, get_document_from_db, load_bom_links

st.set_page_config(page_title="PyPLM", layout="wide")
if "splash_shown" not in st.session_state:
    st.session_state["splash_shown"] = False

if not st.session_state["splash_shown"]:
    splash = st.empty()
    with splash.container():
        st.markdown("### 🐾 Booting up PyPLM...")
        st.code("""
          |\---/|
          | o_o |   Initializing Config Manager...
           \_^_/    🐱 Loading Change Requests...
        """, language="text")
        st.info("🔧 Committing Modules... Please Wait")
        time.sleep(5)
    splash.empty()
    st.session_state["splash_shown"] = True

# Init DB + BOM
create_database()
bom = BOM()
with get_db_connection() as conn:
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM items")
    rows = cursor.fetchall()
    for row in rows:
        item = Item()
        item.item_number = row[0]
        bom.add_item(item)

# Sidebar Navigation
main_menu = st.sidebar.selectbox("Main Menu", [
    "Item Management", "Change Management", "BOM Management", "Document Management",
    "Interactive Tutorial", "PLM Resources", "System Status"
])

if main_menu == "Item Management":
    st.header("📦 Module Management")
    action = st.radio("Choose action", ["Create Item", "Link Items"])
    if action == "Create Item":
        if st.button("🧱 Commit New Module"):
            item = Item()
            bom.add_item(item)
            add_item_to_db(item)
            st.success(f"Committed {item.item_number}")
    elif action == "Link Items":
        parent = st.text_input("Parent Module ID")
        child = st.text_input("Child Module ID")
        if st.button("🔗 Link"):
            p = bom.get_item(parent)
            c = bom.get_item(child)
            if p and c:
                p.add_lower_level_item(c)
                st.success(f"Linked {child} under {parent}")
            else:
                st.error("Modules not found.")

elif main_menu == "Change Management":
    st.header("🔁 Patches & Requests")
    item_id = st.text_input("Target Module ID")
    reason = st.selectbox("Reason", ["A - Feature", "B - Bug", "C - Refactor", "D - Other"])
    cost = st.text_input("Estimated Effort (e.g. 2d, 3h)")
    if st.button("Create CR"):
        item = bom.get_item(item_id)
        if item:
            cr = item.create_change_request(reason[0], cost, "< 2 weeks")
            add_change_request_to_db(cr)
            st.success(f"Created CR#{cr.change_request_number}")
        else:
            st.error("Module not found.")

elif main_menu == "BOM Management":
    st.header("📄 Dependency Viewer")
    parent = st.text_input("Enter Module ID")
    item = bom.get_item(parent)
    if item:
        st.subheader(f"BOM for {item.item_number}")
        st.markdown(f"- **Top Module**: {item.item_number} (Qty: 1)")
        if item.lower_level:
            for i, sub in enumerate(item.lower_level, 1):
                st.markdown(f"  {i}. {sub.item_number}")
        else:
            st.info("No linked dependencies.")

elif main_menu == "Document Management":
    st.header("📎 Document Management")
    st.markdown("To be added...")

elif main_menu == "Interactive Tutorial":
    st.header("🎓 Dev-Onboarding")
    st.markdown("Welcome! Here's how you build your first PLM flow:")
    st.markdown("- Commit module → Link → Create CR → Profit.")
    st.markdown("🧪 You can practice using the main menu.")
    if st.button("I did it!"):
        st.balloons()

elif main_menu == "PLM Resources":
    st.header("📚 Learn About PLM")
    st.markdown("**What is PLM?**")
    st.write("Product Lifecycle Management (PLM) is a geek's dream of controlling versions, changes, and traceability.")
    st.markdown("- [Why Change Management Matters](https://en.wikipedia.org/wiki/Change_management)")
    st.markdown("- [ARAS](https://www.aras.com/), [3DX](https://www.3ds.com/)")

elif main_menu == "System Status":
    st.header("🧠 System Status")
    try:
        cursor = get_db_connection().cursor()
        cursor.execute("SELECT COUNT(*) FROM items")
        item_count = cursor.fetchone()[0]
        st.success(f"Modules: {item_count}")
    except Exception as e:
        st.error("Database issue.")
