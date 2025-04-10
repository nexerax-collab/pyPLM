import streamlit as st
from pyngrok import ngrok
import streamlit as st
import re
import sqlite3
import PyPDF2
import os
import logging

# Set up logging
logging.basicConfig(filename='plm_tool.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Database connection pooling
database_connections = {}

def get_db_connection():
    """Gets a database connection from the pool or creates a new one."""
    if 'conn' not in database_connections:
        database_connections['conn'] = sqlite3.connect('plm_database.db')
        # Enable foreign key constraints
        database_connections['conn'].execute("PRAGMA foreign_keys = ON")
    return database_connections['conn']

# Global variables to store next item number and change request number
next_item_number = 1
next_change_request_number = 1000

# Global variables for recent selections
recent_items= []  # Store last 5 created items
recent_change_requests = []  # Store last 5 created change requests

# Global variables for document numbering
next_document_number = 1
next_bom_number = 1  # Initialize next_bom_number

class Document:
    def __init__(self, document_type, file_path=None, content=None):
        global next_document_number
        self.document_number = self.generate_document_number(document_type)
        self.version = 1
        self.file_path = file_path  # Store file path
        self.content = content

    def generate_document_number(self, document_type):
        global next_document_number
        prefix = document_type[0].upper() + "0"
        document_number = f"{prefix}{next_document_number:03d}"
        next_document_number += 1
        return document_number

    def update_content(self, new_content):
        self.version += 1
        self.content = new_content

    def __str__(self):
        return f"Document {self.document_number} (Version {self.version})"

    def load_from_pdf(self, file_path):
        """Loads document content from a PDF file."""
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            self.content = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                self.content += page.extract_text()

class Item:
    def __init__(self):
        self.item_number = self.generate_item_number()
        self.revision = 'A'
        self.upper_level = None
        self.lower_level = []
        self.change_requests = []
        self.bom = BOM()
        self.documents = []  # List to store document numbers attached to the item

    def generate_item_number(self):
        global next_item_number
        item_number = f"P{next_item_number:04d}"
        next_item_number += 1
        return item_number

    def validate_item_number(self, item_number):
        return re.fullmatch(r"\d{4}", item_number) is not None

    def validate_revision(self, revision):
        return re.fullmatch(r"[A-F0-9]+", revision) is not None

    def add_lower_level_item(self, item):
        self.lower_level.append(item)
        item.upper_level = self

    def __str__(self):
        return f"Item Number: {self.item_number}, Revision: {self.revision}"

    def create_change_request(self, reason, cost_impact, timeline_impact):
        change_request = ChangeRequest(self, reason, cost_impact, timeline_impact)
        self.change_requests.append(change_request)
        return change_request

    def update_revision(self):
        current_revision = self.revision
        next_revision = chr(ord(current_revision) + 1)

        if 'A' <= next_revision <= 'F':
            self.revision = next_revision
            if self.upper_level:
                bom = self.upper_level
                while bom.upper_level is not None:
                    bom = bom.upper_level
                bom.increment_revision()
        else:
            print("Revision cannot be incremented further (max is F).")

    def show_attached_documents(self):
        if self.documents:
            print(f"Documents attached to Item {self.item_number}:")
            for document_number in self.documents:
                document = get_document_from_db(document_number)
                if document:
                    print(document)
                else:
                    print(f"Document {document_number} not found in the database.")
        else:
            print(f"No documents attached to Item {self.item_number}.")

class ChangeRequest:
    def __init__(self, item, reason, cost_impact, timeline_impact):
        global next_change_request_number
        self.change_request_number = next_change_request_number
        next_change_request_number += 1
        self.item = item
        self.reason = reason

        if not cost_impact.endswith("k€"):
            cost_impact += "k€"
        try:
            self.cost_impact_numeric = float(cost_impact[:-2])
        except ValueError:
            self.cost_impact_numeric = 0.0

        self.cost_impact = cost_impact

        if reason == "A":
            self.timeline_impact = timeline_impact if timeline_impact in ["< 2 weeks"] else "< 2 weeks"
        elif reason == "B":
            self.timeline_impact = timeline_impact if timeline_impact in ["< 1 month"] else "< 1 month"
        elif reason == "C":
            self.timeline_impact = timeline_impact if timeline_impact in ["< 3 months"] else "< 3 months"
        elif reason == "D":
            self.timeline_impact = timeline_impact if timeline_impact in ["< 6 months"] else "< 6 months"
        else:
            self.timeline_impact = "Unknown"

        if self.cost_impact_numeric >= 1000 or self.timeline_impact in ["< 3 months", "< 6 months"]:
            self.change_request_type = "Major"
        else:
            self.change_request_type = "Minor"

        self.status = "Created"
        self.documents = []  # List to store document numbers attached to the change request

    def attach_document(self, document_type):
        file_path = input("Enter the path to the PDF file: ")
        if os.path.exists(file_path) and file_path.lower().endswith(".pdf"):
            document = Document(document_type, file_path=file_path)
            document.load_from_pdf(file_path)
            add_document_to_db(document)  # Add document to database
            self.documents.append(document.document_number)  # Attach document to change request
            print(f"Document {document.document_number} attached to Change Request {self.change_request_number}.")
        else:
            print("Invalid file path or file type.")

    def show_attached_documents(self):
        if self.documents:
            print(f"Documents attached to Change Request {self.change_request_number}:")
            for document_number in self.documents:
                document = get_document_from_db(document_number)
                if document:
                    print(document)
                else:
                    print(f"Document {document_number} not found in the database.")
        else:
            print(f"No documents attached to Change Request {self.change_request_number}.")

    def update_status(self, new_status):
        if new_status in ["Created", "In Progress", "Accepted", "Declined"]:
            self.status = new_status
            if new_status == "Accepted":
                self.item.update_revision()
        else:
            print("Invalid change request status.")

    def __str__(self):
        return f"Change Request {self.change_request_number}: {self.reason} ({self.change_request_type}) (Status: {self.status})"

class BOM:
    def __init__(self):
        self.items = {}  # Store items with item number as key
        self.revision = 1  # Initialize BOM revision to 1
        self.item_number = None  # Add item_number attribute to BOM
        self.quantities = {}  # Store quantities for each item in this BOM

    def generate_bom_number(self):
        global next_bom_number
        bom_number = f"B{next_bom_number:04d}"
        next_bom_number += 1
        return bom_number

    def add_item(self, item):
        if item.item_number in self.items:
            print(f"Item {item.item_number} already exists.")
        else:
            self.items[item.item_number] = item
            self.item_number = item.item_number
            self.bom_number = self.generate_bom_number()

    def change_quantity(self, item_number, new_quantity):
        if item_number in self.quantities:
            self.quantities[item_number] = new_quantity
            print(f"Quantity for item {item_number} in BOM updated to {new_quantity}.")
        else:
            print(f"Item {item_number} not found in this BOM.")
    
    def get_item(self, item_number):
        return self.items.get(item_number, None)
        self.quantities[item.item_number] = quantity

    def link_items(self, parent_item_number, child_item_number):
        parent_item = self.get_item(parent_item_number)
        child_item = self.get_item(child_item_number)

        if parent_item and child_item:
            parent_item.add_lower_level_item(child_item)
            print(f"Item {child_item_number} added as a child of {parent_item_number}.")
        else:
            print("Error: One or both items not found.")

    def increment_revision(self):
        """Increments the BOM revision."""
        self.revision += 1
        print(f"BOM revision incremented to {self.revision}.")

    def show_bom(self):
        if not self.items:
            print("BOM is empty.")
            return

        print(f"BOM for Item: {self.item_number}, Revision: {self.revision}")
        for item_number, item in self.items.items():
            quantity = self.quantities.get(item_number, 1)
            print("    Upper Level:", item.upper_level.item_number if item.upper_level else "None")
            print("    Lower Levels:", [p.item_number for p in item.lower_level] if item.lower_level else "None")
            print("  -" * 20)

def print_main_menu():
    print("\nPyPLM - Main Menu")  # Changed name here
    print("1. Item Management")
    print("2. Change Management")
    print("3. Document Management")
    print("4. BOM Management") # Added BOM Management option
    print("0. Exit")
    print("-" * 20)

def print_item_menu():
    print("\nItemManagement Menu")
    print("1. Add a new item")
    print("2. Link items(create a relationship between parent and child)")
    print("3. Show BOM")
    print("0. Back to Main Menu")
    print("-" * 20)

def print_bom_menu():  # New menu for BOM management
    print("\nBOM Management Menu")
    print("1. Change BOM")
    print("0. Back to Main Menu")
    print("-" * 20)

def print_change_menu():
    print("\nChange Management Menu")
    print("1. Create Change Request")
    print("2. Update Change Request Status")
    print("3. Show Change Requests for a Item")
    print("4. Show All Change Requests")
    print("0. Back to Main Menu")
    print("-" * 20)

def print_document_menu():
    print("\nDocument Management Menu")
    print("1. Attach document to a item")
    print("2. Show attached documents for a item")
    print("3. Attach document to a change request")
    print("4. Show attached documents for a change request")
    print("0. Back to Main Menu")
    print("-" * 20)

def add_to_recent(item, recent_list, max_items=5):
    """Adds an item to the recent list, keeping only the last max_items."""
    recent_list.insert(0, item)
    recent_list[:] = recent_list[:max_items]

def get_input_with_recent(prompt, recent_list):
    """Gets input from the user, showing recent items and allowing selection."""
    if recent_list:
        print("Recent items:")
        for i, item in enumerate(recent_list):
            print(f"{i + 1}. {item}")
        print("-" * 10)

    while True:
        user_input = input(prompt)
        if user_input.isdigit() and 1 <= int(user_input) <= len(recent_list):
            return recent_list[int(user_input) - 1]  # Return selected recent item
        else:
            return user_input  # Return the user's input

def create_database():
    """Creates the SQLite database and tables with indexes if they don't exist."""
    # check if the database already exists
    if os.path.isfile("plm_database.db"):
        # print("Database exists and will be used")
        return  # exit the function to avoid recreating existing database
    else:
        # print("Database will be created")
        pass # no database yet, continue creation

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            item_number TEXT PRIMARY KEY,
            revision TEXT,
            upper_level TEXT
        )
    ''')

    # Add index to item_number in items table
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_items_item_number ON items (item_number)")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS change_requests (
            change_request_number INTEGER PRIMARY KEY,
            item_number TEXT,
            reason TEXT,
            cost_impact TEXT,
            timeline_impact TEXT,
            status TEXT,
            FOREIGN KEY (item_number) REFERENCES items (item_number)
        )
    ''')

    # Add index to item_number in change_requests table
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_change_requests_item_number ON change_requests (item_number)")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            document_number TEXT PRIMARY KEY,
            version INTEGER,
            file_path TEXT,
            content TEXT
        )
    ''')

    conn.commit()

def add_item_to_db(item):
    """Adds a item to the database with error handling and logging."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO items (item_number, revision, upper_level) VALUES (?, ?, ?)",
                       (item.item_number, item.revision, item.upper_level.item_number if item.upper_level else None))
        conn.commit()
    except Exception as e:
        logging.error(f"Error adding item to database: {e}")
        print(f"Error adding item to database. Check the log file for details.")

def get_item_from_db(item_number):
    """Gets a item from the database with error handling and logging."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM items WHERE item_number = ?", (item_number,))
        row = cursor.fetchone()

        if row:
            item = Item()
            item.item_number = row[0]
            item.revision = row[1]
            # You'll need to handle setting upper_level based on row[2]
            return item
        else:
            return None
    except Exception as e:
        logging.error(f"Error getting item from database: {e}")
        print(f"Error getting item from database. Check the log file for details.")
        return None

def add_change_request_to_db(change_request):
    """Adds a change request to the database with error handling and logging."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO change_requests (change_request_number, item_number, reason, cost_impact, timeline_impact, status) VALUES (?, ?, ?, ?, ?, ?)",
            (change_request.change_request_number, change_request.item.item_number, change_request.reason,
             change_request.cost_impact, change_request.timeline_impact, change_request.status))
        conn.commit()
    except Exception as e:
        logging.error(f"Error adding change request to database: {e}")
        print(f"Error adding change request to database. Check the log file for details.")

def get_document_from_db(document_number):
    """Retrieves a document from the database with error handling and logging."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE document_number = ?", (document_number,))
        row = cursor.fetchone()

        if row:
            document = Document(document_type="", content=row[3], file_path=row[2])
            document.document_number = row[0]
            document.version = row[1]
            return document
        else:
            return None
    except Exception as e:
        logging.error(f"Error getting document from database: {e}")
        print(f"Error getting document from database. Check the log file for details.")
        return None

def add_document_to_db(document):
    """Adds a document to the database with error handling and logging."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO documents (document_number, version, file_path, content) VALUES (?, ?, ?, ?)",
                       (document.document_number, document.version, document.file_path, document.content))
        conn.commit()
    except sqlite3.IntegrityError:
        print(f"Document with number {document.document_number} already exists.")
    except Exception as e:
        logging.error(f"Error adding document to database: {e}")
        print(f"Error adding document to database. Check the log file for details.")

def attach_document_to_item(item):
        uploaded = files.upload()
        for fn in uploaded.keys():
            file_path = fn  # Get the uploaded file path
            document_type = input("Enter document type: ")
            document = Document(document_type, file_path=file_path)
            try:
                document.load_from_pdf(file_path)
                add_document_to_db(document)  # Add document to database
                item.documents.append(document.document_number)  # Attach document to item
                print(f"Document {document.document_number} attached to Item {item.item_number}.")
            except PyPDF2.errors.PdfReadError:
                print("Error: Could not read the PDF file. Please make sure it is a valid PDF.")
            except Exception as e:
                print(f"An error occurred: {e}")

def attach_document_to_item(change_request):
        uploaded = files.upload()
        for fn in uploaded.keys():
            file_path = fn  # Get the uploaded file path
            document_type = input("Enter document type: ")
            document = Document(document_type, file_path=file_path)
            try:
                document.load_from_pdf(file_path)
                add_document_to_db(document)  # Add document to database
                item.documents.append(document.document_number)  # Attach document to item
                print(f"Document {document.document_number} attached to Item {change_request.change_request_number}.")
            except PyPDF2.errors.PdfReadError:
                print("Error: Could not read the PDF file. Please make sure it is a valid PDF.")
            except Exception as e:
                print(f"An error occurred: {e}")

def change_bom(bom):
    """Allows the user to modify a BOM."""
    while True:
        print("\nChange BOM Options:")
        print("1. Remove item")
        print("2. Add item (link)")
        print("3. Change quantity")
        print("0. Back to BOM Management Menu")
        print("-" * 20)

        choice = input("Enter your choice: ")

        if choice == "1":  # Remove item
            item_number = input("Enter item number to remove: ")
            if item_number in bom.items:
                del bom.items[item_number]
                print(f"Item {item_number} removed from BOM.")
            else:
                print("Item not found in BOM.")

        elif choice == "2":  # Add item (link)
            parent_item_number = input("Enter parent item number: ")
            child_item_number = input("Enter child item number: ")
            bom.link_items(parent_item_number, child_item_number) 

        elif choice == "3":  # Change quantity
            item_number = input("Enter item number to change quantity: ")
            new_quantity = int(input("Enter new quantity: "))
            bom.change_quantity(item_number, new_quantity)

        elif choice == "0":
            break  # Back to BOM Management Menu
        else:
            print("Invalid choice, please try again.")

def main():
    create_database()
    bom = BOM()
    change_requests = []

    # Load items and change requests from the database
    with get_db_connection() as conn:  # Use a context manager for automatic connection closing
        cursor = conn.cursor()

        # Load items
        cursor.execute("SELECT * FROM items")
        for row in cursor.fetchall():
            item = Item()
            item.item_number = row[0]
            item.revision = row[1]
            # Handle upper_level (assuming upper_level stores item_number)
            if row[2]:  # If upper_level is not NULL
                upper_level_item = bom.get_item(row[2])
                if upper_level_item:
                    item.upper_level = upper_level_item
            bom.add_item(item)

        # Load change requests (after loading items)
        cursor.execute("SELECT * FROM change_requests")
        for row in cursor.fetchall():
            item = bom.get_item(row[1])  # Get associated item
            if item:  # Check if item exists in BOM
                change_request = ChangeRequest(item, row[2], row[3], row[4])
                change_request.change_request_number = row[0]
                change_request.status = row[5]
                change_requests.append(change_request)
                item.change_requests.append(change_request)  # Add to item's list

    while True:
        print_main_menu()
        main_choice = input("Enter your choice: ")

        if main_choice == "1":  # Item Management
            while True:
                print_item_menu()  # This function is now print_item_menu
                choice = input("Enter your choice: ")
                if choice == "1":
                    new_item = Item()  # Create an Item object
                    bom.add_item(new_item)
                    add_item_to_db(new_item)
                    print(f"Item {new_item.item_number} (Revision {new_item.revision}) added successfully.")
                elif choice == "2":
                    parent_item_number = input("Enter the parent item number: ")
                    child_item_number = input("Enter the child item number: ")
                    bom.link_items(parent_item_number, child_item_number)
                elif choice == "3":
                    item_number = input("Enter item number to show BOM: ")
                    item = bom.get_item(item_number)
                    if item:
                        item.bom.show_bom()
                    else:
                        print("Item not found.")
                elif choice == "0":
                    break  # Back to Main Menu
                else:
                    print("Invalid choice, please try again.")

        elif main_choice == "2":  # Change Management
            while True:
                print_change_menu()
                choice = input("Enter your choice: ")
                if choice == "1":  # Create Change Request
                    item_number = get_input_with_recent(
                        "Enter item number for change request: ", recent_items)
                    add_to_recent(item_number, recent_items)

                    item = bom.get_item(item_number)
                    if item:
                        print("Change Request Reasons:")
                        print("A: Client Request")
                        print("B: Internal Request")
                        print("C: Bug Fix")
                        print("D: Admin Fix")

                        while True:  # Loop until valid reason is entered
                            reason = input("Enter reason for change request (A, B, C, or D): ").upper()
                            if reason in ["A", "B", "C", "D"]:
                                break
                            else:
                                print("Invalid reason. Please enter A, B, C, or D.")

                        cost_impact = input("Enter cost impact (in k€): ")

                        # Get timeline impact choices based on reason
                        if reason == "A":
                            timeline_impact = "< 2 weeks"
                        elif reason == "B":
                            timeline_impact = "< 1 month"
                        elif reason == "C":
                            timeline_impact = "< 3 months"
                        elif reason == "D":
                            timeline_impact = "< 6 months"
                        else:
                            timeline_impact = "Unknown"

                        change_request = item.create_change_request(
                            reason, cost_impact, timeline_impact)
                        change_requests.append(change_request)
                        print(
                            f"Change request {change_request.change_request_number} created for item {item_number}.")
                        add_to_recent(str(
                            change_request.change_request_number), recent_change_requests)  # Add CR number to recent list
                        add_change_request_to_db(
                            change_request)  # Add to database

                    else:
                        print("Item not found.")
                elif choice == "2":  # Update Change Request Status
                    cr_number = get_input_with_recent(
                        "Enter change request number to update: ", recent_change_requests)
                    add_to_recent(cr_number, recent_change_requests)

                    cr_to_update = None
                    for cr in change_requests:
                        if str(cr.change_request_number) == cr_number:
                            cr_to_update = cr
                            break

                    if cr_to_update:
                        new_status = input(
                            "Enter new status (Created, In Progress, Accepted, Declined): ")
                        cr_to_update.update_status(new_status)
                        print(
                            f"Change request status updated to: {cr_to_update.status}")
                    else:
                        print("Change request not found.")

                elif choice == "3":  # Show Change Requests for a Item
                    item_number = input("Enter item number: ")
                    item = bom.get_item(item_number)
                    if item:
                        if item.change_requests:
                            print(f"Change Requests for Item {item_number}:")
                            for cr in item.change_requests:
                                print(cr)
                        else:
                            print(
                                f"No change requests found for Item {item_number}.")
                    else:
                        print("Item not found.")

                elif choice == "4":  # Show All Change Requests
                    if change_requests:
                        print("All Change Requests:")
                        for cr in change_requests:
                            print(cr)
                            print(f"  - Cost Impact: {cr.cost_impact}")
                            print(
                                f"  - Timeline Impact: {cr.timeline_impact}")
                            print("-" * 20)
                    else:
                        print("No change requests found.")
                elif choice == "0":
                    break  # Back to Main Menu
                else:
                    print("Invalid choice, please try again.")

        elif main_choice == "3":  # Document Management
            while True:
                print_document_menu()
                choice = input("Enter your choice: ")
                if choice == "1":  # Attach document to a item
                    item_number = input("Enter item number: ")
                    item = bom.get_item(item_number)
                    if item:
                        attach_document_to_item(item)
                    else:
                        print("Item not found.")
                elif choice == "2":  # Show attached documents for a item
                    item_number = input("Enter item number: ")
                    item = bom.get_item(item_number)
                    if item:
                        item.show_attached_documents()
                    else:
                        print("Item not found.")
                elif choice == "3":  # Attach document to a change request
                    cr_number = input("Enter change request number: ")
                    cr_to_update = None
                    for cr in change_requests:
                        if str(cr.change_request_number) == cr_number:
                            cr_to_update = cr
                            break

                    if cr_to_update:
                        attach_document_to_change_request(cr_to_update)
                    else:
                        print("Change request not found.")
                elif choice == "4":  # Show attached documents for a change request
                    cr_number = input("Enter change request number: ")
                    cr_to_update = None
                    for cr in change_requests:
                        if str(cr.change_request_number) == cr_number:
                            cr_to_update = cr
                            break

                    if cr_to_update:
                        cr_to_update.show_attached_documents()
                    else:
                        print("Change request not found.")
                elif choice == "0":
                    break  # Back to Main Menu
                else:
                    print("Invalid choice, please try again.")

        elif main_choice == "4":  # BOM Management
            while True:
                print_bom_menu()
                choice = input("Enter your choice: ")
                if choice == "1":  # Change BOM
                    item_number = input("Enter item number for the BOM to change: ")
                    item = bom.get_item(item_number)
                    if item:
                        change_bom(item.bom)  # Call change_bom function
                    else:
                        print("Item not found.")
                elif choice == "0":
                    break  # Back to Main Menu
                else:
                    print("Invalid choice, please try again.")
        
        elif main_choice == "0":
            print("Exiting PyPLM.")  # Changed name here
            # Close the database connection when exiting
            if 'conn' in database_connections:
                database_connections['conn'].close()
            break
        else:
            print("Invalid choice, please try again.")

if __name__ == "__main__":
    main()

