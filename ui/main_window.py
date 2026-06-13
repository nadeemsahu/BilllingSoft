from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                             QPushButton, QStackedWidget, QLabel, QFrame)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QFont, QPixmap
# Placeholders for views
from ui.views.dashboard_view import DashboardView
from ui.views.inventory_view import InventoryView
from ui.views.customers_view import CustomersView
from ui.views.repairs_view import RepairsView
from ui.views.sales_view import SalesView
from ui.views.reports_view import ReportsView
from ui.views.backup_view import BackupView
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nadeem Computers Management System")
        self.setMinimumSize(1200, 800)

        # Main Widget and Layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Create UI Components
        self.setup_sidebar()
        self.setup_main_area()

        self.main_layout.addWidget(self.sidebar)
        self.main_layout.addWidget(self.content_area)

    def setup_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(280)
        
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(0, 20, 0, 20)
        sidebar_layout.setSpacing(5)

        # Sidebar Logo Container
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        self.sidebar_logo = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            self.sidebar_logo.setPixmap(pixmap.scaled(200, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            self.sidebar_logo.setText("NADEEM COMPUTERS")
            self.sidebar_logo.setStyleSheet("color: #8cc63f; font-size: 20px; font-weight: 900;")
        
        self.sidebar_logo.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(self.sidebar_logo)
        logo_layout.setContentsMargins(0, 0, 0, 30)
        sidebar_layout.addLayout(logo_layout)

        # Navigation Buttons
        self.nav_buttons = {}
        
        # Helper to create and add buttons
        def create_and_add_button(name, callback):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.clicked.connect(callback)
            btn.clicked.connect(lambda checked, b=btn: self.update_active_button(b))
            sidebar_layout.addWidget(btn)
            self.nav_buttons[name] = btn

        create_and_add_button("Dashboard", self.show_dashboard)
        create_and_add_button("Repairs", self.show_repairs)
        create_and_add_button("Inventory", self.show_inventory)
        create_and_add_button("Sales & Billing", self.show_sales)
        create_and_add_button("Customers", self.show_customers)
        create_and_add_button("Reports", self.show_reports)
        create_and_add_button("Backup & Restore", self.show_backup)

        sidebar_layout.addStretch()

        # Set Dashboard as active
        if "Dashboard" in self.nav_buttons:
            self.nav_buttons["Dashboard"].setChecked(True)

    def setup_main_area(self):
        self.content_area = QFrame()
        self.content_area.setObjectName("MainContent")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget()
        
        # Add views
        self.views = {
            "Dashboard": DashboardView(),
            "Repairs": RepairsView(),
            "Inventory": InventoryView(),
            "Sales & Billing": SalesView(),
            "Customers": CustomersView(),
            "Reports": ReportsView(),
            "Backup": BackupView()
        }

        for name, view in self.views.items():
            self.stacked_widget.addWidget(view)

        self.content_layout.addWidget(self.stacked_widget)

    def update_active_button(self, active_btn):
        for btn in self.nav_buttons.values():
            if btn != active_btn:
                btn.setChecked(False)

    # Navigation callbacks
    def show_dashboard(self): self.stacked_widget.setCurrentWidget(self.views["Dashboard"])
    def show_repairs(self): self.stacked_widget.setCurrentWidget(self.views["Repairs"])
    def show_inventory(self): self.stacked_widget.setCurrentWidget(self.views["Inventory"])
    def show_sales(self): self.stacked_widget.setCurrentWidget(self.views["Sales & Billing"])
    def show_customers(self): self.stacked_widget.setCurrentWidget(self.views["Customers"])
    def show_reports(self): self.stacked_widget.setCurrentWidget(self.views["Reports"])
    def show_backup(self): self.stacked_widget.setCurrentWidget(self.views["Backup"])

    def closeEvent(self, event):
        from services.backup_service import BackupService
        BackupService.create_backup(auto=True)
        event.accept()
