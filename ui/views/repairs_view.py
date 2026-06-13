from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QHeaderView, QLineEdit, QDialog, QFormLayout,
                             QComboBox, QMessageBox, QDoubleSpinBox, QTextEdit, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from models.repair import RepairModel
from models.customer import CustomerModel
from utils.helpers import format_currency, format_date

class RepairDialog(QDialog):
    def __init__(self, parent=None, repair=None):
        super().__init__(parent)
        self.repair = repair
        self.setWindowTitle("Add Repair" if not repair else "Edit Repair")
        self.setMinimumWidth(500)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        self.init_ui()
        if self.repair:
            self.load_data()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 24, 24, 24)

        card = QFrame()
        card.setObjectName("ModalCard")
        layout = QVBoxLayout(card)

        self.customer_combo = QComboBox()
        customers = CustomerModel.get_all_customers()
        for c in customers:
            self.customer_combo.addItem(f"{c['name']} ({c['phone']})", c['id'])

        self.device_type_input = QLineEdit()
        self.brand_input = QLineEdit()
        self.model_input = QLineEdit()
        self.serial_input = QLineEdit()
        self.problem_input = QTextEdit()
        self.problem_input.setMinimumHeight(100)
        self.accessories_input = QLineEdit()

        def add_field(label, widget):
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #d1d5db; font-weight: bold; margin-bottom: 2px;")
            layout.addWidget(lbl)
            layout.addWidget(widget)
            layout.addSpacing(10)

        add_field("Customer Selection", self.customer_combo)
        add_field("Device Type", self.device_type_input)
        
        row1 = QHBoxLayout()
        col1 = QVBoxLayout()
        lbl1 = QLabel("Brand")
        lbl1.setStyleSheet("color: #d1d5db; font-weight: bold; margin-bottom: 2px;")
        col1.addWidget(lbl1)
        col1.addWidget(self.brand_input)
        
        col2 = QVBoxLayout()
        lbl2 = QLabel("Model")
        lbl2.setStyleSheet("color: #d1d5db; font-weight: bold; margin-bottom: 2px;")
        col2.addWidget(lbl2)
        col2.addWidget(self.model_input)
        
        row1.addLayout(col1)
        row1.addLayout(col2)
        layout.addLayout(row1)
        layout.addSpacing(10)

        add_field("Serial Number", self.serial_input)
        add_field("Problem Description", self.problem_input)
        add_field("Accessories Received", self.accessories_input)

        if self.repair:
            self.customer_combo.setEnabled(False) 

        main_layout.addWidget(card)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Repair Ticket")
        save_btn.setObjectName("checkoutBtn")
        save_btn.clicked.connect(self.save_data)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("secondaryBtn")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        main_layout.addLayout(btn_layout)

    def load_data(self):
        idx = self.customer_combo.findData(self.repair['customer_id'])
        if idx >= 0:
            self.customer_combo.setCurrentIndex(idx)
        self.device_type_input.setText(self.repair.get('device_type', ''))
        self.brand_input.setText(self.repair.get('brand', ''))
        self.model_input.setText(self.repair.get('model', ''))
        self.serial_input.setText(self.repair.get('serial_number', ''))
        self.problem_input.setText(self.repair.get('problem_description', ''))
        self.accessories_input.setText(self.repair.get('accessories', ''))

    def save_data(self):
        customer_id = self.customer_combo.currentData()
        if not customer_id:
            QMessageBox.warning(self, "Error", "Please select a customer.")
            return

        device_type = self.device_type_input.text().strip()
        brand = self.brand_input.text().strip()
        model = self.model_input.text().strip()
        problem = self.problem_input.toPlainText().strip()
        
        if not device_type or not problem:
            QMessageBox.warning(self, "Error", "Device Type and Problem Description are required.")
            return

        if self.repair:
            RepairModel.update_repair(self.repair['id'], device_type, brand, model, 
                                      self.serial_input.text().strip(), problem, 
                                      self.accessories_input.text().strip())
        else:
            RepairModel.add_repair(customer_id, device_type, brand, model,
                                   self.serial_input.text().strip(), problem,
                                   self.accessories_input.text().strip())
        self.accept()

class StatusDialog(QDialog):
    def __init__(self, parent=None, repair=None):
        super().__init__(parent)
        self.repair = repair
        self.setWindowTitle("Update Repair Status")
        self.setMinimumWidth(400)
        self.setStyleSheet(parent.styleSheet() if parent else "")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.status_combo = QComboBox()
        self.status_combo.addItems(['Received', 'Diagnosing', 'Repairing', 'Completed', 'Delivered'])
        self.status_combo.setCurrentText(self.repair['status'])

        self.service_charge = QDoubleSpinBox()
        self.service_charge.setMaximum(99999.99)
        self.service_charge.setValue(self.repair.get('service_charge', 0.0))
        self.service_charge.setPrefix("₹")

        self.parts_cost = QDoubleSpinBox()
        self.parts_cost.setMaximum(99999.99)
        self.parts_cost.setValue(self.repair.get('parts_cost', 0.0))
        self.parts_cost.setPrefix("₹")

        form_layout.addRow("Status:", self.status_combo)
        form_layout.addRow("Service Charge:", self.service_charge)
        form_layout.addRow("Parts Cost:", self.parts_cost)

        layout.addLayout(form_layout)

        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_data)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def save_data(self):
        RepairModel.update_repair_status(
            self.repair['id'], 
            self.status_combo.currentText(),
            self.service_charge.value(),
            self.parts_cost.value()
        )
        self.accept()

class RepairsView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Repair Management")
        title.setObjectName("HeaderTitle")
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Pending", "Completed (Not Delivered)"])
        self.filter_combo.currentTextChanged.connect(self.load_data)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search repairs...")
        self.search_input.setFixedWidth(250)
        self.search_input.textChanged.connect(self.load_data)

        add_btn = QPushButton("New Repair Ticket")
        add_btn.clicked.connect(self.add_repair)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(self.filter_combo)
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(add_btn)

        layout.addLayout(header_layout)

        # Table
        self.table = QTableWidget()
        self.table.setAlternatingRowColors(True)
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["ID", "Customer", "Device", "Status", "Received", "Profit", "Edit", "Status"])
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        layout.addWidget(self.table)
        
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self.load_data)

    def load_data(self):
        search_term = self.search_input.text().strip()
        filter_req = self.filter_combo.currentText()

        if search_term:
            repairs = RepairModel.search_repairs(search_term)
        elif filter_req == "Pending":
            repairs = RepairModel.get_pending_repairs()
        elif filter_req == "Completed (Not Delivered)":
            repairs = RepairModel.get_completed_not_delivered()
        else:
            repairs = RepairModel.get_all_repairs()

        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(repairs))
        
        for row, rep in enumerate(repairs):
            self.table.setItem(row, 0, QTableWidgetItem(str(rep['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(f"{rep.get('customer_name', '')}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{rep.get('device_type','')} {rep.get('brand','')}"))
            status = rep['status']
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            if status == 'Delivered':
                status_item.setForeground(QColor("#a6e3a1"))
                status_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            elif status == 'Pending':
                status_item.setForeground(QColor("#f38ba8"))
                status_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            elif status in ['Diagnosing', 'Repairing']:
                status_item.setForeground(QColor("#f1c40f"))
                status_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            
            self.table.setItem(row, 3, status_item)
            self.table.setItem(row, 4, QTableWidgetItem(format_date(rep.get('date_received', ''))))
            
            profit = rep.get('service_charge', 0) - rep.get('parts_cost', 0)
            profit_item = QTableWidgetItem(format_currency(profit))
            if profit > 0: 
                profit_item.setForeground(QColor("#a6e3a1"))
                profit_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            self.table.setItem(row, 5, profit_item)

            # Edit Button
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, r=rep: self.edit_repair(r))
            self.table.setCellWidget(row, 6, edit_btn)

            # Update Status Button
            status_btn = QPushButton("Update")
            status_btn.clicked.connect(lambda checked, r=rep: self.update_status(r))
            self.table.setCellWidget(row, 7, status_btn)
            
        self.table.setSortingEnabled(True)
            
    def add_repair(self):
        dialog = RepairDialog(self)
        if dialog.exec_():
            self.load_data()

    def edit_repair(self, repair):
        dialog = RepairDialog(self, repair)
        if dialog.exec_():
            self.load_data()

    def update_status(self, repair):
        dialog = StatusDialog(self, repair)
        if dialog.exec_():
            self.load_data()
