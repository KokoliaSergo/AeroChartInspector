from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QComboBox, QTextEdit, QFormLayout, QDialogButtonBox
)
from PySide6.QtCore import Qt
from app.errors.error_model import ERROR_TYPES, SEVERITY_LEVELS

SEVERITY_TOOLTIP = (
    "<b>Severity Classification Guidelines (Aviation QC Standards):</b><br><br>"
    "• <span style='color: #EF4444; font-weight: bold;'>Critical:</span> Safety-critical discrepancy "
    "directly affecting flight safety, terrain/obstacle clearance, or navigation integrity "
    "(e.g., incorrect minimum safe altitudes, wrong runway coordinates, wrong frequency or bearings, "
    "missing obstacles). <i>Must be corrected immediately prior to publication.</i><br><br>"
    "• <span style='color: #D97706; font-weight: bold;'>Major:</span> Operational discrepancy "
    "affecting procedure navigation, route execution, or flight efficiency without immediate collision hazard "
    "(e.g., misspelled waypoint/fix, misleading symbology, erroneous procedure turn profile).<br><br>"
    "• <span style='color: #0284C7; font-weight: bold;'>Minor:</span> Non-safety discrepancy with negligible "
    "operational impact (e.g., cosmetic drafting inconsistencies, minor label overlapping, marginal typo).<br><br>"
    "• <span style='color: #475569; font-weight: bold;'>Observation:</span> Informational remark, drafting note, "
    "or quality recommendation for future chart cycles."
)

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
        form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setVerticalSpacing(10)
        form_layout.setHorizontalSpacing(14)

        self.lbl_id = QLabel(f"<b>{self.error_id_str}</b>")
        self.lbl_id.setFixedHeight(28)
        self.lbl_id.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.lbl_id.setStyleSheet("color: #0284C7; font-size: 14px; font-weight: bold;")
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
        suggestions.extend(["Old chart", "Both"])
        
        seen = set()
        unique_suggestions = [x for x in suggestions if not (x in seen or seen.add(x))]
        self.combo_chart.addItems(unique_suggestions)
        
        if self.default_chart_name and not self.existing_data:
            self.combo_chart.setCurrentText(self.default_chart_name)

        form_layout.addRow("Affected chart:", self.combo_chart)

        self.lbl_severity = QLabel("Severity: <span style='color: #0284C7; font-size: 16px; font-weight: bold;'>ⓘ</span>")
        self.lbl_severity.setToolTip(SEVERITY_TOOLTIP)
        self.lbl_severity.setCursor(Qt.WhatsThisCursor)
        self.lbl_severity.setFixedHeight(28)
        self.lbl_severity.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        self.combo_severity = QComboBox()
        self.combo_severity.addItems(SEVERITY_LEVELS)
        self.combo_severity.setCurrentText("Major")
        self.combo_severity.setToolTip(SEVERITY_TOOLTIP)
        
        sev_tooltips = {
            "Critical": "Critical: Safety-critical discrepancy directly impacting flight safety, terrain/obstacle clearance, or navigation integrity. Must be resolved prior to publication.",
            "Major": "Major: Operational discrepancy affecting flight efficiency or procedure navigation without immediate CFIT/collision hazard.",
            "Minor": "Minor: Non-safety discrepancy with negligible operational impact (e.g., cosmetic drafting errors, minor typographical inconsistencies).",
            "Observation": "Observation: Informational comment, drafting note, or quality recommendation for future chart cycles."
        }
        for i, s in enumerate(SEVERITY_LEVELS):
            self.combo_severity.setItemData(i, sev_tooltips.get(s, ""), Qt.ToolTipRole)
            
        form_layout.addRow(self.lbl_severity, self.combo_severity)

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
        layout.addStretch()

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
            "chart": self.combo_chart.currentText().strip() or "Old chart",
            "severity": self.combo_severity.currentText(),
            "comments": self.txt_comments.toPlainText().strip()
        }
        self.accept()