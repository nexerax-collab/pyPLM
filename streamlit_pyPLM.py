import streamlit as st
import pandas as pd
import sqlite3
import time
from datetime import datetime

# Constants
CURRENT_UTC = "2025-04-15 11:55:00"
CURRENT_USER = "nexerax-collab"

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect(':memory:')
    c = conn.cursor()
    
    # Create tables
    c.execute('''CREATE TABLE IF NOT EXISTS modules
                 (id TEXT PRIMARY KEY, name TEXT, type TEXT, status TEXT, created_at TEXT)''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS changes
                 (id TEXT PRIMARY KEY, module_id TEXT, type TEXT, status TEXT, created_at TEXT)''')
    
    conn.commit()
    return conn

# Module class
class Module:
    def __init__(self, name, module_type):
        self.id = f"MOD_{int(time.time())}"
        self.name = name
        self.type = module_type
        self.status = "Draft"
        self.created_at = CURRENT_UTC

    def save(self, conn):
        c = conn.cursor()
        c.execute('''INSERT INTO modules (id, name, type, status, created_at)
                     VALUES (?, ?, ?, ?, ?)''',
                  (self.id, self.name, self.type, self.status, self.created_at))
        conn.commit()

# Change class
class Change:
    def __init__(self, module_id, change_type):
        self.id = f"CHG_{int(time.time())}"
        self.module_id = module_id
        self.type = change_type
        self.status = "Pending"
        self.created_at = CURRENT_UTC

    def save(self, conn):
        c = conn.cursor()
        c.execute('''INSERT INTO changes (id, module_id, type, status, created_at)
                     VALUES (?, ?, ?, ?, ?)''',
                  (self.id, self.module_id, self.type, self.status, self.created_at))
        conn.commit()

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.db = init_db()
    st.session_state.user_data = {
        'login': CURRENT_USER,
        'session_id': f"SESSION_{int(time.time())}",
        'start_time': CURRENT_UTC
    }

# Page configuration
st.set_page_config(
    page_title="PyPLM - Product Lifecycle Management",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application header
st.markdown(f"""
    <div style='background-color: #f0f2f6; padding: 1em; border-radius: 5px; margin-bottom: 1em;'>
        <h1 style='margin:0'>PyPLM</h1>
        <small style='color: #666;'>Product Lifecycle Management</small>
        <br>
        <small style='font-family: monospace;'>
            🕒 {CURRENT_UTC} UTC • 👤 {CURRENT_USER}
        </small>
    </div>
""", unsafe_allow_html=True)

# Main navigation
main_menu = st.sidebar.selectbox(
    "Navigation",
    [
        "🏠 Introduction",
        "📦 Module Management",
        "🔄 Change Control",
        "📊 Analytics"
    ]
)

# Module Management Section
def show_module_management():
    st.header("📦 Module Management")
    
    tab1, tab2, tab3 = st.tabs(["Create Module", "Browse Modules", "Module Details"])
    
    # Create Module Tab
    with tab1:
        with st.form("create_module"):
            st.subheader("Create New Module")
            
            module_name = st.text_input(
                "Module Name",
                placeholder="e.g., auth-service"
            )
            
            module_type = st.selectbox(
                "Module Type",
                [
                    "🌐 Microservice",
                    "📚 Library",
                    "🧩 Plugin",
                    "🎯 Feature Module"
                ]
            )
            
            description = st.text_area(
                "Description",
                placeholder="Describe your module..."
            )
            
            submitted = st.form_submit_button("Create Module")
            if submitted and module_name:
                module = Module(module_name, module_type)
                module.save(st.session_state.db)
                st.success(f"✅ Module created: {module.id}")
                st.balloons()
    
    # Browse Modules Tab
    with tab2:
        st.subheader("Browse Modules")
        
        c = st.session_state.db.cursor()
        c.execute('SELECT * FROM modules ORDER BY created_at DESC')
        modules = c.fetchall()
        
        if modules:
            df = pd.DataFrame(modules, columns=['ID', 'Name', 'Type', 'Status', 'Created'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No modules created yet.")
    
    # Module Details Tab
    with tab3:
        st.subheader("Module Details")
        
        c = st.session_state.db.cursor()
        c.execute('SELECT id, name FROM modules')
        modules = c.fetchall()
        
        if modules:
            selected_module = st.selectbox(
                "Select Module",
                options=[m[0] for m in modules],
                format_func=lambda x: next(m[1] for m in modules if m[0] == x)
            )
            
            if selected_module:
                c.execute('SELECT * FROM modules WHERE id = ?', (selected_module,))
                module = c.fetchone()
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                        ### Details
                        - **ID:** `{module[0]}`
                        - **Name:** {module[1]}
                        - **Type:** {module[2]}
                        - **Status:** {module[3]}
                        - **Created:** {module[4]}
                    """)
                
                with col2:
                    # Show related changes
                    c.execute('SELECT * FROM changes WHERE module_id = ?', (selected_module,))
                    changes = c.fetchall()
                    if changes:
                        st.markdown("### Changes")
                        for change in changes:
                            st.markdown(f"- {change[2]} ({change[3]})")
                    else:
                        st.info("No changes recorded for this module.")
        else:
            st.info("No modules available.")

# Change Control Section
def show_change_control():
    st.header("🔄 Change Control")
    
    tab1, tab2 = st.tabs(["Submit Change", "Review Changes"])
    
    # Submit Change Tab
    with tab1:
        with st.form("submit_change"):
            st.subheader("Submit New Change")
            
            c = st.session_state.db.cursor()
            c.execute('SELECT id, name FROM modules')
            modules = c.fetchall()
            
            if modules:
                module_id = st.selectbox(
                    "Select Module",
                    options=[m[0] for m in modules],
                    format_func=lambda x: next(m[1] for m in modules if m[0] == x)
                )
                
                change_type = st.selectbox(
                    "Change Type",
                    [
                        "✨ Feature",
                        "🐛 Bug Fix",
                        "🚀 Performance",
                        "📚 Documentation"
                    ]
                )
                
                submitted = st.form_submit_button("Submit Change")
                if submitted:
                    change = Change(module_id, change_type)
                    change.save(st.session_state.db)
                    st.success(f"✅ Change submitted: {change.id}")
            else:
                st.warning("Please create a module first.")
                submitted = st.form_submit_button("Submit Change", disabled=True)
    
    # Review Changes Tab
    with tab2:
        st.subheader("Review Changes")
        
        c = st.session_state.db.cursor()
        c.execute('''
            SELECT c.*, m.name as module_name 
            FROM changes c 
            JOIN modules m ON c.module_id = m.id 
            ORDER BY c.created_at DESC
        ''')
        changes = c.fetchall()
        
        if changes:
            df = pd.DataFrame(changes, columns=['ID', 'Module ID', 'Type', 'Status', 'Created', 'Module Name'])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No changes submitted yet.")

# Main content router
if main_menu == "🏠 Introduction":
    st.header("Welcome to PyPLM")
    st.markdown("""
        ### Getting Started
        1. Create a new module in the Module Management section
        2. Submit changes through Change Control
        3. Track progress in Analytics
    """)

elif main_menu == "📦 Module Management":
    show_module_management()

elif main_menu == "🔄 Change Control":
    show_change_control()

elif main_menu == "📊 Analytics":
    st.header("📊 Analytics")
    
    c = st.session_state.db.cursor()
    
    col1, col2 = st.columns(2)
    
    with col1:
        c.execute('SELECT COUNT(*) FROM modules')
        module_count = c.fetchone()[0]
        st.metric("Total Modules", module_count)
    
    with col2:
        c.execute('SELECT COUNT(*) FROM changes')
        change_count = c.fetchone()[0]
        st.metric("Total Changes", change_count)

# Session info in sidebar
with st.sidebar:
    st.markdown("### 🔍 Session Info")
    st.code(f"""
UTC Time : {CURRENT_UTC}
User     : {CURRENT_USER}
Session  : {st.session_state.user_data['session_id']}
    """)

# Debug mode
if st.sidebar.checkbox("🐛 Debug Mode"):
    st.sidebar.write("Session State:", st.session_state)
