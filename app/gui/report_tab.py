import os
import re
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, 
    QFileDialog, QMessageBox, QLineEdit, QFormLayout, QGroupBox,
    QDialog, QCalendarWidget, QHBoxLayout, QListWidget, QListWidgetItem,
    QScrollArea, QFrame
)
from PySide6.QtCore import QDate, Qt, QSize, QUrl
from PySide6.QtGui import QIcon, QPixmap, QDesktopServices
from app.reports.report_generator import ReportGenerator

class CalendarDialog(QDialog):
    def __init__(self, current_date_str="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Validation Date")
        self.resize(360, 320)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        # Week starts from Monday (Requirement 1)
        self.calendar.setFirstDayOfWeek(Qt.Monday)
        # Remove week numbers from calendar
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setMinimumDate(QDate(2025, 1, 1))
        self.calendar.setMaximumDate(QDate(2035, 12, 31))
        
        if current_date_str:
            qdate = QDate.fromString(current_date_str, "dd-MM-yyyy")
            if qdate.isValid():
                self.calendar.setSelectedDate(qdate)
        
        layout.addWidget(self.calendar)
        
        # Display the selected date prominently
        self.lbl_chosen_date = QLabel()
        self.lbl_chosen_date.setStyleSheet(
            "font-size: 13px; color: #0F172A; padding: 6px 10px; background-color: #F1F5F9; "
            "border: 1px solid #CBD5E1; border-radius: 4px;"
        )
        layout.addWidget(self.lbl_chosen_date)
        self.update_chosen_label()
        
        self.calendar.selectionChanged.connect(self.update_chosen_label)
        self.calendar.clicked.connect(self.update_chosen_label)
        
        btn_layout = QHBoxLayout()
        btn_select = QPushButton("Select")
        btn_select.setStyleSheet("QPushButton { background-color: #0284C7; color: white; font-weight: bold; }")
        btn_select.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_select)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def update_chosen_label(self):
        d_str = self.calendar.selectedDate().toString("dd-MM-yyyy")
        self.lbl_chosen_date.setText(f"<b>Selected Date:</b> <span style='color: #0284C7; font-weight: bold;'>{d_str}</span>")

    def get_selected_date(self) -> str:
        return self.calendar.selectedDate().toString("dd-MM-yyyy")


class ReportTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checked_charts_list = []
        self.init_ui()

    def init_ui(self):
        # Outer container layout
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        
        # Scroll area for smooth, responsive vertical layout
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")
        
        content_widget = QWidget()
        content_widget.setStyleSheet("background-color: transparent;")
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(15, 12, 15, 15)
        layout.setSpacing(12)
        
        layout.addWidget(QLabel("<b>AeroChart Inspector - Review Summary & PDF Report</b>"))
        
        # 1. Review & Log Metadata Group
        qc_group = QGroupBox("Review & Log Metadata")
        qc_layout = QFormLayout()
        qc_layout.setContentsMargins(12, 12, 12, 12)
        qc_layout.setSpacing(8)
        
        self.txt_inspector_name = QLineEdit()
        self.txt_inspector_name.setPlaceholderText("Enter Name and Surname (e.g., John Doe)")
        qc_layout.addRow("Name and Surname:", self.txt_inspector_name)

        date_layout = QHBoxLayout()
        self.txt_validation_date = QLineEdit()
        self.txt_validation_date.setText(datetime.now().strftime("%d-%m-%Y"))
        self.txt_validation_date.setPlaceholderText("DD-MM-YYYY")
        self.txt_validation_date.setToolTip("Validation date in DD-MM-YYYY format")
        
        btn_calendar = QPushButton("Select Date...")
        btn_calendar.setToolTip("Open calendar pop-up to select inspection validation date")
        btn_calendar.clicked.connect(self.open_calendar_dialog)
        
        date_layout.addWidget(self.txt_validation_date)
        date_layout.addWidget(btn_calendar)
        qc_layout.addRow("Validation Date:", date_layout)

        self.txt_log_sheets = QLineEdit()
        self.txt_log_sheets.setPlaceholderText("Enter Log Sheet numbers (e.g., LS-2026-01, LS-2026-02)")
        self.txt_log_sheets.setToolTip("Associated Quality Control log sheet reference numbers")
        qc_layout.addRow("Log Sheet Number(s):", self.txt_log_sheets)

        qc_group.setLayout(qc_layout)
        layout.addWidget(qc_group)

        # 2. List of Checked Charts Box
        charts_group = QGroupBox("List of Checked Charts")
        charts_layout = QVBoxLayout()
        charts_layout.setContentsMargins(12, 14, 12, 12)
        charts_layout.setSpacing(10)
        
        self.list_checked_charts = QListWidget()
        self.list_checked_charts.setToolTip("List of charts verified during this session to be included in the report")
        self.list_checked_charts.setMinimumHeight(110)
        self.list_checked_charts.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 4px;
                color: #1E293B;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 5px 8px;
                border-bottom: 1px solid #F1F5F9;
            }
            QListWidget::item:selected {
                background-color: #E0F2FE;
                color: #0284C7;
                font-weight: bold;
                border-radius: 4px;
            }
        """)
        charts_layout.addWidget(self.list_checked_charts, 1)
        
        charts_btn_layout = QHBoxLayout()
        btn_add_charts = QPushButton("Add Chart(s)...")
        btn_add_charts.setToolTip("Add chart files manually to the list of reviewed charts")
        btn_add_charts.setStyleSheet("QPushButton { background-color: #0284C7; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px; }")
        btn_add_charts.clicked.connect(self.add_checked_charts)
        
        btn_remove_chart = QPushButton("Remove Selected Chart")
        btn_remove_chart.setToolTip("Remove the selected chart from the reviewed charts list")
        btn_remove_chart.setStyleSheet("QPushButton { background-color: #EF4444; color: white; font-weight: bold; padding: 6px 14px; border-radius: 4px; }")
        btn_remove_chart.clicked.connect(self.remove_checked_chart)
        
        charts_btn_layout.addWidget(btn_add_charts)
        charts_btn_layout.addWidget(btn_remove_chart)
        charts_btn_layout.addStretch()
        charts_layout.addLayout(charts_btn_layout, 0)
        
        charts_group.setLayout(charts_layout)
        layout.addWidget(charts_group)

        # 3. Captured Visual Evidence Screenshots (Enlarged & Clean small text without small window box)
        self.evidence_group = QGroupBox("Captured Visual Evidence (Annotated Chart Screenshots)")
        evidence_layout = QVBoxLayout()
        evidence_layout.setContentsMargins(12, 12, 12, 12)
        
        self.list_evidence = QListWidget()
        self.list_evidence.setToolTip("Double-click any screenshot thumbnail to view a full-size preview")
        self.list_evidence.setIconSize(QSize(100, 70))
        self.list_evidence.setMinimumHeight(220)
        self.list_evidence.itemDoubleClicked.connect(self.preview_selected_evidence)
        evidence_layout.addWidget(self.list_evidence)
        
        evidence_btn_layout = QHBoxLayout()
        btn_preview_evidence = QPushButton("Preview Selected Evidence")
        btn_preview_evidence.setToolTip("Open full-size view of the selected screenshot evidence")
        btn_preview_evidence.setStyleSheet("QPushButton { background-color: #0284C7; color: white; font-weight: bold; }")
        btn_preview_evidence.clicked.connect(self.preview_selected_evidence)
        
        btn_remove_evidence = QPushButton("Remove Selected Evidence")
        btn_remove_evidence.setToolTip("Delete the selected screenshot from the report evidence list")
        btn_remove_evidence.setStyleSheet("QPushButton { background-color: #EF4444; color: white; font-weight: bold; }")
        btn_remove_evidence.clicked.connect(self.remove_selected_evidence)
        
        # Clean small text label replacing the small window box
        self.lbl_evidence_count = QLabel("0 evidence(s) available")
        self.lbl_evidence_count.setStyleSheet(
            "background: transparent; border: none; font-size: 11px; color: #64748B; font-weight: normal; margin-left: 10px;"
        )
        self.lbl_evidence_count.setFixedHeight(26)
        
        evidence_btn_layout.addWidget(btn_preview_evidence)
        evidence_btn_layout.addWidget(btn_remove_evidence)
        evidence_btn_layout.addWidget(self.lbl_evidence_count)
        evidence_btn_layout.addStretch()
        evidence_layout.addLayout(evidence_btn_layout)
        
        self.evidence_group.setLayout(evidence_layout)
        layout.addWidget(self.evidence_group)

        # 4. Summary Display Group (Fitted to section, no cutoff or vertical scrollbars)
        summary_group = QGroupBox("Validation Review Summary")
        summary_layout = QVBoxLayout()
        summary_layout.setContentsMargins(12, 12, 12, 12)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(200)
        self.summary_text.setStyleSheet("""
            QTextEdit {
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 10px 14px;
                font-size: 13px;
                line-height: 1.4;
                color: #0F172A;
            }
        """)
        summary_layout.addWidget(self.summary_text)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # 5. Generate PDF Report button (Green styled button)
        self.btn_generate = QPushButton("Generate PDF Report")
        self.btn_generate.setToolTip("Compile and generate official Aeronautical Chart Inspection PDF Report")
        self.btn_generate.setEnabled(False)
        self.btn_generate.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #FFFFFF;
                font-weight: bold;
                font-size: 14px;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
            QPushButton:disabled {
                background-color: #94A3B8;
                color: #E2E8F0;
            }
        """)
        self.btn_generate.clicked.connect(self.generate_report)
        layout.addWidget(self.btn_generate)

        scroll_area.setWidget(content_widget)
        outer_layout.addWidget(scroll_area)

        self.update_summary_metrics()

    def add_checked_charts(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Checked Charts", "", "PDF Files (*.pdf)")
        if files:
            for f in files:
                if f not in self.checked_charts_list:
                    self.checked_charts_list.append(f)
                    self.list_checked_charts.addItem(f.split('/')[-1].split('\\')[-1])
            self.update_summary_metrics()

    def remove_checked_chart(self):
        selected_items = self.list_checked_charts.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Required", "Please select a chart from the list to remove.")
            return
        
        for item in selected_items:
            filename = item.text()
            self.checked_charts_list = [c for c in self.checked_charts_list if c.split('/')[-1].split('\\')[-1] != filename]
            row = self.list_checked_charts.row(item)
            self.list_checked_charts.takeItem(row)
            
        self.update_summary_metrics()

    def refresh_evidence_list(self):
        """Populates the screenshots list from the Comparison tab's saved evidence."""
        self.list_evidence.clear()
        parent_win = self.window()
        comp = getattr(parent_win, 'tab_comparison', None)
        if not comp or not hasattr(comp, 'saved_annotated_pixmaps'):
            self.lbl_evidence_count.setText("0 evidence(s) available")
            self.evidence_group.setTitle("Captured Visual Evidence (Annotated Chart Screenshots) — 0 available")
            return

        pixmaps = comp.saved_annotated_pixmaps
        for idx, pix in enumerate(pixmaps):
            item = QListWidgetItem()
            thumb = pix.scaled(100, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            item.setIcon(QIcon(thumb))
            item.setText(f"Evidence #{idx + 1}")
            self.list_evidence.addItem(item)

        count = len(pixmaps)
        self.lbl_evidence_count.setText(f"{count} evidence(s) available")
        self.evidence_group.setTitle(f"Captured Visual Evidence (Annotated Chart Screenshots) — {count} available")

    def remove_selected_evidence(self):
        """Allows removing unnecessary comparison screenshots before report generation."""
        selected_items = self.list_evidence.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Selection Required", "Please select an evidence screenshot from the list to remove.")
            return

        parent_win = self.window()
        comp = getattr(parent_win, 'tab_comparison', None)
        if not comp or not hasattr(comp, 'saved_annotated_pixmaps'):
            return

        selected_rows = [self.list_evidence.row(item) for item in selected_items]
        selected_rows.sort(reverse=True)
        for row in selected_rows:
            if 0 <= row < len(comp.saved_annotated_pixmaps):
                comp.saved_annotated_pixmaps.pop(row)

        self.refresh_evidence_list()
        self.update_summary_metrics()
        QMessageBox.information(self, "Removed", "Selected evidence screenshot(s) removed successfully.")

    def preview_selected_evidence(self, item=None):
        """Opens a high-resolution preview dialog of the selected annotated screenshot."""
        if item is None or isinstance(item, bool):
            selected_items = self.list_evidence.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Selection Required", "Please select an evidence screenshot to preview.")
                return
            item = selected_items[0]

        row = self.list_evidence.row(item)
        parent_win = self.window()
        comp = getattr(parent_win, 'tab_comparison', None)
        if not comp or not hasattr(comp, 'saved_annotated_pixmaps'):
            return
        if row < 0 or row >= len(comp.saved_annotated_pixmaps):
            return

        pix = comp.saved_annotated_pixmaps[row]
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Evidence #{row + 1} Preview ({pix.width()} × {pix.height()} px)")
        dialog.resize(850, 650)
        d_layout = QVBoxLayout(dialog)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        lbl_img = QLabel()
        lbl_img.setAlignment(Qt.AlignCenter)
        lbl_img.setPixmap(pix)
        scroll.setWidget(lbl_img)
        d_layout.addWidget(scroll)

        btn_close = QPushButton("Close")
        btn_close.clicked.connect(dialog.accept)
        d_layout.addWidget(btn_close)
        dialog.exec()

    def auto_add_checked_chart(self, file_path: str):
        """Automatically adds an updated chart to the checked charts list without duplicates."""
        if not file_path:
            return
        clean_name = file_path.replace('\\', '/').split('/')[-1]
        existing_names = [c.replace('\\', '/').split('/')[-1] for c in self.checked_charts_list]
        if clean_name not in existing_names:
            self.checked_charts_list.append(file_path)
            self.list_checked_charts.addItem(clean_name)
            self.update_summary_metrics()

    def showEvent(self, event):
        super().showEvent(event)
        parent_win = self.window()
        comp = getattr(parent_win, 'tab_comparison', None)
        if comp and getattr(comp, 'path_updated', None):
            self.auto_add_checked_chart(comp.path_updated)
        self.refresh_evidence_list()
        self.update_summary_metrics()

    def update_summary_metrics(self):
        parent_win = self.window()
        errors_list = []
        annotated_count = 0

        if hasattr(parent_win, 'tab_errors') and parent_win.tab_errors:
            errors_list = parent_win.tab_errors.errors_list

        if hasattr(parent_win, 'tab_comparison') and parent_win.tab_comparison:
            comp = parent_win.tab_comparison
            annotated_count = len(comp.saved_annotated_pixmaps)

        total_errors = sum(1 for e in errors_list if not e.id.startswith("NT-"))
        total_notes = sum(1 for e in errors_list if e.id.startswith("NT-"))
        critical = sum(1 for e in errors_list if e.severity == "Critical")
        major = sum(1 for e in errors_list if e.severity == "Major")
        minor = sum(1 for e in errors_list if e.severity == "Minor")
        obs = sum(1 for e in errors_list if e.severity == "Observation")
        checked_count = len(self.checked_charts_list)

        summary_str = (
            f"Active Review Session Details:\n"
            f"----------------------------------------\n"
            f"• Total Checked Charts Added: {checked_count}\n\n"
            f"Validation Summary Metrics:\n"
            f"----------------------------------------\n"
            f"• Total Errors: {total_errors}\n"
            f"• Total Notes: {total_notes}\n"
            f"• Critical Errors: {critical}\n"
            f"• Major Errors: {major}\n"
            f"• Minor Errors: {minor}\n"
            f"• Observations: {obs}\n"
            f"• Number of Saved Annotations: {annotated_count}"
        )
        self.summary_text.setPlainText(summary_str)

        if total_errors > 0 or total_notes > 0 or annotated_count > 0 or checked_count > 0:
            self.btn_generate.setEnabled(True)

    def open_calendar_dialog(self):
        curr_text = self.txt_validation_date.text().strip()
        dialog = CalendarDialog(curr_text, self)
        if dialog.exec() == QDialog.Accepted:
            selected_date = dialog.get_selected_date()
            self.txt_validation_date.setText(selected_date)

    def generate_report(self):
        parent_win = self.window()
        inspector_name = self.txt_inspector_name.text().strip()
        if not inspector_name:
            QMessageBox.warning(self, "Input Required", "Please enter the Name and Surname of the Quality Controller before generating the report.")
            self.txt_inspector_name.setFocus()
            return

        validation_date = self.txt_validation_date.text().strip() or datetime.now().strftime("%d-%m-%Y")
        log_sheets = self.txt_log_sheets.text().strip() or "N/A"
        
        primary_chart = "N/A"
        if hasattr(parent_win, 'tab_comparison') and parent_win.tab_comparison.path_updated:
            primary_chart = parent_win.tab_comparison.path_updated.split('/')[-1].split('\\')[-1]

        # Implement filename logic: LogSheetNumber_NameSurname.pdf
        clean_log = re.sub(r'[\\/*?:"<>|,\s]+', '_', log_sheets).strip('_') if log_sheets and log_sheets != "N/A" else "LogSheet"
        clean_name = "".join(re.sub(r'[\\/*?:"<>|]', '', inspector_name).split()) if inspector_name else "Inspector"
        suggested_filename = f"{clean_log}_{clean_name}.pdf"

        filename, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", suggested_filename, "PDF Files (*.pdf)")
        if filename:
            comp = parent_win.tab_comparison
            err_tab = parent_win.tab_errors
            
            report_info = {
                "chart_a": primary_chart,
                "date": validation_date,
                "reviewer": inspector_name,
                "log_sheets": log_sheets,
                "checked_charts": [c.split('/')[-1].split('\\')[-1] for c in self.checked_charts_list]
            }
            
            evidence_pixmaps = comp.saved_annotated_pixmaps if comp else []
            
            success, err = ReportGenerator.generate_pdf_report(filename, report_info, err_tab.errors_list, evidence_pixmaps)
            if success:
                folder_path = os.path.dirname(os.path.abspath(filename))
                folder_url = QUrl.fromLocalFile(folder_path).toString()

                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("Success")
                msg_box.setIcon(QMessageBox.Information)
                msg_box.setTextFormat(Qt.RichText)
                msg_box.setText(f'Validation report successfully generated:<br><br><a href="{folder_url}" style="color: #0284C7; font-weight: bold; text-decoration: underline;">{folder_path}</a>')
                for lbl in msg_box.findChildren(QLabel):
                    lbl.setOpenExternalLinks(True)
                btn_open = msg_box.addButton("Open Folder", QMessageBox.ActionRole)
                msg_box.addButton(QMessageBox.Ok)
                msg_box.exec()
                if msg_box.clickedButton() == btn_open:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(folder_path))
            else:
                QMessageBox.critical(self, "Error", f"Failed to generate report: {err}")
