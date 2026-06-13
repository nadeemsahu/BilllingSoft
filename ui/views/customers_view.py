from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLineEdit, QDialog, QFormLayout,
                             QMessageBox)
from models.customer import CustomerModel

class CustomerDialog(QDialog):
    def __init__(self, parent=None, customer=None):
        super().__init__(parent)
        self.customer = customer
        self.setWindowTitle("Add Customer" if not customer else "Edit Customer")
        self.setMinimumWidth(400)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        
        self.init_ui()
        if self.customer:
            self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.address_input = QLineEdit()

        form_layout.addRow("Name:", self.name_input)
        form_layout.addRow("Phone:", self.phone_input)
        form_layout.addRow("Address:", self.address_input)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_data)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def load_data(self):
        self.name_input.setText(self.customer['name'])
        self.phone_input.setText(self.customer['phone'])
        self.address_input.setText(self.customer.get('address', ''))

    def save_data(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip()
        address = self.address_input.text().strip()

        if not name or not phone:
            QMessageBox.warning(self, "Error", "Name and Phone are required.")
            return

        try:
            if self.customer:
                success = CustomerModel.update_customer(self.customer['id'], name, phone, address)
                if not success: raise Exception("Failed to update.")
            else:
                success = CustomerModel.add_customer(name, phone, address)
                if not success: raise Exception("Phone number already exists or DB error.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not save customer.\n{str(e)}")


class CustomersView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Customer Management")
        title.setObjectName("HeaderTitle")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search customers by name or phone...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.load_data)

        add_btn = QPushButton("Add Customer")
        add_btn.clicked.connect(self.add_customer)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Address", "Actions"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self.load_data)

    def load_data(self):
        search_term = self.search_input.text().strip()
        if search_term:
            customers = CustomerModel.search_customers(search_term)
        else:
            customers = CustomerModel.get_all_customers()

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(customers))
        
        for row, cus in enumerate(customers):
            self.table.setItem(row, 0, QTableWidgetItem(str(cus['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(cus['name']))
            self.table.setItem(row, 2, QTableWidgetItem(cus['phone']))
            self.table.setItem(row, 3, QTableWidgetItem(cus.get('address', '')))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedWidth(60)
            edit_btn.clicked.connect(lambda checked, c=cus: self.edit_customer(c))
            
            delete_btn = QPushButton("Del")
            delete_btn.setObjectName("deleteBtn")
            delete_btn.setFixedWidth(50)
            delete_btn.clicked.connect(lambda checked, cid=cus['id']: self.delete_customer(cid))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 4, actions_widget)
            
        self.table.setSortingEnabled(True)
            
    def add_customer(self):
        dialog = CustomerDialog(self)
        if dialog.exec_():
            self.load_data()

    def edit_customer(self, customer):
        dialog = CustomerDialog(self, customer)
        if dialog.exec_():
            self.load_data()

    def delete_customer(self, customer_id):
        reply = QMessageBox.question(self, 'Delete Customer', 'Are you sure you want to delete this customer? This may fail if they have linked repairs or sales.',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success = CustomerModel.delete_customer(customer_id)
            if not success:
                QMessageBox.warning(self, "Error", "Could not delete customer. They might have active repairs or sales.")
            self.load_data()
