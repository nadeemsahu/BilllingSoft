from database.db_manager import db
from typing import List, Optional, Dict, Any

class CustomerModel:
    @staticmethod
    def add_customer(name: str, phone: str, address: str = "") -> Optional[int]:
        query = "INSERT INTO customers (name, phone, address) VALUES (?, ?, ?)"
        return db.insert_and_get_id(query, (name, phone, address))

    @staticmethod
    def update_customer(customer_id: int, name: str, phone: str, address: str = "") -> bool:
        query = "UPDATE customers SET name = ?, phone = ?, address = ? WHERE id = ?"
        return db.execute_query(query, (name, phone, address, customer_id))

    @staticmethod
    def delete_customer(customer_id: int) -> bool:
        query = "DELETE FROM customers WHERE id = ?"
        return db.execute_query(query, (customer_id,))

    @staticmethod
    def get_all_customers() -> List[Dict[str, Any]]:
        query = "SELECT * FROM customers ORDER BY name"
        rows = db.fetch_all(query)
        return [dict(row) for row in rows]

    @staticmethod
    def get_customer_by_id(customer_id: int) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM customers WHERE id = ?"
        row = db.fetch_one(query, (customer_id,))
        return dict(row) if row else None

    @staticmethod
    def search_customers(search_term: str) -> List[Dict[str, Any]]:
        term = f"%{search_term}%"
        query = "SELECT * FROM customers WHERE name LIKE ? OR phone LIKE ?"
        rows = db.fetch_all(query, (term, term))
        return [dict(row) for row in rows]
