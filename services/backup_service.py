import os
import shutil
import logging
from datetime import datetime
from database.db_manager import db

class BackupService:
    @staticmethod
    def get_backup_dir():
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backups")
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        return backup_dir

    @staticmethod
    def create_backup(auto=False) -> str:
        try:
            db_path = db.db_path
            if not os.path.exists(db_path):
                return ""

            backup_dir = BackupService.get_backup_dir()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            prefix = "AutoBackup" if auto else "ManualBackup"
            
            backup_filename = f"{prefix}_{timestamp}.db"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            shutil.copy2(db_path, backup_path)
            logging.info(f"Backup created successfully at {backup_path}")
            return backup_path
        except Exception as e:
            logging.error(f"Backup failed: {e}")
            return ""

    @staticmethod
    def restore_backup(backup_path: str) -> bool:
        safety_backup = None
        try:
            db_path = db.db_path
            
            # Create a safety backup of current state before restoring
            safety_backup = db_path + ".safety"
            if os.path.exists(db_path):
                shutil.copy2(db_path, safety_backup)
                
            shutil.copy2(backup_path, db_path)
            logging.info(f"Database restored from {backup_path}")
            return True
        except Exception as e:
            logging.error(f"Restore failed: {e}")
            # Try to restore safety backup
            if safety_backup and os.path.exists(safety_backup):
                shutil.copy2(safety_backup, db_path)
            return False
