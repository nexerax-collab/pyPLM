import streamlit as st
import time
from pyPLM import create_database, get_db_connection, Item, BOM, ChangeRequest, add_item_to_db, add_change_request_to_db, get_document_from_db, load_bom_links

st.set_page_config(page_title="PyPLM", layout="wide")
if "splash_shown" not in st.session_state:
    splash = st.empty()
    with splash.container():
        st.markdown("### 🐾 Booting PyPLM...")
        st.code("""
  |\---/|
  | o_o |   Initializing Config Manager...
   \_^_/    🐱 Loading Modules...
""")
        st.info("🔧 Committing Modules...")
        time.sleep(3)
    splash.empty()
    st.session_state["splash_shown"] = True

# Init
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
    load_bom_links(bom)

menu = st.sidebar.selectbox("Main Menu", [
    "Item Management", "Change Management", "BOM Management", "Tutorial", "Resources", "System Status"
])

if menu == "Item Management":
    st.header("📦 Module Control")
    if st.button("Create Module"):
        item = Item()
        bom.add_item(item)
        add_item_to_db(item)
        st.success(f"Created: {item.item_number}")
    parent = st.text_input("Parent Module")
    child = st.text_input("Child Module")
    if st.button("Link Modules"):
        p = bom.get_item(parent)
        c = bom.get_item(child)
        if p and c:
            p.add_lower_level_item(c)
            st.success(f"Linked {child} under {parent}")
        else:
            st.error("One or both not found.")

elif menu == "Change Management":
    st.header("🔧 Change Requests")
    item_number = st.text_input("Module ID for CR")
    reason = st.selectbox("Reason", ["A - Feature", "B - Bug", "C - Refactor", "D - Other"])
    cost = st.text_input("Effort (e.g. 2d)")
    if st.button("Create Change Request"):
        item = bom.get_item(item_number)
        if item:
            cr = item.create_change_request(reason[0], cost, "< 2 weeks")
            add_change_request_to_db(cr)
            st.success(f"CR#{cr.change_request_number} created")
        else:
            st.warning("Module not found.")

elif menu == "BOM Management":
    st.header("📄 Bill of Materials")
    mid = st.text_input("Module to show")
    item = bom.get_item(mid)
    if item:
        st.markdown(f"**Top Level**: {item.item_number} (Qty: 1)")
        if item.lower_level:
            for i, sub in enumerate(item.lower_level, 1):
                st.markdown(f"{i}. {sub.item_number}")
        else:
            st.info("No submodules linked.")
    else:
        st.warning("Module not found.")

elif menu == "Tutorial":
    st.header("🎓 Interactive Dev Onboarding")
    st.markdown("Learn PLM like a dev. Try: Create > Link > CR.")
    if st.button("Complete Tutorial"):
        st.balloons()

elif menu == "Resources":
    st.header("📚 PLM 101")
    st.markdown("- [Change Management](https://en.wikipedia.org/wiki/Change_management)")
    st.markdown("- [ARAS](https://www.aras.com/), [Dassault 3DX](https://www.3ds.com/)")

elif menu == "System Status":
    st.header("📊 Status")
    try:
        cursor = get_db_connection().cursor()
        cursor.execute("SELECT COUNT(*) FROM items")
        count = cursor.fetchone()[0]
        st.success(f"Modules: {count}")
    except:
        st.error("Could not connect to DB.")
