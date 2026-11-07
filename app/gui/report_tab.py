from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, 
    QFileDialog, QMessageBox, QLineEdit, QFormLayout, QGroupBox,
    QDialog, QCalendarWidget, QHBoxLayout, QListWidget, QListWidgetItem
)
from PySide6.QtCore import QDate
from app.reports.report_generator import ReportGenerator

class CalendarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Validation Date")
        self.resize(320, 280)
        
        layout = QVBoxLayout(self)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setMinimumDate(QDate(2025, 1, 1))
        self.calendar.setMaximumDate(QDate(2035, 12, 31))
        
        layout.addWidget(self.calendar)
        
        btn_layout = QHBoxLayout()
        btn_select = QPushButton("Select")
        btn_select.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold;")
        btn_select.clicked.connect(self.accept)
        
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(btn_select)
        btn_layout.addWidget(btn_cancel)
        layout.addLayout(btn_layout)

    def get_selected_date(self) -> str:
        return self.calendar.selectedDate().toString("yyyy-MM-dd")


class ReportTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.checked_charts_list = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        layout.addWidget(QLabel("<b>AeroChart Inspector - Review Summary & PDF Report</b>"))
        
        qc_group = QGroupBox("Review & Log Metadata")
        qc_layout = QFormLayout()
        
        self.txt_inspector_name = QLineEdit()
        self.txt_inspector_name.setPlaceholderText("Enter Name and Surname (e.g., John Doe)")
        qc_layout.addRow("Name and Surname:", self.txt_inspector_name)

        date_layout = QHBoxLayout()
        self.txt_validation_date = QLineEdit()
        self.txt_validation_date.setText(datetime.now().strftime("%Y-%m-%d"))
        
        btn_calendar = QPushButton("Select Date...")
        btn_calendar.clicked.connect(self.open_calendar_dialog)
        
        date_layout.addWidget(self.txt_validation_date)
        date_layout.addWidget(btn_calendar)
        qc_layout.addRow("Validation Date:", date_layout)

        self.txt_log_sheets = QLineEdit()
        self.txt_log_sheets.setPlaceholderText("Enter Log Sheet numbers (e.g., LS-2026-01, LS-2026-02)")
        qc_layout.addRow("Log Sheet Number(s):", self.txt_log_sheets)

        qc_group.setLayout(qc_layout)
        layout.addWidget(qc_group)

        # --- List of Checked Charts Box ---
        charts_group = QGroupBox("List of Checked Charts")
        charts_layout = QVBoxLayout()
        
        self.list_checked_charts = QListWidget()
        charts_layout.addWidget(self.list_checked_charts)
        
        charts_btn_layout = QHBoxLayout()
        btn_add_charts = QPushButton("Add Chart(s)...")
        btn_add_charts.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold;")
        btn_add_charts.clicked.connect(self.add_checked_charts)
        
        btn_remove_chart = QPushButton("Remove Selected")
        btn_remove_chart.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold;")
        btn_remove_chart.clicked.connect(self.remove_checked_chart)
        
        charts_btn_layout.addWidget(btn_add_charts)
        charts_btn_layout.addWidget(btn_remove_chart)
        charts_btn_layout.addStretch()
        charts_layout.addLayout(charts_btn_layout)
        
        charts_group.setLayout(charts_layout)
        layout.addWidget(charts_group)

        # Summary Display Group
        summary_group = QGroupBox("Validation Review Summary")
        summary_layout = QVBoxLayout()
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.update_summary_metrics()
        summary_layout.addWidget(self.summary_text)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        self.btn_generate = QPushButton("Generate PDF Report")
        self.btn_generate.setEnabled(False)
        self.btn_generate.clicked.connect(self.generate_report)
        layout.addWidget(self.btn_generate)

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

    def showEvent(self, event):
        super().showEvent(event)
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

        total_errors = len(errors_list)
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
            f"• Critical Errors: {critical}\n"
            f"• Major Errors: {major}\n"
            f"• Minor Errors: {minor}\n"
            f"• Observations: {obs}\n"
            f"• Number of Saved Annotations: {annotated_count}"
        )
        self.summary_text.setPlainText(summary_str)

        if total_errors > 0 or annotated_count > 0 or checked_count > 0:
            self.btn_generate.setEnabled(True)

    def open_calendar_dialog(self):
        dialog = CalendarDialog(self)
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

        validation_date = self.txt_validation_date.text().strip() or datetime.now().strftime("%Y-%m-%d")
        log_sheets = self.txt_log_sheets.text().strip() or "N/A"
        
        primary_chart = "N/A"
        if hasattr(parent_win, 'tab_comparison') and parent_win.tab_comparison.path_updated:
            primary_chart = parent_win.tab_comparison.path_updated.split('/')[-1].split('\\')[-1]

        filename, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "Aeronautical_Chart_Validation_Report.pdf", "PDF Files (*.pdf)")
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
                QMessageBox.information(self, "Success", f"Professional validation report successfully generated for {inspector_name}:\n{filename}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to generate report: {err}")