from PySide6.QtCore import QObject, QTimer, Signal

class FlickerManager(QObject):
    state_changed = Signal(str)  # Emits "Updated chart" or "Old chart"

    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QTimer(self)
        self.timer.setInterval(1000)  # Default 1.0 second interval
        self.timer.timeout.connect(self.toggle)
        self.current_state = "Updated chart"

    def start(self):
        self.timer.start()

    def pause(self):
        self.timer.stop()

    def set_interval(self, seconds: float):
        self.timer.setInterval(int(seconds * 1000))

    def toggle(self):
        if self.current_state == "Updated chart":
            self.current_state = "Old chart"
        else:
            self.current_state = "Updated chart"
        self.state_changed.emit(self.current_state)