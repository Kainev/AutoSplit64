from PySide6.QtWidgets import (
    QFrame
)


class HLine(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.setFrameShape(QFrame.Shape.HLine)
        self.setFrameShadow(QFrame.Shadow.Plain)

        self.setStyleSheet("QFrame { color: palette(base); }")
