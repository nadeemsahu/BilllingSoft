import sqlite3
import os
import logging
from typing import List, Dict, Any, Tuple, Optional

class DatabaseManager:
    _instance = None
    db_path: str = ""

    def __new__(cls, db_path=None):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            if db_path is None:
                project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                db_path = os.path.join(project_root, 'shop_data.db')
            cls._instance.db_path = db_path
            cls._instance.init_db()
        return cls._instance

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def init_db(self):
        """Initialize the database with the schema."""
        schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
        if not os.path.exists(schema_path):
            logging.error(f"Schema file not found at {schema_path}")
            return

        with open(schema_path, 'r') as f:
            schema_sql = f.read()

        try:
            with self._get_connection() as conn:
                conn.executescript(schema_sql)
            logging.info("Database initialized successfully.")
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")

    def execute_query(self, query: str, params: tuple = ()) -> bool:
        """Execute insert/update/delete queries."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return True
        except sqlite3.Error as e:
            logging.error(f"Execute query error: {e} - Query: {query}")
            return False

    def insert_and_get_id(self, query: str, params: tuple = ()) -> Optional[int]:
        """Execute insert and return the new row id."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            logging.error(f"Insert error: {e} - Query: {query}")
            return None

    def fetch_all(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """Fetch multiple rows."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchall()
        except sqlite3.Error as e:
            logging.error(f"Fetch all error: {e} - Query: {query}")
            return []

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[sqlite3.Row]:
        """Fetch a single row."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                return cursor.fetchone()
        except sqlite3.Error as e:
            logging.error(f"Fetch one error: {e} - Query: {query}")
            return None

db = DatabaseManager()
