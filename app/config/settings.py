import os
import sys

APP_NAME = "AeroChart Inspector"
VERSION = "1.1"

def get_app_icon_path():
    """Locate icon path across development environment and PyInstaller bundles."""
    candidates = ["app_icon2.ico", "app_icon.ico", "icon.ico", "app_icon.png", "icon.png"]
    search_dirs = []
    
    # Check PyInstaller temporary extraction folder
    if hasattr(sys, "_MEIPASS"):
        search_dirs.append(sys._MEIPASS)
        
    # Check project root and current working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    search_dirs.append(os.path.abspath(os.path.join(script_dir, "..", "..")))
    search_dirs.append(os.path.abspath(os.path.join(script_dir, "..")))
    search_dirs.append(os.getcwd())
    
    for directory in search_dirs:
        for name in candidates:
            full_path = os.path.join(directory, name)
            if os.path.exists(full_path):
                return full_path
    return None

# Professional Aviation Light Blue Theme Stylesheet
THEME_STYLESHEET = """
/* Universal High-Contrast Tooltip Styling - Identical for all buttons across entire app */
QToolTip,
QPushButton QToolTip,
QWidget QToolTip,
QToolButton QToolTip {
    background-color: #E2E8F0;
    color: #000000;
    border: 1px solid #94A3B8;
    border-radius: 4px;
    padding: 2px 6px;
    font-size: 11px;
    font-weight: 500;
}
QMainWindow {
    background-color: #F0F4F8;
    color: #0A192F;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QWidget {
    background-color: #F0F4F8;
    color: #0A192F;
    font-size: 13px;
}
QTabWidget::pane {
    border: 1px solid #CBD5E1;
    background: #FFFFFF;
    border-radius: 4px;
}
QTabBar::tab {
    background: #E2E8F0;
    color: #1E293B;
    padding: 8px 16px;
    margin-right: 2px;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    font-weight: bold;
}
QTabBar::tab:selected {
    background: #FFFFFF;
    color: #0284C7;
    border-bottom: 2px solid #0284C7;
}
QPushButton {
    background-color: #0284C7;
    color: #FFFFFF;
    border: none;
    padding: 6px 14px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #0369A1;
}
QPushButton:pressed {
    background-color: #075985;
}
QPushButton:disabled {
    background-color: #CBD5E1;
    color: #94A3B8;
}
QLineEdit, QComboBox, QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 4px;
    padding: 4px 8px;
    color: #0F172A;
}
QLabel {
    background: transparent;
    color: #1E293B;
}
QTableWidget {
    background-color: #FFFFFF;
    alternate-background-color: #F8FAFC;
    gridline-color: #E2E8F0;
    border: 1px solid #CBD5E1;
}
QHeaderView::section {
    background-color: #E2E8F0;
    color: #1E293B;
    padding: 6px;
    border: none;
    font-weight: bold;
}
"""