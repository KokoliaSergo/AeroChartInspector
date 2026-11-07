import sys
from PySide6.QtWidgets import QApplication
from app.gui.main_window import MainWindow
from app.config.theme import AVIATION_LIGHT_THEME

def main():
    app = QApplication(sys.argv)
    
    # Apply modern aviation light theme (EFB Day Mode)
    app.setStyleSheet(AVIATION_LIGHT_THEME)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()