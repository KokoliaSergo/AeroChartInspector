from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QInputDialog
)
from PySide6.QtCore import Qt, Signal
from app.errors.error_model import ErrorItem
from app.gui.dialogs import AddErrorDialog, SEVERITY_TOOLTIP

class ErrorsTab(QWidget):
    error_added = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.errors_list = []
        self._highest_id_num = 0
        self._highest_note_num = 0
        self.init_ui()

    def get_next_error_id(self) -> str:
        existing_ids = {e.id for e in self.errors_list}
        max_existing = 0
        for e in self.errors_list:
            if e.id.startswith("ERR-"):
                try:
                    num = int(e.id.split("-")[1])
                    if num > max_existing:
                        max_existing = num
                except (ValueError, IndexError):
                    pass
        candidate = max(self._highest_id_num, max_existing) + 1
        while f"ERR-{candidate:03d}" in existing_ids:
            candidate += 1
        self._highest_id_num = candidate
        return f"ERR-{candidate:03d}"

    def get_next_note_id(self) -> str:
        """Sequential ID generator for chart notes NT-001, NT-002, etc."""
        existing_ids = {e.id for e in self.errors_list}
        max_existing = 0
        for e in self.errors_list:
            if e.id.startswith("NT-"):
                try:
                    num = int(e.id.split("-")[1])
                    if num > max_existing:
                        max_existing = num
                except (ValueError, IndexError):
                    pass
        candidate = max(self._highest_note_num, max_existing) + 1
        while f"NT-{candidate:03d}" in existing_ids:
            candidate += 1
        self._highest_note_num = candidate
        return f"NT-{candidate:03d}"

    def init_ui(self):
        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        top_layout.addWidget(QLabel("<b>Recorded Aviation Errors / Discrepancies Log</b>"))
        
        self.btn_sev_guide = QPushButton("ⓘ Severity Guide")
        self.btn_sev_guide.setStyleSheet("background-color: #E0F2FE; color: #0284C7; border: 1px solid #BAE6FD; border-radius: 4px; padding: 5px 12px; font-weight: bold; font-size: 13px;")
        self.btn_sev_guide.setToolTip(SEVERITY_TOOLTIP)
        top_layout.addWidget(self.btn_sev_guide)
        
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
        header_sev = self.table.horizontalHeaderItem(2)
        if header_sev:
            header_sev.setToolTip(SEVERITY_TOOLTIP)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)

    def open_add_error_dialog(self):
        parent_win = self.window()
        default_chart = ""
        if hasattr(parent_win, 'tab_comparison') and parent_win.tab_comparison.path_updated:
            default_chart = parent_win.tab_comparison.path_updated.split('/')[-1].split('\\')[-1]

        error_id_str = self.get_next_error_id()
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

                # Requirement 3: When registering new error in Errors tab, appear on the chart in Chart Comparison tab (upper left corner)
                tab_comparison = getattr(parent_win, 'tab_comparison', None)
                if tab_comparison:
                    tab_comparison.add_error_marker_from_log(data)

    def open_edit_error_dialog(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Required", "Please select an error row from the table to edit.")
            return

        row_idx = selected_rows[0].row()
        id_item = self.table.item(row_idx, 0)
        if not id_item:
            return
        error_id = id_item.text()
        error_item = next((e for e in self.errors_list if e.id == error_id), None)
        if not error_item:
            return

        # If editing a Chart Note (NT-xxx)
        if error_id.startswith("NT-"):
            from app.gui.comparison_tab import EditNoteDialog
            dialog = EditNoteDialog(error_id, error_item.description, self)
            if dialog.exec():
                new_desc = dialog.get_text()
                if new_desc:
                    error_item.description = new_desc
                    self.populate_table()
                    parent_win = self.window()
                    comp = getattr(parent_win, 'tab_comparison', None)
                    if comp and hasattr(comp, 'chart_display'):
                        for n in comp.chart_display.notes:
                            if n.get("id") == error_id:
                                n["text"] = new_desc
                                break
                        comp.chart_display.update()
                    QMessageBox.information(self, "Success", f"Note {error_id} has been updated.")
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
                
                # Sync with ComparisonTab error markers if present
                comp = getattr(parent_win, 'tab_comparison', None)
                if comp and hasattr(comp, 'chart_display'):
                    for m in comp.chart_display.error_markers:
                        if m.get("id") == error_id:
                            m["type"] = data["type"]
                            m["description"] = data["description"]
                            m["severity"] = data["severity"]
                            m["chart"] = data["chart"]
                            m["comments"] = data["comments"]
                            break
                    comp.chart_display.update()
                    
                QMessageBox.information(self, "Success", f"Error {error_id} has been updated.")

    def delete_selected_error(self, prompt_confirmation: bool = True):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Selection Required", "Please select an item from the table to delete.")
            return

        row_idx = selected_rows[0].row()
        id_item = self.table.item(row_idx, 0)
        if not id_item:
            return
        error_id = id_item.text()
        target_item = next((e for e in self.errors_list if e.id == error_id), None)
        if not target_item:
            return

        item_label = "note" if error_id.startswith("NT-") else "error"
        if prompt_confirmation:
            confirm = QMessageBox.question(
                self, "Confirm Deletion", 
                f"Are you sure you want to delete {item_label} {error_id}?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return

        self.errors_list = [e for e in self.errors_list if e.id != error_id]
        self.populate_table()
        if not self.errors_list:
            self.btn_edit.setEnabled(False)
            self.btn_delete.setEnabled(False)

        # Sync with ComparisonTab (error markers and notes)
        parent_win = self.window()
        comp = getattr(parent_win, 'tab_comparison', None)
        if comp and hasattr(comp, 'chart_display'):
            if error_id.startswith("NT-"):
                comp.chart_display.notes = [
                    n for n in comp.chart_display.notes if n.get("id") != error_id
                ]
                if comp.chart_display.selected_note and comp.chart_display.selected_note.get("id") == error_id:
                    comp.chart_display.selected_note = None
                if hasattr(comp, 'btn_remove_note'):
                    comp.btn_remove_note.setEnabled(len(comp.chart_display.notes) > 0)
                    comp.btn_remove_note.setText("Remove Note")
            else:
                comp.chart_display.error_markers = [
                    m for m in comp.chart_display.error_markers if m.get("id") != error_id
                ]
                if getattr(comp.chart_display, 'selected_error', None) and comp.chart_display.selected_error.get("id") == error_id:
                    comp.chart_display.selected_error = None
            comp.chart_display.update()

        tab_report = getattr(parent_win, 'tab_report', None)
        if tab_report:
            tab_report.update_summary_metrics()

        if prompt_confirmation:
            QMessageBox.information(self, "Success", f"{item_label.capitalize()} {error_id} has been removed.")

    def populate_table(self):
        self.table.setSortingEnabled(False)
        self.table.setRowCount(len(self.errors_list))
        for row, err in enumerate(self.errors_list):
            self.table.setItem(row, 0, QTableWidgetItem(err.id))
            self.table.setItem(row, 1, QTableWidgetItem(err.type))
            item_sev = QTableWidgetItem(err.severity)
            item_sev.setToolTip(SEVERITY_TOOLTIP)
            self.table.setItem(row, 2, item_sev)
            self.table.setItem(row, 3, QTableWidgetItem(err.chart))
            self.table.setItem(row, 4, QTableWidgetItem(err.description))
        self.table.setSortingEnabled(True)