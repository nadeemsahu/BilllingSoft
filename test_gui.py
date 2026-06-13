import pytest
from PyQt5.QtCore import Qt
from ui.main_window import MainWindow

@pytest.fixture
def app(qtbot):
    # Initialize the main window
    test_app = MainWindow()
    qtbot.addWidget(test_app)
    return test_app

def test_sidebar_navigation(app, qtbot):
    """Test that clicking sidebar buttons changes the active view."""
    
    # Mapping of button text to expected active view type
    expected_views = {
        "Dashboard": "DashboardView",
        "Repairs": "RepairsView",
        "Inventory": "InventoryView",
        "Sales & Billing": "SalesView",
        "Customers": "CustomersView",
        "Reports": "ReportsView",
        "Backup & Restore": "BackupView"
    }

    for btn_name, expected_view_class in expected_views.items():
        # Find the button in the sidebar
        button = app.nav_buttons.get(btn_name)
        assert button is not None, f"Button '{btn_name}' not found in sidebar"
        
        # Simulate a left click on the button
        qtbot.mouseClick(button, Qt.LeftButton)
        
        # Give the event loop a chance to process the click
        qtbot.wait(100)
        
        # Check if the stacked widget updated to the correct view
        current_widget = app.stacked_widget.currentWidget()
        assert current_widget.__class__.__name__ == expected_view_class, \
            f"Expected view {expected_view_class} for button '{btn_name}', but got {current_widget.__class__.__name__}"
        
        print(f"Verified button '{btn_name}' successfully switched to {expected_view_class}")

def test_inventory_add_button(app, qtbot):
    """Test basic button interaction within a specific view."""
    # Navigate to inventory
    inventory_btn = app.nav_buttons.get("Inventory")
    qtbot.mouseClick(inventory_btn, Qt.LeftButton)
    qtbot.wait(100)
    
    # Get the inventory view
    inventory_view = app.stacked_widget.currentWidget()
    assert inventory_view.__class__.__name__ == "InventoryView"
    
    # Assuming there is an 'add_btn' in InventoryView
    if hasattr(inventory_view, 'add_btn'):
        # Click the add button to ensure it doesn't crash
        qtbot.mouseClick(inventory_view.add_btn, Qt.LeftButton)
        print("Verified 'Add Item' button in InventoryView does not crash.")
