from database.db_manager import db
from models.inventory import InventoryModel
from typing import List, Optional, Dict, Any, Tuple

class SaleModel:
    @staticmethod
    def create_sale(customer_id: Optional[int], total_amount: float, discount: float, items: List[Dict[str, Any]]) -> Optional[int]:
        """
        Create a new sale and its associated items. Also updates inventory.
        items list should contain dictionaries with keys:
        'product_id', 'cost_price', 'selling_price', 'quantity'
        """
        try:
            conn = db._get_connection()
            cursor = conn.cursor()
            
            # Insert sale
            cursor.execute("INSERT INTO sales (customer_id, total_amount, discount) VALUES (?, ?, ?)",
                           (customer_id, total_amount, discount))
            sale_id = cursor.lastrowid
            
            # Insert items and update inventory
            for item in items:
                cursor.execute("""INSERT INTO sale_items (sale_id, product_id, cost_price, selling_price, quantity)
                                  VALUES (?, ?, ?, ?, ?)""",
                               (sale_id, item['product_id'], item['cost_price'], item['selling_price'], item['quantity']))
                
                # Update inventory quantity
                cursor.execute("UPDATE inventory SET quantity = quantity - ? WHERE id = ?",
                               (item['quantity'], item['product_id']))
                
            conn.commit()
            return sale_id
        except Exception as e:
            import logging
            logging.error(f"Error creating sale: {e}")
            if 'conn' in locals():
                conn.rollback()
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    @staticmethod
    def get_all_sales() -> List[Dict[str, Any]]:
        query = """SELECT s.*, c.name as customer_name 
                   FROM sales s 
                   LEFT JOIN customers c ON s.customer_id = c.id 
                   ORDER BY s.date DESC"""
        rows = db.fetch_all(query)
        return [dict(row) for row in rows]

    @staticmethod
    def get_sale_items(sale_id: int) -> List[Dict[str, Any]]:
        query = """SELECT si.*, i.name as product_name
                   FROM sale_items si
                   JOIN inventory i ON si.product_id = i.id
                   WHERE si.sale_id = ?"""
        rows = db.fetch_all(query, (sale_id,))
        return [dict(row) for row in rows]

    @staticmethod
    def search_sales(search_term: str) -> List[Dict[str, Any]]:
        term = f"%{search_term}%"
        # Search by customer name or date
        query = """SELECT s.*, c.name as customer_name 
                   FROM sales s 
                   LEFT JOIN customers c ON s.customer_id = c.id 
                   WHERE c.name LIKE ? OR s.date LIKE ?
                   ORDER BY s.date DESC"""
        rows = db.fetch_all(query, (term, term))
        return [dict(row) for row in rows]
