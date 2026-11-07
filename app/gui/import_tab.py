from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QFileDialog, QMessageBox, QComboBox, QGroupBox, QGridLayout
)
from PySide6.QtCore import Qt, Signal
from app.pdf.pdf_loader import PDFLoader

class ImportTab(QWidget):
    mapping_updated = Signal()
    mapping_selected = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.updated_charts = []
        self.old_charts = []
        self.chart_mapping = {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        title_label = QLabel("<b>AeroChart Inspector - Batch Import & Chart Mapping</b>")
        main_layout.addWidget(title_label)

        grid_layout = QGridLayout()

        # Column 1: Updated Charts
        group_updated = QGroupBox("Updated Charts")
        vbox_up = QVBoxLayout()
        self.list_updated = QListWidget()
        btn_upload_up = QPushButton("Upload Updated PDFs")
        btn_upload_up.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold;")
        btn_upload_up.clicked.connect(self.upload_updated_charts)
        
        vbox_up.addWidget(self.list_updated)
        vbox_up.addWidget(btn_upload_up)
        group_updated.setLayout(vbox_up)
        grid_layout.addWidget(group_updated, 0, 0)

        # Column 2: Old Charts
        group_old = QGroupBox("Old Charts")
        vbox_old = QVBoxLayout()
        self.list_old = QListWidget()
        btn_upload_old = QPushButton("Upload Old PDFs")
        btn_upload_old.setStyleSheet("background-color: #64748B; color: white; font-weight: bold;")
        btn_upload_old.clicked.connect(self.upload_old_charts)
        
        vbox_old.addWidget(self.list_old)
        vbox_old.addWidget(btn_upload_old)
        group_old.setLayout(vbox_old)
        grid_layout.addWidget(group_old, 0, 1)

        main_layout.addLayout(grid_layout)

        # Mapping Section
        mapping_group = QGroupBox("Chart Mapping Configuration")
        mapping_layout = QHBoxLayout()

        self.combo_map_updated = QComboBox()
        self.combo_map_old = QComboBox()
        btn_link = QPushButton("Link Selected Pair")
        btn_link.setStyleSheet("background-color: #10B981; color: white; font-weight: bold;")
        btn_link.clicked.connect(self.link_charts)

        mapping_layout.addWidget(QLabel("Updated:"))
        mapping_layout.addWidget(self.combo_map_updated, 2)
        mapping_layout.addWidget(QLabel("Mapped to Old:"))
        mapping_layout.addWidget(self.combo_map_old, 2)
        mapping_layout.addWidget(btn_link, 1)

        mapping_group.setLayout(mapping_layout)
        main_layout.addWidget(mapping_group)

        # Active Mappings List with Edit & Remove controls
        mapping_display_group = QGroupBox("Active Mappings List (Double-click any item to start comparison)")
        vbox_map_disp = QVBoxLayout()
        
        self.list_mappings = QListWidget()
        self.list_mappings.itemDoubleClicked.connect(self.on_mapping_item_double_clicked)
        vbox_map_disp.addWidget(self.list_mappings)

        map_btn_layout = QHBoxLayout()
        btn_edit_map = QPushButton("Edit Selected Mapping")
        btn_edit_map.setStyleSheet("background-color: #D97706; color: white; font-weight: bold;")
        btn_edit_map.clicked.connect(self.edit_selected_mapping)

        btn_remove_map = QPushButton("Remove Selected Mapping")
        btn_remove_map.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold;")
        btn_remove_map.clicked.connect(self.remove_selected_mapping)

        map_btn_layout.addWidget(btn_edit_map)
        map_btn_layout.addWidget(btn_remove_map)
        map_btn_layout.addStretch()
        vbox_map_disp.addLayout(map_btn_layout)

        mapping_display_group.setLayout(vbox_map_disp)
        main_layout.addWidget(mapping_display_group)

    def upload_updated_charts(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Updated PDFs", "", "PDF Files (*.pdf)")
        if files:
            for f in files:
                success, _, _ = PDFLoader.validate_and_load(f)
                if success and f not in self.updated_charts:
                    self.updated_charts.append(f)
                    self.list_updated.addItem(f.split('/')[-1].split('\\')[-1])
            self.update_combos()

    def upload_old_charts(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Old PDFs", "", "PDF Files (*.pdf)")
        if files:
            for f in files:
                success, _, _ = PDFLoader.validate_and_load(f)
                if success and f not in self.old_charts:
                    self.old_charts.append(f)
                    self.list_old.addItem(f.split('/')[-1].split('\\')[-1])
            self.update_combos()

    def update_combos(self):
        self.combo_map_updated.clear()
        for f in self.updated_charts:
            self.combo_map_updated.addItem(f.split('/')[-1].split('\\')[-1], f)

        self.combo_map_old.clear()
        for f in self.old_charts:
            self.combo_map_old.addItem(f.split('/')[-1].split('\\')[-1], f)

    def link_charts(self):
        if self.combo_map_updated.count() == 0 or self.combo_map_old.count() == 0:
            QMessageBox.warning(self, "Warning", "Please upload charts in both columns before mapping.")
            return

        up_path = self.combo_map_updated.currentData()
        old_path = self.combo_map_old.currentData()

        if up_path and old_path:
            self.chart_mapping[up_path] = old_path
            disp_text = f"{up_path.split('/')[-1].split('\\')[-1]}  --->  {old_path.split('/')[-1].split('\\')[-1]}"
            
            item = None
            for i in range(self.list_mappings.count()):
                it = self.list_mappings.item(i)
                if it.data(Qt.UserRole) == up_path:
                    item = it
                    break
            
            if item:
                item.setText(disp_text)
                item.setData(Qt.UserRole + 1, old_path)
            else:
                newItem = QListWidgetItem(disp_text)
                newItem.setData(Qt.UserRole, up_path)
                newItem.setData(Qt.UserRole + 1, old_path)
                self.list_mappings.addItem(newItem)

            self.mapping_updated.emit()
            QMessageBox.information(self, "Success", "Charts successfully mapped!")

    def edit_selected_mapping(self):
        items = self.list_mappings.selectedItems()
        if not items:
            QMessageBox.warning(self, "Selection Required", "Please select a mapping pair from the list to edit.")
            return
        item = items[0]
        up_path = item.data(Qt.UserRole)
        
        # Set combo boxes to match the selected item
        for i in range(self.combo_map_updated.count()):
            if self.combo_map_updated.itemData(i) == up_path:
                self.combo_map_updated.setCurrentIndex(i)
                break
        QMessageBox.information(self, "Edit Mode", "Select the desired Old chart above and click 'Link Selected Pair' to update this mapping.")

    def remove_selected_mapping(self):
        items = self.list_mappings.selectedItems()
        if not items:
            QMessageBox.warning(self, "Selection Required", "Please select a mapping pair from the list to remove.")
            return
        item = items[0]
        up_path = item.data(Qt.UserRole)
        
        if up_path in self.chart_mapping:
            del self.chart_mapping[up_path]
            
        row = self.list_mappings.row(item)
        self.list_mappings.takeItem(row)
        QMessageBox.information(self, "Removed", "Mapping entry has been removed.")

    def on_mapping_item_double_clicked(self, item: QListWidgetItem):
        up_path = item.data(Qt.UserRole)
        old_path = item.data(Qt.UserRole + 1)
        if up_path and old_path:
            self.mapping_selected.emit(up_path, old_path)

    def get_old_chart_for(self, updated_path: str) -> str:
        return self.chart_mapping.get(updated_path, "")