import streamlit as st
import pandas as pd
import os
from PIL import Image
from pyPLM import (
    create_database, get_db_connection, Item, BOM, ChangeRequest,
    add_item_to_db, add_change_request_to_db, get_document_from_db,
    add_document_to_db, Document
)

st.set_page_config(page_title="PyPLM", layout="centered", initial_sidebar_state="collapsed")

logo = Image.open("logo.png")
st.image(logo, use_column_width=False, width=200)

# Your Streamlit logic would continue from here...