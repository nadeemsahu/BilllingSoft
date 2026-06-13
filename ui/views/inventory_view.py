from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLineEdit, QDialog, QFormLayout,
                             QComboBox, QDoubleSpinBox, QSpinBox, QMessageBox)
from PyQt5.QtCore import Qt
from models.inventory import InventoryModel
from utils.helpers import format_currency

class ProductDialog(QDialog):
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Add Product" if not product else "Edit Product")
        self.setMinimumWidth(400)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        
        self.init_ui()
        if self.product:
            self.load_data()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.name_input = QLineEdit()
        self.type_input = QComboBox()
        self.type_input.addItems(["New", "Refurbished", "Part"])
        
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setMaximum(999999.99)
        self.cost_input.setPrefix("₹")
        
        self.price_input = QDoubleSpinBox()
        self.price_input.setMaximum(999999.99)
        self.price_input.setPrefix("₹")
        
        self.qty_input = QSpinBox()
        self.qty_input.setMaximum(9999)

        form_layout.addRow("Product Name:", self.name_input)
        form_layout.addRow("Type:", self.type_input)
        form_layout.addRow("Cost Price:", self.cost_input)
        form_layout.addRow("Selling Price:", self.price_input)
        form_layout.addRow("Quantity:", self.qty_input)

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
        self.name_input.setText(self.product['name'])
        self.type_input.setCurrentText(self.product['type'])
        self.cost_input.setValue(self.product['cost_price'])
        self.price_input.setValue(self.product['selling_price'])
        self.qty_input.setValue(self.product['quantity'])

    def save_data(self):
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Product Name is required.")
            return

        if self.product:
            success = InventoryModel.update_product(
                self.product['id'], name, self.type_input.currentText(),
                self.cost_input.value(), self.price_input.value(), self.qty_input.value()
            )
            if not success:
                QMessageBox.warning(self, "Error", "Failed to update product.")
                return
        else:
            success = InventoryModel.add_product(
                name, self.type_input.currentText(),
                self.cost_input.value(), self.price_input.value(), self.qty_input.value()
            )
            if not success:
                QMessageBox.warning(self, "Error", "Failed to add product.")
                return
        self.accept()

class InventoryView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Inventory Management")
        title.setObjectName("HeaderTitle")
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.setFixedWidth(300)
        self.search_input.textChanged.connect(self.load_data)

        add_btn = QPushButton("Add Product")
        add_btn.clicked.connect(self.add_product)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["ID", "Name", "Type", "Cost", "Price", "Qty", "Actions"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        # Load initial data
        # Use QTimer to delay initial load until UI is drawn
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self.load_data)

    def load_data(self):
        search_term = self.search_input.text().strip()
        if search_term:
            products = InventoryModel.search_products(search_term)
        else:
            products = InventoryModel.get_all_products()

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(products))
        
        for row, prod in enumerate(products):
            self.table.setItem(row, 0, QTableWidgetItem(str(prod['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(prod['name']))
            self.table.setItem(row, 2, QTableWidgetItem(prod['type']))
            self.table.setItem(row, 3, QTableWidgetItem(format_currency(prod['cost_price'])))
            self.table.setItem(row, 4, QTableWidgetItem(format_currency(prod['selling_price'])))
            
            qty_item = QTableWidgetItem(str(prod['quantity']))
            if prod['quantity'] <= 5: # Low stock alert
                qty_item.setForeground(Qt.red)
                qty_item.setToolTip("Low stock!")
            self.table.setItem(row, 5, qty_item)

            # Actions layout inside cell
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.setFixedWidth(60)
            edit_btn.clicked.connect(lambda checked, p=prod: self.edit_product(p))
            
            delete_btn = QPushButton("Del")
            delete_btn.setObjectName("deleteBtn")
            delete_btn.setFixedWidth(50)
            delete_btn.clicked.connect(lambda checked, pid=prod['id']: self.delete_product(pid))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.table.setCellWidget(row, 6, actions_widget)
            
        self.table.setSortingEnabled(True)
            
    def add_product(self):
        dialog = ProductDialog(self)
        if dialog.exec_():
            self.load_data()

    def edit_product(self, product):
        dialog = ProductDialog(self, product)
        if dialog.exec_():
            self.load_data()

    def delete_product(self, product_id):
        reply = QMessageBox.question(self, 'Delete Product', 'Are you sure you want to delete this product?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            InventoryModel.delete_product(product_id)
            self.load_data()
