from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, QComboBox)
from database.db_manager import db
from utils.helpers import format_currency

class ReportsView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Profit & Reports")
        title.setObjectName("HeaderTitle")
        
        self.time_filter = QComboBox()
        self.time_filter.addItems(["This Month", "Today", "This Year", "All Time"])
        self.time_filter.currentTextChanged.connect(self.load_data)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(QLabel("Timeframe:"))
        header_layout.addWidget(self.time_filter)

        main_layout.addLayout(header_layout)

        # Overview
        self.total_profit_label = QLabel("Total Profit: ₹0.00")
        self.total_profit_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #a2bf8a;")
        main_layout.addWidget(self.total_profit_label)

        # Tables Layout
        tables_layout = QHBoxLayout()

        # Top Products
        products_layout = QVBoxLayout()
        products_layout.addWidget(QLabel("Top Selling Products (By Profit)"))
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(3)
        self.products_table.setHorizontalHeaderLabels(["Product", "Sold Qty", "Profit"])
        self.products_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        products_layout.addWidget(self.products_table)

        # Most Common Repairs
        repairs_layout = QVBoxLayout()
        repairs_layout.addWidget(QLabel("Most Common Repairs"))
        self.repairs_table = QTableWidget()
        self.repairs_table.setColumnCount(3)
        self.repairs_table.setHorizontalHeaderLabels(["Device Type", "Count", "Profit"])
        self.repairs_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        repairs_layout.addWidget(self.repairs_table)

        tables_layout.addLayout(products_layout)
        tables_layout.addLayout(repairs_layout)
        
        main_layout.addLayout(tables_layout)

    def showEvent(self, event):
        super().showEvent(event)
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(10, self.load_data)

    def load_data(self):
        filter_val = self.time_filter.currentText()
        
        # SQLite date modifiers
        date_cond_sales = ""
        date_cond_repairs = ""
        
        if filter_val == "Today":
            date_cond_sales = "AND date(s.date) = date('now', 'localtime')"
            date_cond_repairs = "AND date(date_delivered) = date('now', 'localtime')"
        elif filter_val == "This Month":
            date_cond_sales = "AND strftime('%Y-%m', s.date) = strftime('%Y-%m', 'now', 'localtime')"
            date_cond_repairs = "AND strftime('%Y-%m', date_delivered) = strftime('%Y-%m', 'now', 'localtime')"
        elif filter_val == "This Year":
            date_cond_sales = "AND strftime('%Y', s.date) = strftime('%Y', 'now', 'localtime')"
            date_cond_repairs = "AND strftime('%Y', date_delivered) = strftime('%Y', 'now', 'localtime')"

        # Calculate Total Profit
        sales_profit_q = f"""
            SELECT sum((si.selling_price - si.cost_price) * si.quantity) as val 
            FROM sale_items si 
            JOIN sales s ON si.sale_id = s.id 
            WHERE 1=1 {date_cond_sales}
        """
        repairs_profit_q = f"""
            SELECT sum(service_charge - parts_cost) as val 
            FROM repairs 
            WHERE status = 'Delivered' {date_cond_repairs}
        """

        sp_row = db.fetch_one(sales_profit_q)
        sp = sp_row['val'] if sp_row and sp_row['val'] else 0
        
        rp_row = db.fetch_one(repairs_profit_q)
        rp = rp_row['val'] if rp_row and rp_row['val'] else 0
        self.total_profit_label.setText(f"Total Profit: {format_currency(sp + rp)} (Sales: {format_currency(sp)} | Repairs: {format_currency(rp)})")

        # Top Products
        top_prod_q = f"""
            SELECT i.name, sum(si.quantity) as qty, sum((si.selling_price - si.cost_price) * si.quantity) as profit
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN inventory i ON si.product_id = i.id
            WHERE 1=1 {date_cond_sales}
            GROUP BY i.id
            ORDER BY profit DESC LIMIT 15
        """
        prods = db.fetch_all(top_prod_q)
        self.products_table.setRowCount(len(prods))
        for row, p in enumerate(prods):
            self.products_table.setItem(row, 0, QTableWidgetItem(p['name']))
            self.products_table.setItem(row, 1, QTableWidgetItem(str(p['qty'])))
            self.products_table.setItem(row, 2, QTableWidgetItem(format_currency(p['profit'])))

        # Common Repairs
        top_rep_q = f"""
            SELECT device_type, count(id) as cnt, sum(service_charge - parts_cost) as profit
            FROM repairs
            WHERE status = 'Delivered' {date_cond_repairs}
            GROUP BY device_type
            ORDER BY cnt DESC LIMIT 15
        """
        reps = db.fetch_all(top_rep_q)
        self.repairs_table.setRowCount(len(reps))
        for row, r in enumerate(reps):
            self.repairs_table.setItem(row, 0, QTableWidgetItem(r['device_type']))
            self.repairs_table.setItem(row, 1, QTableWidgetItem(str(r['cnt'])))
            self.repairs_table.setItem(row, 2, QTableWidgetItem(format_currency(r['profit'])))
