from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView)
from PyQt5.QtCore import Qt, QTimer
from database.db_manager import db
from utils.helpers import format_currency

class CardWidget(QFrame):
    def __init__(self, title, value="0"):
        super().__init__()
        self.setObjectName("Card")
        self.setProperty("class", "Card")
        
        layout = QVBoxLayout(self)
        
        self.title_label = QLabel(title)
        self.title_label.setProperty("class", "CardTitle")
        
        self.value_label = QLabel(value)
        self.value_label.setProperty("class", "CardValue")
        
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addStretch()

    def set_value(self, val):
        self.value_label.setText(val)

class DashboardView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # Header
        title = QLabel("Dashboard")
        title.setObjectName("HeaderTitle")
        main_layout.addWidget(title)
        
        # KPI Cards
        cards_layout = QHBoxLayout()
        
        self.today_profit_card = CardWidget("Today's Profit")
        self.monthly_profit_card = CardWidget("Monthly Profit")
        self.pending_repairs_card = CardWidget("Pending Repairs")
        self.low_stock_card = CardWidget("Low Stock Items")
        
        cards_layout.addWidget(self.today_profit_card)
        cards_layout.addWidget(self.monthly_profit_card)
        cards_layout.addWidget(self.pending_repairs_card)
        cards_layout.addWidget(self.low_stock_card)
        
        main_layout.addLayout(cards_layout)
        
        # Bottom section: Recent Data Grid
        bottom_layout = QHBoxLayout()
        
        # Low Stock Table
        low_stock_layout = QVBoxLayout()
        low_stock_layout.addWidget(QLabel("Items Requiring Restock"))
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(3)
        self.stock_table.setHorizontalHeaderLabels(["ID", "Name", "Qty"])
        self.stock_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.stock_table.setEditTriggers(QTableWidget.NoEditTriggers)
        low_stock_layout.addWidget(self.stock_table)
        
        # Pending Repairs Table
        pending_layout = QVBoxLayout()
        pending_layout.addWidget(QLabel("Latest Pending Repairs"))
        self.repairs_table = QTableWidget()
        self.repairs_table.setColumnCount(4)
        self.repairs_table.setHorizontalHeaderLabels(["ID", "Customer", "Device", "Status"])
        self.repairs_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.repairs_table.setEditTriggers(QTableWidget.NoEditTriggers)
        pending_layout.addWidget(self.repairs_table)

        bottom_layout.addLayout(low_stock_layout)
        bottom_layout.addLayout(pending_layout)
        
        main_layout.addLayout(bottom_layout)

    def showEvent(self, event):
        """Refresh data when view becomes visible"""
        super().showEvent(event)
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(10, self.load_data)

    def load_data(self):
        try:
            # Low Stock KPI
            low_stock_count = db.fetch_one("SELECT COUNT(*) as c FROM inventory WHERE quantity <= 5")['c']
            self.low_stock_card.set_value(str(low_stock_count))
            
            # Pending Repairs KPI
            pending_count = db.fetch_one("SELECT COUNT(*) as c FROM repairs WHERE status != 'Delivered'")['c']
            self.pending_repairs_card.set_value(str(pending_count))

            # Profit Calculation (Sales Profit + Repair Profit)
            # Today
            today_sales = db.fetch_all("""
                SELECT sum((si.selling_price - si.cost_price) * si.quantity) as val 
                FROM sale_items si 
                JOIN sales s ON si.sale_id = s.id 
                WHERE date(s.date) = date('now', 'localtime')
            """)[0]['val'] or 0

            today_repairs = db.fetch_all("""
                SELECT sum(service_charge - parts_cost) as val 
                FROM repairs 
                WHERE status = 'Delivered' AND date(date_delivered) = date('now', 'localtime')
            """)[0]['val'] or 0
            
            self.today_profit_card.set_value(format_currency(today_sales + today_repairs))

            # Monthly
            monthly_sales = db.fetch_all("""
                SELECT sum((si.selling_price - si.cost_price) * si.quantity) as val 
                FROM sale_items si 
                JOIN sales s ON si.sale_id = s.id 
                WHERE strftime('%Y-%m', s.date) = strftime('%Y-%m', 'now', 'localtime')
            """)[0]['val'] or 0

            monthly_repairs = db.fetch_all("""
                SELECT sum(service_charge - parts_cost) as val 
                FROM repairs 
                WHERE status = 'Delivered' AND strftime('%Y-%m', date_delivered) = strftime('%Y-%m', 'now', 'localtime')
            """)[0]['val'] or 0
            
            self.monthly_profit_card.set_value(format_currency(monthly_sales + monthly_repairs))

            # Load Tables
            self.load_tables()

        except Exception as e:
            import logging
            logging.error(f"Dashboard load error: {e}")

    def load_tables(self):
        # Low Stock
        items = db.fetch_all("SELECT id, name, quantity FROM inventory WHERE quantity <= 5 ORDER BY quantity ASC LIMIT 10")
        self.stock_table.setRowCount(len(items))
        for row, item in enumerate(items):
            self.stock_table.setItem(row, 0, QTableWidgetItem(str(item['id'])))
            self.stock_table.setItem(row, 1, QTableWidgetItem(item['name']))
            self.stock_table.setItem(row, 2, QTableWidgetItem(str(item['quantity'])))

        # Pending Repairs
        repairs = db.fetch_all("""
            SELECT r.id, c.name, r.device_type, r.status 
            FROM repairs r 
            LEFT JOIN customers c ON r.customer_id = c.id 
            WHERE status != 'Delivered' 
            ORDER BY r.date_received DESC LIMIT 10
        """)
        self.repairs_table.setRowCount(len(repairs))
        for row, rep in enumerate(repairs):
            self.repairs_table.setItem(row, 0, QTableWidgetItem(str(rep['id'])))
            self.repairs_table.setItem(row, 1, QTableWidgetItem(str(rep['name'])))
            self.repairs_table.setItem(row, 2, QTableWidgetItem(str(rep['device_type'])))
            self.repairs_table.setItem(row, 3, QTableWidgetItem(str(rep['status'])))
