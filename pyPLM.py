
import sqlite3
import logging

logging.basicConfig(filename='plm_tool.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    conn = sqlite3.connect('plm_database.db')
    conn.row_factory = sqlite3.Row
    return conn

def create_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            item_number TEXT PRIMARY KEY,
            revision TEXT,
            upper_level TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS change_requests (
            change_request_number INTEGER PRIMARY KEY,
            item_number TEXT,
            reason TEXT,
            cost_impact TEXT,
            timeline_impact TEXT,
            status TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            document_number TEXT PRIMARY KEY,
            version INTEGER,
            file_path TEXT,
            content TEXT
        )
    ''')
    conn.commit()

class BOM:
    def __init__(self):
        self.items = {}

    def add_item(self, item):
        self.items[item.item_number] = item

    def get_item(self, item_number):
        return self.items.get(item_number, None)

class Item:
    def __init__(self):
        self.item_number = self.generate_item_number()
        self.upper_level = None
        self.bom = BOM()

    def generate_item_number(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(CAST(SUBSTR(item_number, 2) AS INTEGER)) FROM items")
        last_number = cursor.fetchone()[0] or 0
        return f"P{last_number + 1:04d}"

    def add_lower_level_item(self, item):
        self.bom.add_item(item)
        item.upper_level = self

    def create_change_request(self, reason, cost_impact, timeline_impact):
        return ChangeRequest(self, reason, cost_impact, timeline_impact)

class ChangeRequest:
    def __init__(self, item, reason, cost_impact, timeline_impact):
        self.change_request_number = self.generate_cr_number()
        self.item = item
        self.reason = reason
        self.cost_impact = cost_impact
        self.timeline_impact = timeline_impact
        self.status = "Created"

    def generate_cr_number(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(change_request_number) FROM change_requests")
        last = cursor.fetchone()[0] or 999
        return last + 1

def add_item_to_db(item):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (item_number, revision, upper_level) VALUES (?, ?, ?)",
                       (item.item_number, "A", item.upper_level.item_number if item.upper_level else None))
        conn.commit()
    except Exception as e:
        logging.error(f"DB Error: {e}")

def add_change_request_to_db(cr):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO change_requests (change_request_number, item_number, reason, cost_impact, timeline_impact, status) VALUES (?, ?, ?, ?, ?, ?)",
                       (cr.change_request_number, cr.item.item_number, cr.reason, cr.cost_impact, cr.timeline_impact, cr.status))
        conn.commit()
    except Exception as e:
        logging.error(f"CR DB Error: {e}")
