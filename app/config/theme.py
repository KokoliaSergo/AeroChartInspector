AVIATION_LIGHT_THEME = """
/* Global Application Font and Background (Light Flight Deck / EFB Day Mode) */
QWidget {
    background-color: #F8FAFC;
    color: #1E293B;
    font-family: 'Segoe UI', -apple-system, Helvetica, Arial, sans-serif;
    font-size: 13px;
}

/* Tab Widget Styling */
QTabWidget::pane {
    border: 1px solid #CBD5E1;
    background-color: #FFFFFF;
    border-radius: 6px;
}

QTabBar::tab {
    background-color: #E2E8F0;
    color: #475569;
    padding: 10px 18px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
}

QTabBar::tab:selected {
    background-color: #FFFFFF;
    color: #0284C7;
    border-bottom: 2px solid #0284C7;
}

QTabBar::tab:hover {
    background-color: #CBD5E1;
    color: #0F172A;
}

/* Group Boxes */
QGroupBox {
    border: 1px solid #CBD5E1;
    border-radius: 8px;
    margin-top: 12px;
    font-weight: bold;
    color: #0284C7;
    background-color: #FFFFFF;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 6px;
    left: 10px;
}

/* Push Buttons */
QPushButton {
    background-color: #E2E8F0;
    color: #1E293B;
    border: 1px solid #CBD5E1;
    padding: 6px 14px;
    border-radius: 4px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #CBD5E1;
    border-color: #94A3B8;
}

QPushButton:pressed {
    background-color: #94A3B8;
}

QPushButton:disabled {
    background-color: #F1F5F9;
    color: #94A3B8;
    border-color: #E2E8F0;
}

/* Input Fields & Combos */
QLineEdit, QComboBox, QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 4px;
    padding: 5px;
    color: #0F172A;
}

QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
    border: 1px solid #0284C7;
}

QComboBox::drop-down {
    subcontrol-origin: padding;
    subcontrol-position: top right;
    width: 24px;
    border-left: 1px solid #CBD5E1;
    border-top-right-radius: 4px;
    border-bottom-right-radius: 4px;
    background-color: #F1F5F9;
}

QComboBox::down-arrow {
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23475569' stroke-width='2.5' stroke-linecap='round' stroke-linejoin='round'><polyline points='6 9 12 15 18 9'></polyline></svg>");
    width: 12px;
    height: 12px;
}

QComboBox::down-arrow:on {
    top: 1px;
    left: 1px;
}

/* Tables */
QTableWidget {
    background-color: #FFFFFF;
    alternate-background-color: #F8FAFC;
    gridline-color: #E2E8F0;
    border: 1px solid #CBD5E1;
    border-radius: 4px;
    color: #1E293B;
}

QHeaderView::section {
    background-color: #E2E8F0;
    color: #0F172A;
    padding: 6px;
    border: 1px solid #CBD5E1;
    font-weight: bold;
}

QTableWidget::item:selected {
    background-color: #0284C7;
    color: white;
}

/* Scrollbars & Sliders */
QScrollBar:vertical {
    background: #F1F5F9;
    width: 10px;
    margin: 0px;
}

QScrollBar::handle:vertical {
    background: #CBD5E1;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background: #94A3B8;
}

QSlider::groove:horizontal {
    height: 6px;
    background: #E2E8F0;
    border-radius: 3px;
}

QSlider::handle:horizontal {
    background: #0284C7;
    border: none;
    width: 14px;
    height: 14px;
    margin: -4px 0;
    border-radius: 7px;
}

QSlider::handle:horizontal:hover {
    background: #0369A1;
}

/* Status Bar */
QStatusBar {
    background-color: #E2E8F0;
    color: #475569;
    border-top: 1px solid #CBD5E1;
}
"""