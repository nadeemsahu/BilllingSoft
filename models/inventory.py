from database.db_manager import db
from typing import List, Optional, Dict, Any

class InventoryModel:
    @staticmethod
    def add_product(name: str, type: str, cost_price: float, selling_price: float, quantity: int) -> Optional[int]:
        query = """INSERT INTO inventory (name, type, cost_price, selling_price, quantity) 
                   VALUES (?, ?, ?, ?, ?)"""
        return db.insert_and_get_id(query, (name, type, cost_price, selling_price, quantity))

    @staticmethod
    def update_product(product_id: int, name: str, type: str, cost_price: float, selling_price: float, quantity: int) -> bool:
        query = """UPDATE inventory 
                   SET name = ?, type = ?, cost_price = ?, selling_price = ?, quantity = ? 
                   WHERE id = ?"""
        return db.execute_query(query, (name, type, cost_price, selling_price, quantity, product_id))

    @staticmethod
    def update_quantity(product_id: int, quantity_change: int) -> bool:
        """Adds quantity_change to current quantity. quantity_change can be negative for sales."""
        query = "UPDATE inventory SET quantity = quantity + ? WHERE id = ?"
        return db.execute_query(query, (quantity_change, product_id))

    @staticmethod
    def delete_product(product_id: int) -> bool:
        query = "DELETE FROM inventory WHERE id = ?"
        return db.execute_query(query, (product_id,))

    @staticmethod
    def get_all_products() -> List[Dict[str, Any]]:
        query = "SELECT * FROM inventory ORDER BY name"
        rows = db.fetch_all(query)
        return [dict(row) for row in rows]

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM inventory WHERE id = ?"
        row = db.fetch_one(query, (product_id,))
        return dict(row) if row else None

    @staticmethod
    def search_products(search_term: str) -> List[Dict[str, Any]]:
        term = f"%{search_term}%"
        query = "SELECT * FROM inventory WHERE name LIKE ? OR type LIKE ?"
        rows = db.fetch_all(query, (term, term))
        return [dict(row) for row in rows]

    @staticmethod
    def get_low_stock_products(threshold: int = 5) -> List[Dict[str, Any]]:
        query = "SELECT * FROM inventory WHERE quantity <= ? ORDER BY quantity ASC"
        rows = db.fetch_all(query, (threshold,))
        return [dict(row) for row in rows]
