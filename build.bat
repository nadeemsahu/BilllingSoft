@echo off
echo Building Computer Shop Management System...
call venv\Scripts\activate.bat
pip install PyQt5 reportlab pyinstaller
pyinstaller --noconfirm --onedir --windowed --name CSMS --add-data "ui/styles.qss;ui/" --add-data "database/schema.sql;database/" --add-data "assets/*;assets/" main.py
echo Build Complete! Check the 'dist/CSMS' folder.
pause
