import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QListWidget, QLineEdit, QPushButton, QMessageBox, QLabel, QFormLayout,
    QStatusBar
)
from PyQt6.QtCore import Qt

# --- Configuration ---
# Define the file path. The script will create the directory if it doesn't exist.
FILE_PATH = os.path.expanduser("./contact_manager/contacts.txt")

# --- Backend Logic (Slightly adapted for GUI use) ---

def add_contact_to_file(name, last_name, phone_number, file_path=FILE_PATH):
    """Adds a contact to the file after checking for duplicate phone numbers."""
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'a+') as file:
            file.seek(0)
            content = file.read()
            if phone_number in content:
                return f"Error: Phone number {phone_number} already exists."
            file.write(f"{name} {last_name}: {phone_number}\n")
            return f"Contact '{name} {last_name}' added successfully."
    except IOError as e:
        return f"File Error: {e}"

def remove_contact_from_file(contact_line, file_path=FILE_PATH):
    """Removes a specific line (contact) from the file."""
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        # Filter out the line to be removed
        updated_lines = [line for line in lines if line.strip() != contact_line.strip()]
        
        with open(file_path, 'w') as file:
            file.writelines(updated_lines)
        return f"Contact '{contact_line.strip()}' removed."
    except FileNotFoundError:
        return "Error: Contact file not found."
    except IOError as e:
        return f"File Error: {e}"


# --- PyQt6 GUI Application ---

class ContactApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Contact Manager")
        self.setGeometry(100, 100, 500, 400) # x, y, width, height

        # Central widget and main layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Status bar for feedback
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.initUI()
        self.refresh_contact_list()

    def initUI(self):
        # 1. Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search contacts...")
        self.search_input.textChanged.connect(self.filter_contacts)
        self.main_layout.addWidget(self.search_input)

        # 2. Contact List
        self.contact_list_widget = QListWidget()
        self.main_layout.addWidget(self.contact_list_widget)

        # 3. Remove Button
        self.remove_button = QPushButton("Remove Selected Contact")
        self.remove_button.clicked.connect(self.remove_contact)
        self.main_layout.addWidget(self.remove_button)

        # 4. Form for adding new contacts
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.lastname_input = QLineEdit()
        self.phone_input = QLineEdit()
        
        form_layout.addRow("First Name:", self.name_input)
        form_layout.addRow("Last Name:", self.lastname_input)
        form_layout.addRow("Phone Number:", self.phone_input)
        
        self.main_layout.addLayout(form_layout)

        # 5. Add Button
        self.add_button = QPushButton("Add Contact")
        self.add_button.clicked.connect(self.add_contact)
        self.main_layout.addWidget(self.add_button)

    def refresh_contact_list(self):
        """Clears and reloads all contacts from the file into the list widget."""
        self.contact_list_widget.clear()
        try:
            with open(FILE_PATH, 'r') as file:
                contacts = file.readlines()
                for contact in contacts:
                    self.contact_list_widget.addItem(contact.strip())
        except FileNotFoundError:
            # If the file doesn't exist, the list will just be empty, which is fine.
            pass 

    def filter_contacts(self):
        """Hides or shows items in the list based on the search text."""
        search_text = self.search_input.text().lower()
        for i in range(self.contact_list_widget.count()):
            item = self.contact_list_widget.item(i)
            item.setHidden(search_text not in item.text().lower())

    def add_contact(self):
        """Handles the 'Add Contact' button click."""
        name = self.name_input.text().strip()
        last_name = self.lastname_input.text().strip()
        phone = self.phone_input.text().strip()

        if not name or not phone:
            self.status_bar.showMessage("First name and phone number are required.", 3000)
            return

        result = add_contact_to_file(name, last_name, phone)
        self.status_bar.showMessage(result, 4000)
        
        # Clear inputs and refresh the list on success
        if "successfully" in result:
            self.name_input.clear()
            self.lastname_input.clear()
            self.phone_input.clear()
            self.refresh_contact_list()

    def remove_contact(self):
        """Handles the 'Remove Selected Contact' button click."""
        selected_item = self.contact_list_widget.currentItem()

        if not selected_item:
            self.status_bar.showMessage("Please select a contact to remove.", 3000)
            return

        # Confirmation dialog to prevent accidental deletion
        reply = QMessageBox.question(
            self, 
            "Confirm Deletion", 
            f"Are you sure you want to remove '{selected_item.text()}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            result = remove_contact_from_file(selected_item.text())
            self.status_bar.showMessage(result, 4000)
            self.refresh_contact_list()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ContactApp()
    window.show()
    sys.exit(app.exec())