from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFileDialog, QMessageBox, QScrollArea, QSlider, QComboBox,
    QInputDialog, QDialog, QTextEdit, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, QPoint, QPointF, Signal, QSize, QEvent, QRectF, QRect
from PySide6.QtGui import (
    QPixmap, QPainter, QPen, QColor, QWheelEvent, QMouseEvent, 
    QPaintEvent, QFont, QFontMetrics, QTextOption, QIcon, QPainterPath
)
from app.pdf.pdf_loader import PDFLoader
from app.pdf.pdf_renderer import PDFRenderer
from app.comparison.flicker import FlickerManager
from app.gui.dialogs import AddErrorDialog
from app.errors.error_model import ErrorItem

FLICKER_BTN_STYLE_OFF = """
    QPushButton {
        background-color: #F59E0B;
        color: #FFFFFF;
        font-weight: bold;
        border-radius: 4px;
        padding: 6px 14px;
    }
    QPushButton:hover {
        background-color: #D97706;
    }
    QPushButton:disabled {
        background-color: #FDE68A;
        color: #92400E;
    }
"""

FLICKER_BTN_STYLE_ON = """
    QPushButton {
        background-color: #10B981;
        color: #FFFFFF;
        font-weight: bold;
        border-radius: 4px;
        padding: 6px 14px;
    }
    QPushButton:hover {
        background-color: #059669;
    }
"""

def create_warning_icon(size: int = 24) -> QIcon:
    """Requirement 2: Creates a crisp monochrome outline warning triangle matching the blue vector style of floating buttons."""
    icon = QIcon()
    for state, color_hex in [("normal", "#0284C7"), ("checked", "#FFFFFF"), ("disabled", "#CBD5E1")]:
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)

        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor(color_hex), 2.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        top_pt = QPointF(size / 2.0, 3.5)
        bl_pt = QPointF(3.5, size - 3.5)
        br_pt = QPointF(size - 3.5, size - 3.5)

        path = QPainterPath()
        path.moveTo(top_pt)
        path.lineTo(bl_pt)
        path.lineTo(br_pt)
        path.closeSubpath()
        painter.drawPath(path)

        bar_pen = QPen(QColor(color_hex), 2.2, Qt.SolidLine, Qt.RoundCap)
        painter.setPen(bar_pen)
        painter.drawLine(QPointF(size / 2.0, 8.5), QPointF(size / 2.0, size - 9.5))
        painter.drawPoint(QPointF(size / 2.0, size - 6.0))

        painter.end()

        if state == "normal":
            icon.addPixmap(pixmap, QIcon.Normal, QIcon.Off)
        elif state == "checked":
            icon.addPixmap(pixmap, QIcon.Normal, QIcon.On)
        elif state == "disabled":
            icon.addPixmap(pixmap, QIcon.Disabled, QIcon.Off)
            icon.addPixmap(pixmap, QIcon.Disabled, QIcon.On)

    return icon


FLOATING_BTN_STYLE = """
    QPushButton {
        background-color: rgba(255, 255, 255, 0.85);
        border: 2px dashed #0284C7;
        border-radius: 8px;
        color: #0284C7;
        font-size: 20px;
        font-weight: bold;
        padding: 0px;
        margin: 0px;
    }
    QPushButton:hover {
        background-color: rgba(224, 242, 254, 0.95);
        border: 2px solid #0284C7;
    }
    QPushButton:checked {
        background-color: #0284C7;
        color: #FFFFFF;
        border: 2px solid #0369A1;
    }
    QPushButton:disabled {
        background-color: rgba(248, 250, 252, 0.6);
        border: 1.5px dashed #CBD5E1;
        color: #CBD5E1;
    }
"""

class EditNoteDialog(QDialog):
    """Requirement 5: Wraps inserted text to fit the dimensions of opened window."""
    def __init__(self, note_id: str, current_text: str = "", parent=None, is_new: bool = False):
        super().__init__(parent)
        title_action = "Add Chart Note" if is_new else "Edit Note"
        self.setWindowTitle(f"{title_action} [{note_id}]")
        self.setMinimumSize(420, 260)
        self.resize(460, 280)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)
        
        lbl_text = "Enter note description or annotation to place on the chart:" if is_new else "Update note text annotation:"
        lbl = QLabel(f"<b>{lbl_text}</b> <span style='color: #0284C7; font-weight: bold;'>[{note_id}]</span>")
        lbl.setStyleSheet("font-size: 13px;")
        layout.addWidget(lbl)
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(current_text)
        self.text_edit.setLineWrapMode(QTextEdit.WidgetWidth)
        self.text_edit.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                color: #0F172A;
            }
            QTextEdit:focus {
                border: 2px solid #0284C7;
            }
        """)
        layout.addWidget(self.text_edit)
        
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.btn_save = QPushButton("Save")
        self.btn_save.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold; padding: 6px 18px; border-radius: 4px;")
        self.btn_save.clicked.connect(self.accept)
        
        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setStyleSheet("background-color: #F1F5F9; color: #475569; border: 1px solid #CBD5E1; padding: 6px 14px; border-radius: 4px;")
        self.btn_cancel.clicked.connect(self.reject)
        
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_cancel)
        layout.addLayout(btn_layout)

    def get_text(self) -> str:
        return self.text_edit.toPlainText().strip()


class ClearDrawingsDialog(QDialog):
    """Requirement 4: Allows user to choose which drawing stroke to remove or clear all."""
    def __init__(self, chart_display, parent=None):
        super().__init__(parent)
        self.chart_display = chart_display
        self.setWindowTitle("Clear / Remove Drawings")
        self.setMinimumWidth(380)
        self.resize(400, 340)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        lbl = QLabel("Select a highlight drawing to remove, or choose Clear All:")
        lbl.setStyleSheet("font-weight: bold; color: #1E293B; font-size: 13px;")
        lbl.setWordWrap(True)
        layout.addWidget(lbl)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 4px;
                background-color: #F8FAFC;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px 10px;
                border-radius: 4px;
                margin-bottom: 3px;
            }
            QListWidget::item:selected {
                background-color: #0284C7;
                color: white;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.list_widget)

        self.populate_list()
        self.list_widget.currentRowChanged.connect(self.on_selection_changed)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.btn_remove = QPushButton("Remove Selected")
        self.btn_remove.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
        self.btn_remove.clicked.connect(self.remove_selected)
        btn_layout.addWidget(self.btn_remove)

        self.btn_clear_all = QPushButton("Clear All Drawings")
        self.btn_clear_all.setStyleSheet("background-color: #F59E0B; color: white; font-weight: bold; padding: 6px 12px; border-radius: 4px;")
        self.btn_clear_all.clicked.connect(self.clear_all)
        btn_layout.addWidget(self.btn_clear_all)

        self.btn_close = QPushButton("Cancel")
        self.btn_close.setStyleSheet("background-color: #F1F5F9; color: #475569; border: 1px solid #CBD5E1; padding: 6px 14px; border-radius: 4px;")
        self.btn_close.clicked.connect(self.reject)
        btn_layout.addWidget(self.btn_close)

        layout.addLayout(btn_layout)

        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)

    def populate_list(self):
        self.list_widget.clear()
        for i, stroke in enumerate(self.chart_display.strokes):
            item = QListWidgetItem(f"Drawing #{i + 1} ({len(stroke)} points)")
            self.list_widget.addItem(item)

    def on_selection_changed(self, row):
        if 0 <= row < len(self.chart_display.strokes):
            self.chart_display.highlighted_stroke_index = row
        else:
            self.chart_display.highlighted_stroke_index = None
        self.chart_display.update()

    def remove_selected(self):
        row = self.list_widget.currentRow()
        if 0 <= row < len(self.chart_display.strokes):
            self.chart_display.strokes.pop(row)
            if not self.chart_display.strokes:
                self.chart_display.highlighted_stroke_index = None
                self.chart_display.update()
                self.accept()
                return
            new_row = min(row, len(self.chart_display.strokes) - 1)
            self.populate_list()
            self.list_widget.setCurrentRow(new_row)
            self.chart_display.update()

    def clear_all(self):
        confirm = QMessageBox.question(
            self, "Confirm Clear All",
            "Are you sure you want to clear all highlight drawings?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            self.chart_display.strokes.clear()
            self.chart_display.highlighted_stroke_index = None
            self.chart_display.update()
            self.accept()

    def reject(self):
        self.chart_display.highlighted_stroke_index = None
        self.chart_display.update()
        super().reject()

    def accept(self):
        self.chart_display.highlighted_stroke_index = None
        self.chart_display.update()
        super().accept()


class InteractiveChartWidget(QLabel):
    drawing_added = Signal()
    rotation_changed = Signal(float)
    note_point_selected = Signal(QPointF)
    error_point_selected = Signal(QPointF)
    note_selected = Signal(str)
    error_selected = Signal(str)

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
        self.rotation_old = 0.0
        self.drag_mode_enabled = False
        
        self.drawing_mode = False
        self.note_mode_enabled = False
        self.error_mode_enabled = False
        
        self.strokes = [] 
        self.current_stroke = []
        self.highlighted_stroke_index = None
        self.notes = []          # List of dicts: {"id": str, "pos": QPointF, "text": str, "chart": str}
        self.error_markers = []  # List of dicts: {"pos": QPointF, "id": str, "type": str, "description": str, "severity": str, "chart": str, "comments": str}
        
        self.selected_note = None
        self.is_dragging_note = False
        self.note_drag_offset = QPointF(0, 0)
        
        self.selected_error = None
        self.is_dragging_error = False
        self.error_drag_offset = QPointF(0, 0)
        
        self.dragging = False
        self.drag_button = None
        self.last_mouse_pos = QPoint()

    def set_charts(self, pix_updated, pix_old):
        self.pixmap_updated = pix_updated
        self.pixmap_old = pix_old
        self.offset_old = QPointF(0.0, 0.0)
        self.rotation_old = 0.0
        self.strokes.clear()
        self.notes.clear()
        self.error_markers.clear()
        self.selected_note = None
        self.is_dragging_note = False
        self.selected_error = None
        self.is_dragging_error = False
        self.note_mode_enabled = False
        self.error_mode_enabled = False
        self.update_widget_size()
        self.update()
        self.rotation_changed.emit(self.rotation_old)

    def clear(self):
        self.pixmap_updated = None
        self.pixmap_old = None
        self.offset_old = QPointF(0.0, 0.0)
        self.rotation_old = 0.0
        self.strokes.clear()
        self.notes.clear()
        self.error_markers.clear()
        self.selected_note = None
        self.is_dragging_note = False
        self.selected_error = None
        self.is_dragging_error = False
        self.note_mode_enabled = False
        self.error_mode_enabled = False
        self.zoom_factor = 1.0
        self.setMinimumSize(700, 700)
        self.resize(700, 700)
        self.update()
        self.rotation_changed.emit(self.rotation_old)

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

    def rotate_old(self, delta_angle: float):
        self.rotation_old = (self.rotation_old + delta_angle) % 360.0
        self.update()
        self.rotation_changed.emit(self.rotation_old)

    def reset_alignment(self):
        self.offset_old = QPointF(0.0, 0.0)
        self.rotation_old = 0.0
        self.update()
        self.rotation_changed.emit(self.rotation_old)

    def clear_drawings(self):
        """Only clears drawing strokes, strictly preserves notes and error markers!"""
        self.strokes.clear()
        self.highlighted_stroke_index = None
        self.update()

    def _get_note_bubble_rect(self, scr_pt: QPointF, note_id: str, text: str, bounds: QRectF = None) -> QRectF:
        font = QFont("Arial", 9)
        fm = QFontMetrics(font)
        badge_text = f"📝 {note_id}"
        
        lines = text.split('\n')
        max_w = max(fm.horizontalAdvance(l) for l in lines) if lines else 60
        max_w = max(max_w, fm.horizontalAdvance(badge_text) + 20)
        bubble_w = max(95.0, min(280.0, float(max_w + 24)))
        
        if bounds and bounds.isValid():
            max_avail_w = max(60.0, bounds.width() - 20.0)
            bubble_w = min(bubble_w, max_avail_w)

        rect_text = fm.boundingRect(0, 0, int(bubble_w - 16), 5000, Qt.TextWordWrap, text)
        bubble_h = max(38.0, float(rect_text.height() + 26))
        
        bubble_x = scr_pt.x() + 14.0
        bubble_y = scr_pt.y() - 14.0

        if bounds and bounds.isValid():
            margin = 8.0
            # If bubble overflows right edge, flip to left of pin
            if bubble_x + bubble_w > bounds.right() - margin:
                left_cand = scr_pt.x() - 14.0 - bubble_w
                if left_cand >= bounds.left() + margin:
                    bubble_x = left_cand
                else:
                    bubble_x = max(bounds.left() + margin, bounds.right() - margin - bubble_w)
            
            # Clamp left
            if bubble_x < bounds.left() + margin:
                bubble_x = bounds.left() + margin
                
            # If bubble overflows bottom, push up
            if bubble_y + bubble_h > bounds.bottom() - margin:
                bubble_y = bounds.bottom() - margin - bubble_h
                
            # If bubble overflows top, push down
            if bubble_y < bounds.top() + margin:
                bubble_y = bounds.top() + margin
                
            # If height exceeds available bounds
            if bubble_h > bounds.height() - 2 * margin:
                bubble_h = max(30.0, bounds.height() - 2 * margin)
                bubble_y = bounds.top() + margin

        return QRectF(bubble_x, bubble_y, bubble_w, bubble_h)

    def hit_test_note(self, screen_pt: QPointF):
        """Hit test for selecting or moving notes on chart."""
        if not self.pixmap_updated or not self.notes:
            return None
        sz_up = self.pixmap_updated.size() * self.zoom_factor
        widget_size = self.size()
        center_x = max(0, (widget_size.width() - sz_up.width()) / 2)
        center_y = max(0, (widget_size.height() - sz_up.height()) / 2)
        bounds = QRectF(center_x, center_y, sz_up.width(), sz_up.height())

        for note in reversed(self.notes):
            scr_pt = self.chart_to_screen_coords(note["pos"], center_x, center_y)
            dx = screen_pt.x() - scr_pt.x()
            dy = screen_pt.y() - scr_pt.y()
            if (dx*dx + dy*dy) <= 144.0: # 12px radius of pin
                return note
            rect = self._get_note_bubble_rect(scr_pt, note.get("id", "NT"), note.get("text", ""), bounds)
            if rect.adjusted(-4, -4, 4, 4).contains(screen_pt):
                return note
        return None

    def _draw_note_callout(self, painter: QPainter, pt: QPointF, note: dict, is_selected: bool = False, bounds: QRectF = None):
        """Draws a professional aeronautical note callout with pointer, ID badge, and text box."""
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        note_id = note.get("id", "NT")
        text = note.get("text", "")

        # Pin marker at target location
        painter.setPen(QPen(QColor("#0284C7"), 2))
        painter.setBrush(QColor("#0284C7"))
        painter.drawEllipse(pt, 4.0, 4.0)
        painter.setBrush(QColor("#FFFFFF"))
        painter.drawEllipse(pt, 1.5, 1.5)
        
        bubble_rect = self._get_note_bubble_rect(pt, note_id, text, bounds)
        
        # Pointer leader line to bubble
        painter.setPen(QPen(QColor("#0284C7"), 1.5, Qt.DashLine))
        if bubble_rect.left() >= pt.x():
            leader_target = QPointF(bubble_rect.left(), min(bubble_rect.bottom(), max(bubble_rect.top(), pt.y())))
        elif bubble_rect.right() <= pt.x():
            leader_target = QPointF(bubble_rect.right(), min(bubble_rect.bottom(), max(bubble_rect.top(), pt.y())))
        elif bubble_rect.top() >= pt.y():
            leader_target = QPointF(min(bubble_rect.right(), max(bubble_rect.left(), pt.x())), bubble_rect.top())
        else:
            leader_target = QPointF(min(bubble_rect.right(), max(bubble_rect.left(), pt.x())), bubble_rect.bottom())
        painter.drawLine(pt, leader_target)
        
        # Yellow note callout box (with selection glow if selected)
        if is_selected:
            glow_rect = bubble_rect.adjusted(-2.5, -2.5, 2.5, 2.5)
            painter.setPen(QPen(QColor("#0284C7"), 2.5))
            painter.setBrush(QColor("#FEF08A"))
            painter.drawRoundedRect(glow_rect, 6.0, 6.0)
        else:
            painter.setPen(QPen(QColor("#0284C7"), 1.5))
            painter.setBrush(QColor("#FEF9C3"))
            painter.drawRoundedRect(bubble_rect, 5.0, 5.0)
        
        # Note ID Header
        id_font = QFont("Arial", 8)
        id_font.setBold(True)
        painter.setFont(id_font)
        painter.setPen(QColor("#0284C7"))
        painter.drawText(QRectF(bubble_rect.left() + 8, bubble_rect.top() + 4, bubble_rect.width() - 16, 14), Qt.AlignLeft, f"📝 {note_id}")

        # Text inside callout
        text_font = QFont("Arial", 9)
        painter.setFont(text_font)
        painter.setPen(QColor("#0F172A"))
        text_rect = QRectF(bubble_rect.left() + 8, bubble_rect.top() + 20, bubble_rect.width() - 16, bubble_rect.height() - 24)
        painter.drawText(text_rect, Qt.TextWordWrap, text)
        painter.restore()

    def _get_error_badge_rect(self, pt: QPointF, error_id: str, bounds: QRectF = None) -> QRectF:
        badge_font = QFont("Arial", 9)
        badge_font.setBold(True)
        fm = QFontMetrics(badge_font)
        badge_text = f"⚠️ {error_id}"
        text_w = fm.horizontalAdvance(badge_text)
        badge_w = text_w + 14
        badge_h = 22.0
        
        badge_x = pt.x() + 8.0
        badge_y = pt.y() - 11.0
        
        if bounds and bounds.isValid():
            margin = 8.0
            if badge_x + badge_w > bounds.right() - margin:
                left_cand = pt.x() - 8.0 - badge_w
                if left_cand >= bounds.left() + margin:
                    badge_x = left_cand
                else:
                    badge_x = max(bounds.left() + margin, bounds.right() - margin - badge_w)
            if badge_x < bounds.left() + margin:
                badge_x = bounds.left() + margin
            if badge_y + badge_h > bounds.bottom() - margin:
                badge_y = bounds.bottom() - margin - badge_h
            if badge_y < bounds.top() + margin:
                badge_y = bounds.top() + margin
                
        return QRectF(badge_x, badge_y, badge_w, badge_h)

    def hit_test_error(self, screen_pt: QPointF):
        """Requirement 6: Hit test for selecting or moving error markers on chart."""
        if not self.pixmap_updated or not self.error_markers:
            return None
        sz_up = self.pixmap_updated.size() * self.zoom_factor
        widget_size = self.size()
        center_x = max(0, (widget_size.width() - sz_up.width()) / 2)
        center_y = max(0, (widget_size.height() - sz_up.height()) / 2)
        bounds = QRectF(center_x, center_y, sz_up.width(), sz_up.height())

        for err in reversed(self.error_markers):
            scr_pt = self.chart_to_screen_coords(err["pos"], center_x, center_y)
            dx = screen_pt.x() - scr_pt.x()
            dy = screen_pt.y() - scr_pt.y()
            if (dx*dx + dy*dy) <= 144.0: # 12px radius of pin
                return err
            rect = self._get_error_badge_rect(scr_pt, err.get("id", "ERR"), bounds)
            if rect.adjusted(-4, -4, 4, 4).contains(screen_pt):
                return err
        return None

    def _draw_error_badge(self, painter: QPainter, pt: QPointF, error_id: str, is_selected: bool = False, bounds: QRectF = None):
        """Draws a high-visibility crimson discrepancy badge [ ⚠️ ERR-00x ] pinned to coordinates."""
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # Target crosshair pin at coordinates
        painter.setPen(QPen(QColor("#EF4444"), 2))
        painter.setBrush(QColor("#EF4444"))
        painter.drawEllipse(pt, 4.0, 4.0)
        painter.drawLine(QPointF(pt.x() - 7, pt.y()), QPointF(pt.x() + 7, pt.y()))
        painter.drawLine(QPointF(pt.x(), pt.y() - 7), QPointF(pt.x(), pt.y() + 7))
        
        badge_rect = self._get_error_badge_rect(pt, error_id, bounds)
        
        # Leader line if badge was shifted/flipped
        painter.setPen(QPen(QColor("#EF4444"), 1.2, Qt.DashLine))
        if badge_rect.left() >= pt.x():
            painter.drawLine(pt, QPointF(badge_rect.left(), pt.y()))
        elif badge_rect.right() <= pt.x():
            painter.drawLine(pt, QPointF(badge_rect.right(), pt.y()))
            
        badge_font = QFont("Arial", 9)
        badge_font.setBold(True)
        painter.setFont(badge_font)
        badge_text = f"⚠️ {error_id}"
        
        # Outer glow (selection glow if selected, white glow if not)
        if is_selected:
            glow_rect = badge_rect.adjusted(-2.5, -2.5, 2.5, 2.5)
            painter.setPen(QPen(QColor("#0284C7"), 2.5))
            painter.setBrush(QColor("#DC2626"))
            painter.drawRoundedRect(glow_rect, 5.0, 5.0)
        else:
            glow_rect = badge_rect.adjusted(-1.5, -1.5, 1.5, 1.5)
            painter.setPen(QPen(QColor("#FFFFFF"), 2.0))
            painter.setBrush(QColor("#DC2626"))
            painter.drawRoundedRect(glow_rect, 4.0, 4.0)
        
        # Text
        painter.setPen(QColor("#FFFFFF"))
        painter.drawText(badge_rect, Qt.AlignCenter, badge_text)
        painter.restore()

    def get_annotated_pixmap(self) -> QPixmap:
        """Requirement 5: Makes a screenshot ONLY of drawings, notes, error badges, and updated chart (ignores old chart)."""
        if not self.pixmap_updated:
            pixmap = QPixmap(self.size())
            pixmap.fill(Qt.white)
            return pixmap
            
        sz_up = self.pixmap_updated.size() * self.zoom_factor
        w = max(1, int(sz_up.width()))
        h = max(1, int(sz_up.height()))
        
        pixmap = QPixmap(w, h)
        pixmap.fill(Qt.white)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.Antialiasing, True)
        
        # 1. Draw ONLY Updated chart (completely ignore old chart, opacity, flicker, and widget margins)
        scaled_up = self.pixmap_updated.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, scaled_up)
        
        # 2. Draw user strokes / drawings
        pen = QPen(QColor(239, 68, 68), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        for stroke in self.strokes:
            scaled_stroke = [QPointF(pt.x() * self.zoom_factor, pt.y() * self.zoom_factor) for pt in stroke]
            for i in range(len(scaled_stroke) - 1):
                painter.drawLine(scaled_stroke[i], scaled_stroke[i+1])
                
        chart_bounds = QRectF(0, 0, w, h)
        # 3. Draw notes (with bounds clamping so large notes never go beyond chart borders)
        for note in self.notes:
            pt = QPointF(note["pos"].x() * self.zoom_factor, note["pos"].y() * self.zoom_factor)
            self._draw_note_callout(painter, pt, note, is_selected=False, bounds=chart_bounds)
            
        # 4. Draw error badges (with bounds clamping)
        for err in self.error_markers:
            pt = QPointF(err["pos"].x() * self.zoom_factor, err["pos"].y() * self.zoom_factor)
            self._draw_error_badge(painter, pt, err["id"], is_selected=False, bounds=chart_bounds)
            
        painter.end()
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

        def draw_scaled_old(p, opacity=1.0):
            if not scaled_old:
                return
            p.save()
            if opacity < 1.0:
                p.setOpacity(opacity)
            center_x_old = x_old + scaled_old.width() / 2.0
            center_y_old = y_old + scaled_old.height() / 2.0
            p.translate(center_x_old, center_y_old)
            if getattr(self, "rotation_old", 0.0) != 0.0:
                p.rotate(self.rotation_old)
            p.drawPixmap(int(-scaled_old.width() / 2.0), int(-scaled_old.height() / 2.0), scaled_old)
            p.restore()

        if self.active_view == "Updated chart":
            painter.drawPixmap(int(x_up), int(y_up), scaled_up)
        elif self.active_view == "Old chart" and scaled_old:
            draw_scaled_old(painter, 1.0)
        else:
            painter.drawPixmap(int(x_up), int(y_up), scaled_up)
            if scaled_old:
                draw_scaled_old(painter, self.opacity_old)

        for idx, stroke in enumerate(self.strokes):
            screen_stroke = [self.chart_to_screen_coords(pt, x_up, y_up) for pt in stroke]
            if getattr(self, 'highlighted_stroke_index', None) == idx:
                halo_pen = QPen(QColor(14, 165, 233, 210), 9, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                painter.setPen(halo_pen)
                for i in range(len(screen_stroke) - 1):
                    painter.drawLine(screen_stroke[i], screen_stroke[i + 1])
                if screen_stroke:
                    painter.save()
                    painter.setPen(Qt.NoPen)
                    painter.setBrush(QColor(14, 165, 233, 230))
                    badge_rect = QRectF(screen_stroke[0].x() - 12, screen_stroke[0].y() - 26, 84, 22)
                    painter.drawRoundedRect(badge_rect, 4, 4)
                    painter.setPen(QColor(255, 255, 255))
                    painter.setFont(QFont("Arial", 9, QFont.Bold))
                    painter.drawText(badge_rect, Qt.AlignCenter, f"Drawing #{idx + 1}")
                    painter.restore()

            pen = QPen(QColor(239, 68, 68), 3, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            painter.setPen(pen)
            for i in range(len(screen_stroke) - 1):
                painter.drawLine(screen_stroke[i], screen_stroke[i+1])
        
        if len(self.current_stroke) > 1:
            screen_current = [self.chart_to_screen_coords(pt, x_up, y_up) for pt in self.current_stroke]
            for i in range(len(screen_current) - 1):
                painter.drawLine(screen_current[i], screen_current[i+1])

        bounds_on_screen = QRectF(x_up, y_up, sz_up.width(), sz_up.height())
        # Draw notes (with selection highlight if selected)
        for note in self.notes:
            scr_pt = self.chart_to_screen_coords(note["pos"], x_up, y_up)
            is_sel = (self.selected_note is not None and self.selected_note.get("id") == note.get("id"))
            self._draw_note_callout(painter, scr_pt, note, is_selected=is_sel, bounds=bounds_on_screen)

        # Draw error markers (with selection highlight if selected)
        for err in self.error_markers:
            scr_pt = self.chart_to_screen_coords(err["pos"], x_up, y_up)
            is_sel = (self.selected_error is not None and self.selected_error.get("id") == err.get("id"))
            self._draw_error_badge(painter, scr_pt, err["id"], is_selected=is_sel, bounds=bounds_on_screen)

        painter.end()

    def wheelEvent(self, event: QWheelEvent):
        angle = event.angleDelta().y()
        factor = 1.15 if angle > 0 else (1.0 / 1.15)
        self.set_zoom(self.zoom_factor * factor)
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            sz_up = self.pixmap_updated.size() * self.zoom_factor if self.pixmap_updated else 1
            widget_size = self.size()
            center_x = max(0, (widget_size.width() - sz_up.width()) / 2) if self.pixmap_updated else 0
            center_y = max(0, (widget_size.height() - sz_up.height()) / 2) if self.pixmap_updated else 0
            screen_pos = QPointF(event.pos())
            local_pt = self.screen_to_chart_coords(screen_pos, center_x, center_y)

            # 1. Mode check for creating note
            if getattr(self, 'note_mode_enabled', False):
                self.note_point_selected.emit(local_pt)
                return
            # 2. Mode check for creating error
            elif getattr(self, 'error_mode_enabled', False):
                self.error_point_selected.emit(local_pt)
                return
            # 3. Drawing mode
            elif self.drawing_mode:
                self.current_stroke = [local_pt]
                return

            # 4. Check if clicking on an existing note to MOVE / SELECT it!
            hit_note = self.hit_test_note(screen_pos)
            if hit_note:
                self.selected_note = hit_note
                self.is_dragging_note = True
                self.note_drag_offset = hit_note["pos"] - local_pt
                self.selected_error = None
                self.setCursor(Qt.ClosedHandCursor)
                self.note_selected.emit(hit_note.get("id", ""))
                self.update()
                return
            else:
                if self.selected_note:
                    self.selected_note = None
                    self.note_selected.emit("")
                    self.update()

            # 5. Check if clicking on an existing error to MOVE / SELECT it! (Requirement 6)
            hit_err = self.hit_test_error(screen_pos)
            if hit_err:
                self.selected_error = hit_err
                self.is_dragging_error = True
                self.error_drag_offset = hit_err["pos"] - local_pt
                self.selected_note = None
                self.setCursor(Qt.ClosedHandCursor)
                self.error_selected.emit(hit_err.get("id", ""))
                self.update()
                return
            else:
                if self.selected_error:
                    self.selected_error = None
                    self.error_selected.emit("")
                    self.update()

            if self.drag_mode_enabled:
                self.dragging = True
                self.drag_button = Qt.LeftButton
                self.last_mouse_pos = event.pos()
        elif event.button() == Qt.RightButton and self.drag_mode_enabled:
            # Right-click drag rotates Old chart in Drag Mode
            self.dragging = True
            self.drag_button = Qt.RightButton
            self.last_mouse_pos = event.pos()

    def mouseMoveEvent(self, event: QMouseEvent):
        screen_pos = QPointF(event.pos())
        sz_up = self.pixmap_updated.size() * self.zoom_factor if self.pixmap_updated else 1
        widget_size = self.size()
        center_x = max(0, (widget_size.width() - sz_up.width()) / 2) if self.pixmap_updated else 0
        center_y = max(0, (widget_size.height() - sz_up.height()) / 2) if self.pixmap_updated else 0
        local_pt = self.screen_to_chart_coords(screen_pos, center_x, center_y)

        # Note movement drag
        if getattr(self, 'is_dragging_note', False) and self.selected_note:
            new_pos = local_pt + self.note_drag_offset
            if self.pixmap_updated:
                new_pos.setX(max(10.0, min(float(self.pixmap_updated.width() - 10), new_pos.x())))
                new_pos.setY(max(10.0, min(float(self.pixmap_updated.height() - 10), new_pos.y())))
            self.selected_note["pos"] = new_pos
            self.update()
            return

        # Error movement drag (Requirement 6)
        if getattr(self, 'is_dragging_error', False) and self.selected_error:
            new_pos = local_pt + self.error_drag_offset
            if self.pixmap_updated:
                new_pos.setX(max(10.0, min(float(self.pixmap_updated.width() - 10), new_pos.x())))
                new_pos.setY(max(10.0, min(float(self.pixmap_updated.height() - 10), new_pos.y())))
            self.selected_error["pos"] = new_pos
            self.update()
            return

        if self.drawing_mode and (event.buttons() & Qt.LeftButton) and self.pixmap_updated:
            self.current_stroke.append(local_pt)
            self.update()
        elif self.dragging and self.drag_mode_enabled:
            delta = event.pos() - self.last_mouse_pos
            self.last_mouse_pos = event.pos()
            if self.drag_button == Qt.LeftButton:
                scaled_delta = QPointF(delta.x() / self.zoom_factor, delta.y() / self.zoom_factor)
                self.offset_old += scaled_delta
                self.update()
            elif self.drag_button == Qt.RightButton:
                self.rotation_old = (self.rotation_old + delta.x() * 0.15) % 360.0
                self.update()
                self.rotation_changed.emit(self.rotation_old)
        else:
            # Hover cursor change for notes and errors
            if not self.drawing_mode and not getattr(self, 'note_mode_enabled', False) and not getattr(self, 'error_mode_enabled', False) and not self.drag_mode_enabled:
                hit_note = self.hit_test_note(screen_pos)
                hit_err = self.hit_test_error(screen_pos)
                if hit_note or hit_err:
                    self.setCursor(Qt.OpenHandCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if getattr(self, 'is_dragging_note', False):
            self.is_dragging_note = False
            self.setCursor(Qt.OpenHandCursor if self.selected_note else Qt.ArrowCursor)
            self.update()
            return
        if getattr(self, 'is_dragging_error', False):
            self.is_dragging_error = False
            self.setCursor(Qt.OpenHandCursor if self.selected_error else Qt.ArrowCursor)
            self.update()
            return
        if event.button() == Qt.LeftButton:
            if self.drawing_mode and self.current_stroke:
                self.strokes.append(list(self.current_stroke))
                self.current_stroke.clear()
                self.update()
                self.drawing_added.emit()
        self.dragging = False
        self.drag_button = None

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            screen_pos = QPointF(event.pos())
            parent_tab = self.window().tab_comparison if hasattr(self.window(), 'tab_comparison') else None
            if parent_tab:
                hit_note = self.hit_test_note(screen_pos)
                if hit_note:
                    parent_tab.edit_note_by_id(hit_note["id"])
                    event.accept()
                    return
                hit_err = self.hit_test_error(screen_pos)
                if hit_err:
                    parent_tab.edit_error_by_id(hit_err["id"])
                    event.accept()
                    return
        super().mouseDoubleClickEvent(event)

    def contextMenuEvent(self, event):
        screen_pos = QPointF(event.pos())
        parent_tab = self.window().tab_comparison if hasattr(self.window(), 'tab_comparison') else None
        
        hit_note = self.hit_test_note(screen_pos)
        if hit_note:
            from PySide6.QtWidgets import QMenu
            menu = QMenu(self)
            action_del = menu.addAction(f"Delete Note {hit_note.get('id', '')}")
            action_edit = menu.addAction(f"Edit Note {hit_note.get('id', '')}")
            selected_action = menu.exec(event.globalPos())
            if parent_tab:
                if selected_action == action_del:
                    parent_tab.delete_note_by_id(hit_note["id"])
                elif selected_action == action_edit:
                    parent_tab.edit_note_by_id(hit_note["id"])
            event.accept()
            return

        hit_err = self.hit_test_error(screen_pos)
        if hit_err:
            from PySide6.QtWidgets import QMenu
            menu = QMenu(self)
            action_del = menu.addAction(f"Delete Error {hit_err.get('id', '')}")
            action_edit = menu.addAction(f"Edit Error {hit_err.get('id', '')}")
            selected_action = menu.exec(event.globalPos())
            if parent_tab:
                if selected_action == action_del:
                    parent_tab.delete_error_by_id(hit_err["id"])
                elif selected_action == action_edit:
                    parent_tab.edit_error_by_id(hit_err["id"])
            event.accept()
            return

        super().contextMenuEvent(event)


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

        # Second Section: 4 parts (Left, CenterLeft, CenterRight, Right) with Upper & Lower rows
        toolbar_section = QHBoxLayout()
        toolbar_section.setContentsMargins(0, 0, 0, 0)
        toolbar_section.setSpacing(16)

        # 1. Left Part
        col_left = QVBoxLayout()
        col_left.setSpacing(6)

        # Left Upper (Picture 11)
        row_left_upper = QHBoxLayout()
        row_left_upper.setSpacing(6)
        self.btn_toggle_drag = QPushButton("Drag Mode: OFF")
        self.btn_toggle_drag.setToolTip("Toggle Drag Mode: Left-drag to pan Old chart, Right-drag to rotate Old chart.")
        self.btn_toggle_drag.setEnabled(False)
        self.btn_toggle_drag.setStyleSheet("background-color: #10B981; color: white; font-weight: bold;")
        self.btn_toggle_drag.clicked.connect(self.toggle_drag_mode)
        row_left_upper.addWidget(self.btn_toggle_drag)

        self.btn_reset_align = QPushButton("Reset Alignment")
        self.btn_reset_align.setEnabled(False)
        self.btn_reset_align.clicked.connect(self.reset_alignment)
        row_left_upper.addWidget(self.btn_reset_align)
        row_left_upper.addStretch()
        col_left.addLayout(row_left_upper)

        # Left Lower (Picture 12)
        row_left_lower = QHBoxLayout()
        row_left_lower.setSpacing(6)
        self.btn_rotate_ccw = QPushButton("↺ -1°")
        self.btn_rotate_ccw.setToolTip("Rotate Old chart 1° counter-clockwise (Drag Mode)")
        self.btn_rotate_ccw.setEnabled(False)
        self.btn_rotate_ccw.clicked.connect(lambda: self.chart_display.rotate_old(-1.0))
        row_left_lower.addWidget(self.btn_rotate_ccw)

        self.btn_rotate_cw = QPushButton("↻ +1°")
        self.btn_rotate_cw.setToolTip("Rotate Old chart 1° clockwise (Drag Mode)")
        self.btn_rotate_cw.setEnabled(False)
        self.btn_rotate_cw.clicked.connect(lambda: self.chart_display.rotate_old(1.0))
        row_left_lower.addWidget(self.btn_rotate_cw)

        self.btn_rotate_90 = QPushButton("⟳ 90°")
        self.btn_rotate_90.setToolTip("Rotate Old chart 90° clockwise (Drag Mode)")
        self.btn_rotate_90.setEnabled(False)
        self.btn_rotate_90.clicked.connect(lambda: self.chart_display.rotate_old(90.0))
        row_left_lower.addWidget(self.btn_rotate_90)

        self.lbl_angle = QLabel("Angle: 0.0°")
        self.lbl_angle.setStyleSheet("color: #475569; font-weight: bold; font-size: 12px; padding-left: 2px;")
        row_left_lower.addWidget(self.lbl_angle)
        row_left_lower.addStretch()
        col_left.addLayout(row_left_lower)

        toolbar_section.addLayout(col_left)

        # 2. CenterLeft Part
        col_center_left = QVBoxLayout()
        col_center_left.setSpacing(6)

        # CenterLeft Upper (Picture 13)
        row_cleft_upper = QHBoxLayout()
        row_cleft_upper.setSpacing(6)
        self.btn_flicker = QPushButton("Start Flicker")
        self.btn_flicker.setStyleSheet(FLICKER_BTN_STYLE_OFF)
        self.btn_flicker.setEnabled(False)
        self.btn_flicker.clicked.connect(self.toggle_flicker)
        row_cleft_upper.addWidget(self.btn_flicker)

        lbl_interval = QLabel("Interval:")
        row_cleft_upper.addWidget(lbl_interval)

        self.combo_interval = QComboBox()
        self.combo_interval.addItems(["0.2s", "0.5s", "1.0s", "2.0s", "3.0s"])
        self.combo_interval.setCurrentIndex(2)
        self.combo_interval.currentIndexChanged.connect(self.change_flicker_interval)
        row_cleft_upper.addWidget(self.combo_interval)
        row_cleft_upper.addStretch()
        col_center_left.addLayout(row_cleft_upper)

        # CenterLeft Lower (Picture 14)
        row_cleft_lower = QHBoxLayout()
        row_cleft_lower.setSpacing(6)
        self.btn_show_updated = QPushButton("Show Updated")
        self.btn_show_updated.setEnabled(False)
        self.btn_show_updated.clicked.connect(lambda: self.set_view_mode("Updated chart"))
        row_cleft_lower.addWidget(self.btn_show_updated)

        self.btn_show_old = QPushButton("Show Old")
        self.btn_show_old.setEnabled(False)
        self.btn_show_old.clicked.connect(lambda: self.set_view_mode("Old chart"))
        row_cleft_lower.addWidget(self.btn_show_old)
        row_cleft_lower.addStretch()
        col_center_left.addLayout(row_cleft_lower)

        toolbar_section.addLayout(col_center_left)

        # 3. CenterRight Part
        col_center_right = QVBoxLayout()
        col_center_right.setSpacing(6)

        # CenterRight Upper (Picture 15)
        row_cright_upper = QHBoxLayout()
        row_cright_upper.setSpacing(6)
        self.btn_draw = QPushButton("Draw Highlight: OFF")
        self.btn_draw.setEnabled(False)
        self.btn_draw.clicked.connect(self.toggle_drawing_mode)
        row_cright_upper.addWidget(self.btn_draw)

        self.btn_clear_draw = QPushButton("Clear Drawings")
        self.btn_clear_draw.setEnabled(False)
        self.btn_clear_draw.clicked.connect(self.prompt_clear_drawings)
        row_cright_upper.addWidget(self.btn_clear_draw)
        row_cright_upper.addStretch()
        col_center_right.addLayout(row_cright_upper)

        # CenterRight Lower (Picture 16)
        row_cright_lower = QHBoxLayout()
        row_cright_lower.setSpacing(6)
        self.btn_note = QPushButton("Add Note: OFF")
        self.btn_note.setToolTip("Click to toggle Note Mode, then click on the chart to place a text note.")
        self.btn_note.setEnabled(False)
        self.btn_note.clicked.connect(self.toggle_note_mode)
        row_cright_lower.addWidget(self.btn_note)

        self.btn_remove_note = QPushButton("Remove Note")
        self.btn_remove_note.setToolTip("Remove selected note from chart and log, or choose one to remove.")
        self.btn_remove_note.setEnabled(False)
        self.btn_remove_note.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold;")
        self.btn_remove_note.clicked.connect(self.remove_selected_note)
        row_cright_lower.addWidget(self.btn_remove_note)
        row_cright_lower.addStretch()
        col_center_right.addLayout(row_cright_lower)

        # Requirements 1 & 2: Ensure identical button sizes for (Draw Highlight <-> Add Note) and (Clear Drawings <-> Remove Note)
        # Uses bold font metrics with ample padding so text is never truncated on any DPI
        btn_font = self.font()
        btn_font.setBold(True)
        fm = QFontMetrics(btn_font)
        pad = 36
        w_highlight_note = max(
            fm.horizontalAdvance("Draw Highlight: OFF") + pad,
            fm.horizontalAdvance("Draw Highlight: ON") + pad,
            fm.horizontalAdvance("Add Note: OFF") + pad,
            fm.horizontalAdvance("Add Note: ON") + pad,
            185
        )
        w_clear_remove = max(
            fm.horizontalAdvance("Clear Drawings") + pad,
            fm.horizontalAdvance("Remove Note") + pad,
            145
        )

        self.btn_draw.setFixedWidth(w_highlight_note)
        self.btn_note.setFixedWidth(w_highlight_note)
        self.btn_clear_draw.setFixedWidth(w_clear_remove)
        self.btn_remove_note.setFixedWidth(w_clear_remove)

        toolbar_section.addLayout(col_center_right)

        # 4. Right Part
        col_right = QVBoxLayout()
        col_right.setSpacing(6)

        # Right Upper (Picture 17)
        row_right_upper = QHBoxLayout()
        row_right_upper.setSpacing(6)
        self.btn_pin_error = QPushButton("Record Error: OFF")
        self.btn_pin_error.setToolTip("Click to toggle Record Error Mode, then click on the chart to log and pin a discrepancy.")
        self.btn_pin_error.setEnabled(False)
        self.btn_pin_error.clicked.connect(self.toggle_error_pin_mode)
        row_right_upper.addWidget(self.btn_pin_error)
        row_right_upper.addStretch()
        col_right.addLayout(row_right_upper)

        # Right Lower (Picture 18)
        row_right_lower = QHBoxLayout()
        row_right_lower.setSpacing(6)
        self.btn_save_annotated = QPushButton("Save Annotated Chart to Report")
        self.btn_save_annotated.setEnabled(False)
        self.btn_save_annotated.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold;")
        self.btn_save_annotated.clicked.connect(self.save_annotated_chart)
        row_right_lower.addWidget(self.btn_save_annotated)
        row_right_lower.addStretch()
        col_right.addLayout(row_right_lower)

        toolbar_section.addLayout(col_right)
        toolbar_section.addStretch()

        layout.addLayout(toolbar_section)

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
        btn_zoom_in.setFixedSize(32, 28)
        btn_zoom_in.setStyleSheet("QPushButton { font-size: 18px; font-weight: bold; padding: 0px; margin: 0px; text-align: center; }")
        btn_zoom_in.clicked.connect(self.zoom_in)

        btn_zoom_out = QPushButton("-")
        btn_zoom_out.setFixedSize(32, 28)
        btn_zoom_out.setStyleSheet("QPushButton { font-size: 20px; font-weight: bold; padding: 0px; margin: 0px; text-align: center; }")
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
        self.chart_display.rotation_changed.connect(self.on_rotation_changed)
        self.chart_display.note_point_selected.connect(self.on_note_point_selected)
        self.chart_display.error_point_selected.connect(self.on_error_point_selected)
        self.chart_display.note_selected.connect(self.on_note_selected_changed)
        self.chart_display.error_selected.connect(self.on_error_selected_changed)
        self.scroll_area.setWidget(self.chart_display)
        layout.addWidget(self.scroll_area)

        # Requirement 2, 4, 6: Floating transparent buttons on the left side of the chart area (Blue Theme)
        self.floating_panel = QWidget(self.scroll_area.viewport())
        self.floating_panel.setStyleSheet("background: transparent; border: none;")
        fp_layout = QVBoxLayout(self.floating_panel)
        fp_layout.setContentsMargins(0, 0, 0, 0)
        fp_layout.setSpacing(8)

        self.float_btn_drag = QPushButton("✥")
        self.float_btn_drag.setFixedSize(42, 42)
        self.float_btn_drag.setCheckable(True)
        self.float_btn_drag.setEnabled(False)
        self.float_btn_drag.setStyleSheet(FLOATING_BTN_STYLE)
        self.float_btn_drag.setToolTip("Drag Mode (Left-click drag to pan, Right-click drag to rotate)")
        self.float_btn_drag.clicked.connect(self.toggle_drag_mode)
        fp_layout.addWidget(self.float_btn_drag)

        self.float_btn_rotate = QPushButton("↻")
        self.float_btn_rotate.setFixedSize(42, 42)
        self.float_btn_rotate.setEnabled(False)
        self.float_btn_rotate.setStyleSheet(FLOATING_BTN_STYLE)
        self.float_btn_rotate.setToolTip("Rotate Mode (Click to rotate 90° clockwise)")
        self.float_btn_rotate.clicked.connect(lambda: self.chart_display.rotate_old(90.0))
        fp_layout.addWidget(self.float_btn_rotate)

        self.float_btn_draw = QPushButton("✎")
        self.float_btn_draw.setFixedSize(42, 42)
        self.float_btn_draw.setCheckable(True)
        self.float_btn_draw.setEnabled(False)
        self.float_btn_draw.setStyleSheet(FLOATING_BTN_STYLE)
        self.float_btn_draw.setToolTip("Drawing Mode (Highlight discrepancy)")
        self.float_btn_draw.clicked.connect(self.toggle_drawing_mode)
        fp_layout.addWidget(self.float_btn_draw)

        # Requirement 4: Monochrome symbol style matching ✥, ↻, ✎, ⌫
        self.float_btn_note = QPushButton("🗈")
        self.float_btn_note.setFixedSize(42, 42)
        self.float_btn_note.setCheckable(True)
        self.float_btn_note.setEnabled(False)
        self.float_btn_note.setStyleSheet(FLOATING_BTN_STYLE)
        self.float_btn_note.setToolTip("Add Note (Click on chart to place a text note)")
        self.float_btn_note.clicked.connect(self.toggle_note_mode)
        fp_layout.addWidget(self.float_btn_note)

        # Requirement 2: Crisp monochrome outline warning triangle matching the blue vector style of floating buttons
        self.float_btn_error = QPushButton()
        self.float_btn_error.setIcon(create_warning_icon(24))
        self.float_btn_error.setIconSize(QSize(24, 24))
        self.float_btn_error.setFixedSize(42, 42)
        self.float_btn_error.setCheckable(True)
        self.float_btn_error.setEnabled(False)
        self.float_btn_error.setStyleSheet(FLOATING_BTN_STYLE)
        self.float_btn_error.setToolTip("Record Error (Click on chart to log and pin error)")
        self.float_btn_error.clicked.connect(self.toggle_error_pin_mode)
        fp_layout.addWidget(self.float_btn_error)

        # Requirement 4: Updated clear button triggering drawing selection dialog
        self.float_btn_clear = QPushButton("⌫")
        self.float_btn_clear.setFixedSize(42, 42)
        self.float_btn_clear.setEnabled(False)
        self.float_btn_clear.setStyleSheet(FLOATING_BTN_STYLE)
        self.float_btn_clear.setToolTip("Clear Drawings")
        self.float_btn_clear.clicked.connect(self.prompt_clear_drawings)
        fp_layout.addWidget(self.float_btn_clear)

        # Requirement 5: Save Annotated Chart floating button matching symbol style
        self.float_btn_save = QPushButton("🖫")
        self.float_btn_save.setFixedSize(42, 42)
        self.float_btn_save.setEnabled(False)
        self.float_btn_save.setStyleSheet(FLOATING_BTN_STYLE)
        self.float_btn_save.setToolTip("Save Annotated Chart to Report")
        self.float_btn_save.clicked.connect(self.save_annotated_chart)
        fp_layout.addWidget(self.float_btn_save)

        self.floating_panel.adjustSize()
        self.floating_panel.move(16, 16)
        self.floating_panel.raise_()
        self.scroll_area.viewport().installEventFilter(self)

    def eventFilter(self, watched, event):
        if hasattr(self, 'scroll_area') and watched == self.scroll_area.viewport():
            if event.type() == QEvent.Resize and hasattr(self, 'floating_panel') and self.floating_panel:
                self.floating_panel.move(16, 16)
                self.floating_panel.raise_()
        return super().eventFilter(watched, event)

    def on_drawing_added(self):
        self.btn_save_annotated.setEnabled(True)
        if hasattr(self, 'float_btn_save'):
            self.float_btn_save.setEnabled(True)
        self.btn_clear_draw.setEnabled(True)
        if hasattr(self, 'float_btn_clear'):
            self.float_btn_clear.setEnabled(True)

    def save_annotated_chart(self):
        pixmap = self.chart_display.get_annotated_pixmap()
        if pixmap and not pixmap.isNull():
            self.saved_annotated_pixmaps.append(pixmap)
            parent_win = self.window()
            tab_report = getattr(parent_win, 'tab_report', None)
            if tab_report:
                tab_report.refresh_evidence_list()
                tab_report.update_summary_metrics()
            QMessageBox.information(
                self, "Success", 
                f"Annotated chart successfully saved to report evidence list! (Total saved: {len(self.saved_annotated_pixmaps)})"
            )

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
            
            # Auto-add to report tab checked charts list
            parent_win = self.window()
            report_tab = getattr(parent_win, 'tab_report', None)
            if report_tab:
                report_tab.auto_add_checked_chart(filename)

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

    def set_flicker_ui_off(self):
        self.btn_flicker.setText("Start Flicker")
        self.btn_flicker.setStyleSheet(FLICKER_BTN_STYLE_OFF)

    def set_flicker_ui_on(self):
        self.btn_flicker.setText("Pause Flicker")
        self.btn_flicker.setStyleSheet(FLICKER_BTN_STYLE_ON)

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
        self.set_flicker_ui_off()
        self.btn_reset_align.setEnabled(True)
        self.btn_toggle_drag.setEnabled(True)
        self.btn_rotate_ccw.setEnabled(True)
        self.btn_rotate_cw.setEnabled(True)
        self.btn_rotate_90.setEnabled(True)
        self.btn_draw.setEnabled(True)
        self.btn_note.setEnabled(True)
        self.btn_remove_note.setEnabled(len(self.chart_display.notes) > 0)
        self.btn_pin_error.setEnabled(True)
        self.btn_clear_draw.setEnabled(True)
        
        # Enable floating overlay buttons
        self.float_btn_drag.setEnabled(True)
        self.float_btn_rotate.setEnabled(True)
        self.float_btn_draw.setEnabled(True)
        self.float_btn_note.setEnabled(True)
        self.float_btn_error.setEnabled(True)
        self.float_btn_clear.setEnabled(True)
        self.float_btn_save.setEnabled(True)
        self.floating_panel.raise_()

        # Restore any existing error markers for this chart from ErrorsTab
        parent_win = self.window()
        tab_errors = getattr(parent_win, 'tab_errors', None)
        if tab_errors and hasattr(tab_errors, 'errors_list'):
            current_chart = ""
            if self.path_updated:
                current_chart = self.path_updated.replace('\\', '/').split('/')[-1]
            existing_ids = {m.get("id") for m in self.chart_display.error_markers}
            for err in tab_errors.errors_list:
                if err.id.startswith("ERR-") and (not err.chart or not current_chart or err.chart == current_chart):
                    if err.id not in existing_ids:
                        self.add_error_marker_from_log({
                            "id": err.id,
                            "type": err.type,
                            "description": err.description,
                            "severity": err.severity,
                            "chart": err.chart,
                            "comments": err.comments
                        })
                        existing_ids.add(err.id)
        
        self.charts_loaded.emit()
        QMessageBox.information(self, "Success", "Charts loaded successfully.")

    def reset_session(self):
        self.flicker_manager.pause()
        self.set_flicker_ui_off()
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
        self.btn_reset_align.setEnabled(False)
        self.btn_toggle_drag.setEnabled(False)
        self.btn_rotate_ccw.setEnabled(False)
        self.btn_rotate_cw.setEnabled(False)
        self.btn_rotate_90.setEnabled(False)
        self.lbl_angle.setText("Angle: 0.0°")
        self.btn_draw.setEnabled(False)
        self.btn_note.setEnabled(False)
        self.btn_remove_note.setEnabled(False)
        self.btn_remove_note.setText("Remove Note")
        self.btn_pin_error.setEnabled(False)
        self.btn_clear_draw.setEnabled(False)
        self.btn_save_annotated.setEnabled(False)
        self.btn_load.setEnabled(False)
        
        # Reset tool mode
        self.set_active_tool_mode("none")
        
        # Reset floating overlay buttons
        self.float_btn_drag.setEnabled(False)
        self.float_btn_drag.setChecked(False)
        self.float_btn_rotate.setEnabled(False)
        self.float_btn_draw.setEnabled(False)
        self.float_btn_draw.setChecked(False)
        self.float_btn_note.setEnabled(False)
        self.float_btn_note.setChecked(False)
        self.float_btn_error.setEnabled(False)
        self.float_btn_error.setChecked(False)
        self.float_btn_clear.setEnabled(False)
        self.float_btn_save.setEnabled(False)
        
        self.charts_cleared.emit()
        QMessageBox.information(self, "Reset", "Comparison session cleared. Previously defined error logs remain intact.")

    def on_rotation_changed(self, angle: float):
        self.lbl_angle.setText(f"Angle: {angle:.1f}°")

    def on_opacity_changed(self, value):
        self.chart_display.set_opacity(value / 100.0)

    def on_note_selected_changed(self, note_id: str):
        """Updates Remove Note button when user clicks a note on chart."""
        if note_id:
            self.btn_remove_note.setEnabled(True)
            self.btn_remove_note.setText(f"Remove Note ({note_id})")
        else:
            self.btn_remove_note.setText("Remove Note")
            self.btn_remove_note.setEnabled(len(self.chart_display.notes) > 0)

    def set_active_tool_mode(self, mode_name: str):
        """Unified mode controller ensuring tool mutually exclusive states."""
        if mode_name in ("drag", "draw", "note", "error") and self.flicker_manager.timer.isActive():
            self.flicker_manager.pause()
            self.set_flicker_ui_off()

        self.chart_display.drag_mode_enabled = (mode_name == "drag")
        self.chart_display.drawing_mode = (mode_name == "draw")
        self.chart_display.note_mode_enabled = (mode_name == "note")
        self.chart_display.error_mode_enabled = (mode_name == "error")

        if mode_name in ("draw", "note", "error"):
            self.chart_display.setCursor(Qt.CrossCursor)
        elif mode_name == "drag":
            self.chart_display.setCursor(Qt.OpenHandCursor)
        else:
            self.chart_display.setCursor(Qt.ArrowCursor)

        # Update button states (Blue theme for active state)
        if mode_name == "drag":
            self.btn_toggle_drag.setText("Drag Mode: ON")
            self.btn_toggle_drag.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold;")
            self.float_btn_drag.setChecked(True)
        else:
            self.btn_toggle_drag.setText("Drag Mode: OFF")
            self.btn_toggle_drag.setStyleSheet("background-color: #10B981; color: white; font-weight: bold;")
            self.float_btn_drag.setChecked(False)

        if mode_name == "draw":
            self.btn_draw.setText("Draw Highlight: ON")
            self.btn_draw.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold;")
            self.float_btn_draw.setChecked(True)
        else:
            self.btn_draw.setText("Draw Highlight: OFF")
            self.btn_draw.setStyleSheet("")
            self.float_btn_draw.setChecked(False)

        if mode_name == "note":
            self.btn_note.setText("Add Note: ON")
            self.btn_note.setStyleSheet("background-color: #0284C7; color: white; font-weight: bold;")
            self.float_btn_note.setChecked(True)
        else:
            self.btn_note.setText("Add Note: OFF")
            self.btn_note.setStyleSheet("")
            self.float_btn_note.setChecked(False)

        if mode_name == "error":
            self.btn_pin_error.setText("Record Error: ON")
            self.btn_pin_error.setStyleSheet("background-color: #EF4444; color: white; font-weight: bold;")
            self.float_btn_error.setChecked(True)
        else:
            self.btn_pin_error.setText("Record Error: OFF")
            self.btn_pin_error.setStyleSheet("")
            self.float_btn_error.setChecked(False)

    def toggle_drag_mode(self, *args):
        new_mode = "none" if self.chart_display.drag_mode_enabled else "drag"
        self.set_active_tool_mode(new_mode)

    def toggle_drawing_mode(self, *args):
        new_mode = "none" if self.chart_display.drawing_mode else "draw"
        self.set_active_tool_mode(new_mode)

    def toggle_note_mode(self, *args, **kwargs):
        """Item 1: Correctly toggles Note mode whether called from button click or code."""
        new_mode = "none" if self.chart_display.note_mode_enabled else "note"
        self.set_active_tool_mode(new_mode)

    def disable_note_mode(self):
        """Turns off Note mode and restores normal cursor."""
        self.set_active_tool_mode("none")

    def toggle_error_pin_mode(self, *args, **kwargs):
        """Item 1: Correctly toggles Record Error mode whether called from button click or code."""
        new_mode = "none" if self.chart_display.error_mode_enabled else "error"
        self.set_active_tool_mode(new_mode)

    def disable_error_pin_mode(self):
        """Turns off Record Error mode and restores normal cursor."""
        self.set_active_tool_mode("none")

    def on_note_point_selected(self, pt: QPointF):
        """Places a text note callout at clicked chart coordinates and registers in Errors tab (Item 4)."""
        parent_win = self.window()
        tab_errors = getattr(parent_win, 'tab_errors', None)
        note_id = tab_errors.get_next_note_id() if tab_errors else "NT-001"

        chart_name = ""
        if self.path_updated:
            chart_name = self.path_updated.replace('\\', '/').split('/')[-1]

        # Requirement 5: Dedicated dialog with wrapped text
        dialog = EditNoteDialog(note_id, "", self, is_new=True)
        if dialog.exec():
            note_text = dialog.get_text()
            if note_text:
                note_obj = {
                    "id": note_id,
                    "pos": pt,
                    "text": note_text,
                    "chart": chart_name
                }
                self.chart_display.notes.append(note_obj)
                self.chart_display.selected_note = note_obj
                self.chart_display.update()
                self.btn_save_annotated.setEnabled(True)
                if hasattr(self, 'float_btn_save'):
                    self.float_btn_save.setEnabled(True)
                self.btn_remove_note.setEnabled(True)
                self.btn_remove_note.setText(f"Remove Note ({note_id})")

                # Item 4: List in Errors tab with ID NT-00x, Type N/A, Severity N/A
                if tab_errors:
                    new_note_err = ErrorItem(
                        error_id=note_id,
                        err_type="N/A",
                        description=note_text,
                        chart=chart_name,
                        severity="N/A",
                        comments="Chart Note"
                    )
                    tab_errors.errors_list.append(new_note_err)
                    tab_errors.populate_table()
                    tab_errors.btn_edit.setEnabled(True)
                    tab_errors.btn_delete.setEnabled(True)
                    tab_errors.error_added.emit()

                tab_report = getattr(parent_win, 'tab_report', None)
                if tab_report:
                    tab_report.update_summary_metrics()

        self.disable_note_mode()

    def on_error_point_selected(self, pt: QPointF):
        """Requirement 6: Opens Add Error dialog, saves to Errors tab, and pins Error ID badge to chart."""
        parent_win = self.window()
        tab_errors = getattr(parent_win, 'tab_errors', None)
        if not tab_errors:
            self.disable_error_pin_mode()
            return

        chart_name = ""
        if self.path_updated:
            chart_name = self.path_updated.replace('\\', '/').split('/')[-1]

        next_id = tab_errors.get_next_error_id()
        dialog = AddErrorDialog(next_id, None, chart_name, self)
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
                tab_errors.errors_list.append(new_err)
                tab_errors.populate_table()
                tab_errors.btn_edit.setEnabled(True)
                tab_errors.btn_delete.setEnabled(True)
                tab_errors.error_added.emit()

                # Requirement 6: Pin Error ID badge on the chart with full metadata
                self.chart_display.error_markers.append({
                    "pos": pt,
                    "id": data["id"],
                    "type": data["type"],
                    "description": data["description"],
                    "severity": data["severity"],
                    "chart": data["chart"],
                    "comments": data["comments"]
                })
                self.chart_display.update()
                self.btn_save_annotated.setEnabled(True)
                if hasattr(self, 'float_btn_save'):
                    self.float_btn_save.setEnabled(True)

                tab_report = getattr(parent_win, 'tab_report', None)
                if tab_report:
                    tab_report.update_summary_metrics()

        self.disable_error_pin_mode()

    def add_error_marker_from_log(self, data: dict):
        """Requirement 3: Adds an error marker in the upper left corner of the chart, fully editable and draggable."""
        error_id = data.get("id", "")
        if not error_id:
            return

        # Check if already present on the chart
        for m in self.chart_display.error_markers:
            if m.get("id") == error_id:
                m["type"] = data.get("type", "")
                m["description"] = data.get("description", "")
                m["severity"] = data.get("severity", "")
                m["chart"] = data.get("chart", "")
                m["comments"] = data.get("comments", "")
                self.chart_display.update()
                return

        # Calculate position in the upper left corner (stagger if multiple markers are in the corner)
        corner_markers = [
            m for m in self.chart_display.error_markers
            if m["pos"].x() < 320 and m["pos"].y() < 320
        ]
        stagger = len(corner_markers)
        pos_x = 45.0 + (stagger % 3) * 80.0
        pos_y = 45.0 + (stagger // 3) * 36.0

        marker_obj = {
            "pos": QPointF(pos_x, pos_y),
            "id": error_id,
            "type": data.get("type", ""),
            "description": data.get("description", ""),
            "severity": data.get("severity", ""),
            "chart": data.get("chart", ""),
            "comments": data.get("comments", "")
        }
        self.chart_display.error_markers.append(marker_obj)
        self.chart_display.update()
        self.btn_save_annotated.setEnabled(True)
        if hasattr(self, 'float_btn_save'):
            self.float_btn_save.setEnabled(True)

    def prompt_clear_drawings(self):
        """Requirement 4: Allows user to choose which drawing shall be removed or clear all."""
        if not self.chart_display.strokes:
            QMessageBox.information(self, "No Drawings", "There are no highlight drawings on the chart to remove.")
            return

        dialog = ClearDrawingsDialog(self.chart_display, self)
        dialog.exec()
        has_drawings = len(self.chart_display.strokes) > 0
        self.btn_clear_draw.setEnabled(has_drawings)
        if hasattr(self, 'float_btn_clear'):
            self.float_btn_clear.setEnabled(has_drawings)

    def remove_selected_note(self):
        """Item 3: Remove selected note or prompt to select which note to remove one by one."""
        if not self.chart_display.notes:
            QMessageBox.information(self, "No Notes", "There are no notes on the chart to remove.")
            return

        note_to_remove = self.chart_display.selected_note
        if not note_to_remove:
            items = [f"{n.get('id', 'NT')}: {n.get('text', '')[:40]}" for n in self.chart_display.notes]
            chosen, ok = QInputDialog.getItem(
                self, "Select Note to Remove", "Choose a note to remove:", items, 0, False
            )
            if ok and chosen:
                chosen_id = chosen.split(":")[0].strip()
                for n in self.chart_display.notes:
                    if n.get("id") == chosen_id:
                        note_to_remove = n
                        break

        if note_to_remove:
            note_id = note_to_remove.get("id", "")
            self.delete_note_by_id(note_id)

    def delete_note_by_id(self, note_id: str, prompt_confirmation: bool = True):
        """Removes a note by ID from chart and errors list."""
        if prompt_confirmation:
            confirm = QMessageBox.question(
                self, "Confirm Remove Note",
                f"Are you sure you want to remove note {note_id}?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return

        self.chart_display.notes = [n for n in self.chart_display.notes if n.get("id") != note_id]
        if self.chart_display.selected_note and self.chart_display.selected_note.get("id") == note_id:
            self.chart_display.selected_note = None
        self.chart_display.update()

        parent_win = self.window()
        tab_errors = getattr(parent_win, 'tab_errors', None)
        if tab_errors:
            tab_errors.errors_list = [e for e in tab_errors.errors_list if e.id != note_id]
            tab_errors.populate_table()
            tab_errors.btn_edit.setEnabled(len(tab_errors.errors_list) > 0)
            tab_errors.btn_delete.setEnabled(len(tab_errors.errors_list) > 0)

        tab_report = getattr(parent_win, 'tab_report', None)
        if tab_report:
            tab_report.update_summary_metrics()

        self.btn_remove_note.setText("Remove Note")
        self.btn_remove_note.setEnabled(len(self.chart_display.notes) > 0)
        if prompt_confirmation:
            QMessageBox.information(self, "Success", f"Note {note_id} has been removed.")

    def edit_note_by_id(self, note_id: str):
        """Requirement 5: Edits note text by ID with wrapped text dialog fitting the window."""
        target_note = next((n for n in self.chart_display.notes if n.get("id") == note_id), None)
        if not target_note:
            return
        dialog = EditNoteDialog(note_id, target_note.get("text", ""), self, is_new=False)
        if dialog.exec():
            new_text = dialog.get_text()
            if new_text:
                target_note["text"] = new_text
                self.chart_display.update()

                parent_win = self.window()
                tab_errors = getattr(parent_win, 'tab_errors', None)
                if tab_errors:
                    for e in tab_errors.errors_list:
                        if e.id == note_id:
                            e.description = new_text
                            break
                    tab_errors.populate_table()

    def on_error_selected_changed(self, error_id: str):
        """Callback when an error marker is selected on the chart."""
        pass

    def edit_error_by_id(self, error_id: str):
        """Requirement 6: Edit error directly from Chart Comparison tab using the same principle as Notes."""
        parent_win = self.window()
        tab_errors = getattr(parent_win, 'tab_errors', None)
        if not tab_errors:
            return

        error_item = next((e for e in tab_errors.errors_list if e.id == error_id), None)
        if not error_item:
            return

        existing_data = {
            "type": error_item.type,
            "description": error_item.description,
            "chart": error_item.chart,
            "severity": error_item.severity,
            "comments": error_item.comments
        }

        default_chart = ""
        if self.path_updated:
            default_chart = self.path_updated.replace('\\', '/').split('/')[-1]

        dialog = AddErrorDialog(error_id, existing_data, default_chart, self)
        if dialog.exec():
            data = dialog.error_data
            if data:
                error_item.type = data["type"]
                error_item.description = data["description"]
                error_item.chart = data["chart"]
                error_item.severity = data["severity"]
                error_item.comments = data["comments"]
                tab_errors.populate_table()

                # Update error marker on chart
                for m in self.chart_display.error_markers:
                    if m.get("id") == error_id:
                        m["type"] = data["type"]
                        m["description"] = data["description"]
                        m["severity"] = data["severity"]
                        m["chart"] = data["chart"]
                        m["comments"] = data["comments"]
                        break
                self.chart_display.update()

                tab_report = getattr(parent_win, 'tab_report', None)
                if tab_report:
                    tab_report.update_summary_metrics()

                QMessageBox.information(self, "Success", f"Error {error_id} has been updated.")

    def delete_error_by_id(self, error_id: str, prompt_confirmation: bool = True):
        """Requirement 6: Delete error by ID directly from Chart Comparison tab."""
        if prompt_confirmation:
            confirm = QMessageBox.question(
                self, "Confirm Remove Error",
                f"Are you sure you want to remove error {error_id}?",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if confirm != QMessageBox.Yes:
                return

        self.chart_display.error_markers = [
            m for m in self.chart_display.error_markers if m.get("id") != error_id
        ]
        if getattr(self.chart_display, 'selected_error', None) and self.chart_display.selected_error.get("id") == error_id:
            self.chart_display.selected_error = None
        self.chart_display.update()

        parent_win = self.window()
        tab_errors = getattr(parent_win, 'tab_errors', None)
        if tab_errors:
            tab_errors.errors_list = [e for e in tab_errors.errors_list if e.id != error_id]
            tab_errors.populate_table()
            tab_errors.btn_edit.setEnabled(len(tab_errors.errors_list) > 0)
            tab_errors.btn_delete.setEnabled(len(tab_errors.errors_list) > 0)

        tab_report = getattr(parent_win, 'tab_report', None)
        if tab_report:
            tab_report.update_summary_metrics()

        if prompt_confirmation:
            QMessageBox.information(self, "Success", f"Error {error_id} has been removed.")

    def set_view_mode(self, mode):
        self.flicker_manager.pause()
        self.set_flicker_ui_off()
        self.chart_display.set_active_view(mode)

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
            self.set_flicker_ui_off()
            self.chart_display.set_active_view("Both")
        else:
            if self.chart_display.drag_mode_enabled:
                self.set_active_tool_mode("none")
            
            self.flicker_manager.start()
            self.set_flicker_ui_on()

    def change_flicker_interval(self, index):
        intervals = [0.2, 0.5, 1.0, 2.0, 3.0]
        self.flicker_manager.set_interval(intervals[index])

    def on_flicker_state_changed(self, chart):
        self.chart_display.set_active_view(chart)