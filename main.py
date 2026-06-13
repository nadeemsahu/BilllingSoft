import sys
import os
import logging
import traceback
from PyQt5.QtWidgets import QApplication, QMessageBox
from ui.main_window import MainWindow

# Provide a logs directory in the application root
log_path = os.path.join(os.path.dirname(__file__), 'error.log')
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def global_exception_handler(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logging.error("Uncaught exception:\n" + error_msg)
    
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle("Application Error")
    msg_box.setText("Something went wrong, but the application caught the error.")
    msg_box.setInformativeText(str(exc_value))
    msg_box.setDetailedText(error_msg)
    msg_box.exec_()

sys.excepthook = global_exception_handler

def main():
    try:
        app = QApplication(sys.argv)
        
        # Load stylesheet
        styles_path = os.path.join(os.path.dirname(__file__), 'ui', 'styles.qss')
        if os.path.exists(styles_path):
            with open(styles_path, 'r') as f:
                app.setStyleSheet(f.read())
        else:
            logging.warning(f"Stylesheet not found at {styles_path}")

        window = MainWindow()
        window.showMaximized()
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical(f"Application crashed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
