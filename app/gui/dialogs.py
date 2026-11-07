from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QComboBox, QTextEdit, QFormLayout, QDialogButtonBox
)
from app.errors.error_model import ERROR_TYPES, SEVERITY_LEVELS

class AddErrorDialog(QDialog):
    def __init__(self, error_id_str, existing_data=None, default_chart_name="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Record New Error" if not existing_data else "Edit Error")
        self.resize(400, 360)
        self.error_data = None
        self.error_id_str = error_id_str
        self.existing_data = existing_data
        self.default_chart_name = default_chart_name
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()

        self.lbl_id = QLabel(f"<b>{self.error_id_str}</b>")
        form_layout.addRow("Error ID:", self.lbl_id)

        self.combo_type = QComboBox()
        self.combo_type.addItems(ERROR_TYPES)
        form_layout.addRow("Error Type:", self.combo_type)

        self.txt_desc = QTextEdit()
        self.txt_desc.setMaximumHeight(65)
        form_layout.addRow("Description:", self.txt_desc)

        self.combo_chart = QComboBox()
        self.combo_chart.setEditable(True)
        
        suggestions = []
        if self.default_chart_name:
            suggestions.append(self.default_chart_name)
        suggestions.extend(["Updated chart", "Old chart", "Both"])
        
        seen = set()
        unique_suggestions = [x for x in suggestions if not (x in seen or seen.add(x))]
        self.combo_chart.addItems(unique_suggestions)
        
        if self.default_chart_name and not self.existing_data:
            self.combo_chart.setCurrentText(self.default_chart_name)

        form_layout.addRow("Affected chart:", self.combo_chart)

        self.combo_severity = QComboBox()
        self.combo_severity.addItems(SEVERITY_LEVELS)
        self.combo_severity.setCurrentText("Major")
        form_layout.addRow("Severity:", self.combo_severity)

        self.txt_comments = QTextEdit()
        self.txt_comments.setMaximumHeight(50)
        form_layout.addRow("Comments:", self.txt_comments)

        if self.existing_data:
            self.combo_type.setCurrentText(self.existing_data.get("type", ERROR_TYPES[0]))
            self.txt_desc.setPlainText(self.existing_data.get("description", ""))
            self.combo_chart.setCurrentText(self.existing_data.get("chart", self.default_chart_name))
            self.combo_severity.setCurrentText(self.existing_data.get("severity", "Major"))
            self.txt_comments.setPlainText(self.existing_data.get("comments", ""))

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.on_save)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def on_save(self):
        if not self.txt_desc.toPlainText().strip():
            self.txt_desc.setPlaceholderText("Description is required!")
            return
            
        self.error_data = {
            "id": self.error_id_str,
            "type": self.combo_type.currentText(),
            "description": self.txt_desc.toPlainText().strip(),
            "chart": self.combo_chart.currentText().strip() or "Updated chart",
            "severity": self.combo_severity.currentText(),
            "comments": self.txt_comments.toPlainText().strip()
        }
        self.accept()