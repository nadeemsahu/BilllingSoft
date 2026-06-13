from database.db_manager import db
from typing import List, Optional, Dict, Any
from datetime import datetime

class RepairModel:
    @staticmethod
    def add_repair(customer_id: int, device_type: str, brand: str, model: str,
                   serial_number: str, problem_description: str, accessories: str) -> Optional[int]:
        query = """INSERT INTO repairs 
                   (customer_id, device_type, brand, model, serial_number, problem_description, accessories, status) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, 'Received')"""
        return db.insert_and_get_id(query, (customer_id, device_type, brand, model, serial_number, problem_description, accessories))

    @staticmethod
    def update_repair_status(repair_id: int, status: str, service_charge: float = 0.0, parts_cost: float = 0.0) -> bool:
        if status == 'Delivered':
            date_delivered = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            query = """UPDATE repairs 
                       SET status = ?, service_charge = ?, parts_cost = ?, date_delivered = ? 
                       WHERE id = ?"""
            return db.execute_query(query, (status, service_charge, parts_cost, date_delivered, repair_id))
        else:
            query = """UPDATE repairs 
                       SET status = ?, service_charge = ?, parts_cost = ? 
                       WHERE id = ?"""
            return db.execute_query(query, (status, service_charge, parts_cost, repair_id))

    @staticmethod
    def update_repair(repair_id: int, device_type: str, brand: str, model: str,
                      serial_number: str, problem_description: str, accessories: str) -> bool:
        query = """UPDATE repairs
                   SET device_type = ?, brand = ?, model = ?, serial_number = ?, problem_description = ?, accessories = ?
                   WHERE id = ?"""
        return db.execute_query(query, (device_type, brand, model, serial_number, problem_description, accessories, repair_id))

    @staticmethod
    def delete_repair(repair_id: int) -> bool:
        query = "DELETE FROM repairs WHERE id = ?"
        return db.execute_query(query, (repair_id,))

    @staticmethod
    def get_all_repairs() -> List[Dict[str, Any]]:
        query = """SELECT r.*, c.name as customer_name, c.phone as customer_phone 
                   FROM repairs r 
                   LEFT JOIN customers c ON r.customer_id = c.id 
                   ORDER BY r.date_received DESC"""
        rows = db.fetch_all(query)
        return [dict(row) for row in rows]

    @staticmethod
    def get_repair_by_id(repair_id: int) -> Optional[Dict[str, Any]]:
        query = """SELECT r.*, c.name as customer_name, c.phone as customer_phone 
                   FROM repairs r 
                   LEFT JOIN customers c ON r.customer_id = c.id 
                   WHERE r.id = ?"""
        row = db.fetch_one(query, (repair_id,))
        return dict(row) if row else None

    @staticmethod
    def get_pending_repairs() -> List[Dict[str, Any]]:
        query = """SELECT r.*, c.name as customer_name
                   FROM repairs r
                   LEFT JOIN customers c ON r.customer_id = c.id
                   WHERE r.status != 'Delivered'
                   ORDER BY r.date_received DESC"""
        rows = db.fetch_all(query)
        return [dict(row) for row in rows]

    @staticmethod
    def get_completed_not_delivered() -> List[Dict[str, Any]]:
        query = """SELECT r.*, c.name as customer_name
                   FROM repairs r
                   LEFT JOIN customers c ON r.customer_id = c.id
                   WHERE r.status = 'Completed'
                   ORDER BY r.date_received DESC"""
        rows = db.fetch_all(query)
        return [dict(row) for row in rows]

    @staticmethod
    def search_repairs(search_term: str) -> List[Dict[str, Any]]:
        term = f"%{search_term}%"
        query = """SELECT r.*, c.name as customer_name, c.phone as customer_phone 
                   FROM repairs r 
                   LEFT JOIN customers c ON r.customer_id = c.id 
                   WHERE c.name LIKE ? OR c.phone LIKE ? OR r.device_type LIKE ? OR r.brand LIKE ? OR r.model LIKE ? OR r.serial_number LIKE ?
                   ORDER BY r.date_received DESC"""
        rows = db.fetch_all(query, (term, term, term, term, term, term))
        return [dict(row) for row in rows]
