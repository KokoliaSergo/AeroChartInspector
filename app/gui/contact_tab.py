from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QFrame, QGroupBox
)
from PySide6.QtCore import Qt
from app.config.settings import APP_NAME, VERSION

class ContactTab(QWidget):
    """Contact Tab displaying application overview and author credentials."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(24, 20, 24, 24)
        layout.setSpacing(18)

        # 1. Header Banner Card
        header_card = QFrame()
        header_card.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0369A1, stop:1 #0284C7);
                border-radius: 8px;
                padding: 16px 20px;
            }
        """)
        header_layout = QVBoxLayout(header_card)
        header_layout.setContentsMargins(12, 8, 12, 8)
        header_layout.setSpacing(4)

        title_lbl = QLabel(f"✈ {APP_NAME} <span style='font-size: 14px; font-weight: normal; color: #E0F2FE;'>v{VERSION}</span>")
        title_lbl.setStyleSheet("color: #FFFFFF; font-size: 22px; font-weight: bold; background: transparent;")
        
        subtitle_lbl = QLabel("Aeronautical Chart Verification, Discrepancy Tracking & Quality Assurance System")
        subtitle_lbl.setStyleSheet("color: #BAE6FD; font-size: 13px; font-weight: 500; background: transparent;")

        header_layout.addWidget(title_lbl)
        header_layout.addWidget(subtitle_lbl)
        layout.addWidget(header_card)

        # 2. Application Overview Card
        about_group = QGroupBox("About AeroChart Inspector")
        about_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #1E293B;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 14px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: #0284C7;
            }
        """)
        about_layout = QVBoxLayout(about_group)
        about_layout.setContentsMargins(18, 14, 18, 16)
        about_layout.setSpacing(10)

        intro_text = (
            "<p style='line-height: 145%; color: #334155; font-size: 13px; margin: 0;'>"
            "<b>AeroChart Inspector</b> is a specialized aviation software application engineered for "
            "aeronautical cartographers, procedure designers, and Flight Operations / Quality Control specialists. "
            "It streamlines the quality assurance process required during AIRAC cycle revisions and chart publishing cycles."
            "</p>"
            "<div style='margin-top: 8px; line-height: 155%; color: #475569; font-size: 12.5px;'>"
            "<b>Key Operational Capabilities:</b><br>"
            "• <b>Dual-Chart Comparison & Overlay:</b> High-resolution rendering of updated charts against baseline predecessors with sub-pixel drag alignment, angle rotation, and alpha blending.<br>"
            "• <b>Rapid Visual Flicker Mode:</b> Alternating visual flicker tool that instantly highlights subtle drafting, obstacle, frequency, waypoint, or procedure discrepancies.<br>"
            "• <b>Aviation Discrepancy Logging:</b> Structured error recording categorized by standardized severity levels (<i>Critical, Major, Minor, Observation</i>) with on-chart coordinate pin badges.<br>"
            "• <b>Independent Markup & Callouts:</b> Discrepancy draw highlights, transparent green verification marks, and movable text notes with flexible leader lines.<br>"
            "• <b>Automated Audit-Ready PDF Reporting:</b> One-click compilation of QC verification reports including metadata, inspected charts lists, and full-resolution visual evidence."
            "</div>"
        )
        about_lbl = QLabel(intro_text)
        about_lbl.setWordWrap(True)
        about_lbl.setTextFormat(Qt.RichText)
        about_lbl.setStyleSheet("background: transparent;")
        about_layout.addWidget(about_lbl)
        layout.addWidget(about_group)

        # 3. Developer & Contact Credentials Card
        contact_group = QGroupBox("Developer & Contact Information")
        contact_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #1E293B;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 14px;
                background-color: #FFFFFF;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: #0284C7;
            }
        """)
        contact_layout = QVBoxLayout(contact_group)
        contact_layout.setContentsMargins(18, 16, 18, 18)
        contact_layout.setSpacing(12)

        author_heading = QLabel("<span style='font-size: 15px; font-weight: bold; color: #0F172A;'>Sergo Kokolia</span> "
                                "<span style='color: #64748B; font-size: 13px;'>— Lead Developer</span>")
        author_heading.setStyleSheet("background: transparent;")
        contact_layout.addWidget(author_heading)

        # Contact items list
        contacts_html = (
            "<table style='border-spacing: 0px 8px; font-size: 13px; color: #334155;'>"
            "<tr>"
            "  <td style='width: 130px; font-weight: bold; color: #475569;'>✉ E-mail:</td>"
            "  <td><a href='mailto:kokolia.sergo@gmail.com' style='color: #0284C7; text-decoration: none; font-weight: 500;'>kokolia.sergo@gmail.com</a></td>"
            "</tr>"
            "<tr>"
            "  <td style='font-weight: bold; color: #475569;'>💬 WhatsApp / Viber:</td>"
            "  <td><a href='https://wa.me/995577142314' style='color: #0284C7; text-decoration: none; font-weight: 500;'>(+995) 577142314</a></td>"
            "</tr>"
            "<tr>"
            "  <td style='font-weight: bold; color: #475569;'>🐙 GitHub:</td>"
            "  <td><a href='https://github.com/KokoliaSergo' style='color: #0284C7; text-decoration: none; font-weight: 500;'>https://github.com/KokoliaSergo</a></td>"
            "</tr>"
            "<tr>"
            "  <td style='font-weight: bold; color: #475569;'>🔗 LinkedIn:</td>"
            "  <td><a href='https://www.linkedin.com/in/sergo-kokolia-b3573187' style='color: #0284C7; text-decoration: none; font-weight: 500;'>https://www.linkedin.com/in/sergo-kokolia-b3573187</a></td>"
            "</tr>"
            "</table>"
        )
        contact_links_lbl = QLabel(contacts_html)
        contact_links_lbl.setOpenExternalLinks(True)
        contact_links_lbl.setTextFormat(Qt.RichText)
        contact_links_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.LinksAccessibleByMouse)
        contact_links_lbl.setStyleSheet("background: transparent;")
        contact_layout.addWidget(contact_links_lbl)

        layout.addWidget(contact_group)
        layout.addStretch()

        scroll_area.setWidget(content_widget)
        outer_layout.addWidget(scroll_area)
