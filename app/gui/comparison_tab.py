from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFileDialog, QMessageBox, QScrollArea, QSlider, QComboBox
)
from PySide6.QtCore import Qt, QPoint, QPointF, Signal, QSize
from PySide6.QtGui import QPixmap, QPainter, QPen, QColor, QWheelEvent, QMouseEvent, QPaintEvent
from app.pdf.pdf_loader import PDFLoader
from app.pdf.pdf_renderer import PDFRenderer
from app.comparison.flicker import FlickerManager

class InteractiveChartWidget(QLabel):
    drawing_added = Signal()

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("background-color: #F1F5F9; border: 1px solid #CBD5E1; border-radius: 6px;")
        self.setMinimumSize(700, 700)
        self.setMouseTracking(True)
        
        self.pixmap_updated = None
        self.pixmap_old = None
        self.opacity_old = 0.5
        self.zoom_factor = 1.0
        self.active_view = "Both"
        
        self.offset_old = QPointF(0.0, 0.0)
        self.drag_mode_enabled = False
        
        self.drawing_mode = False
        self.strokes = [] 
        self.current_stroke = []
        
        self.dragging = False
        self.last_mouse_pos = QPoint()

    def set_charts(self, pix_updated, pix_old):
        self.pixmap_updated = pix_updated
        self.pixmap_old = pix_old
        self.offset_old = QPointF(0.0, 0.0)
        self.strokes.clear()
        self.update_widget_size()
        self.update()

    def clear(self):
        self.pixmap_updated = None
        self.pixmap_old = None
        self.offset_old = QPointF(0.0, 0.0)
        self.strokes.clear()
        self.zoom_factor = 1.0
        self.setMinimumSize(700, 700)
        self.resize(700, 700)
        self.update()

    def update_widget_size(self):
        if self.pixmap_updated:
            sz = self.pixmap_updated.size() * self.zoom_factor
            self.setMinimumSize(sz)
            self.resize(sz)

    def set_opacity(self, val: float):
        self.opacity_old = max(0.0, min(1.0, val))
        self.update()

    def set_zoom(self, zoom: float):
        new_zoom = max(0.25, min(5.0, zoom))
        if new_zoom == self.zoom_factor:
            return
        self.zoom_factor = new_zoom
        self.update_widget_size()
        self.update()

    def set_active_view(self, view: str):
        self.active_view = view
        self.update()

    def reset_alignment(self):
        self.offset_old = QPointF(0.0, 0.0)
        self.update()

    def clear_drawings(self):
        self.strokes.clear()
        self.update()

    def get_annotated_pixmap(self) -> QPixmap:
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.white)
        self.render(pixmap)
        return pixmap

    def screen_to_chart_coords(self, screen_pt: QPointF, base_x: float, base_y: float) -> QPointF:
        return QPointF((screen_pt.x() - base_x) / self.zoom_factor, (screen_pt.y() - base_y) / self.zoom_factor)

    def chart_to_screen_coords(self, chart_pt: QPointF, base_x: float, base_y: float) -> QPointF:
        return QPointF(chart_pt.x() * self.zoom_factor + base_x, chart_pt.y() * self.zoom_factor + base_y)

    def paintEvent(self, event: QPaintEvent):
        if not self.pixmap_updated:
            super().paintEvent(event)
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.Antialiasing, True)

        sz_up = self.pixmap_updated.size() * self.zoom_factor
        scaled_up = self.pixmap_updated.scaled(sz_up, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        widget_size = self.size()
        center_x = max(0, (widget_size.width() - scaled_up.width()) / 2)
        center_y = max(0, (widget_size.height() - scaled_up.height()) / 2)

        x_up = center_x
        y_up = center_y

        if self.pixmap_old:
            sz_old = self.pixmap_old.size() * self.zoom_factor
            scaled_old = self.pixmap_old.scaled(sz_old, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            x_old = center_x + (self.offset_old.x() * self.zoom_factor)
            y_old = center_y + (self.offset_old.y() * self.zoom_factor)
        else:
            scaled_old = None
            x_old, y_old = x_up, y_up

        if self.active_view == "Updated chart":
            painter.drawPixmap(int(x_up), int(y_up), scaled_up)
        elif self.active_view == "Old chart" and scaled_old:
            painter.drawPixmap(int(x_old), int(y_old), scaled_old)
        else:
            painter.drawPixmap(int(x_up), int(y_up), scaled_up)
            if scaled_old:
                painter.setOpacity(self.opacity_old)
                painter.drawPixmap(int(x_old), int(y_old), scaled_old)
                painter.setOpacity(1.0)

        pen = QPen(QColor(239, 68, 68), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        
        for stroke in self.strokes:
            screen_stroke = [self.chart_to_screen_coords(pt, x_up, y_up) for pt in stroke]
            for i in range(len(screen_stroke) - 1):
                painter.drawLine(screen_stroke[i], screen_stroke[i+1])
        
        if len(self.current_stroke) > 1:
            screen_current = [self.chart_to_screen_coords(pt, x_up, y_up) for pt in self.current_stroke]
            for i in range(len(screen_current) - 1):
                painter.drawLine(screen_current[i], screen_current[i+1])

        painter.end()

    def wheelEvent(self, event: QWheelEvent):
        angle = event.angleDelta().y()
        factor = 1.15 if angle > 0 else (1.0 / 1.15)
        self.set_zoom(self.zoom_factor * factor)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if self.drawing_mode:
                sz_up = self.pixmap_updated.size() * self.zoom_factor if self.pixmap_updated else 1
                widget_size = self.size()
                center_x = max(0, (widget_size.width() - sz_up.width()) / 2) if self.pixmap_updated else 0
                center_y = max(0, (widget_size.height() - sz_up.height()) / 2) if self.pixmap_updated else 0
                local_pt = self.screen_to_chart_coords(QPointF(event.pos()), center_x, center_y)
                self.current_stroke = [local_pt]
            elif self.drag_mode_enabled:
                self.dragging = True
                self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drawing_mode and (event.buttons() & Qt.LeftButton) and self.pixmap_updated:
            sz_up = self.pixmap_updated.size() * self.zoom_factor
            widget_size = self.size()
            center_x = max(0, (widget_size.width() - sz_up.width()) / 2)
            center_y = max(0, (widget_size.height() - sz_up.height()) / 2)
            local_pt = self.screen_to_chart_coords(QPointF(event.pos()), center_x, center_y)
            self.current_stroke.append(local_pt)
            self.update()
        elif self.dragging and self.drag_mode_enabled:
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()
            scaled_delta = QPointF(delta.x() / self.zoom_factor, delta.y() / self.zoom_factor)
            self.offset_old += scaled_delta
            self.update()

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if self.drawing_mode and self.current_stroke:
                self.strokes.append(list(self.current_stroke))
                self.current_stroke.clear()
                self.update()
                self.drawing_added.emit()
            self.dragging = False


class ComparisonTab(QWidget):
    charts_loaded = Signal()
    charts_cleared = Signal()

    def __init__(self):
        super().__init__()
        self.doc_updated = None
        self.doc_old = None
        self.path_updated = ""
        self.path_old = ""
        self.saved_annotated_pixmaps = []
        self.flicker_manager = FlickerManager(self)
        self.flicker_manager.state_changed.connect(self.on_flicker_state_changed)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        file_layout = QHBoxLayout()
        
        self.label_updated = QLabel("<b>Updated chart:</b> <span style='color: #0284C7;'>[No file selected]</span>")
        self.label_updated.setStyleSheet("background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 4px; padding: 6px; font-size: 13px;")
        btn_browse_updated = QPushButton("Browse...")
        btn_browse_updated.setMinimumWidth(85)
        btn_browse_updated.clicked.connect(self.browse_chart_updated)
        
        self.label_old = QLabel("<b>Old chart:</b> <span style='color: #475569;'>[No file selected]</span>")
        self.label_old.setStyleSheet("background-color: #FFFFFF; border: 1px solid #CBD5E1; border-radius: 4px; padding: 6px; font-size: 13px;")
        btn_browse_old = QPushButton("Browse...")
        btn_browse_old.setMinimumWidth(85)
        btn_browse_old.clicked.connect(self.browse_chart_old)

        self.btn_load = QPushButton("Load Charts")
        self.btn_load.setEnabled(False)
        self.btn_load.setStyleSheet("background-color: #10B981; color: white; font-weight: bold;")
        self.btn_load.clicked.connect(self.load_charts)

        self.btn_reset_session = QPushButton("Reset Session")
        self.btn_reset_session.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold;")
        self.btn_reset_session.clicked.connect(self.reset_session)

        file_layout.addWidget(self.label_updated, 2)
        file_layout.addWidget(btn_browse_updated)
        file_layout.addSpacing(10)
        file_layout.addWidget(self.label_old, 2)
        file_layout.addWidget(btn_browse_old)
        file_layout.addSpacing(10)
        file_layout.addWidget(self.btn_load)
        file_layout.addWidget(self.btn_reset_session)
        layout.addLayout(file_layout)

        toolbar_layout = QHBoxLayout()

        self.btn_toggle_drag = QPushButton("Drag Mode: OFF")
        self.btn_toggle_drag.setEnabled(False)
        self.btn_toggle_drag.setStyleSheet("background-color: #10B981; color: white; font-weight: bold;")
        self.btn_toggle_drag.clicked.connect(self.toggle_drag_mode)
        toolbar_layout.addWidget(self.btn_toggle_drag)

        self.btn_flicker = QPushButton("Start Flicker")
        self.btn_flicker.setEnabled(False)
        self.btn_flicker.clicked.connect(self.toggle_flicker)
        toolbar_layout.addWidget(self.btn_flicker)

        self.combo_interval = QComboBox()
        self.combo_interval.addItems(["0.2s", "0.5s", "1.0s", "2.0s", "3.0s"])
        self.combo_interval.setCurrentIndex(2)
        self.combo_interval.currentIndexChanged.connect(self.change_flicker_interval)
        toolbar_layout.addWidget(QLabel("Interval:"))
        toolbar_layout.addWidget(self.combo_interval)

        toolbar_layout.addSpacing(10)

        self.btn_show_updated = QPushButton("Show Updated")
        self.btn_show_updated.setEnabled(False)
        self.btn_show_updated.clicked.connect(lambda: self.set_view_mode("Updated chart"))

        self.btn_show_old = QPushButton("Show Old")
        self.btn_show_old.setEnabled(False)
        self.btn_show_old.clicked.connect(lambda: self.set_view_mode("Old chart"))

        toolbar_layout.addWidget(self.btn_show_updated)
        toolbar_layout.addWidget(self.btn_show_old)

        self.btn_reset_align = QPushButton("Reset Alignment")
        self.btn_reset_align.setEnabled(False)
        self.btn_reset_align.clicked.connect(self.reset_alignment)
        toolbar_layout.addWidget(self.btn_reset_align)

        self.btn_draw = QPushButton("Draw Highlight: OFF")
        self.btn_draw.setEnabled(False)
        self.btn_draw.clicked.connect(self.toggle_drawing_mode)
        toolbar_layout.addWidget(self.btn_draw)

        self.btn_clear_draw = QPushButton("Clear Drawings")
        self.btn_clear_draw.setEnabled(False)
        self.btn_clear_draw.clicked.connect(lambda: self.chart_display.clear_drawings())
        toolbar_layout.addWidget(self.btn_clear_draw)

        self.btn_save_annotated = QPushButton("Save Annotated Chart to Report")
        self.btn_save_annotated.setEnabled(False)
        self.btn_save_annotated.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold;")
        self.btn_save_annotated.clicked.connect(self.save_annotated_chart)
        toolbar_layout.addWidget(self.btn_save_annotated)

        toolbar_layout.addStretch()
        layout.addLayout(toolbar_layout)

        sub_toolbar = QHBoxLayout()
        sub_toolbar.addWidget(QLabel("Overlay Balance (Updated/Old):"))
        self.slider_opacity = QSlider(Qt.Horizontal)
        self.slider_opacity.setRange(0, 100)
        self.slider_opacity.setValue(50)
        self.slider_opacity.setEnabled(False)
        self.slider_opacity.valueChanged.connect(self.on_opacity_changed)
        sub_toolbar.addWidget(self.slider_opacity)

        sub_toolbar.addSpacing(20)
        self.label_zoom = QLabel("Zoom: 100%")
        btn_zoom_in = QPushButton("+")
        btn_zoom_in.setFixedWidth(30)
        btn_zoom_in.clicked.connect(self.zoom_in)
        btn_zoom_out = QPushButton("-")
        btn_zoom_out.setFixedWidth(30)
        btn_zoom_out.clicked.connect(self.zoom_out)
        btn_fit = QPushButton("Fit")
        btn_fit.clicked.connect(self.reset_zoom)

        sub_toolbar.addWidget(self.label_zoom)
        sub_toolbar.addWidget(btn_zoom_out)
        sub_toolbar.addWidget(btn_zoom_in)
        sub_toolbar.addWidget(btn_fit)
        layout.addLayout(sub_toolbar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.chart_display = InteractiveChartWidget()
        self.chart_display.drawing_added.connect(self.on_drawing_added)
        self.scroll_area.setWidget(self.chart_display)
        layout.addWidget(self.scroll_area)

    def on_drawing_added(self):
        self.btn_save_annotated.setEnabled(True)

    def save_annotated_chart(self):
        pixmap = self.chart_display.get_annotated_pixmap()
        if pixmap and not pixmap.isNull():
            self.saved_annotated_pixmaps.append(pixmap)
            QMessageBox.information(self, "Success", f"Annotated chart successfully saved to report evidence list! (Total saved: {len(self.saved_annotated_pixmaps)})")

    def browse_chart_updated(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Updated Chart", "", "PDF Files (*.pdf)")
        if filename:
            success, doc, err = PDFLoader.validate_and_load(filename)
            if not success:
                QMessageBox.critical(self, "Invalid PDF", err)
                return
            self.doc_updated = doc
            self.path_updated = filename
            self.label_updated.setText(f"<b>Updated chart:</b> <span style='color: #0284C7;'>[{filename.split('/')[-1].split('\\')[-1]}]</span>")
            
            parent_win = self.window()
            import_tab = getattr(parent_win, 'tab_import', None)
            if import_tab:
                mapped_old = import_tab.get_old_chart_for(filename)
                if mapped_old:
                    success_old, doc_old, _ = PDFLoader.validate_and_load(mapped_old)
                    if success_old:
                        self.doc_old = doc_old
                        self.path_old = mapped_old
                        self.label_old.setText(f"<b>Old chart:</b> <span style='color: #475569;'>[{mapped_old.split('/')[-1].split('\\')[-1]}] (Auto-mapped)</span>")

            self.check_ready()

    def browse_chart_old(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Old Chart", "", "PDF Files (*.pdf)")
        if filename:
            success, doc, err = PDFLoader.validate_and_load(filename)
            if not success:
                QMessageBox.critical(self, "Invalid PDF", err)
                return
            self.doc_old = doc
            self.path_old = filename
            self.label_old.setText(f"<b>Old chart:</b> <span style='color: #475569;'>[{filename.split('/')[-1].split('\\')[-1]}]</span>")
            self.check_ready()

    def check_ready(self):
        if self.doc_updated and self.doc_old:
            self.btn_load.setEnabled(True)

    def load_charts(self):
        if not self.doc_updated or not self.doc_old:
            return
        pix_up = PDFRenderer.render_page_to_pixmap(self.doc_updated[0], zoom=1.5)
        pix_old = PDFRenderer.render_page_to_pixmap(self.doc_old[0], zoom=1.5)
        self.chart_display.set_charts(pix_up, pix_old)
        self.slider_opacity.setEnabled(True)
        self.btn_show_updated.setEnabled(True)
        self.btn_show_old.setEnabled(True)
        self.btn_flicker.setEnabled(True)
        self.btn_reset_align.setEnabled(True)
        self.btn_toggle_drag.setEnabled(True)
        self.btn_draw.setEnabled(True)
        self.btn_clear_draw.setEnabled(True)
        
        self.charts_loaded.emit()
        QMessageBox.information(self, "Success", "Charts loaded successfully.")

    def reset_session(self):
        self.flicker_manager.pause()
        self.doc_updated = None
        self.doc_old = None
        self.path_updated = ""
        self.path_old = ""
        self.saved_annotated_pixmaps.clear()
        self.label_updated.setText("<b>Updated chart:</b> <span style='color: #0284C7;'>[No file selected]</span>")
        self.label_old.setText("<b>Old chart:</b> <span style='color: #475569;'>[No file selected]</span>")
        self.chart_display.clear()
        
        self.slider_opacity.setEnabled(False)
        self.btn_show_updated.setEnabled(False)
        self.btn_show_old.setEnabled(False)
        self.btn_flicker.setEnabled(False)
        self.btn_flicker.setText("Start Flicker")
        self.btn_reset_align.setEnabled(False)
        self.btn_toggle_drag.setEnabled(False)
        self.btn_toggle_drag.setText("Drag Mode: OFF")
        self.chart_display.drag_mode_enabled = False
        self.btn_draw.setEnabled(False)
        self.btn_draw.setText("Draw Highlight: OFF")
        self.chart_display.drawing_mode = False
        self.chart_display.setCursor(Qt.ArrowCursor)
        self.btn_clear_draw.setEnabled(False)
        self.btn_save_annotated.setEnabled(False)
        self.btn_load.setEnabled(False)
        
        self.charts_cleared.emit()
        QMessageBox.information(self, "Reset", "Comparison session cleared. Previously defined error logs remain intact.")

    def on_opacity_changed(self, value):
        self.chart_display.set_opacity(value / 100.0)

    def toggle_drag_mode(self):
        if self.flicker_manager.timer.isActive():
            self.flicker_manager.pause()
            self.btn_flicker.setText("Start Flicker")

        self.chart_display.drag_mode_enabled = not self.chart_display.drag_mode_enabled
        if self.chart_display.drag_mode_enabled:
            self.btn_toggle_drag.setText("Drag Mode: ON")
            self.btn_toggle_drag.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold;")
        else:
            self.btn_toggle_drag.setText("Drag Mode: OFF")
            self.btn_toggle_drag.setStyleSheet("background-color: #10B981; color: white; font-weight: bold;")

    def set_view_mode(self, mode):
        self.flicker_manager.pause()
        self.btn_flicker.setText("Start Flicker")
        self.chart_display.set_active_view(mode)

    def toggle_drawing_mode(self):
        self.chart_display.drawing_mode = not self.chart_display.drawing_mode
        if self.chart_display.drawing_mode:
            self.btn_draw.setText("Draw Highlight: ON")
            self.btn_draw.setStyleSheet("background-color: #EF4444; color: white;")
            self.chart_display.setCursor(Qt.CrossCursor)
        else:
            self.btn_draw.setText("Draw Highlight: OFF")
            self.btn_draw.setStyleSheet("")
            self.chart_display.setCursor(Qt.ArrowCursor)

    def zoom_in(self):
        curr = self.chart_display.zoom_factor * 1.2
        self.chart_display.set_zoom(curr)
        self.label_zoom.setText(f"Zoom: {int(curr * 100)}%")

    def zoom_out(self):
        curr = self.chart_display.zoom_factor / 1.2
        self.chart_display.set_zoom(curr)
        self.label_zoom.setText(f"Zoom: {int(curr * 100)}%")

    def reset_zoom(self):
        self.chart_display.set_zoom(1.0)
        self.label_zoom.setText("Zoom: 100%")

    def reset_alignment(self):
        self.chart_display.reset_alignment()

    def toggle_flicker(self):
        if self.flicker_manager.timer.isActive():
            self.flicker_manager.pause()
            self.btn_flicker.setText("Start Flicker")
            self.chart_display.set_active_view("Both")
        else:
            if self.chart_display.drag_mode_enabled:
                self.chart_display.drag_mode_enabled = False
                self.btn_toggle_drag.setText("Drag Mode: OFF")
                self.btn_toggle_drag.setStyleSheet("background-color: #10B981; color: white; font-weight: bold;")
            
            self.flicker_manager.start()
            self.btn_flicker.setText("Pause Flicker")

    def change_flicker_interval(self, index):
        intervals = [0.2, 0.5, 1.0, 2.0, 3.0]
        self.flicker_manager.set_interval(intervals[index])

    def on_flicker_state_changed(self, chart):
        self.chart_display.set_active_view(chart)