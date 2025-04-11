
import sqlite3

def get_db_connection():
    conn = sqlite3.connect("plm_database.db")
    conn.row_factory = sqlite3.Row
    return conn

class BOM:
    def __init__(self):
        self.items = {}
        self.quantities = {}
        self.revision = 1

    def add_item(self, item):
        self.items[item.item_number] = item

    def get_item(self, item_number):
        return self.items.get(item_number)

    def increment_revision(self):
        self.revision += 1

class Item:
    def __init__(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(CAST(SUBSTR(item_number, 2) AS INTEGER)) FROM items")
        last_number = cursor.fetchone()[0] or 0
        next_number = last_number + 1
        self.item_number = f"P{next_number:04}"
                self.upper_level = None
        self.lower_level = []
        self.bom = BOM()
        self.bom.add_item(self)  # Ensure root item is in BOM
        self.change_requests = []

    def add_lower_level_item(self, item):
        self.lower_level.append(item)
        item.upper_level = self

    def create_change_request(self, reason, cost_impact, timeline_impact):
        return ChangeRequest(self, reason, cost_impact, timeline_impact)

class ChangeRequest:
    def __init__(self, item, reason, cost_impact, timeline_impact):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT MAX(change_request_number) FROM change_requests")
        last = cur.fetchone()[0] or 999
        self.change_request_number = last + 1

        self.item = item
        self.reason = reason
        self.cost_impact = cost_impact
        self.timeline_impact = timeline_impact
        self.status = "Created"

class Document:
    def __init__(self, document_number, version, file_path, content):
        self.document_number = document_number
        self.version = version
        self.file_path = file_path
        self.content = content

def create_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            item_number TEXT PRIMARY KEY,
            revision TEXT,
            upper_level TEXT
        )''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS change_requests (
            change_request_number INTEGER PRIMARY KEY,
            item_number TEXT,
            reason TEXT,
            cost_impact TEXT,
            timeline_impact TEXT,
            status TEXT
        )''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            document_number TEXT PRIMARY KEY,
            version INTEGER,
            file_path TEXT,
            content TEXT
        )''')
    conn.commit()

def add_item_to_db(item):
    conn = get_db_connection()
    conn.execute("INSERT INTO items (item_number, revision, upper_level) VALUES (?, ?, ?)",
                 (item.item_number,  item.upper_level.item_number if item.upper_level else None))
    conn.commit()

def add_change_request_to_db(cr):
    conn = get_db_connection()
    conn.execute('''
        INSERT INTO change_requests (change_request_number, item_number, reason, cost_impact, timeline_impact, status)
        VALUES (?, ?, ?, ?, ?, ?)''',
        (cr.change_request_number, cr.item.item_number, cr.reason, cr.cost_impact, cr.timeline_impact, cr.status))
    conn.commit()

def get_document_from_db(doc_number):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM documents WHERE document_number = ?", (doc_number,))
    row = cur.fetchone()
    if row:
        return Document(row[0], row[1], row[2], row[3])
    return None

def add_document_to_db(doc):
    conn = get_db_connection()
    conn.execute("INSERT INTO documents (document_number, version, file_path, content) VALUES (?, ?, ?, ?)",
                 (doc.document_number, doc.version, doc.file_path, doc.content))
    conn.commit()
