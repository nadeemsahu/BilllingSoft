# BillingSoft - Desktop POS & Repair Management

> A modern offline desktop application for managing computer repairs, sales, inventory, customers, reports, and backups.

---

## 🚀 Overview
This application is a complete point-of-sale and repair management system designed for small computer repair shops. It provides an all-in-one solution to handle repairs, manage inventory, generate billing, maintain customer records, and secure data through local backups without requiring internet access.

Built with:
- **Python** for core logic
- **PyQt5** for a responsive and modern desktop UI
- **SQLite** for reliable local data storage
- **ReportLab** for professional PDF invoice generation

## ✨ Core Features
- **Dashboard**: Quick overview of key business metrics and workflow summary.
- **Inventory Management**: Track products and repair parts with low-stock alerts.
- **Customer Database**: Manage customer profiles and prevent duplicate entries based on phone numbers.
- **Repair Workflow**: Seamlessly track repair status from 'Received' to 'Delivered'.
- **Sales & Billing**: Robust point-of-sale system with cart functionality and automated PDF invoice generation.
- **Reports**: Generate insightful reports on sales revenue and repair performance.
- **Backup & Restore**: Ensure data safety with automated and manual SQLite database backups.

## 📦 Project Layout
- `main.py` — Application entry point with global exception handling.
- `ui/` — PyQt5 user interface components, window structures, stylesheet (`styles.qss`), and views.
- `database/` — SQLite database manager and table schema setup.
- `models/` — Business logic models for customers, inventory, repairs, and sales.
- `services/` — Core background services including backup management and PDF generation.
- `utils/` — Shared helper functions and utilities.
- `backups/` — Automatically generated database backup files.

## ⚙️ Requirements
- Python 3.9+
- `PyQt5` (5.15+)
- `reportlab`
- `pyinstaller` (optional, for packaging into a standalone executable)
- `pytest` (optional, for running tests)

All dependencies are defined in `requirements.txt`.

## 🧪 Quick Start
Follow these steps to set up the project locally:

```cmd
# 1. Clone the repository
git clone https://github.com/nadeemsahu/BilllingSoft.git
cd BilllingSoft

# 2. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\Activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python main.py
```

## 🖥️ Application Modules
Upon launching the main window, you will have direct access to the following modules via the sidebar:
- **Dashboard**: A high-level view of your business operations.
- **Repairs**: Manage incoming repairs, update status, and track delivery.
- **Inventory**: Add, update, or remove items from your store.
- **Sales & Billing**: Process new sales and generate bills instantly.
- **Customers**: View and manage customer information.
- **Reports**: Analyze your business performance.
- **Backup & Restore**: Create backups or restore from a previous state.

## 💾 Backups
- The application creates an **automatic backup** every time it is closed.
- **Manual backups** can be triggered at any time from the Backup view.
- All backup files are stored securely in the local `backups/` directory.

## 🧾 Invoice Generation
Invoices are dynamically generated as professional PDF documents using the built-in `services/pdf_service.py` service. They can be exported directly from the sales workflow and shared with customers.

## 📝 Developer Notes
- The SQLite database file (`shop_data.db`) is initialized automatically on the first run.
- Application styling is centralized and can be easily customized via `ui/styles.qss`.
- If the default logo (`ui/assets/logo.png`) is not found, the application gracefully falls back to displaying a text-based logo in the sidebar.

---

## 📄 License
This project is proprietary and developed specifically for small business computer shops.

## 🤝 Contributing
For bug reports or feature requests, please contact the repository owner or open an issue on GitHub.
