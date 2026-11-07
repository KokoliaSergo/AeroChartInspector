from PySide6.QtWidgets import QMainWindow, QTabWidget, QLabel, QStatusBar, QMessageBox
from PySide6.QtCore import Qt
from app.gui.import_tab import ImportTab
from app.gui.comparison_tab import ComparisonTab
from app.gui.errors_tab import ErrorsTab
from app.gui.report_tab import ReportTab
from app.pdf.pdf_loader import PDFLoader
from app.config.settings import APP_NAME, VERSION

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.resize(1200, 800)
        
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        # Developer attribution in the top-right corner
        self.dev_label = QLabel("<i>Designed and developed by Sergo Kokolia</i>")
        self.dev_label.setStyleSheet("color: #0284C7; font-style: italic; padding-right: 12px; font-size: 12px; background: transparent;")
        self.tabs.setCornerWidget(self.dev_label, Qt.TopRightCorner)
        
        self.tab_import = ImportTab()
        self.tab_comparison = ComparisonTab()
        self.tab_errors = ErrorsTab()
        self.tab_report = ReportTab()
        
        self.tabs.addTab(self.tab_import, "Import")
        self.tabs.addTab(self.tab_comparison, "Chart Comparison")
        self.tabs.addTab(self.tab_errors, "Errors")
        self.tabs.addTab(self.tab_report, "Report")
        
        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Connect signals
        self.tab_comparison.charts_loaded.connect(self.on_charts_loaded)
        self.tab_import.mapping_selected.connect(self.load_mapped_charts_and_switch)

    def load_mapped_charts_and_switch(self, up_path: str, old_path: str):
        success_up, doc_up, err_up = PDFLoader.validate_and_load(up_path)
        success_old, doc_old, err_old = PDFLoader.validate_and_load(old_path)
        
        if not success_up or not success_old:
            QMessageBox.critical(self, "Error", f"Failed to load mapped PDFs:\n{err_up or err_old}")
            return
            
        comp = self.tab_comparison
        comp.doc_updated = doc_up
        comp.path_updated = up_path
        comp.label_updated.setText(f"Updated chart: [{up_path.split('/')[-1].split('\\')[-1]}]")
        
        comp.doc_old = doc_old
        comp.path_old = old_path
        comp.label_old.setText(f"Old chart: [{old_path.split('/')[-1].split('\\')[-1]}]")
        
        comp.check_ready()
        comp.load_charts()
        
        # Switch to the Chart Comparison tab (Index 1)
        self.tabs.setCurrentIndex(1)

    def on_charts_loaded(self):
        self.tab_errors.btn_add.setEnabled(True)
        self.tab_report.btn_generate.setEnabled(True)
        self.tab_report.summary_text.setPlainText(
            f"Review Session Active\n\n"
            f"Updated chart: {self.tab_comparison.path_updated}\n"
            f"Old chart: {self.tab_comparison.path_old}\n"
            f"Total Errors Recorded: 0"
        )