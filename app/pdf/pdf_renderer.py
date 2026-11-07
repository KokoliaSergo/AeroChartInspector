import pymupdf
from PySide6.QtGui import QImage, QPixmap

class PDFRenderer:
    @staticmethod
    def render_page_to_pixmap(page: pymupdf.Page, zoom: float = 1.0) -> QPixmap:
        mat = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
        # Convert to ARGB32 so QPainter setOpacity blending works correctly
        img_rgba = img.convertToFormat(QImage.Format_ARGB32)
        return QPixmap.fromImage(img_rgba)