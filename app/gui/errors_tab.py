from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from app.errors.error_model import ErrorItem
from app.gui.dialogs import AddErrorDialog

class ErrorsTab(QWidget):
    error_added = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.errors_list = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("<b>Recorded Aviation Errors / Discrepancies Log</b>"))
        top_layout.addStretch()

        self.btn_add = QPushButton("Add Error")
        self.btn_add.setEnabled(False)
        self.btn_add.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold;")
        self.btn_add.clicked.connect(self.open_add_error_dialog)
        top_layout.addWidget(self.btn_add)

        self.btn_edit = QPushButton("Edit Selected Error")
        self.btn_edit.setEnabled(False)
        self.btn_edit.setStyleSheet("background-color: #D97706; color: white; font-weight: bold;")
        self.btn_edit.clicked.connect(self.open_edit_error_dialog)
        top_layout.addWidget(self.btn_edit)

        self.btn_delete = QPushButton("Delete Selected Error")
        self.btn_delete.setEnabled(False)
        self.btn_delete.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold;")
        self.btn_delete.clicked.connect(self.delete_selected_error)
        top_layout.addWidget(self.btn_delete)

        layout.addLayout(top_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Type", "Severity", "Chart", "Description"])
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)

    def open_add_error_dialog(self):
        parent_win = self.window()
        default_chart = ""
        if hasattr(parent_win, 'tab_comparison') and parent_win.tab_comparison.path_updated:
            default_chart = parent_win.tab_comparison.path_updated.split('/')[-1].split('\\')[-1]

        error_id_str = f"ERR-{len(self.errors_list) + 1:03d}"
        dialog = AddErrorDialog(error_id_str, None, default_chart, self)
        if dialog.exec():
            data = dialog.error_data
            if data:
                new_err = ErrorItem(
                    error_id=data["id"],
                    err_type=data["type"],
                    description=data["description"],
                    chart=data["chart"],
                    severity=data["severity"],
                    comments=data["comments"]
                )
                self.errors_list.append(new_err)
                self.populate_table()
                self.btn_edit.setEnabled(True)
                self.btn_delete.setEnabled(True)
                self.error_added.emit()

    def open_edit_error_dialog(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Required", "Please select an error row from the table to edit.")
            return

        row_idx = selected_rows[0].row()
        error_id = self.table.item(row_idx, 0).text()

        error_item = next((e for e in self.errors_list if e.id == error_id), None)
        if not error_item:
            return

        existing_data = {
            "type": error_item.type,
            "description": error_item.description,
            "chart": error_item.chart,
            "severity": error_item.severity,
            "comments": error_item.comments
        }

        parent_win = self.window()
        default_chart = ""
        if hasattr(parent_win, 'tab_comparison') and parent_win.tab_comparison.path_updated:
            default_chart = parent_win.tab_comparison.path_updated.split('/')[-1].split('\\')[-1]

        dialog = AddErrorDialog(error_id, existing_data, default_chart, self)
        if dialog.exec():
            data = dialog.error_data
            if data:
                error_item.type = data["type"]
                error_item.description = data["description"]
                error_item.chart = data["chart"]
                error_item.severity = data["severity"]
                error_item.comments = data["comments"]
                self.populate_table()
                QMessageBox.information(self, "Success", f"Error {error_id} has been updated.")

    def delete_selected_error(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Required", "Please select an error row from the table to delete.")
            return

        row_idx = selected_rows[0].row()
        error_id = self.table.item(row_idx, 0).text()

        confirm = QMessageBox.question(
            self, "Confirm Deletion", 
            f"Are you sure you want to delete error {error_id}?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            self.errors_list = [e for e in self.errors_list if e.id != error_id]
            self.populate_table()
            if not self.errors_list:
                self.btn_edit.setEnabled(False)
                self.btn_delete.setEnabled(False)
            QMessageBox.information(self, "Success", f"Error {error_id} has been removed.")

    def populate_table(self):
        self.table.setRowCount(len(self.errors_list))
        for row, err in enumerate(self.errors_list):
            self.table.setItem(row, 0, QTableWidgetItem(err.id))
            self.table.setItem(row, 1, QTableWidgetItem(err.type))
            self.table.setItem(row, 2, QTableWidgetItem(err.severity))
            self.table.setItem(row, 3, QTableWidgetItem(err.chart))
            self.table.setItem(row, 4, QTableWidgetItem(err.description))