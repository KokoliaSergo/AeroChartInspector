import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.gui.main_window import MainWindow
from app.config.theme import AVIATION_LIGHT_THEME

def get_app_icon_path():
    """Locate icon path across development environment and PyInstaller bundles."""
    candidates = ["app_icon.ico", "icon.ico", "app_icon.png", "icon.png"]
    search_dirs = []
    
    # Check PyInstaller temporary extraction folder
    if hasattr(sys, "_MEIPASS"):
        search_dirs.append(sys._MEIPASS)
        
    # Check project root and current working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    search_dirs.append(os.path.abspath(os.path.join(script_dir, "..")))
    search_dirs.append(os.getcwd())
    
    for directory in search_dirs:
        for name in candidates:
            full_path = os.path.join(directory, name)
            if os.path.exists(full_path):
                return full_path
    return None

def main():
    # Set Windows AppUserModelID so the taskbar displays the custom icon properly
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("kokolia.aerochartinspector.v1")
        except Exception:
            pass

    app = QApplication(sys.argv)
    
    # Apply modern aviation light theme (EFB Day Mode)
    app.setStyleSheet(AVIATION_LIGHT_THEME)
    
    # Set runtime application icon if available
    icon_path = get_app_icon_path()
    if icon_path:
        icon = QIcon(icon_path)
        app.setWindowIcon(icon)
    
    window = MainWindow()
    if icon_path:
        window.setWindowIcon(QIcon(icon_path))
        
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()