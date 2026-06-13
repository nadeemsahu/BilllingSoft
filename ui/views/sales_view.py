from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLineEdit, QComboBox, QMessageBox,
                             QSpinBox, QDoubleSpinBox, QGroupBox)
from PyQt5.QtCore import Qt
from models.sale import SaleModel
from models.inventory import InventoryModel
from models.customer import CustomerModel
from utils.helpers import format_currency, format_date
from services.pdf_service import PDFService

class SalesView(QWidget):
    def __init__(self):
        super().__init__()
        self.cart_items = []  # List of dicts
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)

        # Left Side: POS Form & Cart
        pos_layout = QVBoxLayout()
        
        # Customer Selection
        customer_group = QGroupBox("1. Select Customer (Optional)")
        customer_layout = QHBoxLayout()
        self.customer_combo = QComboBox()
        self.customer_combo.addItem("Walk-in / Guest", None)
        self.load_customers()
        customer_layout.addWidget(self.customer_combo)
        customer_group.setLayout(customer_layout)
        pos_layout.addWidget(customer_group)

        # Add to Cart
        add_item_group = QGroupBox("2. Add Products")
        add_layout = QHBoxLayout()
        self.product_combo = QComboBox()
        self.load_products()
        
        self.qty_spin = QSpinBox()
        self.qty_spin.setMinimum(1)
        self.qty_spin.setMaximum(9999)
        
        add_btn = QPushButton("Add to Cart")
        add_btn.clicked.connect(self.add_to_cart)

        add_layout.addWidget(QLabel("Product:"))
        add_layout.addWidget(self.product_combo, stretch=1)
        add_layout.addWidget(QLabel("Qty:"))
        add_layout.addWidget(self.qty_spin)
        add_layout.addWidget(add_btn)
        add_item_group.setLayout(add_layout)
        pos_layout.addWidget(add_item_group)

        # Cart Table
        self.cart_table = QTableWidget()
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.setColumnCount(5)
        self.cart_table.setHorizontalHeaderLabels(["ID", "Name", "Price", "Qty", "Subtotal"])
        self.cart_table.setEditTriggers(QTableWidget.NoEditTriggers)
        pos_layout.addWidget(self.cart_table)

        # Checkout Section
        checkout_layout = QHBoxLayout()
        self.total_label = QLabel("Total: ₹0.00")
        self.total_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #a2bf8a;")
        
        checkout_btn = QPushButton("Complete Sale")
        checkout_btn.setObjectName("checkoutBtn")
        checkout_btn.clicked.connect(self.checkout)

        checkout_layout.addWidget(self.total_label)
        checkout_layout.addStretch()
        checkout_layout.addWidget(checkout_btn)
        pos_layout.addLayout(checkout_layout)

        main_layout.addLayout(pos_layout, stretch=2)

        # Right Side: Recent Sales
        recent_sales_layout = QVBoxLayout()
        recent_sales_layout.addWidget(QLabel("Recent Sales"))
        
        self.sales_table = QTableWidget()
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setColumnCount(4)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Date", "Customer", "Total"])
        recent_sales_layout.addWidget(self.sales_table)

        main_layout.addLayout(recent_sales_layout, stretch=1)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self.load_recent_sales)

    def load_customers(self):
        self.customer_combo.clear()
        self.customer_combo.addItem("Walk-in / Guest", None)
        for c in CustomerModel.get_all_customers():
            self.customer_combo.addItem(f"{c['name']} ({c['phone']})", c['id'])

    def load_products(self):
        self.product_combo.clear()
        for p in InventoryModel.get_all_products():
            if p['quantity'] > 0:
                self.product_combo.addItem(f"{p['name']} - {format_currency(p['selling_price'])} (Stock: {p['quantity']})", p)

    def add_to_cart(self):
        product_data = self.product_combo.currentData()
        if not product_data:
            return

        qty = self.qty_spin.value()
        if qty > product_data['quantity']:
            QMessageBox.warning(self, "Out of Stock", f"Only {product_data['quantity']} available.")
            return

        # Check if already in cart
        for item in self.cart_items:
            if item['product_id'] == product_data['id']:
                if item['quantity'] + qty > product_data['quantity']:
                    QMessageBox.warning(self, "Out of Stock", f"Cannot add more. Max stock is {product_data['quantity']}.")
                    return
                item['quantity'] += qty
                self.refresh_cart()
                return

        self.cart_items.append({
            'product_id': product_data['id'],
            'name': product_data['name'],
            'cost_price': product_data['cost_price'],
            'selling_price': product_data['selling_price'],
            'quantity': qty
        })
        self.refresh_cart()

    def refresh_cart(self):
        self.cart_table.setRowCount(len(self.cart_items))
        total = 0.0
        for row, item in enumerate(self.cart_items):
            self.cart_table.setItem(row, 0, QTableWidgetItem(str(item['product_id'])))
            self.cart_table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.cart_table.setItem(row, 2, QTableWidgetItem(format_currency(item['selling_price'])))
            self.cart_table.setItem(row, 3, QTableWidgetItem(str(item['quantity'])))
            
            subtotal = item['selling_price'] * item['quantity']
            total += subtotal
            self.cart_table.setItem(row, 4, QTableWidgetItem(format_currency(subtotal)))

        self.total_label.setText(f"Total: {format_currency(total)}")

    def checkout(self):
        if not self.cart_items:
            QMessageBox.warning(self, "Empty Cart", "Please add products to cart first.")
            return

        customer_id = self.customer_combo.currentData()
        
        total = sum([item['selling_price'] * item['quantity'] for item in self.cart_items])
        
        sale_id = SaleModel.create_sale(customer_id, total, 0.0, self.cart_items)
        if sale_id:
            try:
                # Generate PDF
                import os
                invoice_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "invoices")
                if not os.path.exists(invoice_dir):
                    os.makedirs(invoice_dir)
                pdf_path = os.path.join(invoice_dir, f"Invoice_{sale_id}.pdf")
                
                # We will call the PDFService here once it's implemented.
                PDFService.generate_invoice(sale_id, customer_id, self.cart_items, total, pdf_path)
                QMessageBox.information(self, "Success", f"Sale completed successfully!\nInvoice saved to {pdf_path}")
            except Exception as e:
                QMessageBox.warning(self, "Sale Completed", f"Sale saved but failed to generate PDF: {e}")

            # Reset
            self.cart_items = []
            self.refresh_cart()
            self.load_products() # To update stock counts in dropdown
            self.load_recent_sales()
        else:
            QMessageBox.critical(self, "Error", "Failed to complete sale. Database error.")

    def load_recent_sales(self):
        sales = SaleModel.get_all_sales()[:50] # Show last 50
        self.sales_table.setRowCount(len(sales))
        for row, sale in enumerate(sales):
            self.sales_table.setItem(row, 0, QTableWidgetItem(str(sale['id'])))
            self.sales_table.setItem(row, 1, QTableWidgetItem(format_date(sale['date'])))
            self.sales_table.setItem(row, 2, QTableWidgetItem(sale.get('customer_name', 'Guest') or 'Guest'))
            self.sales_table.setItem(row, 3, QTableWidgetItem(format_currency(sale['total_amount'])))
