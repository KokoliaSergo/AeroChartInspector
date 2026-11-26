import os
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app.gui.main_window import MainWindow
from app.config.theme import AVIATION_LIGHT_THEME
from app.config.settings import get_app_icon_path

def main():
    # Set Windows AppUserModelID so the taskbar displays the custom icon properly
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("kokolia.aerochartinspector.v1.1")
        except Exception:
            pass

    app = QApplication(sys.argv)
    
    # Apply modern aviation light theme (EFB Day Mode)
    app.setStyleSheet(AVIATION_LIGHT_THEME)
    
    # Force high-contrast tooltip palette globally on QApplication
    # This guarantees that native Windows-rendered tooltips on external PCs are always readable
    from PySide6.QtGui import QPalette, QColor
    tooltip_palette = app.palette()
    tooltip_palette.setColor(QPalette.ToolTipBase, QColor("#E2E8F0"))
    tooltip_palette.setColor(QPalette.ToolTipText, QColor("#000000"))
    app.setPalette(tooltip_palette)
    
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