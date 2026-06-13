from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFileDialog, QMessageBox, QGroupBox)
from services.backup_service import BackupService
import os

class BackupView(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        title = QLabel("Backup & Restore")
        title.setObjectName("HeaderTitle")
        main_layout.addWidget(title)

        backup_group = QGroupBox("Create Backup")
        backup_layout = QVBoxLayout()
        backup_desc = QLabel("Manually create a backup of your entire database.")
        backup_btn = QPushButton("Create Manual Backup")
        backup_btn.setFixedWidth(200)
        backup_btn.clicked.connect(self.do_backup)
        backup_layout.addWidget(backup_desc)
        backup_layout.addWidget(backup_btn)
        backup_group.setLayout(backup_layout)
        
        restore_group = QGroupBox("Restore Backup")
        restore_layout = QVBoxLayout()
        restore_desc = QLabel("Restore your database from an existing .db backup file.\nWarning: This will overwrite your current data.")
        restore_btn = QPushButton("Restore from File")
        restore_btn.setFixedWidth(200)
        restore_btn.clicked.connect(self.do_restore)
        restore_layout.addWidget(restore_desc)
        restore_layout.addWidget(restore_btn)
        restore_group.setLayout(restore_layout)

        main_layout.addWidget(backup_group)
        main_layout.addWidget(restore_group)
        main_layout.addStretch()

    def do_backup(self):
        path = BackupService.create_backup()
        if path:
            QMessageBox.information(self, "Success", f"Backup created successfully at:\n{path}")
        else:
            QMessageBox.critical(self, "Error", "Failed to create backup.")

    def do_restore(self):
        reply = QMessageBox.question(self, 'Restore Database', 
                                     'Are you sure you want to restore? This will replace all current data. The app needs to be restarted afterward.',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            file_name, _ = QFileDialog.getOpenFileName(self, "Select Backup File", BackupService.get_backup_dir(), "Database Files (*.db)")
            if file_name:
                success = BackupService.restore_backup(file_name)
                if success:
                    QMessageBox.information(self, "Success", "Database restored successfully. Please close and reopen the application.")
                else:
                    QMessageBox.critical(self, "Error", "Failed to restore database.")
